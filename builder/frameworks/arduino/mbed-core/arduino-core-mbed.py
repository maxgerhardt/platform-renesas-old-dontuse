# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

https://github.com/arduino/ArduinoCore-mbed
"""

import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinorenesas")
assert os.path.isdir(FRAMEWORK_DIR)


def load_flags(filename):
    if not filename:
        return []

    file_path = os.path.join(FRAMEWORK_DIR, "variants", board.get(
        "build.variant"), "%s.txt" % filename)
    if not os.path.isfile(file_path):
        print("Warning: Couldn't find file '%s'" % file_path)
        return []

    with open(file_path, "r") as fp:
        return [f.strip() for f in fp.readlines() if f.strip()]

def configure_fpu_flags(board_config):
    board_cpu = board_config.get("build.cpu", "")
    if board_cpu not in ("cortex-m4", "cortex-m7"):
        return

    fpv_version = "4-sp" if board_cpu == "cortex-m4" else "5"
    env.Append(
        ASFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv%s-d16" % fpv_version
        ],

        # already contained in cxxflags.txt
        #CCFLAGS=[
        #    "-mfloat-abi=hard",
        #    "-mfpu=fpv%s-d16" % fpv_version
        #],

        LINKFLAGS=[
            "-mcpu=%s" % board_cpu,
            "-mfloat-abi=hard",
            "-mfpu=fpv%s-d16" % fpv_version
        ]
    )


cflags = set(load_flags("cflags"))
cxxflags = set(load_flags("cxxflags"))
ccflags = cflags.intersection(cxxflags)

env.Append(
    ASFLAGS=[f for f in ccflags if isinstance(f, str) and f.startswith("-m")],
    ASPPFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=sorted(list(cflags - ccflags)),

    CCFLAGS=sorted(list(ccflags)),

    CPPDEFINES=[d.replace("-D", "") for d in load_flags("defines")],

    CXXFLAGS=sorted(list(cxxflags - ccflags)),

    LIBPATH=[
        os.path.join(FRAMEWORK_DIR, "variants", board.get("build.variant")),
        os.path.join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "libs")
    ],

    LINKFLAGS=[],

    LIBSOURCE_DIRS=[os.path.join(FRAMEWORK_DIR, "libraries")],

    LIBS=[]
)

env.Append(
    # Due to long path names "-iprefix" hook is required to avoid toolchain crashes
    CCFLAGS=[
        "-iprefix" + os.path.join(FRAMEWORK_DIR),
        "@%s" % os.path.join(FRAMEWORK_DIR, "variants", board.get(
            "build.variant"), "includes.txt"),
        "-nostdlib",
        "-fno-builtin"
    ],

    CXXFLAGS=[
        "-std=gnu++17",
        "-fno-use-cxa-atexit",
        "-fno-rtti",
        "-fno-exceptions"
    ],

    CFLAGS=[
        "-std=gnu11"
    ],

    CPPDEFINES=[
        ("ARDUINO", 10819),
        "ARDUINO_ARCH_RENESAS",
        ("F_CPU", "$BOARD_F_CPU"),
        "_XOPEN_SOURCE"
    ],

    CPPPATH=[
        os.path.join(FRAMEWORK_DIR, "cores", board.get("build.core")),
        os.path.join(FRAMEWORK_DIR, "cores", board.get(
            "build.core"), "api", "deprecated"),
        os.path.join(FRAMEWORK_DIR, "cores", board.get(
            "build.core"), "api", "deprecated-avr-comp"),
        os.path.join(FRAMEWORK_DIR, "cores", board.get(
            "build.core"), "tinyusb")
    ],

    LINKFLAGS=[
        "-Wl,--gc-sections",
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ]
)

# Weird: The Arduino core builds without any warnings flags. Filter them all out, too.
env.Replace(CCFLAGS = list(filter(lambda x: not str(x).startswith("-W"), env["CCFLAGS"])))
env.Replace(CFLAGS = list(filter(lambda x: not str(x).startswith("-W"), env["CFLAGS"])))
env.Replace(CXXFLAGS = list(filter(lambda x: not str(x).startswith("-W"), env["CXXFLAGS"])))
# Additionally suprress warning in cm_backtrace.c
env.Append(CFLAGS=["-Wno-discarded-qualifiers"])

#
# Configure FPU flags
#

configure_fpu_flags(board)

#
# Linker requires preprocessing with specific defines
#

if not board.get("build.ldscript", ""):
    ldscript = os.path.join(
        FRAMEWORK_DIR, "variants", board.get("build.variant"), "fsp.ld")
    if board.get("build.mbed.ldscript", ""):
        ldscript = env.subst(board.get("build.arduino.ldscript"))
    # no preprocessing of linker script! It should be used as-is
    if os.path.isfile(ldscript):
        env.Replace(LDSCRIPT_PATH=ldscript)
    else:
        print("Warning! Couldn't find linker script file!")

# Framework requires all symbols from mbed libraries
#env.Prepend(_LIBFLAGS="-Wl,--whole-archive ")
#  -Wl,--no-whole-archive 
env.Append(_LIBFLAGS=" -lstdc++ -lsupc++ -lm -lc -lgcc -lnosys")

libs = []

if "build.variant" in board:
    env.Append(CPPPATH=[
        os.path.join(FRAMEWORK_DIR, "variants", board.get("build.variant"))
    ])

    env.BuildSources(
            os.path.join("$BUILD_DIR", "FrameworkArduinoVariant"),
            os.path.join(FRAMEWORK_DIR, "variants", board.get("build.variant"))
    )

    libs.append(
        File(
            os.path.join(FRAMEWORK_DIR, "variants", board.get("build.variant"), "libs", "libfsp.a")
        )
    )


libs.append(
    env.BuildLibrary(
        os.path.join("$BUILD_DIR", "FrameworkArduino"),
        os.path.join(FRAMEWORK_DIR, "cores", board.get("build.core"))))

env.Prepend(LIBS=libs)
