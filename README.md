<p align="center">
    <img width="720" src="https://raw.githubusercontent.com/STMicroelectronics/meta-st-x-linux-isp/master/x-linux-isp-logo.png">
</p>

X-LINUX-ISP version: v6.2.0

## Enhancements, new features
* Support OpenSTLinux 6.2.1
* Support ST 2A algorithms offering improved accuracy and stability
* New lux estimation service

## Limitation
* None

# Overview
X-LINUX-ISP is a free of charge open-source software package targeting the
STM32MP25x and STM32MP21x series that embed an ISP camera pipeline.<br>
This meta-layer delivers the **STM32 ISP IQTune application** running on the
target to interact with the **STM32 ISP IQTune desktop application**
executed on the host computer (connected through USB), allowing access to the
ISP configuration and sensor tuning procedure.

# meta-st-x-linux-isp
X-LINUX-ISP OpenEmbedded meta layer to be integrated into OpenSTLinux
distribution. It contains recipes for STM32 ISP IQTune embedded application
and its dependencies for STM32MP25x and STM32MP21x series.

## Compatibility
The X-LINUX-ISP OpenSTLinux Expansion Package v6.2.0 is compatible with the
Yocto Project™ build system Scarthgap. It is validated over the OpenSTLinux
Distribution v6.2.1 on STM32MP25x and STM32MP21x series.

## Versioning
The major versioning of the X-LINUX-ISP OpenSTLinux Expansion Package is aligned
on the major versioning of the OpenSTLinux Distribution. This prevents painful
backward compatibility attempts and makes dependencies straightforward.<br>
The X-LINUX-ISP generic versioning v**x**.**y**.**z** is built as follows:
* **x**: major version matching the OpenSTLinux Distribution major version.
  Each new major version is incompatible with previous OpenSTLinux Distribution
  versions.
* **y**: minor version, which is changed when new functionalities are added to
  the X-LINUX-ISP OpenSTLinux Expansion Package in a backward compatible manner.
* **z**: patch version to introduce bug fixes. A patch version is implemented in
  a backward compatible manner.

## Available frameworks and tools within the meta-layer
[X-LINUX-ISP v6.2.0 expansion package](https://wiki.st.com/stm32mpu/wiki/Category:X-LINUX-ISP_expansion_package):
* ISP software:
  * ISP software framework is now part of OpenSTLinux 6.2.1 distribution
  (not delivered within x-linux-isp expansion package)

* Utilities:
  * STM32 ISP IQTune application (running on the target) used to tune the ISP
  by providing communication services between the host and the device

* Host tools:
  * STM32 ISP IQTune desktop application that provide services to tune the ISP
    present in STM32 devices

## Further information on how to install and how to use X-LINUX-ISP Starter package
<https://wiki.st.com/stm32mpu/wiki/X-LINUX-ISP_Starter_package>

## Further information on how to install and how to use X-LINUX-ISP Distribution package
<https://wiki.st.com/stm32mpu/wiki/X-LINUX-ISP_Distribution_package>

## Application samples
<https://wiki.st.com/stm32mpu/wiki/Category:ISP_-_Application_examples>

## STM32 ISP tuning procedure
<https://wiki.st.com/stm32mpu/wiki/How_to_tune_ISP_using_the_STM32_ISP_IQTune>