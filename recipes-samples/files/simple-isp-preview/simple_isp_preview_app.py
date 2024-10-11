#!/usr/bin/python3
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

import os
os.environ['GST_DEBUG'] = '1'
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gst
import signal
import subprocess
import os.path
import re

# Init gstreamer
Gst.init(None)
Gst.init_check(None)
# Init gtk
Gtk.init(None)
Gtk.init_check(None)

# Path definition
RESOURCES_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) + "/resources/"

# Static information about the preview size
PREVIEW_WIDTH  = 640
PREVIEW_HEIGHT = 480

class GstWidget(Gtk.Box):
    """
    Class that handles Gstreamer pipeline using gtkwaylandsink and appsink
    """
    def __init__(self, app):
        super().__init__()
        # connect the gtkwidget with the realize callback
        self.connect('realize', self._on_realize)
        self.app = app

    def _on_realize(self, widget):
        self._camera_pipeline_creation()

    def _camera_pipeline_creation(self):
        """
        creation of the gstreamer pipeline when gstwidget is created dedicated to handle
        camera stream
        """
        # gstreamer pipeline creation
        self.gst_pipeline = Gst.Pipeline.new("Simple ISP preview application")

        # creation of the source element
        self.libcamerasrc = Gst.ElementFactory.make("libcamerasrc", "libcamera")
        if not self.libcamerasrc:
            raise Exception("Could not create Gstreamer camera source element")

        #creation of the libcamerasrc caps for the 3 pipelines
        caps = "video/x-raw,width=" + str(PREVIEW_WIDTH) + ",height=" + str(PREVIEW_HEIGHT) + ",format=RGB16"
        print("Main pipe configuration: ", caps)
        caps_src = Gst.Caps.from_string(caps)

        # creation of the queues elements
        queue  = Gst.ElementFactory.make("queue", "queue")

        # creation of the gtkwaylandsink element to handle the gestreamer video stream
        gtkwaylandsink = Gst.ElementFactory.make("gtkwaylandsink")
        self.pack_start(gtkwaylandsink.props.widget, True, True, 0)
        gtkwaylandsink.props.widget.show()

        # Check if all elements were created
        if not all([self.gst_pipeline, self.libcamerasrc, queue, gtkwaylandsink]):
            print("Not all elements could be created. Exiting.")
            return False

        # Add all elements to the pipeline
        self.gst_pipeline.add(self.libcamerasrc)
        self.gst_pipeline.add(queue)
        self.gst_pipeline.add(gtkwaylandsink)

        # linking elements together
        # libcamerasrc | src   --> queue  [caps_src] --> gtkwaylandsink

        queue.link_filtered(gtkwaylandsink, caps_src)

        src_pad = self.libcamerasrc.get_static_pad("src")
        src_pad.link(queue.get_static_pad("sink"))

        # view-finder
        src_pad.set_property("stream-role", 3)

        # getting pipeline bus
        self.bus_preview = self.gst_pipeline.get_bus()
        self.bus_preview.add_signal_watch()
        self.bus_preview.connect('message::error', self._msg_error_cb)
        self.bus_preview.connect('message::eos', self._msg_eos_cb)
        self.bus_preview.connect('message::info', self._msg_info_cb)
        self.bus_preview.connect('message::state-changed', self._msg_state_changed_cb)

        # set pipeline in playing mode
        self.gst_pipeline.set_state(Gst.State.PLAYING)

        return True

    def _msg_eos_cb(self, bus, message):
        """
        catch gstreamer end of stream signal
        """
        print('eos message -> {}'.format(message))

    def _msg_info_cb(self, bus, message):
        """
        catch gstreamer info signal
        """
        print('info message -> {}'.format(message))

    def _msg_error_cb(self, bus, message):
        """
        catch gstreamer error signal
        """
        print('error message -> {}'.format(message.parse_error()))

    def _msg_state_changed_cb(self, bus, message):
        """
        catch gstreamer state changed signal
        """
        oldstate,newstate,pending = message.parse_state_changed()
        if (oldstate == Gst.State.NULL) and (newstate == Gst.State.READY):
            Gst.debug_bin_to_dot_file(self.gst_pipeline, Gst.DebugGraphDetails.ALL,"pipeline_py_NULL_READY")

    def set_libcamera_property(self, property, value):
        self.libcamerasrc.set_property(property, value)

    def get_libcamera_property(self, property):
        return self.libcamerasrc.get_property(property)

class MainWindow(Gtk.Window):
    """
    This class handles all the functions necessary
    to display video stream in GTK GUI
    """
    def __init__(self,app):
        """
        Setup instances of class and shared variables
        useful for the application
        """
        Gtk.Window.__init__(self)
        self.app = app
        self._main_ui_creation()

    def _set_ui_param(self):
        """
        Setup all the UI parameter
        """
        self.ui_icon_exit_size = '50'

    def _main_ui_creation(self):
        """
        Setup the Gtk UI of the main window
        """
        # remove the title bar
        self.set_decorated(False)

        self.first_drawing_call = True
        GdkDisplay = Gdk.Display.get_default()
        monitor = Gdk.Display.get_monitor(GdkDisplay, 0)
        workarea = Gdk.Monitor.get_workarea(monitor)

        GdkScreen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        css_path = RESOURCES_DIRECTORY + "Default.css"
        self.set_name("main_window")
        provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_screen(GdkScreen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.maximize()
        self.screen_width = workarea.width
        self.screen_height = workarea.height

        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('destroy', Gtk.main_quit)
        self._set_ui_param()

        # setup video box containing gst stream in camera preview mode
        # and a openCV picture in still picture mode
        self.video_box = Gtk.HBox()
        self.video_box.set_name("gui_main_video")

        # camera preview => gst stream
        self.video_widget = self.app.gst_widget
        self.video_widget.set_app_paintable(True)
        self.video_box.pack_start(self.video_widget, True, True, 0)

        # setup the exit box which contains the exit button
        self.exit_box = Gtk.VBox()
        self.exit_box.set_name("gui_main_exit")
        self.exit_icon_path = RESOURCES_DIRECTORY + 'exit_' + self.ui_icon_exit_size + 'x' +  self.ui_icon_exit_size + '.png'
        self.exit_icon = Gtk.Image.new_from_file(self.exit_icon_path)
        self.exit_icon_event = Gtk.EventBox()
        self.exit_icon_event.add(self.exit_icon)
        self.exit_box.pack_start(self.exit_icon_event,False,False,2)

        # setup main box which group the three previous boxes
        self.main_box =  Gtk.HBox()
        self.exit_box.set_name("gui_main")
        self.main_box.pack_start(self.video_box,True,True,0)
        self.main_box.pack_start(self.exit_box,False,False,0)
        self.add(self.main_box)
        return True

class OverlayWindow(Gtk.Window):
    """
    This class handles all the functions necessary
    to display overlayed information on top of the
    video stream
    """
    def __init__(self,app):
        """
        Setup instances of class and shared variables
        usefull for the application
        """
        Gtk.Window.__init__(self)
        self.app = app
        self.decimation = 0
        self.stat_area = [0, 0, 0, 0]
        self._overlay_ui_creation()

    def _set_ui_param(self):
        """
        Setup all the UI parameter
        """
        self.ui_icon_exit_size = '50'

    def _exit_icon_cb(self,eventbox, event):
        """
        Exit callback to close application
        """
        self.app.exit_app()

    def _overlay_ui_creation(self):
        """
        Setup the Gtk UI of the overlay window
        """
        # remove the title bar
        self.set_decorated(False)

        self.first_drawing_call = True
        GdkDisplay = Gdk.Display.get_default()
        monitor = Gdk.Display.get_monitor(GdkDisplay, 0)
        workarea = Gdk.Monitor.get_workarea(monitor)

        GdkScreen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        css_path = RESOURCES_DIRECTORY + "Default.css"
        self.set_name("overlay_window")
        provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_screen(GdkScreen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.maximize()
        self.screen_width = workarea.width
        self.screen_height = workarea.height

        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('destroy', Gtk.main_quit)
        self._set_ui_param()

        # setup video box containing a transparent drawing area
        # to draw over the video stream
        self.video_box = Gtk.HBox()
        self.video_box.set_name("gui_overlay_video")
        self.video_box.set_app_paintable(True)
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.drawing)
        self.drawing_area.set_name("overlay_draw")
        self.drawing_area.set_app_paintable(True)
        self.video_box.pack_start(self.drawing_area, True, True, 0)

        # setup the exit box which contains the exit button
        self.exit_box = Gtk.VBox()
        self.exit_box.set_name("gui_overlay_exit")
        self.exit_icon_path = RESOURCES_DIRECTORY + 'exit_' + self.ui_icon_exit_size + 'x' +  self.ui_icon_exit_size + '.png'
        self.exit_icon = Gtk.Image.new_from_file(self.exit_icon_path)
        self.exit_icon_event = Gtk.EventBox()
        self.exit_icon_event.add(self.exit_icon)
        self.exit_icon_event.connect("button_press_event",self._exit_icon_cb)
        self.exit_box.pack_start(self.exit_icon_event,False,False,2)

        # setup main box which group the three previous boxes
        self.main_box =  Gtk.HBox()
        self.exit_box.set_name("gui_overlay")
        self.main_box.pack_start(self.video_box,True,True,0)
        self.main_box.pack_start(self.exit_box,False,False,0)
        self.add(self.main_box)
        return True

    def drawing(self, widget, cr):
        """
        Drawing callback used to draw with cairo on
        the drawing area
        """
        if self.app.first_drawing_call :
            self.app.first_drawing_call = False
            self.drawing_width = widget.get_allocated_width()
            self.drawing_height = widget.get_allocated_height()
            self.label_printed = True
            # uncomment this line to display stat area
            #GLib.idle_add(self.update_stat_area)

            #adapt the drawing overlay depending on the image/camera stream displayed
            preview_ratio = float(PREVIEW_WIDTH) / float(PREVIEW_HEIGHT)
            self.preview_height = self.drawing_height
            self.preview_width =  preview_ratio * self.preview_height
            if self.preview_width >= self.drawing_width:
                self.offset_x = 0
                self.preview_width = self.drawing_width
                self.preview_height = self.preview_width / preview_ratio
                self.offset_y = (self.drawing_height - self.preview_height)/2
            else :
                self.offset_x = (self.drawing_width - self.preview_width)/2
                self.offset_y = 0

            return False

        if self.decimation:
            ratio_x = self.preview_width / self.app.sensor_width / self.decimation
            ratio_y = self.preview_height / self.app.sensor_height / self.decimation
            # Red dash line
            cr.set_source_rgb(1.0, 0.0, 0.0)  # Red color
            cr.set_dash([10.0, 5.0])  # 10 units dash, 5 units gap
            cr.set_line_width(2.0)
            # Draw the rectangle
            cr.rectangle((self.stat_area[0] * ratio_x) + self.offset_x,
                         (self.stat_area[1] * ratio_y) + self.offset_y,
                         (self.stat_area[2] * ratio_x),
                         (self.stat_area[3] * ratio_y))
            cr.stroke()

        return True

    def update_stat_area(self):
        # If new position of statistic area is detected then draw it on the overlay area
        self.decimation = self.app.gst_widget.libcamerasrc.get_property('decimation-factor')
        if self.decimation:
            rectangle = self.app.gst_widget.libcamerasrc.get_property('statistic-area')
            for elem1, elem2 in zip(rectangle, self.stat_area):
                if elem1 != elem2:
                    self.stat_area = rectangle
                    self.app.update_ui()

        return True

class Application:
    """
    Class that handles the whole application
    """
    def __init__(self):
        #init variables uses :
        self.first_drawing_call = True
        self.window_width = 0
        self.window_height = 0
        self.sensor_name = None
        self.sensor_bayer_pattern = None
        self.sensor_pixel_depth = None
        self.sensor_width = None
        self.sensor_height = None
        self.sensor_expo_min = None
        self.sensor_expo_max = None
        self.sensor_gain_min = None
        self.sensor_gain_max = None
        self.get_sensor_information()
        self.get_display_resolution()

        #instantiate the Gstreamer pipeline
        self.gst_widget = GstWidget(self)
        #instantiate the main window
        self.main_window = MainWindow(self)
        #instantiate the overlay window
        self.overlay_window = OverlayWindow(self)
        self.show_all()

    def get_sensor_information(self):
        tmp_file = "/tmp/sensor_info.txt"
        cmd = "cam -c1 -C15 --list-controls --list-properties --meta >> " + tmp_file
        subprocess.run(cmd, shell=True)

        # Check if /tmp/sensor_info.txt file exists
        if not os.path.exists(tmp_file):
            print("Fail to recover sensor information.")
            print("The application cannot start")
            os._exit(1)
        else:
            # Define the regular expression pattern
            pattern_name = r'Property: Model = (\w+)'
            pattern_bayer_arrangement = r'Property: ColorFilterArrangement = (\d+)'
            pattern_pixel_depth = r'SensorBitsPerPixel = (\d+)'
            pattern_resolution = r'Property: PixelArraySize = (\d+)x(\d+)'
            pattern_expo = r'Control: ExposureTime: \[(\d+)\.\.(\d+)\]'
            pattern_gain = r'Control: AnalogueGain_dB: \[([0-9.]+)\.\.([0-9.]+)\]'

            # Read the file and search for the pattern
            with open(tmp_file, 'r') as file:
                for line in file:
                    match = re.search(pattern_name, line)
                    if match:
                        self.sensor_name = str(match.group(1))
                    match = re.search(pattern_bayer_arrangement, line)
                    if match:
                        self.sensor_bayer_pattern = int(match.group(1))
                    match = re.search(pattern_pixel_depth, line)
                    if match:
                        self.sensor_pixel_depth = int(match.group(1))
                    match = re.search(pattern_resolution, line)
                    if match:
                        self.sensor_width  = int(match.group(1))
                        self.sensor_height = int(match.group(2))
                    match = re.search(pattern_expo, line)
                    if match:
                        self.sensor_expo_min = int(match.group(1))
                        self.sensor_expo_max = int(match.group(2))
                    match = re.search(pattern_gain, line)
                    if match:
                        self.sensor_gain_min = int(float(match.group(1)))
                        self.sensor_gain_max = int(float(match.group(2)))

            # remove the temporary file
            os.remove(tmp_file)

        if self.sensor_name is None:
            print("Sensor information: fail to get sensor name")
            print("The application cannot start")
            os._exit(1)
        if self.sensor_bayer_pattern is None:
            print("Sensor information: fail to get bayer pattern information")
            print("The application cannot start")
            os._exit(1)
        if self.sensor_width is None or self.sensor_height is None:
            print("Sensor information: fail to get sensor width x height values")
            print("The application cannot start")
            os._exit(1)
        if self.sensor_expo_min is None or self.sensor_expo_max is None:
            print("Sensor information: fail to get exposure min/max values")
            print("The application cannot start")
            os._exit(1)
        if self.sensor_gain_min is None or self.sensor_gain_max is None:
            print("Sensor information: fail to get gain min/max values")
            print("The application cannot start")
            os._exit(1)

        print("Detected sensor: " + self.sensor_name + " (" + str(self.sensor_width) + "x" + str(self.sensor_height) + ")")

    def get_display_resolution(self):
        """
        Used to ask the system for the display resolution
        """
        cmd = "modetest -M stm -c > /tmp/display_resolution.txt"
        subprocess.run(cmd, shell=True)
        display_info_pattern = "#0"
        display_information = ""
        display_resolution = ""
        display_width = ""
        display_height = ""

        f = open("/tmp/display_resolution.txt", "r")
        for line in f :
            if display_info_pattern in line:
                display_information = line
        display_information_splited = display_information.split()
        for i in display_information_splited :
            if "x" in i :
                display_resolution = i
        display_resolution = display_resolution.replace('x',' ')
        display_resolution = display_resolution.split()
        display_width = display_resolution[0]
        display_height = display_resolution[1]

        print("display resolution is : ",display_width, " x ", display_height)
        self.window_width = int(display_width)
        self.window_height = int(display_height)
        return 0

    # Updating the labels and the inference infos displayed on the GUI interface - camera input
    def update_statistic_area_overlay(self):
        """
        Updating the statistic area size and position
        """
        # TODO

        return True

    def update_ui(self):
        """
        refresh overlay UI
        """
        self.update_statistic_area_overlay()
        self.main_window.queue_draw()
        self.overlay_window.queue_draw()

    def show_all(self):
        self.main_window.connect("delete-event", Gtk.main_quit)
        self.main_window.show_all()
        self.overlay_window.connect("delete-event", Gtk.main_quit)
        self.overlay_window.show_all()
        return True

    def exit_app(self):
        self.main_window.destroy()
        self.overlay_window.destroy()
        Gtk.main_quit()
        return False

def signal_handler(sig, frame):
    application.exit_app()

if __name__ == '__main__':
    # add signal to catch CRTL+C
    signal.signal(signal.SIGINT, signal_handler)

    #Application initialisation
    try:
        application = Application()
    except Exception as exc:
        print("Main Exception: ", exc )

    Gtk.main()
    print("gtk main finished")
    print("application exited properly")
    os._exit(0)
