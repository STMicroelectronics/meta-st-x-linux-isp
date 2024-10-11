<p align="center">
    <img width="720" src="https://raw.githubusercontent.com/STMicroelectronics/meta-st-x-linux-isp/master/x-linux-isp-logo.png">
</p>

X-LINUX-ISP version: v5.0.0

X-LINUX-ISP is a free of charge open-source software package providing ISP
(Image Signal Processing) image quality software targeting the STM32MP25x series
that embed an ISP camera pipeline called.<br>
It brings advanced image quality capabilities that allow developers working with
OpenSTLinux to **create ISP-based application very easily.**
* **Pre-integrated** into Linux distribution based on ST environment
* include **libcamera** with the support of the DCMIPP ISP Image Processing
  Algorithm (IPA) integrating **Auto Exposure (AE)** and **Auto White Balance
  (AWB)** and all ISP controls
* include **libcamerasrc gstreamer plugin** supporting DCMIPP ISP properties
* include **Sensor tuning application** (running on the target) that allows to
  interact with the **STM32 ISP IQTune desktop application** executed on the
  host computer (connected through USB) allowing to access ISP configuration and
  perform a sensor tuning procedure
* include **Simple ISP preview application example** taking advantage of
  libcamera and libcamerasrc gstreamer plugin for easy prototyping.
* Delivered under **GitHub as a Yocto meta-layer**

# meta-st-x-linux-isp
X-LINUX-ISP OpenEmbedded meta layer to be integrated into OpenSTLinux
distribution. It contains recipes for ISP image quality software, tools and
application examples for STM32MP25 series.

## Compatibility
The X-LINUX-ISP OpenSTLinux Expansion Package v5.0.0 is compatible with the
Yocto Project™ build system Mickledore. It is validated over the OpenSTLinux
Distribution v5.1.x on STM32MP25x series.

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
[X-LINUX-ISP v5.0.0 expansion package](https://wiki.st.com/stm32mpu/wiki/Category:X-LINUX-ISP_expansion_package):
* ISP software:
  * libcamera with the support of the DCMIPP ISP Image Processing Algorithm
    (IPA) integrating Auto Exposure (AE) and Auto White Balance (AWB) and all
    ISP controls
  * libcamerasrc gstreamer plugin supporting DCMIPP ISP properties

* Application examples:
  * Simple ISP preview :
    * Python™ example taking advantage of libcamera and libcamerasrc gstreamer
      plugin for easy prototyping

* Utilities:
  * X-LINUX-ISP tool suite provides tools for software information and ISP
    packages management.
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

