# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013,2014  Contributor
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
"""Host formatter."""

from operator import attrgetter
from six import iteritems

from aquilon.aqdb.model import Host
from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.worker.formats.compileable import CompileableFormatter
from aquilon.worker.formats.list import ListFormatter
from aquilon.worker.dbwrappers.feature import (model_features,
                                               personality_features)


class HostFormatter(CompileableFormatter):
    def fill_proto(self, host, skeleton, embedded=True, indirect_attrs=True):
        super(HostFormatter, self).fill_proto(host, skeleton)
        skeleton.type = "host"  # Deprecated
        dbhw_ent = host.hardware_entity
        skeleton.hostname = str(dbhw_ent.primary_name.fqdn.name)
        skeleton.fqdn = str(dbhw_ent.primary_name.fqdn)
        skeleton.dns_domain = str(dbhw_ent.primary_name.fqdn.dns_domain.name)
        skeleton.sysloc = str(dbhw_ent.location.sysloc())
        if dbhw_ent.primary_ip:
            skeleton.ip = str(dbhw_ent.primary_ip)
        for iface in dbhw_ent.interfaces:
            if iface.interface_type != 'public' or not iface.bootable:
                continue
            skeleton.mac = str(iface.mac)

        if host.resholder:
            self.redirect_proto(host.resholder.resources, skeleton.resources)

        if host.cluster and not embedded:
            skeleton.cluster = host.cluster.name

        skeleton.owner_eonid = host.effective_owner_grn.eon_id
        self.redirect_proto(host.archetype, skeleton.archetype)  # Deprecated
        self.redirect_proto(host.operating_system, skeleton.operating_system)
        self.redirect_proto(dbhw_ent, skeleton.machine)

        for si in host.services_used:
            srv_msg = skeleton.services_used.add()
            srv_msg.service = si.service.name
            srv_msg.instance = si.name
        for srv in host.services_provided:
            si = srv.service_instance
            srv_msg = skeleton.services_provided.add()
            srv_msg.service = si.service.name
            srv_msg.instance = si.name

        for target, eon_id_set in iteritems(host.effective_grns):
            for grn_rec in eon_id_set:
                map = skeleton.eonid_maps.add()
                map.target = target
                map.eonid = grn_rec.eon_id

        if host.virtual_switch:
            self.redirect_proto(host.virtual_switch, skeleton.virtual_switch)

    def format_raw(self, host, indent="", embedded=True, indirect_attrs=True):
        # The 'aq show host' command returns a host object; however, we
        # want to display the information about the hardware entity
        # (machine or network_device) first, so we redirect.  The
        # formatters should subclass HardwareEntityFormatter, then call
        # redirect_raw_host_details to display the actual host details.
        return self.redirect_raw(host.hardware_entity, indent)

    def format_raw_host_details(self, host, indent="", embedded=True,
                                indirect_attrs=True):
        # Subclasses of HardwareEntityFormatter that have an associated
        # host object can call redirect_raw_host_details, which will in
        # turn invoke this method.
        details = []
        if host.cluster:
            details.append(indent + "  Member of {0:c}: {0.name}"
                           .format(host.cluster))
        if host.resholder and host.resholder.resources:
            details.append(indent + "  Resources:")
            for resource in sorted(host.resholder.resources,
                                   key=attrgetter('resource_type', 'name')):
                details.append(self.redirect_raw(resource, indent + "    "))

        # TODO: supress features when redirecting personality/archetype
        details.append(self.redirect_raw(host.personality, indent + "  "))
        details.append(self.redirect_raw(host.archetype, indent + "  "))

        details.append(self.redirect_raw(host.operating_system, indent + "  "))
        details.append(indent + "  {0:c}: {1}"
                       .format(host.branch, host.authored_branch))
        details.append(self.redirect_raw(host.status, indent + "  "))
        details.append(indent +
                       "  Advertise Status: %s" % host.advertise_status)

        if host.owner_grn:
            details.append(indent + "  Owned by {0:c}: {0.grn}"
                           .format(host.owner_grn))
        for grn_rec in sorted(host.grns, key=attrgetter("target", "eon_id")):
            details.append(indent + "  Used by {0.grn:c}: {0.grn.grn} "
                           "[target: {0.target}]".format(grn_rec))

        if host.virtual_switch:
            details.append(self.redirect_raw(host.virtual_switch,
                                             indent + "  "))

        for feature in sorted(model_features(host.hardware_entity.model,
                                             host.archetype, host.personality),
                              key=attrgetter('name')):
            details.append(indent + "  {0:c}: {0.name}".format(feature))
        (pre, post) = personality_features(host.personality)
        for feature in sorted(pre, key=attrgetter('name')):
            details.append(indent + "  {0:c}: {0.name} [pre_personality]"
                           .format(feature))
        for feature in sorted(post, key=attrgetter('name')):
            details.append(indent + "  {0:c}: {0.name} [post_personality]"
                           .format(feature))

        for si in sorted(host.services_used,
                         key=attrgetter("service.name", "name")):
            details.append(indent + "  Uses Service: %s Instance: %s"
                           % (si.service.name, si.name))
        for srv in sorted(host.services_provided,
                          key=attrgetter("service_instance.service.name",
                                         "service_instance.name")):
            details.append(indent + "  Provides Service: %s Instance: %s"
                           % (srv.service_instance.service.name,
                              srv.service_instance.name))
            details.append(self.redirect_raw(srv, indent + "    "))
        if host.comments:
            details.append(indent + "  Comments: %s" % host.comments)

        return "\n".join(details)

ObjectFormatter.handlers[Host] = HostFormatter()


class GrnHostList(list):
    """By convention, holds a list of hosts to be formatted to provide
       (grn-only) data."""
    pass


class GrnHostListFormatter(ListFormatter):
    def format_raw(self, shlist, indent="", embedded=True,
                   indirect_attrs=True):
        details = []
        for host in shlist:
            if host.hardware_entity.primary_name:
                details.append(indent + "Primary Name: "
                                        "{0:a}".format(host.hardware_entity.primary_name))
            hstr = "  Owned by {0:c}: {0.grn}".format(host.effective_owner_grn)

            if host.effective_owner_grn == host.owner_grn:
                details.append(indent + hstr)
            else:
                details.append(indent + hstr + " [inherited]")

            eon_targets = [grn.target for grn in host.grns]
            for target, eon_id_set in iteritems(host.effective_grns):
                inherited = ""
                if target not in eon_targets:
                    inherited = " [inherited]"
                for grn_rec in sorted(eon_id_set):
                    details.append(indent + "  Used by {0:c}: {0.grn} "
                                            "[target: {1}]{2}"
                                   .format(grn_rec, target, inherited))
        return "\n".join(details)

    def format_proto(self, hostlist, container, embedded=True,
                     indirect_attrs=True):
        for host in hostlist:
            msg = container.add()
            dbhw_ent = host.hardware_entity
            # FIXME: this is wrong, hostname should be the short name
            msg.hostname = str(dbhw_ent.primary_name)
            msg.fqdn = str(dbhw_ent.primary_name)
            msg.dns_domain = str(dbhw_ent.primary_name.fqdn.dns_domain.name)
            self.redirect_proto(host.branch, msg.domain)
            msg.status = str(host.status.name)
            msg.owner_eonid = host.effective_owner_grn.eon_id

            msg.personality.archetype.name = str(host.archetype)
            msg.personality.name = str(host.personality)
            msg.personality.host_environment = str(host.personality.host_environment)
            msg.personality.owner_eonid = host.personality.owner_eon_id

            # eon id maps TBD need both effective and actual
            for grn_rec in sorted(host.personality.grns,
                                  key=attrgetter("target", "eon_id")):
                map = msg.personality.eonid_maps.add()
                map.target = grn_rec.target
                map.eonid = grn_rec.eon_id

            for target, eon_id_set in iteritems(host.effective_grns):
                for grn_rec in eon_id_set:
                    map = msg.eonid_maps.add()
                    map.target = target
                    map.eonid = grn_rec.eon_id

ObjectFormatter.handlers[GrnHostList] = GrnHostListFormatter()
