# Copyright (C) 2024, STMicroelectronics - All Rights Reserved

SUMMARY = "X-LINUX-ISP tool manager"
DESCRIPTION = "X-LINUX-ISP is a free of charge open-source software \
package dedicated to Image Signal Processing. "

HOMEPAGE = "https://github.com/stmicroelectronics/meta-st-x-linux-isp"

LICENSE = "SLA0044"
LIC_FILES_CHKSUM  = "file://LICENSE;md5=91fc08c2e8dfcd4229b69819ef52827c"

NO_GENERIC_LICENSE[SLA0044] = "LICENSE"
LICENSE:${PN} = "SLA0044"

SRC_URI = " file://x-linux-isp-tool/LICENSE \
            file://x-linux-isp-tool/x-linux-isp-tool.cc \
            file://x-linux-isp-tool/README_sym \
            file://x-linux-isp-tool/Makefile \
"

BBCLASSEXTEND = " nativesdk "

S = "${WORKDIR}/${BPN}"

do_configure() {
    # Get package version
    xpkg_ver=$(sed -n 's/^.*X-LINUX-ISP version: //p' README_sym)

    # Get software
    xpkg_soft=$(sed -n '/^* ISP software:/,/^* Application examples:/{/^* Application examples:/!p}' README_sym | sed '$d' | sed '1d; $!s/$/ \\n \\/')

    # Get applications
    xpkg_app=$(sed -n '/^* Application examples:/,/^* Utilities:/{/^* Utilities:/!p}' README_sym | sed '$d' | sed '1d; $!s/$/ \\n \\/')

    # Get utilities
    xpkg_util=$(sed -n '/^* Utilities:/,/^* Host tools:/{/^* Host tools:/!p}' README_sym | sed '$d' | sed '1d; $!s/$/ \\n \\/')

    # Get wiki link
    xpkg_link=$(grep -o 'https://wiki.st.com/stm32mp.*Starter_package>' README_sym | sed 's/>$//')

    cat << EOF > readme.h

#include <iostream>
const std::string README_VERSION = "${xpkg_ver}";
const std::string README_SOFTWARE = "${xpkg_soft}";
const std::string README_APPLI = "${xpkg_app}";
const std::string README_UTILITIES = "${xpkg_util}";
const std::string WIKI_LINK = "${xpkg_link}";
EOF
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${S}/x-linux-isp ${D}${bindir}
}

FILES:${PN} = "${bindir}"

# Add dependency on the apt configuration for x-linux-isp
RDEPENDS:${PN}:class-target += "apt-openstlinux-x-linux-isp"
