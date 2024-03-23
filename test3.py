from pynput import mouse


# 定义回调函数，处理鼠标事件
def on_click(x, y, button, pressed):
    if pressed:
        print('鼠标按键 {0} 按下在 ({1}, {2})'.format(button, x, y))
    else:
        print('鼠标按键 {0} 弹起在 ({1}, {2})'.format(button, x, y))


# 启动监听鼠标事件
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
