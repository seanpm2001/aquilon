# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon

import os
from aquilon.server.templates.base import Plenary

class PlenaryPersonality(Plenary):
    def __init__(self, dbpersona, archetype):
        Plenary.__init__(self)
        self.name = dbpersona.relative_path
        self.plenary_core = "personality/%(name)s" % self.__dict__
        self.plenary_template = self.plenary_core + "/config"
        self.template_type = ''
        self.archetype = archetype
        self.dir = os.path.join(self.config.get("broker", "plenarydir"), archetype)

    def body(self, lines):
        lines.append("variable PERSONALITY = '%(name)s';" % self.__dict__)
        lines.append("include { 'personality/config' };");


