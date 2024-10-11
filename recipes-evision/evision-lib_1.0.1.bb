# Copyright (C) 2024, STMicroelectronics - All Rights Reserved
SUMMARY = "evision package to install AE an AWB algorithm libraries"
LICENSE = "SLA0044"
LIC_FILES_CHKSUM  = "file://evision-lib/LICENSE;md5=91fc08c2e8dfcd4229b69819ef52827c"

NO_GENERIC_LICENSE[SLA0044] = "evision-lib/LICENSE"
LICENSE:${PN} = "SLA0044"

SRC_URI = "file://evision-lib/;subdir=${BPN}-${PV}  \
"

S = "${WORKDIR}/${BPN}-${PV}"

do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
    # includes
    install -d ${D}${includedir}/evision
    cp -r ${S}/evision-lib/*.h ${D}${includedir}/evision
    cp -r ${S}/evision-lib/LICENSE ${D}${includedir}/evision

    # libraries
    install -d ${D}${libdir}
    install -m 0755 ${S}/evision-lib/*.so.1 ${D}${libdir}/
}
