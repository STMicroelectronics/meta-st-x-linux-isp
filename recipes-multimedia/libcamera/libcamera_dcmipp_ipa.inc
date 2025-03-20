DEPENDS += " evision-lib"

LIBCAMERA_PIPELINES = "dcmipp"
LIBCAMERA_IPAS = "dcmipp"

EXTRA_OEMESON += " \
    -Dipas=${LIBCAMERA_IPAS} \
    -Devision_algo=true \
"

do_configure:prepend() {
    cp ${RECIPE_SYSROOT}/usr/include/evision/*.h ${S}/src/ipa/dcmipp/algorithms
}

RDEPENDS:${PN} += " \
    evision-lib \
"

RDEPENDS:${PN}-gst += " \
    gstreamer1.0-python \
    libcamera (>= ${EXTENDPKGV}) \
"
