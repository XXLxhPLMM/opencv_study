from pynput import keyboard
import pyautogui
import numpy as np
import cv2
import threading
# import time
import mss
from pynput.mouse import Controller

# 截取整个屏幕并将其转换为 NumPy 数组
template = cv2.imread('tem.png')
# 创建鼠标控制器
mouse = Controller()


# 获取二值图
def get2img(img_data):
    img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
    _, img_data = cv2.threshold(img_data, 99, 0, cv2.THRESH_TOZERO_INV)
    _, img_data = cv2.threshold(img_data, 70, 0, cv2.THRESH_TOZERO)
    return img_data


# 模板二值图
template = get2img(template)

# 获取模板图像的尺寸
w, h = template.shape[::-1]

# 脚本开关状态
is_on = False

monitor = None

# 启用延迟
mouse_delay = False
delay = 0.15
# 鼠标x
mouse_x = 60
# 鼠标y
mouse_y = 130
# 匹配宽度
mate_w = 100
# 匹配高度
mate_h = 100


def thread_function():
    with mss.mss() as sct:
        global monitor
        monitor = sct.monitors[1]
        screen_width = monitor["width"]
        screen_height = monitor["height"]
        monitor = {"left": 0, "top": 0, "width": screen_width, "height": screen_height}
        print("开启")
        i = 0
        while True:

            if not is_on:
                monitor = {"left": 0, "top": 0, "width": screen_width, "height": screen_height}
                print("关闭")
                return
            i = i + 1
            # start_time = time.time()
            screenshot_pil = sct.grab(monitor)
            sample = np.array(screenshot_pil)
            # sample = cv2.cvtColor(sample, cv2.COLOR_RGB2BGR)
            # cv2.imwrite(f"{i}.png", sample)
            res = cv2.matchTemplate(get2img(sample), template, cv2.TM_CCOEFF_NORMED)
            # end_time = time.time()  # 记录程序结束时间
            # elapsed_time = end_time - start_time
            # print("匹配模板", elapsed_time)

            threshold = 0.7  # 设定阈值
            loc = np.where(res >= threshold)
            # min_hue = 0
            data = zip(*loc[::-1])
            if len(list(data)) == 0:
                monitor = {"left": 0, "top": 0, "width": screen_width, "height": screen_height}
                continue
            # 标记匹配位置
            for pt in zip(*loc[::-1]):
                x = pt[0]
                y = pt[1]
                sw = x + w
                sh = y + h
                # 提取指定区域的色相
                roi = sample[y:sh, x:sw]
                mean_hue = np.mean(roi[:, :, 0])  # 计算指定区域的平均色相
                if mean_hue > 35 or mean_hue < 25:
                    continue
                fx = x + mouse_x + monitor.get('left')
                fy = y + mouse_y + monitor.get('top')
                if mouse_delay:
                    pyautogui.dragTo(fx, fy, duration=delay)
                else:
                    mouse.position = (fx, fy)

                monitor = {"left": monitor.get('left') + x - mate_w, "top": monitor.get('top') + y - mate_h,
                           "width": mate_w * 2,
                           "height": mate_h * 2}
                break


def on_press(key):
    try:
        # 按键按下事件处理逻辑
        if key.char == "l" or key.char == "L":
            exit()
        if key.char != "N" and key.char != 'n':
            return
        global is_on
        is_on = not is_on
        if is_on:
            th = threading.Thread(target=thread_function)

            # 启动线程
            th.start()

        # # 使用模板匹配算法

    except AttributeError:
        pass


# 监听键盘按下和释放事件
with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()
