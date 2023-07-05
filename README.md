# Renesas: development platform for [PlatformIO](https://platformio.org)

[![Build Status](https://github.com/maxgerhardt/platform-renesas/workflows/Examples/badge.svg)](https://github.com/maxgerhardt/platform-renesas/actions)

The flexible Renesas Advanced (RA) 32-bit microcontrollers (MCUs) are industry-leading 32-bit MCUs with the Arm® Cortex®-M33, -M23 and -M4 processor cores and PSA certification. RA delivers key advantages compared to competitive Arm Cortex-M MCUs by providing stronger embedded security, superior CoreMark® performance and ultra-low power operation. PSA certification provides customers the confidence and assurance to quickly deploy secure IoT endpoint and edge devices, and smart factory equipment for Industry 4.0.

The Arduino Uno R4 Minima and WiFI are built upon a Renesas RA4M1-series chip, whereas the Portenta C33 is built upon a RA6M5-series chip.

You can read more about them at
    * [Renesas RA4M1](https://www.renesas.com/us/en/products/microcontrollers-microprocessors/ra-cortex-m-mcus/ra4m1-32-bit-microcontrollers-48mhz-arm-cortex-m4-and-lcd-controller-and-cap-touch-hmi)
    * [Renesas RA6M5](https://www.renesas.com/us/en/products/microcontrollers-microprocessors/ra-cortex-m-mcus/ra6m5-200mhz-arm-cortex-m33-trustzone-highest-integration-ethernet-and-can-fd)

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
