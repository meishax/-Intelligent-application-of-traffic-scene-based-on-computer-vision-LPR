#!/user/bin/env python
# -*- coding:utf-8 -*-

import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import time


def SpeedTest(image_path):  # 定义测试速度函数
    grr = cv2.imread(image_path)
    model = pr.LPR("model/cascade.xml", "model/model12.h5",
                   "model/ocr_plate_all_gru.h5")  # 输入之前训练好的目标检测，车牌边界左右回归，车牌文字检测模型权重
    model.SimpleRecognizePlateByE2E(grr)
    t0 = time.time()
    for x in range(20):
        model.SimpleRecognizePlateByE2E(grr)
    t = (time.time() - t0) / 20.0  # 计算运行时间
    print("Image size :" + str(grr.shape[1]) + "x" + str(grr.shape[0]) + " need " + str(
        round(t * 1000, 2)) + "ms")  # 输出图片尺寸和运行时间


from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

fontC = ImageFont.truetype("./Font/platech.ttf", 14, 0)


def drawRectBox(image, rect, addText):  # 定义划定车牌矩形框函数，即定位车牌位置
    cv2.rectangle(image, (int(rect[0]), int(rect[1])), (int(rect[0] + rect[2]), int(rect[1] + rect[3])), (0, 0, 255), 2,
                  cv2.LINE_AA)
    cv2.rectangle(image, (int(rect[0] - 1), int(rect[1]) - 16), (int(rect[0] + 115), int(rect[1])), (0, 0, 255), -1,
                  cv2.LINE_AA)  # 设定矩形框的边界范围
    img = Image.fromarray(image)
    draw = ImageDraw.Draw(img)
    draw.text((int(rect[0] + 1), int(rect[1] - 16)), addText.encode('utf-8').decode('utf-8'), (255, 255, 255),
              font=fontC)
    imagex = np.array(img)
    return imagex  # 返回带有矩形框的车牌


import HyperLPRLite as pr  # 引入LPR大类
import cv2
import numpy as np


def start(image_path):
    grr = cv2.imread(image_path)  # 读取修改图片位置，路径里不要有中文，图片命名的时候不要以a,b,f,n和数字开头,否则会报错
    model = pr.LPR("model/cascade.xml", "model/model12.h5",
                   "model/ocr_plate_all_gru.h5")  # 输入之前训练好的目标检测，车牌边界左右回归，车牌文字检测模型
    for pstr, confidence, rect in model.SimpleRecognizePlateByE2E(grr):
        if confidence > 0.7:  # 若置信度大于0.7，则识别结果可信(最大为1)
            image = drawRectBox(grr, rect, pstr + " " + str(round(confidence, 3)))
            print("plate_str:")
            print(pstr)
            print("plate_confidence")
            print(confidence)  # 输出识别结果以及置信度
            print("rect")
            print(rect)
            result = {}
            result['pstr'] = pstr
            result['confidence'] = confidence
            result['image'] = image
            result['rect'] = rect
            return result
        else:
            return None


if __name__ == '__main__':
    # SpeedTest("/Users/ihandy/Downloads/qq/HyperLPR-master/images_rec/demo.jpg")
    # #读取图片位置，路径里不要有中文，图片命名的时候不要以a,b,f,n和数字开头,否则会报错
    #  result = start("/Users/ihandy/Downloads/qq/HyperLPR-gui/images_rec/demo.jpg")
    result = start("/HyperLPR-gui/HyperLPR-gui/images_rec/demo.jpg")
    if result is None:
        print("is none")
        exit()

    print(result)
