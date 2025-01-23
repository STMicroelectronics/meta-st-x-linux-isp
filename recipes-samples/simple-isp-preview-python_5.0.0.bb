# Copyright (C) 2024, STMicroelectronics - All Rights Reserved
SUMMARY = "STM32 ISP Simple preview application."
DESCRIPTION = "Simple preview application use libcamerasrc gstreamer plugin \
               to start a camera preview using the ISP functionnalities."

LICENSE = "SLA0044"
LIC_FILES_CHKSUM  = "file://simple-isp-preview/LICENSE;md5=91fc08c2e8dfcd4229b69819ef52827c"
NO_GENERIC_LICENSE[SLA0044] = "simple-isp-preview/LICENSE"
LICENSE:${PN} = "SLA0044"

inherit python3-dir

SRC_URI  = " file://simple-isp-preview;subdir=sources "
SRC_URI += " file://resources;subdir=sources "

S = "${WORKDIR}/sources"

do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
    install -d ${D}${prefix}/local/demo/gtk-application
    install -d ${D}${prefix}/local/x-linux-isp
    install -d ${D}${prefix}/local/x-linux-isp/simple-isp-preview
    install -d ${D}${prefix}/local/x-linux-isp/simple-isp-preview/resources

    # install applications into the demo launcher
    install -m 0755 ${S}/simple-isp-preview/*.yaml ${D}${prefix}/local/demo/gtk-application

    # install application and launcher scripts
    install -m 0755 ${S}/simple-isp-preview/simple_isp_preview_app.py ${D}${prefix}/local/x-linux-isp/simple-isp-preview
    install -m 0755 ${S}/simple-isp-preview/launch_python*.sh ${D}${prefix}/local/x-linux-isp/simple-isp-preview

    # install the LICENSE file associated with the scripts
    install -m 0444 ${S}/simple-isp-preview/LICENSE ${D}${prefix}/local/x-linux-isp/simple-isp-preview

    # install all resource files
    # .png files
    install -m 0644 ${S}/resources/*.png ${D}${prefix}/local/x-linux-isp/simple-isp-preview/resources
    # configuration scripts
    install -m 0644 ${S}/resources/Default.css ${D}${prefix}/local/x-linux-isp/simple-isp-preview/resources
}

FILES:${PN} += "${prefix}/local/"

RDEPENDS:${PN} += " \
    gstreamer1.0-plugins-bad-waylandsink \
    gstreamer1.0-plugins-bad-debugutilsbad \
    gstreamer1.0-plugins-base-app \
    gtk+3 \
    libcamera-gst (>1:0.2.0-r0.0) \
    ${PYTHON_PN}-core \
    bash \
"
