import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QCheckBox, QSpinBox, QHBoxLayout
from pynput import keyboard, mouse
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
mouse_controller = Controller()


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
# 延迟半径
delay_radius = 300
# 使用鼠标修正模式
mouse_amend = False
# 修正百分比
amend_num = 0.1
# 开启锁定鼠标回拉
mouse_break = True
# 鼠标返回延迟
mouse_break_delay = 0.1
# 脚本开关
script_switch = False


def thread_function():
    with mss.mss() as sct:
        global monitor
        monitor = sct.monitors[1]
        screen_width = monitor["width"]
        screen_height = monitor["height"]
        monitor = {"left": 0, "top": 0, "width": screen_width, "height": screen_height}
        # print("开启")
        i = 0
        while True:
            if not is_on or not script_switch:
                monitor = {"left": 0, "top": 0, "width": screen_width, "height": screen_height}
                # print("关闭")
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
                fx = x + mouse_x + monitor.get('left')  # 定位 x坐标
                fy = y + mouse_y + monitor.get('top')  # 定位 y坐标
                if mouse_delay:  # 判断是否开启 延迟锁定
                    # 获取当前鼠标位置
                    now_x, now_y = pyautogui.position()
                    # 计算两点距离
                    distance = math.sqrt((fx - now_x) ** 2 + (fy - now_y) ** 2)
                    if mouse_amend:
                        if distance > delay_radius:
                            #
                            mouse_controller.position = (
                                now_x + (fx - now_x) * amend_num, now_y + (fy - now_y) * amend_num)
                    else:
                        if distance > delay_radius:
                            pyautogui.dragTo(fx, fy, duration=delay)
                        else:
                            mouse_controller.position = (fx, fy)
                else:
                    mouse_controller.position = (fx, fy)

                monitor = {"left": monitor.get('left') + x - mate_w, "top": monitor.get('top') + y - mate_h,
                           "width": mate_w * 2,
                           "height": mate_h * 2}
                break


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('锁')
        self.setGeometry(100, 100, 300, 300)

        main_widget = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel('关闭')
        layout.addWidget(self.label)
        self.script_switch = QLabel('脚本关')
        layout.addWidget(self.script_switch)
        # 创建水平布局并添加按钮
        hbox = QHBoxLayout()
        # 鼠标延迟控制
        self.checkbox = QCheckBox('开启鼠标延迟')
        self.checkbox.stateChanged.connect(self.on_state_changed)
        hbox.addWidget(self.checkbox)
        # 开启鼠标修正
        self.amend_checkbox = QCheckBox('开启鼠标修正模式')
        self.amend_checkbox.stateChanged.connect(self.on_mouse_amend)
        mouse_break_checkbox = QCheckBox('鼠标锁定回拉')
        global mouse_break
        mouse_break_checkbox.setChecked(mouse_break)

        # 修改
        def onMouseBreak(value):
            global mouse_break
            mouse_break = value

        mouse_break_checkbox.stateChanged.connect(onMouseBreak)
        layout.addWidget(mouse_break_checkbox)
        # 回拉延迟
        break_hbox = QHBoxLayout()
        x_z_label = QLabel("返回延迟:(单位 ms)")
        break_hbox.addWidget(x_z_label)
        xz_num_input = QSpinBox()
        xz_num_input.setMinimum(0)  # 最小值
        xz_num_input.setMaximum(1000)  # 最大值
        global mouse_break_delay
        xz_num_input.setValue(int(mouse_break_delay * 1000))

        def onBreakNum(val):
            global mouse_break_delay
            mouse_break_delay = val / 1000

        xz_num_input.valueChanged.connect(onBreakNum)  # 连接数值变化信号到槽函数
        break_hbox.addWidget(xz_num_input)
        layout.addLayout(break_hbox)

        hbox.addWidget(self.amend_checkbox)
        layout.addLayout(hbox)
        xz_hbox = QHBoxLayout()
        x_z_label = QLabel("修正百分比:(单位 %)")
        xz_hbox.addWidget(x_z_label)
        xz_num_input = QSpinBox()
        xz_num_input.setMinimum(0)  # 最小值
        xz_num_input.setMaximum(100)  # 最大值
        xz_num_input.setValue(int(amend_num * 100))
        xz_num_input.valueChanged.connect(self.on_x_z)  # 连接数值变化信号到槽函数
        xz_hbox.addWidget(xz_num_input)
        layout.addLayout(xz_hbox)
        # 创建水平布局并添加按钮
        hbox2 = QHBoxLayout()
        # 延迟大小
        self.delay_num_desc = QLabel("延迟大小:(单位 ms)")
        hbox2.addWidget(self.delay_num_desc)
        self.delay_input = QSpinBox()
        self.delay_input.setMinimum(0)  # 最小值
        self.delay_input.setMaximum(1000)  # 最大值
        self.delay_input.setValue(int(delay * 1000))  # 最大值
        self.delay_input.valueChanged.connect(self.on_delay_num)  # 连接数值变化信号到槽函数
        hbox2.addWidget(self.delay_input)
        layout.addLayout(hbox2)
        # 锁x位置
        # 创建水平布局并添加按钮
        hbox3 = QHBoxLayout()
        delay_radius_desc = QLabel("延迟半径:(单位 px)")
        hbox3.addWidget(delay_radius_desc)
        delay_radius_input = QSpinBox()
        delay_radius_input.setMinimum(0)  # 最小值
        delay_radius_input.setMaximum(1000)  # 最大值
        delay_radius_input.setValue(delay_radius)  # 最大值
        delay_radius_input.valueChanged.connect(self.on_delay_radius_num)  # 连接数值变化信号到槽函数
        hbox3.addWidget(delay_radius_input)
        layout.addLayout(hbox3)
        # 锁x位置
        hbox4 = QHBoxLayout()
        mouse_x_desc = QLabel("锁人x坐标:(单位 px)")
        hbox4.addWidget(mouse_x_desc)
        mouse_x_input = QSpinBox()
        mouse_x_input.setMinimum(0)  # 最小值
        mouse_x_input.setMaximum(1000)  # 最大值
        mouse_x_input.setValue(mouse_x)  # 最大值
        mouse_x_input.valueChanged.connect(self.on_mouse_x_num)  # 连接数值变化信号到槽函数
        hbox4.addWidget(mouse_x_input)
        layout.addLayout(hbox4)
        # 锁y位置
        hbox5 = QHBoxLayout()
        mouse_y_desc = QLabel("锁人y坐标:(单位 px)")
        hbox5.addWidget(mouse_y_desc)
        mouse_y_input = QSpinBox()
        mouse_y_input.setMinimum(0)  # 最小值
        mouse_y_input.setMaximum(1000)  # 最大值
        mouse_y_input.setValue(mouse_y)  # 最大值
        mouse_y_input.valueChanged.connect(self.on_mouse_y_num)  # 连接数值变化信号到槽函数
        hbox5.addWidget(mouse_y_input)
        layout.addLayout(hbox5)
        # 匹配宽度
        hbox6 = QHBoxLayout()
        mate_w_desc = QLabel("匹配宽度 width:(单位 px)")
        hbox6.addWidget(mate_w_desc)
        mate_w_input = QSpinBox()
        mate_w_input.setMinimum(0)  # 最小值
        mate_w_input.setMaximum(1000)  # 最大值
        mate_w_input.setValue(mate_w)  # 最大值
        mate_w_input.valueChanged.connect(self.on_mate_w_num)  # 连接数值变化信号到槽函数
        hbox6.addWidget(mate_w_input)
        layout.addLayout(hbox6)
        # 匹配宽度
        hbox7 = QHBoxLayout()
        mate_h_desc = QLabel("匹配宽度 height:(单位 px)")
        hbox7.addWidget(mate_h_desc)
        mate_h_input = QSpinBox()
        mate_h_input.setMinimum(0)  # 最小值
        mate_h_input.setMaximum(1000)  # 最大值
        mate_h_input.setValue(mate_h)  # 最大值
        mate_h_input.valueChanged.connect(self.on_mate_h_num)  # 连接数值变化信号到槽函数
        hbox7.addWidget(mate_h_input)
        layout.addLayout(hbox7)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    @staticmethod
    def on_state_changed(state):
        global mouse_delay
        if state == 2:  # 选中状态
            mouse_delay = True
        else:  # 未选中状态
            mouse_delay = False

    @staticmethod
    def on_delay_num(value):
        print(value)
        global delay
        delay = value / 1000  # 转换为毫秒

    @staticmethod
    def on_mouse_x_num(value):
        global mouse_x
        mouse_x = value

    @staticmethod
    def on_mouse_y_num(value):
        global mouse_y
        mouse_y = value

    @staticmethod
    def on_mate_w_num(value):
        global mate_w
        mate_w = value

    @staticmethod
    def on_mate_h_num(value):
        global mate_h
        mate_h = value

    @staticmethod
    def on_delay_radius_num(value):
        global delay_radius
        delay_radius = value

    @staticmethod
    def on_mouse_amend(value):
        global mouse_amend
        mouse_amend = value

    # 修正参数
    @staticmethod
    def on_x_z(value):
        global amend_num
        amend_num = value / 100


old_mouse = (0, 0)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()


    def start():
        global is_on
        is_on = not is_on
        if is_on:
            th = threading.Thread(target=thread_function)
            window.label.setText("开启模板匹配")
            # 启动线程
            th.start()
        else:
            window.label.setText("关闭模板匹配")


    def on_click(x, y, button, pressed):
        global old_mouse
        if pressed:
            old_mouse = (x, y)
            if button == mouse.Button.left or button == mouse.Button.x1:
                start()
        else:
            if button == mouse.Button.left or button == mouse.Button.x1:
                start()
            if mouse_break:
                pyautogui.moveTo(old_mouse[0], old_mouse[1], mouse_break_delay)


    mouseListener = mouse.Listener(on_click=on_click)
    mouseListener.start()


    def onkey_event(key):
        try:
            if key.char != "N" and key.char != 'n':
                return
            global script_switch
            script_switch = not script_switch
            if script_switch:
                window.script_switch.setText('脚本开')
            else:
                window.script_switch.setText('脚本关')
            # # 使用模板匹配算法

        except AttributeError:
            pass


    # 监听键盘按下和释放事件
    listener = keyboard.Listener(
        on_press=onkey_event)
    listener.start()
    window.show()
    sys.exit(app.exec_())
