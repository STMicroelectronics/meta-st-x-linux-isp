require libcamera-stm32mp-dcmipp-ipa.inc

FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
        file://0001-libcamera-x-linux-isp-v6.1.0.patch \
"

PE = "2"
