SUMMARY = "X-LINUX-ISP full components (Libcamera DCMIPP IPA, tuning application and appliation samples)"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PROVIDES = "${PACKAGES}"
PACKAGES = "\
    packagegroup-x-linux-isp \
    packagegroup-x-linux-isp-iqtune \
    packagegroup-x-linux-isp-libcamera \
"

# Manage to provide all framework tools base packages with overall one
RDEPENDS:packagegroup-x-linux-isp = "   \
    packagegroup-x-linux-isp-iqtune     \
    packagegroup-x-linux-isp-libcamera  \
    x-linux-isp-tool \
"

SUMMARY:packagegroup-x-linux-isp-iqtune = "X-LINUX-ISP IQTune application components"
RDEPENDS:packagegroup-x-linux-isp-iqtune = " \
    stm32-isp-iqtune-application-python \
    libcamera-gst (>1:0.2.0-r0.0) \
"

SUMMARY:packagegroup-x-linux-isp-libcamera = "X-LINUX-ISP libcamera and application example components"
RDEPENDS:packagegroup-x-linux-isp-libcamera = " \
    simple-isp-preview-python \
    libcamera-gst (>1:0.2.0-r0.0) \
"
