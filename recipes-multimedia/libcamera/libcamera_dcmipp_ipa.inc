DEPENDS += " evision-lib linux-stm32mp gstreamer1.0-plugins-bad"

LIBCAMERA_PIPELINES = "dcmipp"
LIBCAMERA_IPAS = "dcmipp"

EXTRA_OEMESON += " \
    -Dipas=${LIBCAMERA_IPAS} \
    -Devision_algo=true \
"

do_configure:prepend() {
    cp ${RECIPE_SYSROOT}/usr/include/evision/*.h ${S}/src/ipa/dcmipp/algorithms
}

inherit module-base

python populate_packages:prepend () {
    import os

    pkgdata_dir = d.getVar('PKGDATA_DIR')

    # get the recipe version of the stm32 dcmipp kernel module
    kernel_version = d.getVar('KERNEL_VERSION')
    file = os.path.join(pkgdata_dir, 'runtime', 'kernel-module-stm32-dcmipp-' + kernel_version)

    if not file:
        bb.fatal("No file found matching pattern: {}".format(file_pattern))

    pkgv = None
    pr = None
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('PKGV:'):
                pkgv = line.split(':')[1].strip()
            elif line.startswith('PR:'):
                pr = line.split(':')[1].strip()

    # update the RDEPENDS with the stm32 dcmipp kernel module version
    pn = d.getVar('PN')
    rdepends = d.getVar('RDEPENDS:' + pn)
    rdepends = rdepends + " kernel-module-stm32-dcmipp-%s (>= %s-%s) " % (kernel_version, pkgv, pr)
    d.setVar('RDEPENDS:' + pn, rdepends)

    # get the recipe version of gstreamer1.0-plugins-bad-waylandsinkg
    file = os.path.join(pkgdata_dir, 'runtime', 'gstreamer1.0-plugins-bad-waylandsink')

    if not file:
        bb.fatal("No files found matching pattern: {}".format(file_pattern))

    pkgv = None
    pr = None
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('PKGV:'):
                pkgv = line.split(':')[1].strip()
            elif line.startswith('PR:'):
                pr = line.split(':')[1].strip()

    # update the RDEPENDS with the gstreamer1.0-plugins-bad-waylandsink version
    pn = d.getVar('PN')
    rdepends = d.getVar('RDEPENDS:' + pn)
    rdepends = rdepends + " gstreamer1.0-plugins-bad-waylandsink (>= %s-%s) " % (pkgv, pr)
    d.setVar('RDEPENDS:' + pn, rdepends)
}


RDEPENDS:${PN} += " \
    evision-lib \
"

RDEPENDS:${PN}-gst += " \
    gstreamer1.0-python \
    libcamera (>= ${EXTENDPKGV}) \
"
