require recipes-st/images/st-image-isp.bb

SUMMARY = "OpenSTLinux Image Signal Processing for Computer Vision image based on weston image"

inherit python3-dir

#
# INSTALL addons
#
CORE_IMAGE_EXTRA_INSTALL += " \
    ${PYTHON_PN}-numpy \
    ${PYTHON_PN}-pillow \
"
