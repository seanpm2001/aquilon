#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#
# This file is part of Aquilon.
#
# See the LICENSE file for all the licensing information.
#
"""Basic setup.py for packaging Aquilon itself"""

import glob
import os
import shutil
import sys
from distutils.core import setup
from subprocess import Popen
from distutils.command.install_scripts import install_scripts

VERSIONFILE = "VERSION"

class install_init_d_stuff(install_scripts):
    """Renames the aqd.rh init script into aqd"""
    def run(self):
        shutil.move("etc/rc.d/init.d/aqd.rh", "etc/rc.d/init.d/aqd")
        os.unlink("etc/rc.d/init.d/aqd.ms")
        install_scripts.run(self)


def get_version():
    try:
        with open(VERSIONFILE) as f:
            return f.readline().strip()
    except IOError:
        with open(VERSIONFILE, "w") as f:
            p = Popen("git describe".split(), stdout=f)
            if p.wait() == 0:
                return get_version()
            else:
                raise

setup(name="aquilon",
      version=get_version(),
      description="Aquilon",
      long_description="""Aquilon looks cool""",
      license="Apache 2.0",
      author="Quattor collaboration",
      author_email="quattor-aquilon@lists.sourceforge.net",
      package_dir={'' : 'lib/python2.6'},
      packages=["aquilon"],
      cmdclass = {"install_scripts" : install_init_d_stuff},
      data_files=[("/usr/share/aquilon/config", glob.glob("etc/*.conf*")),
                  ("/usr/share/aquilon", glob.glob("etc/*.xml")),
                  ("/etc/init.d", ["etc/rc.d/init.d/aqd"])],

      scripts=glob.glob(os.path.join("bin", "a*")),
      url="http://quattor.org")
