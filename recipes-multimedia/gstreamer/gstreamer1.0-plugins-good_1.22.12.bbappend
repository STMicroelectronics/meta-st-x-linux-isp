FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI:append = " \
    file://1001-v4l2-pool-Add-missing-gst_buffer_unref.patch \
"

PR = "r1"
