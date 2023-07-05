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

import json
import os
import sys

from platformio.managers.platform import PlatformBase


IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")
IS_MAC = sys.platform.startswith("darwin")

class RenesasPlatform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        if not variables.get("board"):
            return super().configure_default_packages(variables, targets)        
        board = variables.get("board")
        board_config = self.board_config(board)
        upload_protocol = variables.get(
            "upload_protocol", board_config.get("upload.protocol", "")
        )
        disabled_pkgs = []
        upload_tool = "tool-openocd"
        if upload_protocol == "sam-ba":
            upload_tool = "tool-bossac"
        elif upload_protocol == "jlink":
            upload_tool = "tool-jlink"
        elif upload_protocol == "dfu":
            upload_tool = "tool-dfuutil"

        if upload_tool:
            for name, opts in self.packages.items():
                if "type" not in opts or opts["type"] != "uploader":
                    continue
                if name != upload_tool:
                    disabled_pkgs.append(name)

        frameworks = variables.get("pioframework", [])
        if "arduino" in frameworks:
            if board.startswith(("uno", "portenta")):
                self.frameworks["arduino"]["package"] = "framework-arduinorenesas"
                self.frameworks["arduino"][
                    "script"
                ] = "builder/frameworks/arduino/mbed-core/arduino-core-mbed.py"

        default_protocol = board_config.get("upload.protocol") or ""
        if variables.get("upload_protocol", default_protocol) == "dfu":
            self.packages["tool-dfuutil"]["optional"] = False
            if IS_LINUX:
                self.packages["tool-dfuutil"]["version"] = "https://github.com/maxgerhardt/tool-dfuutil-new.git#linux_x64"
            elif IS_MAC:
                self.packages["tool-dfuutil"]["version"] = "https://github.com/maxgerhardt/tool-dfuutil-new.git#mac"
        elif variables.get("upload_protocol", default_protocol) == "sam-ba":
            # ugly: we need tool-bossac 1.9.1, registry only has 1.9.0.
            # source it from different branches of a repo
            self.packages["tool-bossac"]["optional"] = False
            if IS_LINUX:
                self.packages["tool-bossac"]["version"] = "https://github.com/maxgerhardt/tool-bossac-1.9.1.git#linux-x64"
            elif IS_MAC:
                self.packages["tool-bossac"]["version"] = "https://github.com/maxgerhardt/tool-bossac-1.9.1.git#mac"

        # configure J-LINK tool
        jlink_conds = [
            "jlink" in variables.get(option, "")
            for option in ("upload_protocol", "debug_tool")
        ]
        if board:
            jlink_conds.extend([
                "jlink" in board_config.get(key, "")
                for key in ("debug.default_tools", "upload.protocol")
            ])
        jlink_pkgname = "tool-jlink"
        if not any(jlink_conds) and jlink_pkgname in self.packages:
            del self.packages[jlink_pkgname]

        for name in disabled_pkgs:
            if name in self.packages:
                del self.packages[name]
        return PlatformBase.configure_default_packages(self, variables,
                                                       targets)

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug["tools"] = {}

        # BlackMagic, J-Link, ST-Link
        for link in ("blackmagic", "jlink", "stlink", "cmsis-dap"):
            if link not in upload_protocols or link in debug["tools"]:
                continue
            if link == "blackmagic":
                debug["tools"]["blackmagic"] = {
                    "hwids": [["0x1d50", "0x6018"]],
                    "require_debug_port": True
                }
            elif link == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug["tools"][link] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "SWD",
                            "-select", "USB",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe"
                                       if IS_WINDOWS else
                                       "JLinkGDBServer")
                    }
                }
            else:
                server_args = [
                    "-s", "$PACKAGE_DIR/openocd/scripts",
                    # add our custom OpenOCD configs too
                    "-s", os.path.join(os.path.dirname(os.path.realpath(__file__)), "misc", "openocd")
                ]
                if debug.get("openocd_board"):
                    server_args.extend([
                        "-f", "board/%s.cfg" % debug.get("openocd_board")
                    ])
                else:
                    assert debug.get("openocd_target"), (
                        "Missed target configuration for %s" % board.id)
                    server_args.extend([
                        "-f", "interface/%s.cfg" % link
                    ])
                    # For Arduino Uno R4 WiFi: OpenOCD won't find the CMSIS-DAP
                    # Unless we explicitly tell it the VID + PID
                    # should be refactored later to only trigger this with onboard debug
                    if link == "cmsis-dap":
                        server_args.extend([
                            "-c",
                            "cmsis_dap_vid_pid 0x2341 0x1002"
                        ])
                    server_args.extend([
                        "-c", "transport select %s" % (
                            "hla_swd" if link == "stlink" else "swd"),
                        "-f", "target/%s.cfg" % debug.get("openocd_target")
                    ])
                    server_args.extend(debug.get("openocd_extra_args", []))

                debug["tools"][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    },
                    # OpenOCD has no native flashing capabilities
                    # For the Renesas chips. We need to preload using the
                    # regular upload commands.
                    "load_cmds": "preload",
                    "init_cmds": [
                        "define pio_reset_halt_target",
                        "   monitor reset halt",
                        "end",
                        "define pio_reset_run_target",
                        "   monitor reset",
                        "end",
                        # make peripheral memory etc. readable
                        # since OpenOCD doesn't provide us with any target information (no flash driver etc.)
                        "set mem inaccessible-by-default off",
                        # fix to use hardware breakpoints of ARM CPU, not flash breakpoints. Doesn't break otherwise.
                        "mem 0 0x40000 ro",
                        "target extended-remote $DEBUG_PORT",
                        "$LOAD_CMDS",
                        "pio_reset_halt_target",
                        "$INIT_BREAK",
                    ]
                }
            debug["tools"][link]["onboard"] = link in debug.get("onboard_tools", [])
            debug["tools"][link]["default"] = link in debug.get("default_tools", [])

        board.manifest["debug"] = debug
        return board

    def configure_debug_session(self, debug_config):
        if debug_config.speed:
            server_executable = (debug_config.server or {}).get("executable", "").lower()
            if "openocd" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-c", "adapter speed %s" % debug_config.speed]
                )
            elif "jlink" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-speed", debug_config.speed]
                )
