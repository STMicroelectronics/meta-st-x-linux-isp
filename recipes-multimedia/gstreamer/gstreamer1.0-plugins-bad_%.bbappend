FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI:append = " \
    file://0082-Revert-waylandsink-match-drm-kernel-driver-alignment.patch \
    file://0083-Revert-gtkwaylandsink-match-drm-kernel-driver-alignm.patch \
"

PR = "r2"
