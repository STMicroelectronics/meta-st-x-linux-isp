FILESEXTRAPATHS:prepend := "${THISDIR}:"

SRC_URI += "file://${LINUX_VERSION}/0001-stm32-dcmipp-enable-disable-demosaicing-block-via-is.patch \
"

PR = "r3"
