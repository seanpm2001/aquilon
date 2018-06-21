# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018  Contributor
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Contains the logic for `aq add chassis`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.types import ChassisType
from aquilon.aqdb.model import Chassis, Model
from aquilon.aqdb.model.network import get_net_id_from_ip
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.dns import grab_address
from aquilon.worker.dbwrappers.grn import lookup_grn
from aquilon.worker.dbwrappers.hardware_entity import (
    get_default_chassis_grn_eonid,
    update_primary_ip,
)
from aquilon.worker.dbwrappers.interface import (get_or_create_interface,
                                                 check_ip_restrictions,
                                                 assign_address)
from aquilon.worker.dbwrappers.location import get_location
from aquilon.exceptions_ import NotFoundException
from aquilon.worker.processes import DSDBRunner


class CommandAddChassis(BrokerCommand):

    required_parameters = ["chassis", "rack", "model"]

    def render(self, session, logger, chassis, label, rack, model, vendor,
               ip, interface, mac, serial, comments, grn, eon_id, exporter,
               **_):
        dbdns_rec, _ = grab_address(session, chassis, ip,
                                    allow_restricted_domain=True,
                                    allow_reserved=True, preclude=True,
                                    exporter=exporter, require_grn=False)
        if not label:
            label = dbdns_rec.fqdn.name
            try:
                Chassis.check_label(label)
            except ArgumentError:
                raise ArgumentError("Could not deduce a valid hardware label "
                                    "from the chassis name.  Please specify "
                                    "--label.")

        dblocation = get_location(session, rack=rack)
        dbmodel = Model.get_unique(session, name=model, vendor=vendor,
                                   model_type=ChassisType.Chassis)
        if not dbmodel:
            dbmodel = Model.get_unique(session, name=model, vendor=vendor,
                                       model_type=ChassisType.AuroraChassis)
        if not dbmodel:
            raise NotFoundException("Model {}, model_type chassis or aurora_chassis not found.".format(model))

        # FIXME: Precreate chassis slots?
        dbchassis = Chassis(label=label, location=dblocation, model=dbmodel,
                            serial_no=serial, comments=comments)
        session.add(dbchassis)
        dbchassis.primary_name = dbdns_rec

        # Set the GRN for the chassis
        if not grn and not eon_id:
            grn, eon_id = get_default_chassis_grn_eonid(self.config)

        dbgrn = lookup_grn(session, grn, eon_id, logger=logger,
                           config=self.config)
        dbchassis.owner_grn = dbgrn

        # FIXME: get default name from the model
        if not interface:
            interface = "oa"
        dbinterface = get_or_create_interface(session, dbchassis,
                                              name=interface, mac=mac,
                                              interface_type="oa")
        if ip:
            dbnetwork = get_net_id_from_ip(session, ip)
            check_ip_restrictions(dbnetwork, ip)
            assign_address(dbinterface, ip, dbnetwork, logger=logger)

        session.flush()

        if ip:
            dsdb_runner = DSDBRunner(logger=logger)
            dsdb_runner.update_host(dbchassis, None)
            dsdb_runner.commit_or_rollback("Could not add chassis to DSDB")
        return
