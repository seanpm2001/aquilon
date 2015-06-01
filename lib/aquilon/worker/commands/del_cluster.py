# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2014,2015  Contributor
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

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Cluster, ServiceAddress
from aquilon.worker.logger import CLIENT_INFO
from aquilon.notify.index import trigger_notifications
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.dbwrappers.resources import walk_resources
from aquilon.worker.dbwrappers.service_instance import check_no_provided_service
from aquilon.worker.templates import Plenary, PlenaryCollection


def del_cluster(session, logger, dbcluster, config):
    check_no_provided_service(dbcluster)

    if dbcluster.virtual_machines:
        machines = ", ".join(sorted(m.label for m in
                                    dbcluster.virtual_machines))
        raise ArgumentError("%s is still in use by virtual machines: %s." %
                            (format(dbcluster), machines))

    if hasattr(dbcluster, 'members') and dbcluster.members:
        raise ArgumentError("%s is still in use by clusters: %s." %
                            (format(dbcluster),
                             ", ".join(sorted(c.name for c in
                                              dbcluster.members))))
    elif dbcluster.hosts:
        hosts = ", ".join(sorted(h.fqdn for h in dbcluster.hosts))
        raise ArgumentError("%s is still in use by hosts: %s." %
                            (format(dbcluster), hosts))

    # Service addresses cannot be deleted by cascading rules only
    for res in walk_resources(dbcluster):
        if isinstance(res, ServiceAddress):
            raise ArgumentError("{0} still has {1:l} assigned, please delete "
                                "it first.".format(dbcluster, res))

    plenaries = PlenaryCollection(logger=logger)
    plenaries.append(Plenary.get_plenary(dbcluster))

    if dbcluster.metacluster:
        dbmetacluster = dbcluster.metacluster
        plenaries.append(Plenary.get_plenary(dbmetacluster))
        dbmetacluster.members.remove(dbcluster)
        dbmetacluster.validate()

    if dbcluster.resholder:
        plenaries.extend(map(Plenary.get_plenary,
                             dbcluster.resholder.resources))

    session.delete(dbcluster)

    session.flush()

    plenaries.write(remove_profile=True)

    trigger_notifications(config, logger, CLIENT_INFO)

    return


class CommandDelCluster(BrokerCommand):

    required_parameters = ["cluster"]

    def render(self, session, logger, cluster, **arguments):
        dbcluster = Cluster.get_unique(session, cluster, compel=True)
        del_cluster(session, logger, dbcluster, self.config)
