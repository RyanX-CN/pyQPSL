from Tool import loading_info, Dict, SharedStateController, np, pyqtBoundSignal, tifffile, time, random, numpy_array_shift_2d


def Reconstruction_Read_Sample_Dcimg(img_path: str,
                                     report_signal: pyqtBoundSignal):
    # res = np.random.randint(0, 65535,
    #                         size=(100, 510, 520)).astype(dtype=np.uint16)
    res = tifffile.imread(img_path)
    time.sleep(1)
    report_signal.emit(res)


def Reconstruction_Work(parameters: Dict, start_signal: pyqtBoundSignal,
                        report_signal: pyqtBoundSignal,
                        stop_signal: pyqtBoundSignal):
    start_signal.emit()
    num = len(parameters["input_files"])
    state_controller: SharedStateController = parameters["stateController"]
    report_signal.emit(0)
    for i in range(num):
        loading_info("dealing {0}".format(parameters["input_files"][i]))
        time.sleep(1)
        report_signal.emit(i + 1)
        if state_controller.is_stop():
            break

    stop_signal.emit()


def Pretreatment_Read_TIFF_img(img_path: str, report_signal: pyqtBoundSignal):
    res = tifffile.imread(img_path)
    res: np.ndarray
    if len(res.shape) == 2:
        A = [res]
        dx, dy = 0, 0
        for i in range(20):
            dx += random.randint(0, 30) - 15
            dy += random.randint(0, 30) - 15
            A.append(numpy_array_shift_2d(res, dx, dy))
        report_signal.emit(np.stack(A, axis=0))
    else:
        report_signal.emit(res)


def Pretreatment_Read_TIFF_Division_img(img_path: str,
                                        report_signal: pyqtBoundSignal):
    res = tifffile.imread(img_path)
    res: np.ndarray
    if len(res.shape) == 2:
        A = [res]
        dx, dy = 0, 0
        for i in range(10):
            dx += random.randint(0, 30) - 15
            dy += random.randint(0, 30) - 15
            A.append(numpy_array_shift_2d(res, dx, dy))
        report_signal.emit(np.stack(A, axis=0))
    else:
        report_signal.emit(res)


def Pretreatment_Read_Flatten_img(input_path: str, save_path: str,
                                  report_signal: pyqtBoundSignal):
    res1 = tifffile.imread(input_path)
    res2 = tifffile.imread(save_path)
    res1: np.ndarray
    res2: np.ndarray
    if len(res1.shape) == 2:
        A = [res1]
        B = [res2]
        dx, dy = 0, 0
        for i in range(20):
            dx += random.randint(0, 30) - 15
            dy += random.randint(0, 30) - 15
            A.append(numpy_array_shift_2d(res1, dx, dy))
            B.append(numpy_array_shift_2d(res2, dx, dy))
        report_signal.emit(np.stack(A, axis=0), np.stack(B, axis=0))
    else:
        report_signal.emit(res1, res2)


def Calibration_Work(parameters: Dict, start_signal: pyqtBoundSignal,
                     report_signal: pyqtBoundSignal,
                     stop_signal: pyqtBoundSignal):
    start_signal.emit()
    state_controller: SharedStateController = parameters["stateController"]
    for i in range(100):
        time.sleep(0.01)
        report_signal.emit(i + 1)
        if state_controller.is_stop():
            break
    stop_signal.emit()


def Flatten_Work(parameters: Dict, start_signal: pyqtBoundSignal,
                 report_signal: pyqtBoundSignal, stop_signal: pyqtBoundSignal):
    start_signal.emit()
    state_controller: SharedStateController = parameters["stateController"]
    for i in range(100):
        time.sleep(0.01)
        report_signal.emit(i + 1)
        if state_controller.is_stop():
            break
    stop_signal.emit()


def Reconstruction2_Work(parameters: Dict, start_signal: pyqtBoundSignal,
                         report_signal: pyqtBoundSignal,
                         stop_signal: pyqtBoundSignal):
    start_signal.emit()
    state_controller: SharedStateController = parameters["stateController"]
    for i in range(100):
        time.sleep(0.01)
        report_signal.emit(i + 1)
        if state_controller.is_stop():
            break
    stop_signal.emit()