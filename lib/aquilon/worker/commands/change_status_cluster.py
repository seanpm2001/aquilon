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
"""Contains the logic for `aq change status --cluster`."""

from aquilon.aqdb.model import Cluster, MetaCluster, ClusterLifecycle
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.templates import Plenary, PlenaryCollection, TemplateDomain


class CommandChangeClusterStatus(BrokerCommand):

    required_parameters = ["cluster"]

    def render(self, session, logger, cluster, metacluster, buildstatus,
               **arguments):
        if cluster:
            # TODO: disallow metaclusters here
            dbcluster = Cluster.get_unique(session, cluster, compel=True)
            if isinstance(dbcluster, MetaCluster):
                logger.client_info("Please use the --metacluster option for "
                                   "metaclusters.")
        else:
            dbcluster = MetaCluster.get_unique(session, metacluster,
                                               compel=True)

        dbstatus = ClusterLifecycle.get_instance(session, buildstatus)

        if not dbcluster.status.transition(dbcluster, dbstatus):
            return

        if not dbcluster.archetype.is_compileable:
            return

        session.flush()

        plenaries = PlenaryCollection(logger=logger)
        plenaries.append(Plenary.get_plenary(dbcluster,
                                             allow_incomplete=False))
        plenaries.extend(Plenary.get_plenary(dbhost, allow_incomplete=False)
                         for dbhost in dbcluster.hosts)

        td = TemplateDomain(dbcluster.branch, dbcluster.sandbox_author,
                            logger=logger)
        # Force a host lock as pan might overwrite the profile...
        with plenaries.get_key():
            plenaries.stash()
            try:
                plenaries.write(locked=True)
                td.compile(session, only=plenaries.object_templates,
                           locked=True)
            except:
                plenaries.restore_stash()
                raise
        return
