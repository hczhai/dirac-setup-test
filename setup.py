#!/usr/bin/env python3

import os
import sys
import subprocess
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.command.build_scripts import build_scripts


class CMakeExt(Extension):
    def __init__(self, name, cmdir='.'):
        Extension.__init__(self, name, [])
        self.cmake_lists_dir = os.path.abspath(cmdir)

from distutils.dep_util import newer
from distutils import log
from stat import ST_MODE
from distutils.util import convert_path

class BinBuild(build_scripts):

    def initialize_options(self):
        build_scripts.initialize_options(self)
        self.build_temp = None

    def finalize_options(self):
        build_scripts.finalize_options(self)
        self.set_undefined_options('build', ('build_temp', 'build_temp'))

    def copy_scripts(self):
        self.mkpath(self.build_dir)
        outfiles = []
        updated_files = []
        for script in self.scripts:
            script = os.path.join(self.build_temp, script)
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            outfiles.append(outfile)

            if not self.force and not newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                continue

            updated_files.append(outfile)
            self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 0o7777
                    newmode = (oldmode | 0o555) & 0o7777
                    if newmode != oldmode:
                        log.info("changing mode of %s from %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)
        return outfiles, updated_files


class CMakeBuild(build_ext):

    def build_extensions(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
            print(out.decode("utf-8"))
        except OSError:
            raise RuntimeError('Cannot find CMake executable!')

        print('Python3: ', sys.executable)
        print('Build Dir: ', self.build_temp)

        for ext in self.extensions:

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)

            subprocess.check_call([os.path.join(ext.cmake_lists_dir, "setup"),
                                  "--python={}".format(sys.executable), self.build_temp],
                                  cwd=self.build_temp)

            subprocess.check_call(['cmake', '--build', '.', '--', '--jobs=2'],
                                  cwd=self.build_temp)

    def get_ext_filename(self, ext_name):
        return ext_name

from distutils.command.build import build
build.sub_commands = ([c for c in build.sub_commands if c[0] == 'build_ext'] +
                      [c for c in build.sub_commands if c[0] != 'build_ext'])

setup(name='dirac22',
    version='0.0.1',
    packages=find_packages(),
    ext_modules=[CMakeExt('pam')],
    cmdclass={'build_ext': CMakeBuild, 'build_scripts': BinBuild},
    license='LICENSE',
    description="dirac22",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Unknown',
    scripts=["pam", "dirac.x"],
    install_requires=[]
)
