# Renesas: development platform for [PlatformIO](https://platformio.org)

[![Build Status](https://github.com/maxgerhardt/platform-renesas/workflows/Examples/badge.svg)](https://github.com/maxgerhardt/platform-renesas/actions)

The Renesas RA4M1 group of microcontrollers (MCUs) uses the high-performance Arm® Cortex®-M4 core and offers a segment LCD controller and a capacitive touch sensing unit input for intensive HMI designs. The RA4M1 MCU is built on a highly efficient low power process and is supported by an open and flexible ecosystem concept—the Flexible Software Package (FSP), built on FreeRTOS—and is expandable to use other RTOSes and middleware. The RA4M1 is suitable for applications where a large amount of capacitive touch channels and a segment LCD controller are required.

* [Home](https://registry.platformio.org/platforms/platformio/renesas) (home page in the PlatformIO Registry)
* [Documentation](https://docs.platformio.org/page/platforms/renesas.html) (advanced usage, packages, boards, frameworks, etc.)

# Usage

1. [Install PlatformIO](https://platformio.org)
2. Install this third-party platform by [opening a PlatformIO Core CLI](https://docs.platformio.org/en/latest/integration/ide/vscode.html#platformio-core-cli) and executing `pio pkg install -g -p "https://github.com/maxgerhardt/platform-renesas.git"`
3. Create PlatformIO project and configure a platform option in [platformio.ini](https://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = renesas
board = ...
...
```

## Development version

```ini
[env:development]
platform = https://github.com/maxgerhardt/platform-renesas.git
board = ...
...
```

# Configuration

Please navigate to [documentation](https://docs.platformio.org/page/platforms/renesas.html).
