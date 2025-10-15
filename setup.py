import os
import subprocess
import sys
from glob import glob
from itertools import chain
from os.path import exists, join

import numpy as np
import setuptools.command.build_ext
from setuptools import Extension, setup, find_packages

platform_is_windows = sys.platform == "win32"

msvc_extra_compile_args_config = [
    "/source-charset:utf-8",
    "/execution-charset:utf-8",
]


def msvc_extra_compile_args(compile_args):
    cas = set(compile_args)
    xs = filter(lambda x: x not in cas, msvc_extra_compile_args_config)
    return list(chain(compile_args, xs))


msvc_define_macros_config = [
    ("_CRT_NONSTDC_NO_WARNINGS", None),
    ("_CRT_SECURE_NO_WARNINGS", None),
]


def msvc_define_macros(macros):
    mns = set([i[0] for i in macros])
    xs = filter(lambda x: x[0] not in mns, msvc_define_macros_config)
    return list(chain(macros, xs))


class custom_build_ext(setuptools.command.build_ext.build_ext):
    def build_extensions(self):
        compiler_type_is_msvc = self.compiler.compiler_type == "msvc"
        for entry in self.extensions:
            if compiler_type_is_msvc:
                entry.extra_compile_args = msvc_extra_compile_args(
                    entry.extra_compile_args
                    if hasattr(entry, "extra_compile_args")
                    else []
                )
                entry.define_macros = msvc_define_macros(
                    entry.define_macros if hasattr(entry, "define_macros") else []
                )

        setuptools.command.build_ext.build_ext.build_extensions(self)


def check_cmake_in_path():
    try:
        result = subprocess.run(
            ["cmake", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            # CMake is in the system path
            return True, result.stdout.strip()
        else:
            # CMake is not in the system path
            return False, None
    except FileNotFoundError:
        # CMake command not found
        return False, None


if os.name == "nt":  # Check if the OS is Windows
    # Check if CMake is in the system path
    cmake_found, cmake_version = check_cmake_in_path()

    if cmake_found:
        print(
            f"CMake is in the system path. Version: \
              {cmake_version}"
        )
    else:
        raise SystemError(
            "CMake is not found in the \
                          system path. Make sure CMake \
                          is installed and in the system \
                          path."
        )

# open_jtalk sources
src_top = join("lib", "open_jtalk", "src")

# generate config.h for mecab
# NOTE: need to run cmake to generate config.h
# we could do it on python side but it would be very tricky,
# so far let's use cmake tool
if not exists(join(src_top, "mecab", "src", "config.h")):
    cwd = os.getcwd()
    build_dir = join(src_top, "build")
    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)

    r = subprocess.run(["cmake", ".."])
    r.check_returncode()
    os.chdir(cwd)

all_src = []
include_dirs = []
for s in [
    "jpcommon",
    "mecab/src",
    "mecab2njd",
    "njd",
    "njd2jpcommon",
    "njd_set_accent_phrase",
    "njd_set_accent_type",
    "njd_set_digit",
    "njd_set_long_vowel",
    "njd_set_pronunciation",
    "njd_set_unvoiced_vowel",
    "text2mecab",
]:
    all_src += glob(join(src_top, s, "*.c"))
    all_src += glob(join(src_top, s, "*.cpp"))
    include_dirs.append(join(os.getcwd(), src_top, s))

# Extension for OpenJTalk frontend
ext_modules = [
    Extension(
        name="pyopenjtalk.openjtalk",
        sources=[join("pyopenjtalk", "openjtalk.pyx")] + all_src,
        include_dirs=include_dirs,
        extra_compile_args=[],
        extra_link_args=[],
        language="c++",
        define_macros=[
            ("HAVE_CONFIG_H", None),
            ("DIC_VERSION", "102"),
            ("MECAB_DEFAULT_RC", '"dummy"'),
            ("PACKAGE", '"open_jtalk"'),
            ("VERSION", '"1.10"'),
            ("CHARSET_UTF_8", None),
        ],
    )
]

# Extension for HTSEngine backend
htsengine_src_top = join("lib", "hts_engine_API", "src")
all_htsengine_src = glob(join(htsengine_src_top, "lib", "*.c"))
ext_modules += [
    Extension(
        name="pyopenjtalk.htsengine",
        sources=[join("pyopenjtalk", "htsengine.pyx")] + all_htsengine_src,
        include_dirs=[np.get_include(), join(htsengine_src_top, "include")],
        extra_compile_args=[],
        extra_link_args=[],
        libraries=["winmm"] if platform_is_windows else [],
        language="c++",
        define_macros=[
            ("AUDIO_PLAY_NONE", None),
            ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
        ],
    )
]

setup(ext_modules=ext_modules,
      name="pyopenjtalk",
      use_scm_version={"version_file": "pyopenjtalk/version.py", "version_file_template": '__version__ = "{version}"'},
      cmdclass={"build_ext": custom_build_ext},
      packages=find_packages(include=["pyopenjtalk*"]),
      include_package_data=True,
      exclude_package_data={"*": ["*.pyx", "*.pxd"]},
      setup_requires=[
            "setuptools>=64",
            "setuptools_scm>=8",
            "cython>=0.29.16",
            "cmake",
            "numpy>=1.25.0; python_version>='3.9'",
            "oldest-supported-numpy; python_version<'3.9'",
        ],
      install_requires=[
            "importlib_resources; python_version<'3.9'",
            "numpy>=1.20.0",
            "tqdm",
        ],
      description="A python wrapper for OpenJTalk",
      long_description=open("README.md").read() if os.path.exists("README.md") else "",
      long_description_content_type="text/markdown",
      python_requires=">=3.8",
      license="MIT",
      author="Ryuichi Yamamoto",
      author_email="zryuichi@gmail.com",
      url="https://github.com/r9y9/pyopenjtalk",
      keywords=["OpenJTalk", "Research"],
      classifiers=[
          "Operating System :: POSIX",
          "Operating System :: Unix",
          "Operating System :: MacOS",
          "Operating System :: Microsoft :: Windows",
          "Programming Language :: Cython",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "License :: OSI Approved :: MIT License",
          "Topic :: Scientific/Engineering",
          "Topic :: Software Development",
          "Intended Audience :: Science/Research",
          "Intended Audience :: Developers",
      ]
    )
