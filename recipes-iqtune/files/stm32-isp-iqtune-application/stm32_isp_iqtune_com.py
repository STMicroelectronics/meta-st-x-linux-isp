#!/usr/bin/python3
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

import serial
import ctypes
import time
import subprocess
import threading
from struct import pack, unpack
from enum import Enum

class CmdOperation(Enum):
  CMD_OP_SET           = 0x00
  CMD_OP_GET           = 0x01
  CMD_OP_SET_OK        = 0x80
  CMD_OP_SET_FAILURE   = 0x81
  CMD_OP_GET_OK        = 0x82
  CMD_OP_GET_FAILURE   = 0x83

class CmdID(Enum):
  CMD_STATREMOVAL         = 0x00
  CMD_DECIMATION          = 0x01
  CMD_DEMOSAICING         = 0x02
  CMD_CONTRAST            = 0x03
  CMD_STATISTICAREA       = 0x04
  CMD_SENSORGAIN          = 0x05
  CMD_SENSOREXPOSURE      = 0x06
  CMD_BADPIXELALGO        = 0x07
  CMD_BADPIXELSTATIC      = 0x08
  CMD_BLACKLEVELSTATIC    = 0x09
  CMD_AECALGO             = 0x0A
  CMD_AWBALGO             = 0x0B
  CMD_AWBPROFILE          = 0x0C
  CMD_ISPGAINSTATIC       = 0x0D
  CMD_COLORCONVSTATIC     = 0x0E
  CMD_STATISTICUP         = 0x0F
  CMD_STATISTICDOWN       = 0x10
  CMD_DUMP_PREVIEW_FRAME  = 0x11
  CMD_DUMP_ISP_FRAME      = 0x12
  CMD_DUMP_RAW_FRAME      = 0x13
  CMD_STOPPREVIEW         = 0x14
  CMD_STARTPREVIEW        = 0x15
  CMD_DCMIPPVERSION       = 0x16
  CMD_GAMMA               = 0x17
  CMD_SENSORINFO          = 0x18
  CMD_SENSORTESTPATTERN   = 0x19
#Application API commands for test purpose
  CMD_USER_EXPOSURETARGET = 0x80
  CMD_USER_LISTWBREFMODES = 0x81
  CMD_USER_WBREFMODE      = 0x82

class IQTuneCom():
    """
    Class that handles communication between the application and the host computer
    """
    def __init__(self, app):
        self._app = app
        self._comport = '/dev/ttyGS0'
        self._baudrate = 115200
        self._ser = None

        # Disable ethernet usb gadget
        cmd = 'su -c "stm32_usbotg_eth_config.sh stop"'
        ret = subprocess.run(cmd, shell=True)
        if ret.returncode != 0:
            print("Fail to disable ethernet usb gadget")
        # Enable serial usb gadget for USB serial communication
        cmd = 'su -c "stm32_usbotg_acm_config.sh start"'
        ret = subprocess.run(cmd, shell=True)
        if ret.returncode != 0:
            print("Fail to enable selrial usb gadget")

    def __del__(self):
        self._close()
        # Disable serial usb gadget
        cmd = 'su -c "stm32_usbotg_acm_config.sh stop"'
        test = subprocess.run(cmd, shell=True)
        if test.returncode != 0:
            print("Fail to disable serial usb gadget")
        # Restore ethernet usb gadget
        cmd = 'su -c "stm32_usbotg_eth_config.sh start"'
        test = subprocess.run(cmd, shell=True)
        if test.returncode != 0:
            print("Fail to restore ethernet usb gadget")

    def _open(self):
        if self._ser is None or not self._ser.is_open:
            self._ser = serial.Serial(self._comport, self._baudrate)

    def _close(self):
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def _get_data(self):
        self._open()
        try:
            nb_bytes = self._ser.in_waiting
            if nb_bytes > 0:
                data = self._ser.read(size=nb_bytes)
                #print("get data nb_bytes=" + str(nb_bytes))
                #print(data)
                return data
        except:
            # serial error detected
            if self._ser.is_open:
                self._close()
        return

    def _send_data(self, data):
        self._open()
        try:
            #print("send data")
            #print(data)
            self._ser.write(data)
            self._ser.flush()
        except:
            # serial error detected
            if self._ser.is_open:
                self._close()
        return

    def _update_statistic_profile(self):
        # this function is called in a thread to update the statistic profile
        # after a sleep of 1.5 seconds so that the algorithm are not slow down
        # anymore by the full stats profile.
        # 0 = Full stats (histogram and average, up and down)
        # 1 = average up stats
        # 2 = average down stats
        time.sleep(1.5)  # Wait for 1.5 seconds
        self._app.gst_widget.set_libcamera_property('statistic-profile', 2)

    def cleanup(self):
        self.__del__()

    def cmd_parser_setconfig(self, data):
        """
        set config requested
        """
        # Depending on the field structure used, alignement is done on a uint32 word for the enable field.
        # For some configuration, the enable value is coded on a single byte or a uint32 word to match the
        # structure alignment from uint8 to uint32 transition.
        ret = 0
        tempo = 0
        values = []
        cmd = data[1]
        if cmd == CmdID.CMD_STATREMOVAL.value:
            # Statistic removal not supported with the IQTune desktop application.
            # The statistic removal is managed by the entry pad of the ISP subdev using the crop property
            # ex: media-ctl -d $media_dev --set-v4l2 "'dcmipp_main_isp':0[crop:(0,5)/1280x713]"
            # This command return an error
            ret = 1

        elif cmd == CmdID.CMD_DEMOSAICING.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                val = unpack('4B', data[6:10]) # Skip the bayer pattern type which is already programmed and cannot be changed
                self._app.gst_widget.set_libcamera_property('demosaicing-filters', val)
            self._app.gst_widget.set_libcamera_property('demosaicing-enable', enable)

        elif cmd == CmdID.CMD_CONTRAST.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                values = unpack('<9I', data[8:44]) # padding byte inserted data[5:8] by the ctype structure alignment
                self._app.gst_widget.set_libcamera_property('contrast-values', values)
            self._app.gst_widget.set_libcamera_property('contrast-enable', enable)

        elif cmd == CmdID.CMD_STATISTICAREA.value:
            # retrieve values from the command
            values = unpack('<4I', data[4:20])
            self._app.gst_widget.set_libcamera_property('statistic-area', values)
            tempo = 0.8 # add tempo when stat area is set to ensure that the statistic values are computed before receiving a get stat command.

        elif cmd == CmdID.CMD_SENSORGAIN.value:
            # retrieve values from the command
            val = unpack('<1I', data[4:8])[0]
            self._app.gst_widget.set_libcamera_property('sensor-gain', float(val)/1000) # convert from mdB to dB

        elif cmd == CmdID.CMD_SENSOREXPOSURE.value:
            # retrieve values from the command
            val = unpack('<1I', data[4:8])[0]
            self._app.gst_widget.set_libcamera_property('sensor-exposure', val)

        elif cmd == CmdID.CMD_BADPIXELALGO.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                val = unpack('<1I', data[8:12])[0] # padding byte inserted data[5:8] by the ctype structure alignment
                self._app.gst_widget.set_libcamera_property('badpixel-algo-threshold', val)
            else:
                self._app.gst_widget.set_libcamera_property('badpixel-algo-threshold', 0)

        elif cmd == CmdID.CMD_BADPIXELSTATIC.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                val = data[5]
                self._app.gst_widget.set_libcamera_property('badpixel-strength', val)
            self._app.gst_widget.set_libcamera_property('badpixel-enable', enable)

        elif cmd == CmdID.CMD_BLACKLEVELSTATIC.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                values = unpack('3B', data[5:8])
                self._app.gst_widget.set_libcamera_property('black-level-values', values)
            self._app.gst_widget.set_libcamera_property('black-level-enable', enable)

        elif cmd == CmdID.CMD_AECALGO.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                val = data[5]
                # convert the exposure compensation enum into float value
                if ctypes.c_int8(val).value == -4:
                    val = -2.0
                elif ctypes.c_int8(val).value == -3:
                    val = -1.5
                elif ctypes.c_int8(val).value == -2:
                    val = -1.0
                elif ctypes.c_int8(val).value == -1:
                    val = -0.5
                elif ctypes.c_int8(val).value == 0:
                    val = 0.0
                elif ctypes.c_int8(val).value == 1:
                    val = 0.5
                elif ctypes.c_int8(val).value == 2:
                    val = 1.0
                elif ctypes.c_int8(val).value == 3:
                    val = 1.5
                elif ctypes.c_int8(val).value == 4:
                    val = 2.0
                self._app.gst_widget.set_libcamera_property('aec-algo-exposure-compensation', val)
            self._app.gst_widget.set_libcamera_property('aec-algo-enable', enable)

        elif cmd == CmdID.CMD_AWBALGO.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                profileNames = []
                profileNames.append(data[5:37].decode('utf-8'))    #
                profileNames.append(data[37:69].decode('utf-8'))   #
                profileNames.append(data[69:101].decode('utf-8'))  # 5 profiles ID of 32 characters (32 bytes)
                profileNames.append(data[101:133].decode('utf-8')) #
                profileNames.append(data[133:165].decode('utf-8')) #
                self._app.gst_widget.set_libcamera_property('awb-algo-profile-names', profileNames)
                # padding byte inserted data[165:168] by the ctype structure alignment
                refColorTemps = unpack('<5I', data[168:188]) # 5 reference color temperature values of 4 bytes
                self._app.gst_widget.set_libcamera_property('awb-algo-profile-color-temps', refColorTemps)
                ispGains = unpack('<15I', data[188:248]) # 5 ISP gain profile of 3 values of 4 bytes
                self._app.gst_widget.set_libcamera_property('awb-algo-profile-isp-gains', ispGains)
                ccmCoeffs = unpack('<45i', data[248:428]) # 5 CCM of 3x3 values of 4 bytes
                self._app.gst_widget.set_libcamera_property('awb-algo-profile-ccms', ccmCoeffs)
            self._app.gst_widget.set_libcamera_property('awb-algo-enable', enable)

        elif cmd == CmdID.CMD_ISPGAINSTATIC.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                values = unpack('<3I', data[8:20]) # padding byte inserted data[5:8] by the ctype structure alignment
                self._app.gst_widget.set_libcamera_property('isp-gain-values', values)
            self._app.gst_widget.set_libcamera_property('isp-gain-enable', enable)

        elif cmd == CmdID.CMD_COLORCONVSTATIC.value:
            # retrieve values from the command
            enable = data[4]
            if enable:
                values = unpack('<9i', data[8:44]) # padding byte inserted data[5:8] by the ctype structure alignment
                self._app.gst_widget.set_libcamera_property('ccm-values', values)
            self._app.gst_widget.set_libcamera_property('ccm-enable', enable)

        elif cmd == CmdID.CMD_STOPPREVIEW.value:
            # With Gstreamer implementation we do not need to stop/start the preview to capture frames
            # Simply skip the stop preview request.
            ret = 0

        elif cmd == CmdID.CMD_STARTPREVIEW.value:
            # With Gstreamer implementation we do not need to stop/start the preview to capture frames
            # Simply skip the start preview request.
            ret = 0

        elif cmd == CmdID.CMD_GAMMA.value:
            # Gamma is automaticaly activated by libcamera according to the role set by the user
            # This command return an error
            ret = 1

        elif cmd == CmdID.CMD_SENSORTESTPATTERN.value:
            print("CMD_SENSORTESTPATTERN")

        else:
            print("Unkown set config command (" + str(cmd) + ")")
            ret = 1

        # send command anwser
        tempo += 0.15 # tempo of minimum 0.1 seconds before sending back the command
        time.sleep(tempo)
        if ret:
            tx_data = bytes([CmdOperation.CMD_OP_GET_FAILURE.value, cmd, ret])
            self._send_data(tx_data)
            return False

        tx_data = bytes([CmdOperation.CMD_OP_GET_OK.value, cmd])
        self._send_data(tx_data)
        return True

    def cmd_parser_getconfig(self, data):
        """
        get config requested
        """
        # Depending on the field structure used, alignement is done on a uint32 word for the enable field.
        # For some configuration, the enable value is coded on a single byte or a uint32 word to match the
        # structure alignment from uint8 to uint32 transition.
        ret = 0
        cmd = data[1]
        if cmd == CmdID.CMD_STATREMOVAL.value:
            # Statistic removal not supported with the IQTune desktop application.
            # The statistic removal is managed by the entry pad of the ISP subdev using the crop property
            # ex: media-ctl -d $media_dev --set-v4l2 "'dcmipp_main_isp':0[crop:(0,5)/1280x713]"
            ret = 1

        elif cmd == CmdID.CMD_DECIMATION.value:
            val = self._app.gst_widget.get_libcamera_property('decimation-factor')
            read_values = pack('B', val)

        elif cmd == CmdID.CMD_DEMOSAICING.value:
            enable = self._app.gst_widget.get_libcamera_property('demosaicing-enable')
            values = self._app.gst_widget.get_libcamera_property('demosaicing-filters')
            read_values = pack('B', enable)
            read_values = read_values + pack('B', self._app.sensor_bayer_pattern)
            for val in values:
                read_values = read_values + pack('B', val)

        elif cmd == CmdID.CMD_CONTRAST.value:
            enable = self._app.gst_widget.get_libcamera_property('contrast-enable')
            values = self._app.gst_widget.get_libcamera_property('contrast-values')
            read_values = pack('<I', enable)
            for val in values:
                read_values = read_values + pack('<I', val)

        elif cmd == CmdID.CMD_STATISTICAREA.value:
            values = self._app.gst_widget.get_libcamera_property('statistic-area')
            read_values = b''
            for val in values:
                read_values = read_values + pack('<I', val)

        elif cmd == CmdID.CMD_SENSORGAIN.value:
            val = self._app.gst_widget.get_libcamera_property('sensor-gain')
            read_values = pack('<I', int(val * 1000)) # convert from dB to mdB

        elif cmd == CmdID.CMD_SENSOREXPOSURE.value:
            val = self._app.gst_widget.get_libcamera_property('sensor-exposure')
            read_values = pack('<I', val)

        elif cmd == CmdID.CMD_BADPIXELALGO.value:
            val = self._app.gst_widget.get_libcamera_property('badpixel-algo-threshold')
            if val == 0:
                # the badpixel algo is disabled
                read_values = pack('<I', False)
            else:
                # the badpixel algo is enabled
                read_values = pack('<I', True)
            read_values = read_values + pack('<I', val)

        elif cmd == CmdID.CMD_BADPIXELSTATIC.value:
            enable = self._app.gst_widget.get_libcamera_property('badpixel-enable')
            strength = self._app.gst_widget.get_libcamera_property('badpixel-strength')
            count = self._app.gst_widget.get_libcamera_property('badpixel-count')
            read_values = pack('B', enable)
            read_values = read_values + pack('B', strength)
            read_values = read_values + b'\x00' * 2 # padding to keep c-type structure aligned
            read_values = read_values + pack('<I', count)

        elif cmd == CmdID.CMD_BLACKLEVELSTATIC.value:
            enable = self._app.gst_widget.get_libcamera_property('black-level-enable')
            values = self._app.gst_widget.get_libcamera_property('black-level-values')
            read_values = pack('B', enable)
            for val in values:
                read_values = read_values + pack('B', val)

        elif cmd == CmdID.CMD_AECALGO.value:
            enable = self._app.gst_widget.get_libcamera_property('aec-algo-enable')
            expval = self._app.gst_widget.get_libcamera_property('aec-algo-exposure-compensation')
            exptarget = self._app.gst_widget.get_libcamera_property('aec-algo-exposure-target')
            # convert float value to exposure compensation enum value
            if expval == -2.0:
                expval = -4
            elif expval == -1.5:
                expval = -3
            elif expval == -1.0:
                expval = -2
            elif expval == -0.5:
                expval = -1
            elif expval == 0.0:
                expval = 0
            elif expval == 0.5:
                expval = 1
            elif expval == 1.0:
                expval = 2
            elif expval == 1.5:
                expval = 3
            elif expval == 2.0:
                expval = 4
            read_values = pack('B', enable)
            read_values = read_values + pack('b', expval)
            read_values = read_values + b'\x00' * 2 # padding to keep c-type structure aligned
            read_values = read_values + pack('<I', exptarget)

        elif cmd == CmdID.CMD_AWBALGO.value:
            enable = self._app.gst_widget.get_libcamera_property('awb-algo-enable')
            profileNames = self._app.gst_widget.get_libcamera_property('awb-algo-profile-names')
            refColorTemps = self._app.gst_widget.get_libcamera_property('awb-algo-profile-color-temps')
            ispGains = self._app.gst_widget.get_libcamera_property('awb-algo-profile-isp-gains')
            ccmCoeffs = self._app.gst_widget.get_libcamera_property('awb-algo-profile-ccms')
            read_values = pack('B', enable)
            for val in profileNames:
                read_values = read_values + val.encode('utf-8') + b'\x00' * (32 - len(val)) # 32 bytes aligned
            read_values = read_values + b'\x00' * 3 # padding to keep c-type structure aligned
            for val in refColorTemps:
                read_values = read_values + pack('<I', val)
            for val in ispGains:
                read_values = read_values + pack('<I', val)
            for val in ccmCoeffs:
                read_values = read_values + pack('<i', val)

        elif cmd == CmdID.CMD_AWBPROFILE.value:
            currentProfileName = self._app.gst_widget.get_libcamera_property('awb-current-profile-name')
            if currentProfileName is None:
                    currentProfileName = ""
            currentColorTemp = self._app.gst_widget.get_libcamera_property('awb-current-profile-color-temp')
            read_values = currentProfileName.encode('utf-8') + b'\x00' * (32 - len(currentProfileName)) # 32 bytes aligned
            read_values = read_values + pack('<I', currentColorTemp)

        elif cmd == CmdID.CMD_ISPGAINSTATIC.value:
            enable = self._app.gst_widget.get_libcamera_property('isp-gain-enable')
            values = self._app.gst_widget.get_libcamera_property('isp-gain-values')
            read_values = pack('<I', enable)
            for val in values:
                read_values = read_values + pack('<I', val)

        elif cmd == CmdID.CMD_COLORCONVSTATIC.value:
            enable = self._app.gst_widget.get_libcamera_property('ccm-enable')
            values = self._app.gst_widget.get_libcamera_property('ccm-values')
            read_values = pack('<I', enable)
            for val in values:
                read_values = read_values + pack('<i', val)

        elif cmd == CmdID.CMD_STATISTICUP.value:
            # Set statistic profile to get full stats:
            # 0 = Full stats (histogram and average, up and down)
            # 1 = average up stats
            # 2 = average down stats
            self._app.gst_widget.set_libcamera_property('statistic-profile', 0)
            avg_values = self._app.gst_widget.get_libcamera_property('statistic-get-average-up')
            bin_values = self._app.gst_widget.get_libcamera_property('statistic-get-histogram-up')
            read_values = b''
            for val in avg_values:
                read_values = read_values + pack('B', val)
            for val in bin_values:
                read_values = read_values + pack('<I', val)

        elif cmd == CmdID.CMD_STATISTICDOWN.value:
            # Set statistic profile to get full stats:
            # 0 = Full stats (histogram and average, up and down)
            # 1 = average up stats
            # 2 = average down stats
            self._app.gst_widget.set_libcamera_property('statistic-profile', 0)
            avg_values = self._app.gst_widget.get_libcamera_property('statistic-get-average-down')
            bin_values = self._app.gst_widget.get_libcamera_property('statistic-get-histogram-down')
            read_values = b''
            for val in avg_values:
                read_values = read_values + pack('B', val)
            for val in bin_values:
                read_values = read_values + pack('<I', val)
            # revert back the statistic profile in some seconds
            threading.Thread(target=self._update_statistic_profile).start()


        elif cmd == CmdID.CMD_DUMP_PREVIEW_FRAME.value:
            # Wait parameter are applied before asking for a preview dump
            time.sleep(0.2)
            self._app.gst_widget.dump_preview = True
            # Wait while dump is really performed
            while self._app.gst_widget.dump_preview:
                time.sleep(0.01)

            # if dump size if 0 then return error
            if self._app.gst_widget.dump_size == 0:
                ret = 1

            # Fill read_values variable with the metadata frame information concatenate with the buffer itself
            read_values = b''
            read_values = read_values + pack('<I', self._app.gst_widget.dump_size)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_width)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_height)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_pitch)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_format)
            read_values = read_values + b'DUMP DATA[' + self._app.gst_widget.dump_buffer + b'DUMP DATA]'

        elif cmd == CmdID.CMD_DUMP_ISP_FRAME.value:
            self._app.gst_widget.dump_rgb = True
            # Wait while dump is really performed
            while self._app.gst_widget.dump_rgb:
                time.sleep(0.01)

            # if dump size if 0 then return error
            if self._app.gst_widget.dump_size == 0:
                ret = 1

            # Fill read_values variable with the metadata frame information concatenate with the buffer itself
            read_values = b''
            read_values = read_values + pack('<I', self._app.gst_widget.dump_size)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_width)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_height)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_pitch)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_format)
            read_values = read_values + b'DUMP DATA[' + self._app.gst_widget.dump_buffer + b'DUMP DATA]'

        elif cmd == CmdID.CMD_DUMP_RAW_FRAME.value:
            self._app.gst_widget.dump_raw = True
            # Wait while dump is really performed
            while self._app.gst_widget.dump_raw:
                time.sleep(0.01)

            # if dump size if 0 then return error
            if self._app.gst_widget.dump_size == 0:
                ret = 1

            # Fill read_values variable with the metadata frame information concatenate with the buffer itself
            read_values = b''
            read_values = read_values + pack('<I', self._app.gst_widget.dump_size)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_width)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_height)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_pitch)
            read_values = read_values + pack('<I', self._app.gst_widget.dump_format)
            read_values = read_values + b'DUMP DATA[' + self._app.gst_widget.dump_buffer + b'DUMP DATA]'

        elif cmd == CmdID.CMD_DCMIPPVERSION.value:
            values = self._app.gst_widget.get_libcamera_property('hw-revision')
            read_values = b''
            for val in values:
                read_values = read_values + pack('<I', val)

        elif cmd == CmdID.CMD_GAMMA.value:
            # Gamma is automaticaly activated by libcamera according to the role set by the user
            # This command return an error
            ret = 1

        elif cmd == CmdID.CMD_SENSORINFO.value:
            read_values = b''
            read_values = read_values + self._app.sensor_name.encode('utf-8') + b'\x00' * (32 - len(self._app.sensor_name)) # 32 bytes aligned
            read_values = read_values + pack('B', self._app.sensor_bayer_pattern)
            read_values = read_values + pack('B', self._app.sensor_pixel_depth)
            read_values = read_values + b'\x00' * 2 # padding to keep c-type structure aligned
            read_values = read_values + pack('<I', self._app.sensor_width)
            read_values = read_values + pack('<I', self._app.sensor_height)
            read_values = read_values + pack('<I', self._app.sensor_gain_min)
            read_values = read_values + pack('<I', self._app.sensor_gain_max)
            read_values = read_values + pack('<I', self._app.sensor_expo_min)
            read_values = read_values + pack('<I', self._app.sensor_expo_max)

        elif cmd == CmdID.CMD_SENSORTESTPATTERN.value:
            print("CMD_SENSORTESTPATTERN")
        else:
            print("Unkown get config command (" + str(cmd) + ")")
            ret = 1

        # send command anwser
        if ret:
            tx_data = bytes([CmdOperation.CMD_OP_GET_FAILURE.value, cmd, ret])
            self._send_data(tx_data)
            return False

        tx_data = bytes([CmdOperation.CMD_OP_GET_OK.value, cmd, 0, 0]) + read_values
        self._send_data(tx_data)
        return True

    def cmd_parser_process_command(self, data):
        """
        parse the received data
        """
        operation = data[0]
        if operation == CmdOperation.CMD_OP_SET.value:
            self.cmd_parser_setconfig(data)
        elif operation == CmdOperation.CMD_OP_GET.value:
            self.cmd_parser_getconfig(data)
        else:
            return False

        return True

    def loop(self):
        """
        loop function call as a gtk idle function to check com port reception
        regularly
        """
        data = self._get_data()
        if data:
            if not self.cmd_parser_process_command(data):
                print("Error while processing the received command")

        return True