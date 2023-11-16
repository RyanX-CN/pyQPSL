from Tool import *
os_path_append("./Plugins/ThorlabsPlugin/bin")
try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup import configure_path
    configure_path()
except ImportError:
    configure_path = None

from .thorlabs_tsi_sdk.tl_camera import TLCameraSDK, TLCamera, Frame
from .thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from .thorlabs_tsi_sdk.tl_camera_enums import OPERATION_MODE
from .thorlabs_tsi_sdk.tl_camera_enums import TRIGGER_POLARITY
from .thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from PIL import Image, ImageTk
import typing
import threading
import asyncio
try:
    #  For Python 2.7 queue is named Queue
    import Queue as queue
except ImportError:
    import queue
import cv2

class ImageAcquisitionThread(threading.Thread):

    def __init__(self, camera, spin_hwcap, mode):
        # type: (TLCamera) -> ImageAcquisitionThread
        super(ImageAcquisitionThread, self).__init__()
        self._camera = camera
        self._previous_timestamp = 0
        self.spin_hwcap = spin_hwcap
        self.mode = mode
        self.cur_frames_count = 0
        self.total_frames_count = self.spin_hwcap.value()

        # setup color processing if necessary
        if self._camera.camera_sensor_type != SENSOR_TYPE.BAYER:
            # Sensor type is not compatible with the color processing library
            self._is_color = False
        else:
            self._mono_to_color_sdk = MonoToColorProcessorSDK()
            self._image_width = self._camera.image_width_pixels
            self._image_height = self._camera.image_height_pixels
            self._mono_to_color_processor = self._mono_to_color_sdk.create_mono_to_color_processor(
                SENSOR_TYPE.BAYER,
                self._camera.color_filter_array_phase,
                self._camera.get_color_correction_matrix(),
                self._camera.get_default_white_balance_matrix(),
                self._camera.bit_depth
            )
            self._is_color = True

        self._bit_depth = camera.bit_depth
        self._camera.image_poll_timeout_ms = 2000  # Do not want to block for long periods of time
        self._image_queue = queue.Queue(maxsize=2)
        self._hwcap_queue = queue.Queue(maxsize=0)
        self._stop_event = threading.Event()

    def get_output_queue(self):
        # type: (type(None)) -> queue.Queue
        return self._image_queue

    def get_output_hwcapqueue(self):
        # type: (type(None)) -> queue.Queue
        return self._hwcap_queue

    def stop(self):
        self._stop_event.set()

    def _get_color_image(self, frame):
        # type: (Frame) -> Image
        # verify the image size
        width = frame.image_buffer.shape[1]
        height = frame.image_buffer.shape[0]
        if (width != self._image_width) or (height != self._image_height):
            self._image_width = width
            self._image_height = height
            print("Image dimension change detected, image acquisition thread was updated")
        # color the image. transform_to_24 will scale to 8 bits per channel
        color_image_data = self._mono_to_color_processor.transform_to_24(frame.image_buffer,
                                                                         self._image_width,
                                                                         self._image_height)
        color_image_data = color_image_data.reshape(self._image_height, self._image_width, 3)
        # return PIL Image object
        return Image.fromarray(color_image_data, mode='RGB')

    def _get_image(self, frame):
        # type: (Frame) -> Image
        # no coloring, just scale down image to 8 bpp and place into PIL Image object
        #scaled_image = frame.image_buffer >> (self._bit_depth - 8)
        scaled_image = frame.image_buffer >> (self._bit_depth-8)
        return Image.fromarray(scaled_image)
        
    def run(self):
        while not self._stop_event.is_set():
            try:
                frame = self._camera.get_pending_frame_or_null()
                if frame is not None:
                    '''
                    if self._is_color:
                        pil_image = self._get_color_image(frame)
                    else:
                        pil_image = self._get_image(frame)
                    self._image_queue.put_nowait(pil_image)
                    '''

                    #硬件触发下进行
                    if self.mode == 1:
                        if self.cur_frames_count < self.total_frames_count:
                            self._hwcap_queue.put_nowait(frame.image_buffer)
                            self.cur_frames_count+=1
                            #print('cur_frames_count:'+str(self.cur_frames_count))
                    elif self.mode == 0:
                        if self._is_color:
                            pil_image = self._get_color_image(frame)
                        else:
                            pil_image = self._get_image(frame)
                        self._image_queue.put_nowait(pil_image)

            except queue.Full:
                # No point in keeping this image around when the queue is full, let's skip to the next one
                if self._hwcap_queue.full:
                    print("hwcap_queue " + " full")
                pass
            except Exception as error:
                print("Encountered error: {error}, image acquisition will stop.".format(error=error))
                break
        print("Image acquisition has stopped")
        if self._is_color:
            self._mono_to_color_processor.dispose()
            self._mono_to_color_sdk.dispose()

'''
class ImageGetHwCaptureThread(threading.Thread):
    def __init__(self, hwcap_queue, spin_hwcap, label_hwcap_process, cap_getdmdir):
        super(ImageGetHwCaptureThread, self).__init__()
        self.hwcap_queue = hwcap_queue
        self.spin_hwcap = spin_hwcap
        self.label_hwcap_process = label_hwcap_process
        self.cap_getdmdir = cap_getdmdir
        self._stop_event = threading.Event()

        #硬件触发使用
        folder = self.cap_getdmdir.get_path()
        if len(folder) > 0:
            self.filename = folder + "/"+time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))+'.bin'

        self.cur_frames_count = 0
        self.total_frames_count = self.spin_hwcap.value()
        self.dlg = 'cap:'+str(self.cur_frames_count)
        self.label_hwcap_process.set_text(self.dlg)
        self.bin_data = np.array([], dtype=np.uint16)

    def _set_hwcapture(self, image_data):
        self.cur_frames_count += 1
        image_data = image_data.astype('uint16')
        self.bin_data = np.append(self.bin_data, image_data)

        if self.cur_frames_count%1000==0 or  self.cur_frames_count == self.total_frames_count:
            with open(self.filename, 'ab+') as f:   # ab+: 在文本末尾追加内容
                f.write(bytes(self.bin_data))
                f.close()
                self.bin_data = np.array([], dtype=np.uint16)

        self.dlg = 'cap:'+str(self.cur_frames_count)
        self.label_hwcap_process.set_text(self.dlg)

    def run(self):
        while not self._stop_event.is_set():
            try:
                if self.cur_frames_count < self.total_frames_count:
                    image_data = self.hwcap_queue.get_nowait()
                    self._set_hwcapture(image_data)
            except queue.Empty:
                pass 
            except Exception as error:
                print("Encountered error: {error}, ImageGetHwCaptureThread will stop.".format(error=error))
                break

    def stop(self):
        self._stop_event.set()
'''

class ImageSet2labelThread(threading.Thread):
    def __init__(self, image_queue, hwcap_queue,  label_screen, label_fps, spin_hwcap, label_hwcap_process, cap_getdmdir, camera, mode):
        super(ImageSet2labelThread, self).__init__()
        self.image_queue = image_queue
        self.hwcap_queue = hwcap_queue
        self.lab_screen = label_screen
        self.lab_fps = label_fps
        self.spin_hwcap = spin_hwcap
        self.label_hwcap_process = label_hwcap_process
        self.cap_getdmdir = cap_getdmdir
        self.camera = camera
        self.mode = mode
        self._stop_event = threading.Event()

        self._bit_depth = self.camera.bit_depth
        self.dispcount = 0

        #硬件触发使用
        folder = self.cap_getdmdir.get_path()
        if len(folder) > 0:
            self.filename = folder + "/"+time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))+'.bin'

        self.cur_frames_count = 0
        self.total_frames_count = self.spin_hwcap.value()
        self.dlg = 'cap:'+str(self.cur_frames_count)
        self.label_hwcap_process.set_text(self.dlg)
        self.bin_data = np.array([], dtype=np.uint16)

    def _set_screen(self, img):
        #img = np.max(img) - img
        img = img.astype('uint8')
        height, width = img.shape
        bytesPerLine = 1*width
        #cv2.cvtColor(img, cv2.COLOR_BayerBG2GRAY, img)
        qimg = QImage(img, 
                width, 
                height,
                bytesPerLine,
                QImage.Format.Format_Grayscale8)
        pixmap = QPixmap(qimg)
        #QApplication.processEvents()
        self.lab_screen.setPixmap(pixmap)
        self.lab_screen.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.lab_screen.update()
        self.lab_fps.set_text('fps:'+ str(self.camera.get_measured_frame_rate_fps()))
        self.lab_fps.update()

    def _set_hwcapture(self, image_data):
        self.cur_frames_count += 1
        image_data = image_data.astype('uint16')
        self.bin_data = np.append(self.bin_data, image_data)

        if self.cur_frames_count%1000==0 or  self.cur_frames_count == self.total_frames_count:
            with open(self.filename, 'ab+') as f:   # ab+: 在文本末尾追加内容
                f.write(bytes(self.bin_data))
                f.close()
                self.bin_data = np.array([], dtype=np.uint16)

        #QApplication.processEvents()
        self.dlg = 'cap:'+str(self.cur_frames_count)
        self.label_hwcap_process.set_text(self.dlg)
        self.label_hwcap_process.update()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            try:
                if self.mode == 0:
                    image = self.image_queue.get_nowait()
                    image_arr = np.asarray(image)
                    self._set_screen(image_arr)
                elif self.mode == 1:
                    image_buffer = self.hwcap_queue.get_nowait()

                    # 抓图
                    if self.cur_frames_count < self.total_frames_count:
                        self._set_hwcapture(image_buffer)

                    time.sleep(0.01)                
                    # 预览
                    scaled_image = image_buffer >> (self._bit_depth - 8)
                    pil_image  = Image.fromarray(scaled_image)
                    image_arr = np.asarray(pil_image)
                    self._set_screen(image_arr)

                    time.sleep(0.01) 
                        
            except queue.Empty:
                pass 
            except Exception as error:
                print("Encountered error: {error}, image set to label will stop.".format(error=error))
                break

class ThorlabsPluginWorker(QPSLWorker):
    def __init__(self, parent: QWidget, object_name: str, virtual_mode: bool):
        super(ThorlabsPluginWorker, self).__init__(parent=parent,
                                                  object_name=object_name)

class ThorlabsPluginUI(QPSLTabWidget):

    def __init__(self,
                 parent: QWidget,
                 object_name="Thorlabs",
                 virtual_mode=False,
                 font_family="Arial"):
        super(ThorlabsPluginUI, self).__init__(parent=parent,
                                               object_name=object_name)

        self.m_font_family = font_family
        self.m_worker = ThorlabsPluginWorker(self,
                                            object_name="worker",
                                            virtual_mode=virtual_mode)
        self.camera = None
        self.sdk = None
        self.image_acquisition_thread = None
        self.image_set2label_thread = None
        self.mode = 0
        self.setupUi()
        #self.init_screen()
        self.setupLogic()

    def setup_config_cap(self):
        self.savepath.add_widget(
            widget=QPSLGetDirectoryBox(self.savepath,
                                        object_name="cap_getdmdir",
                                        text="抓图路径:"))              #savepath-0
        self.savepath.add_widget(
            widget=QPSLTextLabel(self.savepath,
                                    object_name="label_capdir",
                                    frame_shape=QFrame.Shape.NoFrame))  #savepath-1

        self.savepath.set_stretch(sizes=(2, 3))

    #@QPSLObjectBase.log_decorator()
    def setupUi(self):
        self.setMinimumSize(2000, 1500)
    
        # tab_video下的控件水平摆放
        self.add_tab(tab=QPSLGridGroupList(self, object_name="tab_video"), title="video")
        self.tab_video.add_widget_simple(widget=QPSLScalePixmapLabel(self.tab_video, object_name="lab_screen"),grid=(0, 0, 0, 0))              #tab_video-0
        self.tab_video.add_widget_simple(widget=QPSLVerticalGroupList(self.tab_video, object_name="control"),grid=(0, 0, 1, 1))                #tab_video-1
        self.tab_video.add_widget_simple(widget=QPSLGridGroupList(self.tab_video, object_name="roi"),grid=(1, 1, 0, 0))                        #tab_video-2
        self.tab_video.add_widget_simple(widget=QPSLHorizontalGroupList(self.tab_video, object_name="savepath"),grid=(1, 1, 1, 1))             #tab_video-3

        ## Control
        self.control.add_widget(
                widget=QPSLToggleButton(self.control,
                                        object_name="btn_cnt",
                                        closed_text="disconnect",
                                        opened_text="connect"))           #control-0
        self.btn_cnt.set_opened()

        
        self.control.add_widget(
                widget=QPSLToggleButton(self.control,
                                        object_name="btn_play",
                                        closed_text="stop",
                                        opened_text="play"))           #control-1
        self.btn_play.set_opened()
        self.btn_play.setEnabled(False)
        
        self.control.add_widget(widget=QPSLRadioButton(
            self.control, object_name="btn_sw_mode", text="software mode"))      #control-2
        self.btn_sw_mode.setChecked(True)
        #self.btn_sw_mode.setEnabled(False)
            

        self.control.add_widget(widget=QPSLRadioButton(
            self.control, object_name="btn_hw_mode", text="hardware mode"))      #control-3
        #self.btn_hw_mode.setEnabled(False)

        self.control.add_widget(widget=QPSLSpinBox(
            self.control,
            object_name="spin_exposure",
            min=40,
            max=26843432,
            value=40,
            prefix="exposure:",
            suffix="us"))                                                 #control-4
        self.spin_exposure.setEnabled(False)

        self.control.add_widget(widget=QPSLSpinBox(
            self.control,
            object_name="spin_gain",
            min=0,
            max=480,
            value=50,
            prefix="gain:",
            suffix=""))                                                   #control-5
        self.spin_gain.setEnabled(False)

        self.control.add_widget(widget=QPSLDoubleSpinBox(
            self.control,
            object_name="spin_fps",
            min=0.906,
            max=34.815,
            value=34.815,
            prefix="fps:",
            suffix="",
            decimals = 3))                                                   #control-6
        self.spin_fps.setEnabled(False)

        self.control.add_widget(widget=QPSLSpinBox(
            self.control,
            object_name="spin_hwcap",
            min=0,
            max=40000,
            value=10000,
            prefix="hwcap_cnt:",
            suffix=""))                                                   #control-7
        self.spin_hwcap.setEnabled(False)

        self.control.add_widget(
            widget=QPSLTextLabel(self.control,
                                    object_name="label_hwcap_process",
                                    frame_shape=QFrame.Shape.NoFrame))    #control-8
        self.label_hwcap_process.set_text("cap:0")

        self.control.add_widget(
            widget=QPSLTextLabel(self.control,
                                    object_name="label_fps",
                                    frame_shape=QFrame.Shape.NoFrame))    #control-9
        self.label_fps.set_text("fps:")

        self.control.add_widget(widget=QPSLPushButton(
            self.control, object_name="btn_capture", text="capture"))      #control-10
        self.btn_capture.setEnabled(False)

        
        ## ROI
        self.roi.add_widget_simple(widget=QPSLSpinBox(
            self.roi,
            object_name="spin_roi_upper_left_x",
            min=0,
            max=1440,
            value=0,
            prefix="ROI-左上x坐标:",
            suffix=""), grid=(0,0,0,0))                                    #roi-0

        self.roi.add_widget_simple(widget=QPSLSpinBox(
            self.roi,
            object_name="spin_roi_upper_left_y",
            min=0,
            max=1080,
            value=0,
            prefix="ROI-左上y坐标:",
            suffix=""), grid=(0,0,1,1))                                   #roi-1
 
        self.roi.add_widget_simple(widget=QPSLSpinBox(
            self.roi,
            object_name="spin_roi_lower_right_x",
            min=0,
            max=1440,
            value=1440,
            prefix="ROI-右下x坐标:",
            suffix=""), grid=(1,1,0,0))                                   #roi-2

        self.roi.add_widget_simple(widget=QPSLSpinBox(
            self.roi,
            object_name="spin_roi_lower_right_y",
            min=0,
            max=1080,
            value=1080,
            prefix="ROI-右下y坐标:",
            suffix=""), grid=(1,1,1,1))                                  #roi-3

        ## savepath
        self.setup_config_cap()



        #print(self.control.get_widget(0))

        #self.control.set_stretch(sizes=(1, 1, 1, 1, 1, 1))
        #self.tab_video.set_stretch(sizes=(3, 1))
        self.tab_video.set_stretch(row_sizes=[5,1], column_sizes=[3,1])

    def init_screen(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        npix = QPixmap(cur_dir + '/../../resources/screen_base.png')
        self.lab_screen.setPixmap(npix)
        self.lab_screen.setScaledContents(True)
        
    def setupLogic(self):
        connect_queued(self.btn_play.sig_open, self.on_btn_stop_video_clicked)
        connect_queued(self.btn_play.sig_close, self.on_btn_play_video_clicked)

        connect_direct(self.btn_capture.clicked, self.on_btn_capture_clicked)
        
        connect_direct(self.cap_getdmdir.sig_path_changed,
                       self.label_capdir.setText)
        self.cap_getdmdir.set_path("D:/")

        connect_direct(self.spin_gain.sig_value_changed, self.edit_spin_gain)
        connect_direct(self.spin_exposure.sig_value_changed, self.edit_spin_exposure)
        connect_direct(self.spin_fps.sig_value_changed, self.edit_spin_fps)

        connect_direct(self.btn_sw_mode.clicked, self.on_btn_trigger_sw_clicked)
        connect_direct(self.btn_hw_mode.clicked, self.on_btn_trigger_hw_clicked)

        connect_direct(self.btn_cnt.sig_open, self.on_btn_disconnect_clicked)
        connect_direct(self.btn_cnt.sig_close, self.on_btn_connect_clicked)


    def edit_spin_gain(self):
        try:
            print('gain:'+str(self.spin_gain.value()))
            self.camera.gain = self.spin_gain.value()
        except Exception as error:
            print("Encountered error: {error}, edit_spin_gain error.".format(error=error)) 

    def edit_spin_exposure(self):
        try:
            print('exposure:'+str(self.spin_exposure.value()))
            self.camera.exposure_time_us = self.spin_exposure.value()
            #更新帧率范围
            self.spin_fps.setMaximum(self.camera.frame_rate_control_value_range.max)
            self.spin_fps.setMinimum(self.camera.frame_rate_control_value_range.min)
            self.spin_fps.setValue(self.camera.frame_rate_control_value)
            self.spin_fps.setSuffix('('+str(self.camera.frame_rate_control_value_range.min)+','+str(self.camera.frame_rate_control_value_range.max)+')')
            self.spin_fps.update()
        except Exception as error:
            print("Encountered error: {error}, edit_spin_exposure error.".format(error=error)) 

    def edit_spin_fps(self):
        try:
            print('fps:'+str(self.spin_fps.value()))
            self.camera.frame_rate_control_value = self.spin_fps.value()
            #更新曝光
            self.spin_exposure.setMaximum(self.camera.exposure_time_range_us.max)
            self.spin_exposure.setMinimum(self.camera.exposure_time_range_us.min)
            self.spin_exposure.setValue(self.camera.exposure_time_us)
            self.spin_exposure.setSuffix('us' + '('+str(self.camera.exposure_time_range_us.min)+'us'+','+str(self.camera.exposure_time_range_us.max)+'us'+')')
            self.spin_exposure.update()
        except Exception as error:
            print("Encountered error: {error}, edit_spin_fps error.".format(error=error)) 
 
    def on_btn_play_video_clicked(self):
        print('play')
        
        try:
            print(self.camera.operation_mode)
            #print(self.camera.get_is_operation_mode_supported(OPERATION_MODE.HARDWARE_TRIGGERED))

            print("Generating app...")
            print('gain range:'+str(self.camera.gain_range))
            print('exposure range:'+str(self.camera.exposure_time_range_us))
            print('frame rate range:'+str(self.camera.frame_rate_control_value_range))

            self.image_acquisition_thread = ImageAcquisitionThread(self.camera, self.spin_hwcap, self.mode)
            print("Starting image acquisition thread...")
            self.image_acquisition_thread.start()

            print("Starting ImageSet2label Thread...")
            self.image_set2label_thread = ImageSet2labelThread(self.image_acquisition_thread.get_output_queue(), self.image_acquisition_thread.get_output_hwcapqueue(), 
                self.lab_screen, self.label_fps, self.spin_hwcap, self.label_hwcap_process, self.cap_getdmdir, self.camera, self.mode)
            self.image_set2label_thread.start()

            '''
            if self.mode == 1:
                print("Starting ImageGetHwCapture Thread...")
                self.ImageGetHwCaptureThread = ImageGetHwCaptureThread(self.image_acquisition_thread.get_output_hwcapqueue(), self.spin_hwcap, self.label_hwcap_process, self.cap_getdmdir)
                self.ImageGetHwCaptureThread.start()
            '''
            
            self.btn_capture.setEnabled(True)
            self.btn_sw_mode.setEnabled(False)
            self.btn_hw_mode.setEnabled(False)
            self.spin_hwcap.setEnabled(False)
            self.btn_play.set_closed()
        except Exception as error:
            print("Encountered error: {error}, on_btn_play_video_clicked error.".format(error=error)) 
            
    def on_btn_stop_video_clicked(self):
        print('stop')
        print("Waiting for image acquisition thread to finish...")
        if self.image_set2label_thread:
            self.image_set2label_thread.stop()
            self.image_set2label_thread.join()

        if self.image_acquisition_thread:
            self.image_acquisition_thread.stop()
            self.image_acquisition_thread.join()

        '''
        if self.mode == 1:
            if self.ImageGetHwCaptureThread:
                self.ImageGetHwCaptureThread.stop()
                self.ImageGetHwCaptureThread.join()
        '''

        print("Closing resources...")
        self.btn_capture.setEnabled(False)
        self.btn_play.set_opened()
        self.spin_hwcap.setEnabled(True)

    def on_btn_capture_clicked(self):
        print('capture')
        folder = self.cap_getdmdir.get_path()
        if len(folder) > 0:
            filename = folder + "/"+time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))+'.tif'
        
        NUMBER_OF_IMAGES = 10  # Number of TIFF images to be saved
        TAG_BITDEPTH = 32768
        TAG_EXPOSURE = 32769
        
        #  setup the camera for continuous acquisition
        #self.camera.frames_per_trigger_zero_for_unlimited = 0
        #self.camera.image_poll_timeout_ms = 2000  # 2 second timeout
        #self.camera.arm(2)

        # save these values to place in our custom TIFF tags later
        bit_depth = self.camera.bit_depth
        exposure = self.camera.exposure_time_us

        # need to save the image width and height for color processing
        image_width = self.camera.image_width_pixels
        image_height = self.camera.image_height_pixels

        # initialize a mono to color processor if this is a color camera
        is_color_camera = (self.camera.camera_sensor_type == SENSOR_TYPE.BAYER)
        mono_to_color_sdk = None
        mono_to_color_processor = None
        if is_color_camera:
            mono_to_color_sdk = MonoToColorProcessorSDK()
            mono_to_color_processor = mono_to_color_sdk.create_mono_to_color_processor(
                self.camera.camera_sensor_type,
                self.camera.color_filter_array_phase,
                self.camera.get_color_correction_matrix(),
                self.camera.get_default_white_balance_matrix(),
                self.camera.bit_depth
            )

        # begin acquisition
        #self.camera.issue_software_trigger()
        frames_counted = 0
        while frames_counted < NUMBER_OF_IMAGES:
            frame = self.camera.get_pending_frame_or_null()
            if frame is None:
                raise TimeoutError("Timeout was reached while polling for a frame, program will now exit")

            frames_counted += 1
            
            image_data = frame.image_buffer
            #image_data = image_data >> (bit_depth - 8)
            image_data = image_data.astype('uint16')
            
            if is_color_camera:
                # transform the raw image data into RGB color data
                image_data = mono_to_color_processor.transform_to_48(image_data, image_width, image_height)
                image_data = image_data.reshape(image_height, image_width, 3)

            with tifffile.TiffWriter(filename, append=True) as tiff:
                """
                    Setting append=True here means that calling tiff.save will add the image as a page to a multipage TIFF. 
                """
                tiff.save(data=image_data,  # np.ushort image data array from the camera
                            compression=0,   # amount of compression (0-9), by default it is uncompressed (0)
                            extratags=[(TAG_BITDEPTH, 'I', 1, bit_depth, False),  # custom TIFF tag for bit depth
                                        (TAG_EXPOSURE, 'I', 1, exposure, False)]  # custom TIFF tag for exposure
                            )
        #self.camera.disarm()

        # we did not use context manager for color processor, so manually dispose of it
        if is_color_camera:
            try:
                mono_to_color_processor.dispose()
            except Exception as exception:
                print("Unable to dispose mono to color processor: " + str(exception))
            try:
                mono_to_color_sdk.dispose()
            except Exception as exception:
                print("Unable to dispose mono to color sdk: " + str(exception))

        print(filename)

    def on_btn_trigger_hw_clicked(self):
        print("hw mode")
        self.mode = 1

    def on_btn_trigger_sw_clicked(self):
        print("sw mode")
        self.mode = 0

    def on_btn_connect_clicked(self):
        print("connect")
        try:
            self.sdk = TLCameraSDK()
            self.camera_list = self.sdk.discover_available_cameras()
            self.camera = self.sdk.open_camera(self.camera_list[0])

            if self.mode == 0:
                self.camera.operation_mode = OPERATION_MODE.SOFTWARE_TRIGGERED
                self.camera.is_frame_rate_control_enabled = True
            elif self.mode == 1:
                self.camera.operation_mode = OPERATION_MODE.BULB
                self.camera.trigger_polarity = TRIGGER_POLARITY.ACTIVE_HIGH
                self.camera.is_frame_rate_control_enabled = False
                self.spin_hwcap.setEnabled(True)

            self.camera.roi = (self.spin_roi_upper_left_x.value(), self.spin_roi_upper_left_y.value(), self.spin_roi_lower_right_x.value(), self.spin_roi_lower_right_y.value())
            print("Setting camera parameters...")
            self.camera.frames_per_trigger_zero_for_unlimited = 0
            self.camera.arm(2)

            if self.mode == 0:
                self.camera.issue_software_trigger()

            # 根据当下相机的配置获取gain、exprosure、fps的上下限
            self.spin_gain.setMaximum(self.camera.gain_range.max)
            self.spin_gain.setMinimum(self.camera.gain_range.min)
            self.spin_gain.setValue(self.camera.gain)
            self.spin_gain.setSuffix('('+str(self.camera.gain_range.min)+','+str(self.camera.gain_range.max)+')')

            
            self.spin_exposure.setMaximum(self.camera.exposure_time_range_us.max)
            self.spin_exposure.setMinimum(self.camera.exposure_time_range_us.min)
            self.spin_exposure.setValue(self.camera.exposure_time_us)
            self.spin_exposure.setSuffix('us' + '('+str(self.camera.exposure_time_range_us.min)+'us'+','+str(self.camera.exposure_time_range_us.max)+'us'+')')

            
            self.spin_fps.setMaximum(self.camera.frame_rate_control_value_range.max)
            self.spin_fps.setMinimum(self.camera.frame_rate_control_value_range.min)
            self.spin_fps.setValue(self.camera.frame_rate_control_value)
            self.spin_fps.setSuffix('('+str(self.camera.frame_rate_control_value_range.min)+','+str(self.camera.frame_rate_control_value_range.max)+')')

            self.btn_cnt.set_closed()
            self.btn_play.setEnabled(True)
            self.btn_play.set_opened()
            self.btn_sw_mode.setEnabled(False)
            self.btn_hw_mode.setEnabled(False)
            self.spin_roi_upper_left_x.setEnabled(False)
            self.spin_roi_upper_left_y.setEnabled(False)
            self.spin_roi_lower_right_x.setEnabled(False)
            self.spin_roi_lower_right_y.setEnabled(False)
            self.spin_exposure.setEnabled(True)
            self.spin_gain.setEnabled(True)
            self.spin_fps.setEnabled(True)


        except Exception as error:
            print("Encountered error: {error}, on_btn_connect_clicked error.".format(error=error)) 
            if self.camera:
                self.camera.dispose()
            if self.sdk:
                self.sdk.dispose()

    def on_btn_disconnect_clicked(self):
        print("disconnect")
        print("Waiting for image acquisition thread to finish...")
        try:
            if self.image_set2label_thread:
                self.image_set2label_thread.stop()
                self.image_set2label_thread.join()

            if self.image_acquisition_thread:
                self.image_acquisition_thread.stop()
                self.image_acquisition_thread.join()

            '''
            if self.mode == 1:
                if self.ImageGetHwCaptureThread:
                    self.ImageGetHwCaptureThread.stop()
                    self.ImageGetHwCaptureThread.join()
            '''

            self.camera.dispose()
            self.sdk.dispose()
            self.btn_cnt.set_opened()
            self.btn_play.setEnabled(False)
            self.btn_play.set_closed()
            self.btn_sw_mode.setEnabled(True)
            self.btn_hw_mode.setEnabled(True)
            self.spin_roi_upper_left_x.setEnabled(True)
            self.spin_roi_upper_left_y.setEnabled(True)
            self.spin_roi_lower_right_x.setEnabled(True)
            self.spin_roi_lower_right_y.setEnabled(True)
            self.spin_exposure.setEnabled(False)
            self.spin_gain.setEnabled(False)
            self.spin_fps.setEnabled(False)
            self.spin_hwcap.setEnabled(False)
            self.lab_screen.clear()

            #self.init_screen()

        except Exception as error:
            print("Encountered error: {error}, on_btn_disconnect_clicked error.".format(error=error)) 

    @property
    def tab_video(self) -> QPSLHorizontalGroupList:
        return self.get_tab(0)

    # tab_video
    @property
    def lab_screen(self) -> QPSLScalePixmapLabel:
        return self.tab_video.get_widget(0)

    @property
    def control(self) -> QPSLVerticalGroupList:
        return self.tab_video.get_widget(1)

    @property
    def roi(self) -> QPSLGridGroupList:
        return self.tab_video.get_widget(2)

    @property
    def savepath(self) -> QPSLHorizontalGroupList:
        return self.tab_video.get_widget(3)

    # control
    @property
    def btn_cnt(self) -> QPSLToggleButton:
        return self.control.get_widget(0)
    
    @property
    def btn_play(self) -> QPSLToggleButton:
        return self.control.get_widget(1)

    @property
    def btn_sw_mode(self) -> QPSLRadioButton:
        return self.control.get_widget(2)

    @property
    def btn_hw_mode(self) -> QPSLRadioButton:
        return self.control.get_widget(3)

    @property
    def spin_exposure(self) -> QPSLSpinBox:
        return self.control.get_widget(4)

    @property
    def spin_gain(self) -> QPSLSpinBox:
        return self.control.get_widget(5)

    @property
    def spin_fps(self) -> QPSLDoubleSpinBox:
        return self.control.get_widget(6)

    @property
    def spin_hwcap(self) -> QPSLSpinBox:
        return self.control.get_widget(7)

    @property
    def label_hwcap_process(self) -> QPSLTextLabel:
        return self.control.get_widget(8)
        
    @property
    def label_fps(self) -> QPSLTextLabel:
        return self.control.get_widget(9)
        
    @property
    def btn_capture(self) -> QPSLPushButton:
        return self.control.get_widget(10)

    # save_path
    @property
    def cap_getdmdir(self) -> QPSLGetDirectoryBox:
        return self.savepath.get_widget(0)

    @property
    def label_capdir(self) -> QPSLTextLabel:
        return self.savepath.get_widget(1)

    # roi
    @property
    def spin_roi_upper_left_x(self) -> QPSLSpinBox:
        return self.roi.get_widget(0)

    @property
    def spin_roi_upper_left_y(self) -> QPSLSpinBox:
        return self.roi.get_widget(1)

    @property
    def spin_roi_lower_right_x(self) -> QPSLSpinBox:
        return self.roi.get_widget(2)

    @property
    def spin_roi_lower_right_y(self) -> QPSLSpinBox:
        return self.roi.get_widget(3)



        


MainWidget = ThorlabsPluginUI