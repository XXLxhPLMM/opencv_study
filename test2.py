import keyword
import mss
from pynput import keyboard
import pyautogui
import numpy as np
import cv2
# import threading
import time

# 截取整个屏幕并将其转换为 NumPy 数组
# screenshot_pil = ImageGrab.grab()
# image_data = np.array(screenshot_pil)
# image_data = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
# cv2.imshow("'Image'", image_data)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
template = cv2.imread('tem.png')


# 获取二值图
def get2img(img_data):
    img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
    # # _, img_data = cv2.threshold(img_data, 115, 1, cv2.THRESH_TOZERO_INV)
    # _, img_data = cv2.threshold(img_data, 99, 0, cv2.THRESH_TOZERO_INV)
    # # _, img_data = cv2.threshold(img_data, 70, 1, cv2.THRESH_TOZERO)
    _, img_data = cv2.threshold(img_data, 99, 0, cv2.THRESH_TOZERO_INV)
    _, img_data = cv2.threshold(img_data, 70, 0, cv2.THRESH_TOZERO)
    return img_data


# 模板二值图
template = get2img(template)

# 获取模板图像的尺寸
w, h = template.shape[::-1]
monitor = {"left": 288, "top": 162, "width": 1632, "height": 918}
# 脚本开关状态
is_on = False
with mss.mss() as sct:
    while True:
        # i = i + 1
        start_time = time.time()
        screenshot_pil = sct.grab(monitor)
        end_time = time.time()  # 记录程序结束时间
        elapsed_time = end_time - start_time
        print("到获取图像n", elapsed_time)
        sample = np.array(screenshot_pil)
        sample = cv2.cvtColor(sample, cv2.COLOR_RGB2BGR)
        end_time = time.time()  # 记录程序结束时间
        elapsed_time = end_time - start_time
        print("灰度", elapsed_time)
        g_sample = get2img(sample)
        end_time = time.time()  # 记录程序结束时间
        elapsed_time = end_time - start_time
        print("到获取灰度图", elapsed_time)
        res = cv2.matchTemplate(g_sample, template, cv2.TM_SQDIFF_NORMED)
        end_time = time.time()  # 记录程序结束时间
        elapsed_time = end_time - start_time
        print("到匹配模板", elapsed_time)

        threshold = 0.7  # 设定阈值
        loc = np.where(res >= threshold)
        # min_hue = 0
        # 标记匹配位置
        for pt in zip(*loc[::-1]):
            x = pt[0] + w
            y = pt[1] + 5
            sw = x + 100
            sh = y + h - 15
            # 提取指定区域的色相
            roi = sample[y:sh, x:sw]
            mean_hue = np.mean(roi[:, :, 0])  # 计算指定区域的平均色相
            # print(mean_hue)
            if mean_hue > 50:
                continue
            fx = x + 40
            fy = y + 130
            # pyautogui.moveTo(fx, fy)
        end_time = time.time()  # 记录程序结束时间
        elapsed_time = end_time - start_time
        print(elapsed_time)
