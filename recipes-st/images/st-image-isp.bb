require recipes-st/images/st-image-weston.bb

SUMMARY = "OpenSTLinux Image Signal Processing for Computer Vision image based on weston image"

inherit python3-dir

# Define a proper userfs for st-image-isp
STM32MP_USERFS_IMAGE = "st-image-isp-userfs"
# Define the size of userfs
STM32MP_USERFS_SIZE = "307200"
PARTITIONS_IMAGES[userfs]   = "${STM32MP_USERFS_IMAGE},${STM32MP_USERFS_LABEL},${STM32MP_USERFS_MOUNTPOINT},${STM32MP_USERFS_SIZE},FileSystem"

IMAGE_ISP_PART = "   \
    packagegroup-x-linux-isp \
"

#
# INSTALL addons
#
CORE_IMAGE_EXTRA_INSTALL += " \
    ${IMAGE_ISP_PART}          \
"
