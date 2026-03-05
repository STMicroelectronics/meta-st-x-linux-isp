# Copyright (C) 2026, STMicroelectronics - All Rights Reserved

SUMMARY = "X-LINUX-ISP apt configuration"
DESCRIPTION = "This package updates the apt configuration to access \
X-LINUX-ISP packages. \
It also adds a disclaimer licenses file refering to the wiki page."

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://apt-openstlinux-x-linux-isp/10-st-disclaimer-extra-isp \
    file://apt-openstlinux-x-linux-isp/6.2/extra.isp.packages.openstlinux.st.com.list \
"

# The package is target-independant
inherit allarch

S = "${WORKDIR}"

RDEPENDS:${PN} = " \
    apt-openstlinux (>= 6.2-r0) \
    apt-openstlinux (< 6.3) \
"

FILES:${PN} = " \
    ${sysconfdir} \
"

# No need these tasks
do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
    install -d ${D}/${sysconfdir}/apt/sources.list.d
    install -d ${D}/${sysconfdir}/apt/apt.conf.d
    install ${S}/apt-openstlinux-x-linux-isp/6.2/extra.isp.packages.openstlinux.st.com.list ${D}${sysconfdir}/apt/sources.list.d
    install ${S}/apt-openstlinux-x-linux-isp/10-st-disclaimer-extra-isp ${D}${sysconfdir}/apt/apt.conf.d
}
