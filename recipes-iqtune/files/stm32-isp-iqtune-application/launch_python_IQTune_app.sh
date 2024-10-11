#!/bin/sh
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

weston_user=$(ps aux | grep '/usr/bin/weston '|grep -v 'grep'|awk '{print $1}')

cmd="python3 /usr/local/x-linux-isp/stm32-isp-iqtune-app/stm32_isp_iqtune_app.py"

if [ "$weston_user" != "root" ]; then
    echo "user : "$weston_user
    script -qc "su -l $weston_user -c '$cmd'"
else
    $cmd
fi
