#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""
Module for testing the broker commands.

Ideally, real unit tests are self-contained.  In practice, for many of
these commands that would be painful.  The 'del' commands generally rely
on some 'add' commands having been run first.  The same holds for 'bind'
and 'unbind', 'map' and 'unmap', etc.
"""

import os
import sys
import unittest

if __name__ == "__main__":
    BINDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    SRCDIR = os.path.join(BINDIR, "..", "..")
    sys.path.append(os.path.join(SRCDIR, "lib", "python2.5"))

from test_start import TestBrokerStart
from test_ping import TestPing
from test_status import TestStatus
from test_permission import TestPermission
from test_add_dns_domain import TestAddDnsDomain
from test_add_domain import TestAddDomain
from test_get_domain import TestGetDomain
from test_put_domain import TestPutDomain
from test_deploy_domain import TestDeployDomain
from test_sync_domain import TestSyncDomain
from test_add_service import TestAddService
from test_add_required_service import TestAddRequiredService
from test_add_building import TestAddBuilding
from test_add_rack import TestAddRack
from test_add_cpu import TestAddCpu
from test_add_model import TestAddModel
from test_add_tor_switch import TestAddTorSwitch
from test_add_chassis import TestAddChassis
from test_add_machine import TestAddMachine
from test_add_disk import TestAddDisk
from test_add_interface import TestAddInterface
from test_add_host import TestAddHost
from test_add_aquilon_host import TestAddAquilonHost
from test_add_windows_host import TestAddWindowsHost
from test_add_aurora_host import TestAddAuroraHost
from test_map_service import TestMapService
from test_bind_client import TestBindClient
from test_make_aquilon import TestMakeAquilon
from test_unbind_client import TestUnbindClient
from test_rebind_client import TestRebindClient
from test_reconfigure import TestReconfigure
from test_bind_server import TestBindServer
from test_constraints_bind_server import TestBindServerConstraints
from test_constraints_domain import TestDomainConstraints
from test_constraints_machine import TestMachineConstraints
from test_constraints_tor_switch import TestTorSwitchConstraints
from test_show_hostiplist import TestShowHostIPList
from test_show_hostmachinelist import TestShowHostMachineList
from test_show_service_all import TestShowServiceAll
from test_update_interface import TestUpdateInterface
from test_pxeswitch import TestPxeswitch
from test_manage import TestManage
from test_constraints_umask import TestUmaskConstraints
from test_unbind_server import TestUnbindServer
from test_unmap_service import TestUnmapService
from test_del_host import TestDelHost
from test_del_interface import TestDelInterface
from test_del_disk import TestDelDisk
from test_del_machine import TestDelMachine
from test_del_chassis import TestDelChassis
from test_del_tor_switch import TestDelTorSwitch
from test_del_model import TestDelModel
from test_del_cpu import TestDelCpu
from test_del_rack import TestDelRack
from test_del_building import TestDelBuilding
from test_del_required_service import TestDelRequiredService
from test_del_service import TestDelService
from test_del_domain import TestDelDomain
from test_del_dns_domain import TestDelDnsDomain
from test_client_failure import TestClientFailure
from test_stop import TestBrokerStop


class BrokerTestSuite(unittest.TestSuite):
    """Set up the broker's unit tests in an order that allows full coverage.

    The general strategy is to start the broker, test adding things,
    test deleting things, and then shut down the broker.  Most of the show
    commands are tested as verification tests in add/del tests.  Those that
    are not have explicit tests between add and delete.

    """

    def __init__(self, *args, **kwargs):
        unittest.TestSuite.__init__(self, *args, **kwargs)
        for test in [TestBrokerStart, TestPing, TestStatus, TestPermission,
                TestAddDnsDomain, TestAddDomain,
                TestGetDomain, TestPutDomain, TestDeployDomain, TestSyncDomain,
                TestAddService, TestAddRequiredService, TestAddBuilding,
                TestAddRack, TestAddCpu, TestAddModel, TestAddTorSwitch,
                TestAddChassis, TestAddMachine, TestAddDisk, TestAddInterface,
                TestAddHost,
                TestAddAquilonHost, TestAddWindowsHost, TestAddAuroraHost,
                TestMapService, TestBindClient, TestMakeAquilon,
                TestUnbindClient, TestRebindClient, TestReconfigure,
                TestBindServer,
                TestBindServerConstraints,
                TestDomainConstraints, TestMachineConstraints,
                TestTorSwitchConstraints,
                TestShowHostIPList, TestShowHostMachineList,
                TestShowServiceAll,
                TestUpdateInterface,
                TestPxeswitch, TestManage,
                TestUmaskConstraints,
                TestUnbindServer, TestUnmapService, TestDelHost,
                TestDelInterface, TestDelDisk, TestDelMachine, TestDelChassis,
                TestDelTorSwitch, TestDelModel, TestDelCpu, TestDelRack,
                TestDelBuilding, TestDelRequiredService, TestDelService,
                TestDelDomain, TestDelDnsDomain,
                TestClientFailure,
                TestBrokerStop]:
            self.addTest(unittest.TestLoader().loadTestsFromTestCase(test))


if __name__=='__main__':
    suite = BrokerTestSuite()
    unittest.TextTestRunner(verbosity=2).run(suite)

