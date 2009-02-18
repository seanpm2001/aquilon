# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq manage`."""


import os
from aquilon.server.broker import BrokerCommand
from aquilon.server.dbwrappers.domain import verify_domain
from aquilon.server.dbwrappers.host import hostname_to_host
from aquilon.server.templates.host import PlenaryHost
from aquilon.server.processes import remove_file
from aquilon.server.templates.base import compileLock, compileRelease
from aquilon.exceptions_ import IncompleteError

class CommandManage(BrokerCommand):

    required_parameters = ["domain", "hostname"]

    def render(self, session, domain, hostname, **arguments):
        # FIXME: Need to verify that this server handles this domain?
        dbdomain = verify_domain(session, domain,
                self.config.get("broker", "servername"))
        dbhost = hostname_to_host(session, hostname)

        try:
            compileLock()

            # Clean up any old files in the old domain
            # Note, that these files may not exist if we've never compiled
            # in the old domain, so we just try the lot.
            plenary = PlenaryHost(dbhost)
            plenary.remove(locked=True)
            plenary = None
            qdir = self.config.get("broker", "quattordir")
            domain = dbhost.domain.name
            fqdn = dbhost.fqdn
            f = os.path.join(qdir, "build", "xml", domain, fqdn+".xml")
            remove_file(f)
            f = os.path.join(qdir, "build", "xml", domain, fqdn+".xml.dep")
            remove_file(f)

            dbhost.domain = dbdomain
            session.add(dbhost)

            # Now we recreate the plenary to ensure that the domain is ready
            # to compile, however (esp. if there was no existing template), we
            # have to be aware that there might not be enough information yet
            # with which we can create a template
            try:
                plenary = PlenaryHost(dbhost)
                plenary.write(locked=True)
            except IncompleteError, e:
                # This template cannot be written, we leave it alone
                # It would be nice to flag the state in the the host?
                pass

        finally:
            compileRelease()

        return


