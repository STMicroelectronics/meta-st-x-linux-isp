require libcamera_dcmipp_ipa.inc

FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += " \
        file://0001-libcamera-x-linux-isp-v6.0.0.patch \
"

PR = "r2"
