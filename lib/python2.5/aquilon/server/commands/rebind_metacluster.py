# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2008,2009  Contributor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the EU DataGrid Software License.  You should
# have received a copy of the license with this program, and the
# license is published at
# http://eu-datagrid.web.cern.ch/eu-datagrid/license.html.
#
# THE FOLLOWING DISCLAIMER APPLIES TO ALL SOFTWARE CODE AND OTHER
# MATERIALS CONTRIBUTED IN CONNECTION WITH THIS PROGRAM.
#
# THIS SOFTWARE IS LICENSED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE AND ANY WARRANTY OF NON-INFRINGEMENT, ARE
# DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. THIS
# SOFTWARE MAY BE REDISTRIBUTED TO OTHERS ONLY BY EFFECTIVELY USING
# THIS OR ANOTHER EQUIVALENT DISCLAIMER AS WELL AS ANY OTHER LICENSE
# TERMS THAT MAY APPLY.


from aquilon.exceptions_ import NotFoundException, ArgumentError
from aquilon.server.broker import BrokerCommand
from aquilon.server.dbwrappers.host import hostname_to_host
from aquilon.aqdb.model import MetaCluster, Cluster, MetaClusterMember


class CommandRebindMetaCluster(BrokerCommand):

    required_parameters = ["metacluster", "cluster", "cluster_type"]

    def render(self, session, hostname, cluster, cluster_type, **arguments):
        dbhost = hostname_to_host(session, hostname)
        dbcluster = Cluster.get_unique(session, cluster,
                                       cluster_type=cluster_type)
        if not dbcluster:
            raise NotFoundException("%s cluster '%s' not found." %
                                    (cluster_type, cluster))
        dbmetacluster = MetaCluster.get_unique(session, metacluster)
        if not dbmetacluster:
            raise NotFoundException("MetaCluster '%s' not found." %
                                    metacluster)
        old_metacluster = None
        if dbcluster.mc_cluster and dbcluster.mc_cluster != dbmetacluster:
            old_metacluster = dbcluster.mc_cluster
            dbmcm = MetaClusterMember.get_unique(session,
                metacluster_id=old_metacluster.id, cluster_id=dbcluster.id)
            session.delete(dbmcm)
            session.refresh(dbcluster)
            session.refresh(old_metacluster)
        if not dbcluster.mc_cluster:
            if len(dbmetacluster.members) == dbmetacluster.max_clusters:
                raise ArgumentError("MetaCluster '%s' already contains "
                                    "the maximum number of clusters (%s)." %
                                    (metacluster, dbmetacluster.max_clusters))
            try:
                dbmcm = MetaClusterMember(metacluster=dbmetacluster,
                                          cluster=dbcluster)
                session.add(dbmcm)
            except ValueError, e:
                raise ArgumentError(e.message)
        # If this cluster is already bound to the metacluster,
        # rewrite the plenary anyway.

        session.flush()
        session.refresh(dbmetacluster)
        session.refresh(dbcluster)

        # FIXME: Rewrite/add the appropriate plenary files for
        # dbcluster, dbmetacluster, and old_metacluster
        return


