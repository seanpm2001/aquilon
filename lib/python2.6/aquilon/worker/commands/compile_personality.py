# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013  Contributor
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
"""Contains the logic for `aq compile --personality`."""


from aquilon.exceptions_ import ArgumentError
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.dbwrappers.branch import get_branch_and_author
from aquilon.worker.dbwrappers.host import validate_branch_author
from aquilon.worker.templates.domain import TemplateDomain
from aquilon.aqdb.model import (Host, Personality)


class CommandCompilePersonality(BrokerCommand):

    required_parameters = ["personality"]
    requires_readonly = True

    def render(self, session, logger, domain, sandbox, archetype, personality,
               pancinclude, pancexclude, pancdebug, cleandeps,
               **arguments):
        dbdomain = None
        dbauthor = None
        if domain or sandbox:
            (dbdomain, dbauthor) = get_branch_and_author(session, logger,
                                                         domain=domain,
                                                         sandbox=sandbox,
                                                         compel=True)

        dbpersonality = Personality.get_unique(session, name=personality,
                                           archetype=archetype, compel=True)
        if pancdebug:
            pancinclude = r'.*'
            pancexclude = r'components/spma/functions'

        q = session.query(Host)
        q = q.filter_by(personality=dbpersonality)
        if dbdomain:
            q = q.filter_by(branch=dbdomain)
        if dbauthor:
            q = q.filter_by(sandbox_author=dbauthor)

        host_list = q.all()

        validate_branch_author(host_list)
        # if domain not determined set it
        # to the domain of first host
        if not dbdomain:
            dbdomain = host_list[0].branch
            dbauthor = host_list[0].sandbox_author

        dom = TemplateDomain(dbdomain, dbauthor,
                             logger=logger)
        profile_list = [h.fqdn for h in host_list]
        dom.compile(session, only=profile_list,
                    panc_debug_include=pancinclude,
                    panc_debug_exclude=pancexclude,
                    cleandeps=cleandeps)
        return
