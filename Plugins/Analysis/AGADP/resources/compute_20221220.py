import warnings

warnings.filterwarnings('ignore')
import tensorflow as tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
import numpy as np
import os
import cv2
import re
import matplotlib.pyplot as plt
import math
from skimage import morphology
import os.path
import io
import pandas as pd
import xlrd
from pandas import Series, DataFrame
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

#------------------------------------读取vf报告上的信息-----------------------------------------
from logging import WARNING
import pdfminer.pdfpage, pdfminer.converter, pdfminer.pdfinterp, pdfminer.psparser, pdfminer.pdfdocument, pdfminer.pdfparser
for mod in [
        pdfminer.pdfpage, pdfminer.converter, pdfminer.pdfinterp,
        pdfminer.psparser, pdfminer.pdfdocument, pdfminer.pdfparser
]:
    mod.log.setLevel(WARNING)
import matplotlib.pyplot

matplotlib.pyplot.set_loglevel("warning")


def get_pdf_page(input_path, fname):
    '''
    取得页面个数
    '''
    filename = input_path + '/' + fname
    fp = open(filename, 'rb')
    return len([p for p in PDFPage.get_pages(fp)])


def pdf_parser(input_path, fname, page_number):
    '''
    取得转换为html的字符
    '''
    filename = os.path.join(input_path, fname)
    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr,
                           retstr,
                           codec=codec,
                           layoutmode="exact",
                           laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    all_pages = [p for p in PDFPage.get_pages(fp)]
    interpreter.process_page(all_pages[page_number])  # 无法分成多个函数处理, 目前只能重新读取并处理
    txt_string = retstr.getvalue()
    retstr.truncate(0)
    return txt_string.decode("utf-8")


def get_all_char(txtdata):
    span_left = '<span style="position:absolute; color:black; left:(\d+)px; top:(\d+)px; font-size:\d+px;">'
    span_right = "</span>"
    value = re.findall(span_left + "([\s\S]+?)" + span_right, txtdata)
    char_df = DataFrame(value, columns=["X", "Y", "V"])
    char_df["X"] = char_df["X"].astype(int)
    char_df["Y"] = char_df["Y"].astype(int)
    return char_df


def char_in_box(box, df):
    '''
    读取box范围内的字符, 并且拼接成字符串
    '''
    x0, y0, dx, dy = (int(u) for u in box)
    part = (df.where((df["X"] > x0) & (df["X"] < x0 + dx) & (df["Y"] > y0)
                     & (df["Y"] < y0 + dy)).dropna())
    return "".join(part["V"].tolist())


def get_basic_info(char_df):
    location_dict = {
        "name and birthday": (50, 130, 200, 30),  # 有不同的检查方式, 位置需要有一定的冗余
        "Eye and exam date time in G Standard":
        (50, 175, 200, 20),  # 有不同的检查方式, 后面再切换
        "Eye and exam date time in LVC Standard": (50, 175, 200, 30),  # 简单粗暴有效
        "Programs": (120, 700, 130, 4),
        "RF": (300, 720, 100, 10),
        "Pupil": (100, 745, 100, 10),
        "MS": (507, 710, 50, 10),
        "MD": (507, 720, 50, 10),
        "sLV": (507, 730, 50, 10),
    }
    Programs_type = char_in_box(location_dict["Programs"], char_df)
    Programs_type = "G Standard"
    if "G Standard" in Programs_type:
        Eye_and_exam_date_time = char_in_box(
            location_dict["Eye and exam date time in G Standard"], char_df)
    elif "LVC Standard" in Programs_type:
        Eye_and_exam_date_time = char_in_box(
            location_dict["Eye and exam date time in LVC Standard"], char_df)


#     print(Eye_and_exam_date_time.split("/"))
    eye, exam_date, exam_time = (x.strip()
                                 for x in Eye_and_exam_date_time.split("/"))

    name_and_birthday = char_in_box(location_dict["name and birthday"],
                                    char_df)
    #     print(name_and_birthday)
    name, birthday = (x.strip() for x in name_and_birthday.split(","))
    try:
        birthday, _ = (x.strip() for x in birthday.split("ID"))
    except:
        pass
    RF, Pupil, MS, MD, sLV = (char_in_box(location_dict[key], char_df)
                              for key in ["RF", "Pupil", "MS", "MD", "sLV"])

    s = Series([
        name, birthday, exam_date + "/" + exam_time, eye, Programs_type, RF,
        Pupil, MS, MD, sLV
    ],
               index=[
                   "name", "birthday", "exam_date", "eye", "Programs_type",
                   "RF", "Pupil", "MS", "MD", "sLV"
               ])
    #     print(s.birthday)
    s.birthday = pd.to_datetime(s.birthday)
    s.exam_date = pd.to_datetime(s.exam_date)
    s.iloc[5:] = pd.to_numeric(s.iloc[5:])
    return s


def get_VF_value(char_df):
    value_c_x = 445
    value_c_y = 290
    value_location = [
        (445, 290, 10, 10), (450, 295, 10, 10), (440, 295, 10, 10),
        (440, 285, 10, 10), (450, 285, 10, 10), (460, 305, 10, 10),
        (435, 305, 10, 10), (435, 280, 10, 10), (460, 280, 10, 10),
        (470, 295, 10, 10), (470, 315, 10, 10), (455, 315, 10, 10),
        (440, 315, 10, 10), (425, 315, 10, 10), (425, 295, 10, 10),
        (425, 285, 10, 10), (425, 270, 10, 10), (440, 270, 10, 10),
        (450, 270, 10, 10), (470, 270, 10, 10), (470, 285, 10, 10),
        (485, 305, 10, 10), (480, 325, 10, 10), (460, 330, 10, 10),
        (435, 330, 10, 10), (415, 325, 10, 10), (410, 305, 10, 10),
        (410, 280, 10, 10), (415, 260, 10, 10), (435, 255, 10, 10),
        (460, 255, 10, 10), (480, 260, 10, 10), (485, 280, 10, 10),
        (505, 305, 10, 10), (500, 325, 10, 10), (500, 345, 10, 10),
        (480, 345, 10, 10), (460, 345, 10, 10), (435, 345, 10, 10),
        (415, 345, 10, 10), (395, 345, 10, 10), (395, 325, 10, 10),
        (390, 305, 10, 10), (390, 280, 10, 10), (395, 260, 10, 10),
        (395, 240, 10, 10), (415, 240, 10, 10), (435, 240, 10, 10),
        (460, 240, 10, 10), (480, 240, 10, 10), (500, 240, 10, 10),
        (500, 260, 10, 10), (505, 280, 10, 10), (515, 315, 10, 10),
        (470, 360, 10, 10), (425, 360, 10, 10), (375, 305, 10, 10),
        (375, 280, 10, 10), (425, 220, 10, 10), (470, 220, 10, 10),
        (515, 270, 10, 10)
    ]
    VF_values = [(char_in_box(v, char_df).strip()) for v in value_location]
    VF_s = Series(VF_values)
    return pd.to_numeric(VF_s)


def get_LVC_value(char_df):
    LVC_value_location = [
        #第1行
        (230, 250, 20, 20),
        (275, 250, 20, 20),
        (320, 250, 20, 20),
        (365, 250, 20, 20),

        #第2行
        (185, 295, 20, 20),
        (230, 295, 20, 20),
        (275, 295, 20, 20),
        (320, 295, 20, 20),
        (365, 295, 20, 20),
        (410, 295, 20, 20),

        #第3行
        (140, 340, 20, 20),
        (185, 340, 20, 20),
        (230, 340, 20, 20),
        (275, 340, 20, 20),
        (320, 340, 20, 20),
        (365, 340, 20, 20),
        (410, 340, 20, 20),
        (455, 340, 20, 20),

        #第4行
        (95, 385, 20, 20),
        (140, 385, 20, 20),
        (185, 385, 20, 20),
        (230, 385, 20, 20),
        (275, 385, 20, 20),
        (320, 385, 20, 20),
        (365, 385, 20, 20),
        (410, 385, 20, 20),
        (455, 385, 20, 20),
        (500, 385, 20, 20),

        #第5行
        (95, 430, 20, 20),
        (140, 430, 20, 20),
        (185, 430, 20, 20),
        (230, 430, 20, 20),
        (275, 430, 20, 20),
        (320, 430, 20, 20),
        (365, 430, 20, 20),
        (410, 430, 20, 20),
        (455, 430, 20, 20),
        (500, 430, 20, 20),

        #中心点
        (295, 450, 20, 20),

        #第6行
        (95, 475, 20, 20),
        (140, 475, 20, 20),
        (185, 475, 20, 20),
        (230, 475, 20, 20),
        (275, 475, 20, 20),
        (320, 475, 20, 20),
        (365, 475, 20, 20),
        (410, 475, 20, 20),
        (455, 475, 20, 20),
        (500, 475, 20, 20),

        #第7行
        (95, 520, 20, 20),
        (140, 520, 20, 20),
        (185, 520, 20, 20),
        (230, 520, 20, 20),
        (275, 520, 20, 20),
        (320, 520, 20, 20),
        (365, 520, 20, 20),
        (410, 520, 20, 20),
        (455, 520, 20, 20),
        (500, 520, 20, 20),

        #第8行
        (140, 565, 20, 20),
        (185, 565, 20, 20),
        (230, 565, 20, 20),
        (275, 565, 20, 20),
        (320, 565, 20, 20),
        (365, 565, 20, 20),
        (410, 565, 20, 20),
        (455, 565, 20, 20),

        #第9行
        (185, 610, 20, 20),
        (230, 610, 20, 20),
        (275, 610, 20, 20),
        (320, 610, 20, 20),
        (365, 610, 20, 20),
        (410, 610, 20, 20),

        #第10行
        (230, 655, 20, 20),
        (275, 655, 20, 20),
        (320, 655, 20, 20),
        (365, 655, 20, 20),
    ]
    VF_values = [(char_in_box(v, char_df).strip()) for v in LVC_value_location]
    VF_s = Series(VF_values)
    return pd.to_numeric(VF_s)


def process_single_file(input_path, fname, output_path, save=False):
    #print("process the file: \t{}".format(os.path.join(input_path,fname)))
    total_page = get_pdf_page(input_path, fname)
    series_list = []
    for p_number in range(total_page):
        t_data = pdf_parser(input_path, fname, p_number)
        c_df = get_all_char(t_data)
        s1 = get_basic_info(c_df)
        if "G Standard" in s1.Programs_type:
            s2 = get_VF_value(c_df)
        elif "LVC" in s1.Programs_type:
            s2 = get_LVC_value(c_df)
        s = pd.concat([s1, s2])
        series_list.append(s)
        if save:
            df = DataFrame(s)
            output_fname = os.path.join(
                output_path,
                "{}_p{}.csv".format(os.path.splitext(fname)[0], p_number + 1))
            df.to_csv(output_fname)
            # print("save to " + output_fname)

    return s1, s2


def process_file_list(input_path, output_path, filename_list, save=False):
    series_list = []
    for fname in filename_list:
        try:
            s_list = process_single_file(input_path,
                                         fname,
                                         output_path,
                                         save=save)
            for s in s_list:
                series_list.append(s)
        except:
            # print("failed in the file: \t{}".format(
            # os.path.join(input_path, fname)))
            pass
    return DataFrame(series_list)


def process_folder(input_path,
                   output_path,
                   save_together=True,
                   save_individual=False):
    pdffiles = [
        name for name in os.listdir(input_path) if name.endswith('.pdf')
    ]
    df = process_file_list(input_path,
                           output_path,
                           pdffiles,
                           save=save_individual)
    if save_together:
        df.to_csv(os.path.join(output_path, "octopus_data.csv"))
    return df


def vf_value_extract(input_path, fname):
    output_path = "./"  # 输出的csv文件位置
    ## 处理单个文件, 并且保存
    s1, s2 = process_single_file(input_path, fname, output_path, save=False)
    return s1, s2


#------------------------------------vf值转为图像-----------------------------------------


def vf_img(vf_data, file_dir, thre_dir):
    THRE_AGE = 45
    data = xlrd.open_workbook(file_dir)
    table = data.sheet_by_name('Octopus')
    x_location = table.col_values(1)
    y_location = table.col_values(2)

    x_location_new = x_location
    y_location_new = y_location
    del x_location_new[32]
    del x_location_new[21]
    del y_location_new[32]
    del y_location_new[21]

    left = min(x_location_new)
    right = max(x_location_new)
    up = max(y_location_new)
    low = min(y_location_new)

    delta = 13
    left_new = left - delta
    right_new = right + delta
    up_new = up + delta
    low_new = low - delta
    width_new = right_new - left_new
    height_new = up_new - low_new

    scale = 224
    scale_blind = 224

    x_blind = 485
    y_blind = 290

    x_location = [(x - left_new) / width_new * scale_blind
                  for x in x_location_new]
    y_location = [(y - low_new) / height_new * scale_blind
                  for y in y_location_new]
    x_location_new = [(x - left_new) / width_new * scale
                      for x in x_location_new]
    y_location_new = [(y - low_new) / height_new * scale
                      for y in y_location_new]

    # np.savez('location.npz', x=x_location_new, y=y_location_new)
    x_blind = int((x_blind - left_new) / width_new * scale_blind)
    y_blind = int((y_blind - low_new) / height_new * scale_blind)

    thre = xlrd.open_workbook(thre_dir)
    table = thre.sheet_by_name('Sheet1')
    bias = table.row_values(1)[1:]
    slop = table.row_values(2)[1:]

    v_min = -38
    v_max = -4

    #data = xlrd.open_workbook(data_dir)
    #table = data.sheet_by_name('Sheet1')
    row_value = vf_data
    del row_value[33]
    del row_value[22]

    row_value = [float(x) for x in row_value]
    slop_thre = [x * (row_value[0] - THRE_AGE) for x in slop]
    bias_thre = [i + j for i, j in zip(bias, slop_thre)]
    row_value = [x - y for x, y in zip(row_value[1:], bias_thre)]

    row_value = [min(x, -4) for x in row_value]

    row_value = [(x - v_min) / (v_max - v_min) * 255 for x in row_value]

    num_cells = len(x_location_new)
    voronoi = np.zeros((scale, scale))

    imgx = np.shape(voronoi)[0]
    imgy = np.shape(voronoi)[1]

    for x in range(imgx):
        for y in range(imgy):
            center_x = (imgx - 1) / 2
            center_y = (imgy - 1) / 2
            if math.hypot(x - center_x, y - center_y) > scale / 2:
                continue
            dmin = math.hypot(imgx - 1, imgy - 1)
            j = -1
            for i in range(num_cells):
                d = math.hypot(x_location_new[i] - x, y_location_new[i] - y)
                if d < dmin:
                    dmin = d
                    j = i
            voronoi[y, x] = row_value[j]
    voronoi = np.uint8(voronoi)
    img = cv2.circle(voronoi, (x_blind, y_blind), 12, 0, -1)
    img = np.uint8(img)
    #img = Image.fromarray(voronoi)
    #img.save('./' + str(row_num) + '.tif')
    return img


#------------------------------------cfp预处理-----------------------------------------


def cv2_imread(path, mode):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), mode)
    return img


def cv2_imwrite(img, path):  #可以读取中文路径
    cv2.imencode('.tif', img)[1].tofile(path)  #tif和tiff一样


def cv2_imshow(img, box_w=640, box_h=640):
    cv2.namedWindow("p", 0)
    cv2.resizeWindow("p", box_w, box_h)
    cv2.imshow('p', img)
    cv2.waitKey(0)


def crop_1st(img):
    # 第1次裁剪：裁减掉原图的黑边和患者信息
    h = np.shape(img)[0]
    w = np.shape(img)[1]

    if (h == 1556) and (w == 1924):  # 因为眼底照有不同尺寸的
        # 裁掉左上角的患者信息
        img[0:300, 0:300, :] = 0

        # 进行截取
        crop_img = img[17:1551, 183:1717, :]  # (1534, 1534, 3)

    if (h == 2136) and (w == 3216):  # 因为眼底照有不同尺寸的
        # 裁掉左上角的患者信息
        img[0:300, 0:300, :] = 0

        # 进行截取
        crop_img = img[15:2136 - 15, 555:3216 - 555, :]  # (2106, 2106, 3)

    if (h == 1728) and (w == 2592):  # 因为眼底照有不同尺寸的
        # 裁掉左上角的患者信息
        img[:, 0:500, :] = 0
        img[:, 2592 - 500:, :] = 0

        # 进行截取
        crop_img = img[75:1728 - 75, 507:2592 - 507, :]  # (1578, 1578, 3)

    # 进行缩放
    out_img = cv2.resize(crop_img,
                         (1534, 1534))  # (1534, 1534, 3) dtype('uint8')

    return out_img


def crop_2nd(img, r):
    # 第2次裁剪：以内切圆进行裁剪，避免边缘亮度过高
    width = np.shape(img)[0]
    height = np.shape(img)[1]

    for i in range(width):
        for j in range(height):
            center_x = (width - 1) / 2
            center_y = (height - 1) / 2
            d = math.hypot(i - center_x, j - center_y)
            if d > r:
                img[i, j] = 0

    return img


def draw_circle(img, maxLoc, r):
    # 取圆
    for i in range(np.shape(img)[0]):
        for j in range(np.shape(img)[1]):
            center_x = maxLoc[0]
            center_y = maxLoc[1]
            d = math.hypot(i - center_y, j - center_x)
            if d > r:
                img[i, j] = 0
    return img


def crop_3rd(img, r):
    # 第3次裁剪：以最亮点为中心进行圆形裁剪，避免视盘周围高亮度血管影响
    (minVal, maxVal, minLoc,
     maxLoc) = cv2.minMaxLoc(img)  #利用cv2.minMaxLoc寻找到图像中最亮和最暗的区域

    x_min = x_max = y_min = y_max = 0
    if ((maxLoc[0] - r)) < 0:
        r = maxLoc[0]
    if ((maxLoc[1] - r)) < 0:
        r = maxLoc[1]
    # if maxLoc[0] + r > np.shape(img)[0]:  #y方向
    #     r = np.shape(ori_img)[0] - maxLoc[0]
    # if maxLoc[1] + r > np.shape(img)[1]:  #y方向
    #     r = np.shape(ori_img)[1] - maxLoc[1]

    img = draw_circle(img, maxLoc, r)

    return img


def Roi(binary_img, ori_img, C3):

    # 计算二值化图像质心
    mass_x, mass_y = np.where(binary_img == 1)

    #cent_x = int(np.average(mass_x)) #y方向
    #cent_y = int(np.average(mass_y)) #x方向

    # 加权取质心
    X = []
    Y = []
    C3 = C3 * binary_img
    total = np.sum(C3)
    for i in range(np.shape(mass_x)[0]):
        value = C3[mass_x[i], mass_y[i]]
        x_weight = mass_x[i] * value  #y方向
        y_weight = mass_y[i] * value  #x方向
        X.append(x_weight)
        Y.append(y_weight)
    cent_x = int(round(np.sum(X) / total))  #round四舍五入取整
    cent_y = int(round(np.sum(Y) / total))

    #print('cent_x = ',cent_x)
    #print('cent_y = ',cent_y)

    # 绘制质心
    #plt.plot(cent_y, cent_x, marker='o', color="white")
    #plt.imshow(C3)
    #plt.show()

    left = np.min(mass_y)  #x方向
    right = np.max(mass_y)  #x方向
    top = np.max(mass_x)  #y方向
    bottom = np.min(mass_x)  #y方向
    width = right - left
    height = top - bottom

    length = np.max([width, height])

    n = 1  # length扩充倍数
    Length = n * length

    if cent_x - Length < 0:  #y方向
        Length = cent_x
    if cent_y - Length < 0:  #x方向
        Length = cent_y
    if cent_x + Length > np.shape(ori_img)[0]:  #y方向
        Length = np.shape(ori_img)[0] - cent_x
    if cent_y + Length > np.shape(ori_img)[1]:  #x方向
        Length = np.shape(ori_img)[1] - cent_y

    #print(Length)

    roi = ori_img[cent_x - Length:cent_x + Length,
                  cent_y - Length:cent_y + Length, :]
    return roi, width, height, length, Length, cent_x, cent_y


def crop_4th(roi, thresh_value):
    C11, C22, C33 = cv2.split(roi)
    mass_x, mass_y = np.where(C33 < thresh_value)
    if np.shape(mass_x)[0] != 0:
        width = np.shape(C33)[0]
        height = np.shape(C33)[1]
        x_min = np.min(mass_y)  # x和y坐标调换
        x_max = np.max(mass_y)

        if x_min <= width / 2:
            roi_end = C33[:, x_max:]
            h = np.shape(roi_end)[0]
            w = np.shape(roi_end)[1]
            roi_end = roi[math.ceil((h - w) / 2):h - math.floor((h - w) / 2),
                          x_max:, :]
        else:
            roi_end = C33[:, :x_min]
            h = np.shape(roi_end)[0]
            w = np.shape(roi_end)[1]
            roi_end = roi[math.ceil((h - w) / 2):h -
                          math.floor((h - w) / 2), :x_min, :]  #向上取整和向下取整
    else:
        roi_end = roi

    return roi_end


def image_preprocess(ori_img):

    #-----裁剪roi区域-----
    cpf_img = crop_1st(ori_img)
    #cv2_imshow(cpf_img)

    C1, C2, C3 = cv2.split(cpf_img)

    # 1、发现C3通道视盘显示效果更好
    img = C3
    img = C3 / np.max(C3)  # 归一化，因为之后要对每幅图以同样的阈值进行二值化
    #plt.imshow(img)
    #plt.show()

    # 2、以内切圆进行裁剪，避免边缘亮度过高
    r1 = 700
    img = crop_2nd(img, r1)
    #plt.imshow(img)
    #plt.show()

    # 3、以最亮点为中心进行圆形裁剪，避免视盘周围高亮度血管影响
    r2 = 200
    img = crop_3rd(img, r2)
    #plt.imshow(img)
    #plt.show()

    # 4、二值化
    ret, thresh1 = cv2.threshold(
        img, 0.7, 1, cv2.THRESH_BINARY)  # ret阈值，thresh1二值化图像  dtype('float64')
    #plt.imshow(thresh1)
    #plt.show()

    # 5、删除非连通小区域，将二值化后视盘周围的细枝末节删除掉
    thresh2 = np.array(thresh1, dtype=bool)  #转化为bool
    thresh3 = morphology.remove_small_objects(
        thresh2, 20, connectivity=1)  #删除面积小于 min_size 的对，对象必须是bool
    #plt.imshow(thresh3)
    #plt.show()

    # 6、计算质心与最大长宽并提取roi
    roi, w, h, length, Length, cent_x, cent_y = Roi(thresh3, cpf_img, C3)

    # 7、去除眼球边缘黑边，防止模型当做特征进行学习（如果有的话）
    thresh_value = 7
    roi_end = crop_4th(roi, thresh_value)

    roi_end = cv2.resize(roi_end, (224, 224))

    #cv2.imshow('roi', roi_end)
    #cv2_imwrite(roi_end, save_path+'/'+img_path)

    #-----clahe增强-----

    lab = cv2.cvtColor(roi_end, cv2.COLOR_BGR2LAB)

    L, A, B = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=1.7, tileGridSize=(8, 8))  #2.45

    L_c = clahe.apply(L)  #End #输入图像必须为CV_8UC1 or CV_16UC1类型，U无符号整形，1单通道
    A_c = clahe.apply(A)
    B_c = clahe.apply(B)

    lab = cv2.merge([L_c, A_c, B_c])
    bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    img_resize = cv2.resize(bgr, (224, 224))

    return img_resize


#------------------------------------GRAM图-----------------------------------------


def visualize_single_input(ori_image, data_type_name, conv_output, conv_grad,
                           gb_viz, save_path):
    a = 1  #heatmap图显示权重 vf=1.5, cfp=1.2
    b = 1  #img图显示权重
    output = conv_output  # [7,7,512]
    #output = 255 * output / np.max(output)
    grads_val = conv_grad  # [7,7,512]
    #grads_val = 255 * grads_val / np.max(grads_val)
    #print("grads_val shape:", grads_val.shape)
    #print("gb_viz shape:", gb_viz.shape)

    weights = np.mean(grads_val, axis=(0, 1))  # alpha_k, [512]
    cam = np.zeros(output.shape[0:2], dtype=np.float32)  # [7,7]

    # Taking a weighted average
    for i, w in enumerate(weights):
        cam += w * output[:, :, i]

    # Passing through ReLU
    cam = np.maximum(cam, 0)  #ReLU
    cam = cam / (1E-10 + np.max(cam))  # scale 0 to 1.0
    #plt.imshow(cam)
    #plt.show()
    #cam = resize(cam, (224,224), preserve_range=True) #(224, 224)
    cam = cv2.resize(cam, (224 + 30, 224 + 30))
    cam = cam[14:224 + 14, 14:224 + 14]  # [upper: lower, left: right]
    #plt.imshow(cam)
    #plt.show()

    if data_type_name == 'cpf':
        image = ori_image[:, :, (2, 1, 0)]
    else:
        image = cv2.merge([ori_image, ori_image, ori_image])

    img = image.astype(float)  #(224, 224, 3)
    #img -= np.min(img)
    #img /= img.max() #归一化
    # print(img)
    cam_heatmap = cv2.applyColorMap(np.uint8(255 * cam),
                                    cv2.COLORMAP_JET)  #(224, 224, 3)
    cam_heatmap = cv2.cvtColor(cam_heatmap, cv2.COLOR_BGR2RGB)
    #plt.imshow(cam_heatmap)
    #plt.show()
    cam_img = a * np.float32(cam_heatmap) + b * np.float32(img)
    cam_img = 255 * cam_img / np.max(cam_img)
    cam_img = np.uint8(cam_img)

    plt.xticks([])
    plt.yticks([])
    path = save_path
    plt.imsave(path, cam_img, dpi=300)
    return path

    # plt.imshow(cam_img)
    # plt.xticks([])
    # plt.yticks([])
    # path = save_path
    # plt.savefig(path, bbox_inches='tight', dpi=300, pad_inches=0)
    # return path
    #plt.show()
    #return image, cam_heatmap, gb_viz, gd_gb, cam_img


#------------------------------------神经网络-----------------------------------------


class ResNet():

    def __init__(self, img, label, model_path):
        self.img = img
        self.label = label
        self.model_path = model_path
        self.L2 = 0.005

    def z_score(self, data):  #(32, 224, 224, 4)
        # multi
        mean_list = [29.99, 54.53, 104.98, 109.98]  ###
        std_list = [27.98, 48.25, 80.63, 117.02]  ###
        # cpf
        #mean_list = [44.72, 78.27, 149.39, 0.00]
        #std_list = [24.55, 38.59, 48.04, 1.00] # std=0，但是0不能做分母，只要保证算完最终值为0即可
        # vf
        #mean_list = [0.00, 0.00, 0.00, 170.65]
        #std_list = [1.00, 1.00, 1.00, 102.67]
        depth = np.shape(data)[-1]
        for i in range(depth):
            data[:, :, :, i] = (data[:, :, :, i] - mean_list[i]) / std_list[i]
        return data

    def conv2d(self, input_matrix, kernel, strides, padding):
        initializer = tf.contrib.layers.xavier_initializer()
        regularizer = tf.contrib.layers.l2_regularizer(self.L2)
        weight = tf.Variable(initializer(kernel))
        tf.add_to_collection(tf.GraphKeys.REGULARIZATION_LOSSES,
                             regularizer(weight))
        bias = tf.Variable(initializer([kernel[3]]))
        output = tf.nn.conv2d(
            input_matrix, weight, strides=strides, padding=padding) + bias
        return output

    def max_pool(self, input_matrix, kernel, strides, padding):
        output = tf.nn.max_pool(input_matrix, kernel, strides, padding)
        return output

    def avg_pool(self, input_matrix, kernel, strides, padding):
        output = tf.nn.avg_pool(input_matrix, kernel, strides, padding)
        return output

    def ID_block(self, input_matrix, kernel, strides, padding, train_BN,
                 drop_percent):
        output_BN1 = tf.layers.batch_normalization(input_matrix,
                                                   training=train_BN)
        output_AF1 = tf.nn.relu(output_BN1)
        output_conv1 = self.conv2d(output_AF1, kernel, strides, padding)
        output_dropout = tf.nn.dropout(output_conv1, drop_percent)
        output_BN2 = tf.layers.batch_normalization(output_dropout,
                                                   training=train_BN)
        output_AF2 = tf.nn.relu(output_BN2)
        output_conv2 = self.conv2d(output_AF2, kernel, strides, padding)
        output = tf.add(input_matrix, output_conv2)
        return output

    def DS_block(self, input_matrix, kernel, DS_kernel, strides, DS_strides,
                 padding, train_BN, drop_percent):
        output_BN1 = tf.layers.batch_normalization(input_matrix,
                                                   training=train_BN)
        output_AF1 = tf.nn.relu(output_BN1)
        output_conv1 = self.conv2d(output_AF1, DS_kernel, DS_strides, padding)
        output_dropout = tf.nn.dropout(output_conv1, drop_percent)
        output_BN2 = tf.layers.batch_normalization(output_dropout,
                                                   training=train_BN)
        output_AF2 = tf.nn.relu(output_BN2)
        output_conv2 = self.conv2d(output_AF2, kernel, strides, padding)
        output_ID = self.conv2d(input_matrix, DS_kernel, DS_strides, padding)
        output = tf.add(output_ID, output_conv2)
        return output

    def fc(self, input_matrix, kernel):
        initializer = tf.contrib.layers.xavier_initializer()
        regularizer = tf.contrib.layers.l2_regularizer(self.L2)
        weight = tf.Variable(initializer(kernel))
        tf.add_to_collection(tf.GraphKeys.REGULARIZATION_LOSSES,
                             regularizer(weight))
        bias = tf.Variable(initializer([kernel[1]]))
        output = tf.matmul(input_matrix, weight) + bias
        return output

    def architecture_34(self, image, train_BN, learning_rate, drop_percent):
        output_conv1 = tf.nn.relu(
            self.conv2d(image, [7, 7, 4, 64], [1, 2, 2, 1], 'SAME'))
        output_pool1 = self.max_pool(output_conv1, [1, 3, 3, 1], [1, 2, 2, 1],
                                     'SAME')
        output_ID1 = self.ID_block(output_pool1, [3, 3, 64, 64], [1, 1, 1, 1],
                                   'SAME', train_BN, drop_percent)
        output_ID2 = self.ID_block(output_ID1, [3, 3, 64, 64], [1, 1, 1, 1],
                                   'SAME', train_BN, drop_percent)
        output_ID3 = self.ID_block(output_ID2, [3, 3, 64, 64], [1, 1, 1, 1],
                                   'SAME', train_BN, drop_percent)
        output_DS4 = self.DS_block(output_ID3, [3, 3, 128, 128],
                                   [3, 3, 64, 128], [1, 1, 1, 1], [1, 2, 2, 1],
                                   'SAME', train_BN, drop_percent)
        output_ID5 = self.ID_block(output_DS4, [3, 3, 128, 128], [1, 1, 1, 1],
                                   'SAME', train_BN, drop_percent)
        output_ID6 = self.ID_block(output_ID5, [3, 3, 128, 128], [1, 1, 1, 1],
                                   'SAME', train_BN, drop_percent)
        output_ID7 = self.ID_block(output_ID6, [3, 3, 128, 128], [1, 1, 1, 1],
                                   'SAME', train_BN, drop_percent)
        output_DS8 = self.DS_block(output_ID7, [3, 3, 256, 256],
                                   [3, 3, 128, 256], [1, 1, 1, 1],
                                   [1, 2, 2, 1], 'SAME', train_BN,
                                   drop_percent)
        output_ID9 = self.ID_block(output_DS8, [3, 3, 256, 256], [1, 1, 1, 1],
                                   'SAME', train_BN, drop_percent)
        output_ID10 = self.ID_block(output_ID9, [3, 3, 256, 256], [1, 1, 1, 1],
                                    'SAME', train_BN, drop_percent)
        output_ID11 = self.ID_block(output_ID10, [3, 3, 256, 256],
                                    [1, 1, 1, 1], 'SAME', train_BN,
                                    drop_percent)
        output_ID12 = self.ID_block(output_ID11, [3, 3, 256, 256],
                                    [1, 1, 1, 1], 'SAME', train_BN,
                                    drop_percent)
        output_ID13 = self.ID_block(output_ID12, [3, 3, 256, 256],
                                    [1, 1, 1, 1], 'SAME', train_BN,
                                    drop_percent)
        output_DS14 = self.DS_block(output_ID13, [3, 3, 512, 512],
                                    [3, 3, 256, 512], [1, 1, 1, 1],
                                    [1, 2, 2, 1], 'SAME', train_BN,
                                    drop_percent)
        output_ID15 = self.ID_block(output_DS14, [3, 3, 512, 512],
                                    [1, 1, 1, 1], 'SAME', train_BN,
                                    drop_percent)
        output_ID16 = self.ID_block(output_ID15, [3, 3, 512, 512],
                                    [1, 1, 1, 1], 'SAME', train_BN,
                                    drop_percent)
        output_pool2 = self.avg_pool(output_ID16, [1, 7, 7, 1], [1, 1, 1, 1],
                                     'VALID')
        input_fc = tf.reshape(output_pool2, [-1, 1 * 1 * 512])
        output_fc = self.fc(input_fc, [1 * 1 * 512, 2])

        prob = tf.nn.softmax(output_fc)

        saver = tf.train.Saver(max_to_keep=1)

        return prob, output_fc, output_ID16, saver

    def execution(self):
        image = tf.placeholder(tf.float32, [None, 224, 224, 4])
        y = tf.placeholder(tf.float32, [None, 2])
        train_BN = tf.placeholder(tf.bool)
        drop_percent = tf.placeholder(tf.float32)

        learning_rate = tf.Variable(0.5e-4, tf.float32)

        prob, output_fc, output_ID16, saver = self.architecture_34(
            image=image,
            train_BN=train_BN,
            learning_rate=learning_rate,
            drop_percent=drop_percent)

        target_conv_layer = output_ID16
        y_c = tf.reduce_sum(tf.multiply(output_fc, y),
                            axis=1)  #(batchsize, 1) 预测结果分类的得分
        target_conv_layer_grad = tf.gradients(y_c, target_conv_layer)[0]
        gb_grad = tf.gradients(y_c, image)[0]

        gpuConfig = tf.ConfigProto(allow_soft_placement=True)
        gpuConfig.gpu_options.allow_growth = True
        with tf.Session(config=gpuConfig) as sess:
            sess.run(
                tf.group(tf.global_variables_initializer(),
                         tf.local_variables_initializer()))
            saver.restore(sess, self.model_path)

            imgs = np.expand_dims(self.img,
                                  axis=0)  #(1, 224, 224, 4) dtype('uint8')

            prediction = sess.run(prob,
                                  feed_dict={
                                      image: self.z_score(imgs),
                                      train_BN: False,
                                      drop_percent: 1.0
                                  })  #预测概率list
            res = np.argmax(prediction, axis=-1)  # prediction result
            probi = np.max(prediction)
            target_conv_layer = sess.run(target_conv_layer,
                                         feed_dict={
                                             image: self.z_score(imgs),
                                             train_BN: False,
                                             drop_percent: 1.0
                                         })  #(1,224,224,4)
            target_conv_layer_grad = sess.run(target_conv_layer_grad,
                                              feed_dict={
                                                  image: self.z_score(imgs),
                                                  y: self.label,
                                                  train_BN: False,
                                                  drop_percent: 1.0
                                              })  #(1,224,224,4)
            gb_grad = sess.run(gb_grad,
                               feed_dict={
                                   image: self.z_score(imgs),
                                   y: self.label,
                                   train_BN: False,
                                   drop_percent: 1.0
                               })  #(1,224,224,4)
        tf.reset_default_graph()
        return res, probi, target_conv_layer, target_conv_layer_grad, gb_grad


################################################################


def up_load_work(parameters: dict, start_signal, report_signal, stop_signal):
    try:
        if start_signal:
            start_signal.emit()
        input_path = parameters["input_path"]
        fname = parameters["fname"]
        file_dir = parameters["file_dir"]
        thre_dir = parameters["thre_dir"]
        cpf_path = parameters["cpf_path"]
        model_path = parameters["model_path"]
        img_save_path = parameters["img_save_path"]

        # ... do stuffs
        # when it's ok, call report_signal.emit(dict)
        #--------------------数据处理---------------------------
        # vf
        basic_info, vf_value = vf_value_extract(input_path, fname)
        patient_name = basic_info['name']
        patient_birth = basic_info['birthday']
        patient_age = 30
        exam_date = basic_info['exam_date']
        exam_time = 1
        eye = basic_info['eye']
        answer = parameters.copy()
        answer['basic_info'] = basic_info
        answer['vf_value'] = vf_value
        answer['patient_name'] = patient_name
        answer['patient_birth'] = patient_birth
        answer['patient_age'] = patient_age
        answer['exam_date'] = exam_date
        answer['exam_time'] = exam_time
        answer['eye'] = eye
        if report_signal:
            report_signal.emit(answer)
        else:
            return answer
    finally:
        if stop_signal:
            stop_signal.emit()


def diagnosis_work(parameters: dict, start_signal, report_signal, stop_signal):
    try:
        if start_signal:
            start_signal.emit()
        input_path = parameters["input_path"]
        fname = parameters["fname"]
        file_dir = parameters["file_dir"]
        thre_dir = parameters["thre_dir"]
        cpf_path = parameters["cpf_path"]
        model_path = parameters["model_path"]
        img_save_path = parameters["img_save_path"]

        basic_info = parameters['basic_info']
        vf_value = parameters['vf_value']
        patient_name = parameters['patient_name']
        patient_birth = parameters['patient_birth']
        patient_age = parameters['patient_age']
        exam_date = parameters['exam_date']
        exam_time = parameters['exam_time']
        eye = parameters['eye']
        vf_data = [patient_age]
        for i in range(len(vf_value)):
            vf_data.append(vf_value[i])

        ori_img_vf = vf_img(vf_data, file_dir, thre_dir)

        # cfp
        ori_img_cpf = cv2_imread(cpf_path, cv2.IMREAD_COLOR)
        roi_cpf = image_preprocess(ori_img_cpf)

        # 融合
        C1, C2, C3 = cv2.split(roi_cpf)
        C4 = ori_img_vf  ### 针对多模态的情况

        img = cv2.merge([C1, C2, C3, C4])  # (224, 224, 4) dtype('uint8')
        #img = np.expand_dims(img,axis=0) #(1, 224, 224, 4) dtype('uint8')

        #--------------------模型诊断---------------------------
        label = [0, 1]
        label = np.expand_dims(label, axis=0)  #(1, 2)
        zeros = np.zeros((224, 224), dtype="uint8")

        resnet = ResNet(img, label, model_path)
        diagnose_res, diagnose_prob, target_conv_layer, target_conv_layer_grad, gb_grad = resnet.execution(
        )  #(1, 7, 7, 512), (1, 7, 7, 512), (1, 224, 224, 4)

        #--------------------诊断结果---------------------------
        # 诊断结果和概率
        diagnosis_probility = diagnose_prob  #预测概率
        if diagnose_res[0] == 0:
            diagnosis_result = 'negitive'  #预测结果
            positive_probility = round((1 - diagnosis_probility) * 100,
                                       2)  #阳性结果
            negitive_probility = round(diagnose_prob * 100, 2)  #阴性结果
        if diagnose_res[0] == 1:
            diagnosis_result = 'positive'
            negitive_probility = round((1 - diagnosis_probility) * 100, 2)
            positive_probility = round(diagnose_prob * 100, 2)
        answer_dict = dict()
        answer_dict['diagnosis_result'] = diagnosis_result
        answer_dict['positive_probility'] = positive_probility
        answer_dict['negitive_probility'] = negitive_probility

        # 显著性地图
        # cfp
        C11 = C1
        C21 = C2
        C31 = C3
        C41 = zeros
        img_cfp = cv2.merge([C11, C21, C31, C41])

        resnet1 = ResNet(img_cfp, label, model_path)
        diagnose_res1, diagnose_prob1, target_conv_layer1, target_conv_layer_grad1, gb_grad1 = resnet1.execution(
        )  #(1, 7, 7, 512), (1, 7, 7, 512), (1, 224, 224, 4)
        target_conv_layer1 = np.squeeze(target_conv_layer1)  #(7, 7, 512)
        target_conv_layer_grad1 = np.squeeze(
            target_conv_layer_grad1)  #(7, 7, 512)
        gb_grad1 = np.squeeze(gb_grad1)  #(224, 224, 4)
        answer_dict['pic1'] = visualize_single_input(
            roi_cpf, 'cpf', target_conv_layer1, target_conv_layer_grad1,
            gb_grad1, img_save_path + '/cam_img_cpf.jpg')

        # vf
        C12 = zeros
        C22 = zeros
        C32 = zeros
        C42 = C4
        img_vf = cv2.merge([C12, C22, C32, C42])

        resnet2 = ResNet(img_vf, label, model_path)
        diagnose_res2, diagnose_prob2, target_conv_layer2, target_conv_layer_grad2, gb_grad2 = resnet2.execution(
        )  #(1, 7, 7, 512), (1, 7, 7, 512), (1, 224, 224, 4)
        target_conv_layer2 = np.squeeze(target_conv_layer2)  #(7, 7, 512)
        target_conv_layer_grad2 = np.squeeze(
            target_conv_layer_grad2)  #(7, 7, 512)
        gb_grad2 = np.squeeze(gb_grad2)  #(224, 224, 4)
        answer_dict['pic2'] = visualize_single_input(
            ori_img_vf, 'vf', target_conv_layer2, target_conv_layer_grad2,
            gb_grad2, img_save_path + '/cam_img_vf.jpg')

        # 处理后的输入图像
        cv2_imwrite(roi_cpf, img_save_path + '/cfp.jpg')
        answer_dict['pic3'] = img_save_path + '/cfp.jpg'
        cv2_imwrite(ori_img_vf, img_save_path + '/vf.jpg')
        answer_dict['pic4'] = img_save_path + '/vf.jpg'

        if report_signal:
            report_signal.emit(answer_dict)
    finally:
        if stop_signal:
            stop_signal.emit()


def __main_work():
    input_path = './vf/pdf'  # vf视野报告PDF所在的位置
    fname = "568-OD-20170216164717_31000901_65822[1].pdf"  # 需要读取的vf视野报告PDF
    file_dir = './vf/Location.xlsx'  # vf视野必须文件
    thre_dir = './vf/正常阈值+随年龄变化.xlsx'  # vf视野必须文件
    cpf_path = './cfp/20190408114541_31000901_18226.jpg'  # cfp眼底照位置
    model_path = './model/120/Frame.ckpt'  # 深度学习模型位置
    img_save_path = './result'
    parameters = dict()
    parameters["input_path"] = input_path
    parameters["fname"] = fname
    parameters["file_dir"] = file_dir
    parameters["thre_dir"] = thre_dir
    parameters["cpf_path"] = cpf_path
    parameters["model_path"] = model_path
    parameters["img_save_path"] = img_save_path
    upload_answer = up_load_work(parameters=parameters,
                                 start_signal=None,
                                 report_signal=None,
                                 stop_signal=None)
    basic_info, vf_value, patient_name, patient_birth, patient_age, exam_date, exam_time, eye = upload_answer[
        'basic_info'], upload_answer['vf_value'], upload_answer[
            'patient_name'], upload_answer['patient_birth'], upload_answer[
                'patient_age'], upload_answer['exam_date'], upload_answer[
                    'exam_time'], upload_answer['eye']

    parameters = dict()
    parameters["input_path"] = input_path
    parameters["fname"] = fname
    parameters["file_dir"] = file_dir
    parameters["thre_dir"] = thre_dir
    parameters["cpf_path"] = cpf_path
    parameters["model_path"] = model_path
    parameters["img_save_path"] = img_save_path
    parameters['basic_info'] = basic_info
    parameters['vf_value'] = vf_value
    parameters['patient_name'] = patient_name
    parameters['patient_birth'] = patient_birth
    parameters['patient_age'] = patient_age
    parameters['exam_date'] = exam_date
    parameters['exam_time'] = exam_time
    parameters['eye'] = eye
    diagnosis_work(parameters=parameters,
                   start_signal=None,
                   report_signal=None,
                   stop_signal=None)
