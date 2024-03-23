# from PIL import ImageGrab

import numpy as np
import cv2
import time


def get2img(img_data):
    img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)

    _, img_data = cv2.threshold(img_data, 99, 0, cv2.THRESH_TOZERO_INV)
    _, img_data = cv2.threshold(img_data, 70, 0, cv2.THRESH_TOZERO)
    return img_data


# screenshot_pil = ImageGrab.grab()
# image_data = np.array(screenshot_pil)
# image_data = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
sample = cv2.imread('1.png')
template = cv2.imread('tem2.png')
# 模板二值图
template = get2img(template)
print(cv2.cuda.getCudaEnabledDeviceCount())
# 获取模板图像的尺寸
w, h = template.shape[::-1]
start_time = time.time()
res = cv2.matchTemplate(get2img(sample), template, cv2.TM_CCORR_NORMED)
end_time = time.time()  # 记录程序结束时间
elapsed_time = end_time - start_time
print("匹配耗时", elapsed_time)
threshold = 0.6  # 设定阈值
loc = np.where(res >= threshold)
# 标记匹配位置
for pt in zip(*loc[::-1]):
    x = pt[0] + w
    y = pt[1] + 5
    sw = x + 100
    sh = y + h - 15
    # 提取指定区域的色相
    roi = sample[y:sh, x:sw]
    mean_hue = np.mean(roi[:, :, 0])  # 计算指定区域的平均色相
    print(mean_hue)
    if mean_hue > 50 or mean_hue < 45:
        continue
    fx = x + 40
    fy = y + 130
    # pyautogui.moveTo(fx, fy)
    cv2.rectangle(sample, (x, y), (sw, sh), (0, 255, 255), 1)
    cv2.rectangle(sample, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 1)
cv2.imshow("'Image'", sample)
cv2.waitKey(0)
cv2.destroyAllWindows()
