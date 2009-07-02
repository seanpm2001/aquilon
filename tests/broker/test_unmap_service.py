#!/usr/bin/env python2.5
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
"""Module for testing the unmap service command."""

import os
import sys
import unittest

if __name__ == "__main__":
    BINDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    SRCDIR = os.path.join(BINDIR, "..", "..")
    sys.path.append(os.path.join(SRCDIR, "lib", "python2.5"))

from brokertest import TestBrokerCommand


class TestUnmapService(TestBrokerCommand):

    def testunmapafs(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "afs", "--instance", "q.ny.ms.com",
                        "--archetype", "aquilon"])

    def testverifyunmapafs(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=afs", "--instance=q.ny.ms.com", "--building=ut"]
        self.notfoundtest(command)

    def testunmapdns(self):
        self.noouttest(["unmap", "service", "--hub", "ny",
                        "--service", "dns", "--instance", "nyinfratest",
                        "--archetype", "aquilon"])

    def testverifyunmapdns(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=dns", "--instance=nyinfratest", "--hub=ny"]
        self.notfoundtest(command)

    def testunmapaqd(self):
        self.noouttest(["unmap", "service", "--campus", "ny",
                        "--service", "aqd", "--instance", "ny-prod",
                        "--archetype", "aquilon"])

    def testverifyunmapaqd(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=aqd", "--instance=ny-prod", "--campus=ny"]
        self.notfoundtest(command)

    def testunmapbootserver(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "bootserver", "--instance", "np.test",
                        "--archetype", "aquilon"])

    def testverifyunmapbootserver(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=bootserver", "--instance=np.test",
                   "--building=ut"]
        self.notfoundtest(command)

    # Not unmap'ing ntp to test that the service instance is still
    # deleted correctly.  (Deleting the service instance will blow
    # away any maps.)
   #def testunmapntp(self):
   #    self.noouttest(["unmap", "service", "--city", "ny",
   #                    "--service", "ntp", "--instance", "pa.ny.na",
   #                    "--archetype", "aquilon"])

   #def testverifyunmapntp(self):
   #    command = ["show_map", "--archetype=aquilon",
   #               "--service=ntp", "--instance=pa.ny.na", "--city=ny"]
   #    self.notfoundtest(command)

    def testunmaputsi1(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "utsvc", "--instance", "utsi1",
                        "--archetype", "aquilon"])

    def testverifyunmaputsi1(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=utsvc", "--instance=utsi1", "--building=ut"]
        self.notfoundtest(command)

    def testunmaputsi2(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "utsvc", "--instance", "utsi2",
                        "--archetype", "aquilon"])

    def testverifyunmaputsi2(self):
        command = ["show_map", "--archetype=aquilon",
                   "--service=utsvc", "--instance=utsi2", "--building=ut"]
        self.notfoundtest(command)

    def testunmapchooser(self):
        for service in ["chooser1", "chooser2", "chooser3"]:
            for n in ['a', 'b', 'c']:
                if service == 'chooser2' and n == 'b':
                    continue
                if service == 'chooser3' and n == 'c':
                    continue
                instance = "ut.%s" % n
                self.noouttest(["unmap", "service", "--building", "ut",
                                "--archetype", "aquilon",
                                "--service", service, "--instance", instance])

    def testunmapwithpersona(self):
        self.noouttest(["unmap", "service", "--company", "ms", "--service", "utsvc",
                        "--instance", "utsi2", "--archetype", "aquilon",
                        "--personality", "lemon-oracle"])

    def testverifyunmapwithpersona(self):
        command = "show map --archetype aquilon --personality lemon-oracle --service utsvc"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "", command)

    # TODO: If/when there is another mapped personality, explicitly skip
    # the unmap operation to test that del_service automatically removes
    # the mapping.

    def testunmapwindowsfail(self):
        command = ["unmap", "service", "--company", "ms",
                   "--service", "utsvc", "--instance", "utsi2",
                   "--archetype", "windows"]
        out = self.unimplementederrortest(command)
        self.matchoutput(out,
                         "Archetype level ServiceMaps other than "
                         "aquilon are not yet available",
                         command)

    def testunmapesx(self):
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "esx_license", "--instance", "ut.a",
                        "--archetype", "vmhost",
                        "--personality", "esx_server"])
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "esx_license", "--instance", "ut.b",
                        "--archetype", "vmhost",
                        "--personality", "esx_server"])
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "esx_management", "--instance", "ut.a",
                        "--archetype", "vmhost",
                        "--personality", "esx_server"])
        self.noouttest(["unmap", "service", "--building", "ut",
                        "--service", "esx_management", "--instance", "ut.b",
                        "--archetype", "vmhost",
                        "--personality", "esx_server"])

    def testverifyunmapesx(self):
        command = ["show_map", "--archetype=vmhost",
                   "--personality=esx_server", "--building=ut"]
        out = self.commandtest(command)
        self.matchclean(out, "Service: esx_license Instance: ut.a ", command)
        self.matchclean(out, "Service: esx_license Instance: ut.b ", command)
        self.matchclean(out, "Service: esx_management Instance: ut.a ",
                        command)
        self.matchclean(out, "Service: esx_management Instance: ut.b ",
                        command)


if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUnmapService)
    unittest.TextTestRunner(verbosity=2).run(suite)
