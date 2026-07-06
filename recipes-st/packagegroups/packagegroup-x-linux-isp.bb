SUMMARY = "X-LINUX-ISP full components (tuning application and dependencies (gstreamer, usb gadget, ...)"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PROVIDES = "${PACKAGES}"
PACKAGES = "\
    packagegroup-x-linux-isp \
"

# Manage to provide all framework tools base packages with overall one
RDEPENDS:packagegroup-x-linux-isp = "   \
    stm32-isp-iqtune-application-python \
    x-linux-isp-tool \
"
