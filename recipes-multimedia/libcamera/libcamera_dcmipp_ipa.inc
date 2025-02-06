DEPENDS += " evision-lib linux-stm32mp"

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
    # get the recipe version of the stm32 dcmipp kernel module
    import os
    import glob

    pkgdata_dir = d.getVar('PKGDATA_DIR')
    file_pattern = os.path.join(pkgdata_dir, 'runtime', 'kernel-module-stm32-dcmipp*')
    files = glob.glob(file_pattern)

    if not files:
        bb.fatal("No files found matching pattern: {}".format(file_pattern))

    file_path = files[0]  # Assuming you want the first match if there are multiple

    pkgv = None
    pr = None
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('PKGV:'):
                pkgv = line.split(':')[1].strip()
            elif line.startswith('PR:'):
                pr = line.split(':')[1].strip()

    # update the RDEPENDS with the stm32 dcmipp kernel module version
    pn = d.getVar('PN')
    kernel_version = d.getVar('KERNEL_VERSION')
    rdepends = d.getVar('RDEPENDS:' + pn)
    rdepends = rdepends + " kernel-module-stm32-dcmipp-%s (>= %s-%s) " % (kernel_version, pkgv, pr)
    d.setVar('RDEPENDS:' + pn, rdepends)
}


RDEPENDS:${PN} += " \
    evision-lib \
"

RDEPENDS:${PN}-gst += " \
    gstreamer1.0-python \
    libcamera (>= ${EXTENDPKGV}) \
"
