FILESEXTRAPATHS:prepend := "${THISDIR}:"

SRC_URI += "file://${LINUX_VERSION}/0001-stm32-dcmipp-enable-disable-demosaicing-block-via-is.patch \
            file://${LINUX_VERSION}/0002-media-dcmipp-statcap-add-stat_location-stat_ready-wi.patch \
            file://${LINUX_VERSION}/0003-media-dcmipp-statcap-correct-bins-stat-capture.patch \
            file://${LINUX_VERSION}/0004-media-dcmipp-statcap-average-stat-capture-requires-2.patch \
            file://${LINUX_VERSION}/0005-media-dcmipp-statcap-set-back-COLD_START-on-ctrl-cha.patch \
            file://${LINUX_VERSION}/0006-fixup-media-dcmipp-statcap-stat-region-pixel-count-r.patch \
            file://${LINUX_VERSION}/0007-media-dcmipp-statcap-use-luminance-by-default-for-BI.patch \
"

PR = "r2"