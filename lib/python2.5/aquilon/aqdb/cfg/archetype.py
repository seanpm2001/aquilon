#!/ms/dist/python/PROJ/core/2.5.0/bin/python
""" Archetype specifies the metaclass of the build """

import sys
import os

if __name__ == '__main__':
    DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.realpath(os.path.join(DIR, '..', '..', '..')))
    import aquilon.aqdb.depends

from aquilon.aqdb.table_types.name_table import make_name_class


Archetype = make_name_class('Archetype','archetype')
archetype = Archetype.__table__
archetype.primary_key.name = 'archetype_pk'

table = archetype

def populate(db, *args, **kw):
    if len(db.s.query(Archetype).all()) > 0:
        return

    for a_name in ['aquilon', 'windows', 'aurora']:
        a = Archetype(name=a_name)
        db.s.add(a)
    db.s.commit()

    a = db.s.query(Archetype).first()
    assert(a)

# Copyright (C) 2008 Morgan Stanley
# This module is part of Aquilon

# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-

