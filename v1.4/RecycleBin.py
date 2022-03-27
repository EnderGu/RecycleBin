# 作者：r=a(1-sinθ)
# 开发时间：2022/3/21 22:31
import shutil
import tkinter as tk
import windnd
import tkinter.messagebox as mb
import tkinter.colorchooser as cc
import time
import os
import random
from pynput import keyboard
from threading import Thread
from tkinter import ttk

bin_name = None
have_bin_flag = False
have_alpha_flag = False
frame_bin_open_setting = None
frame_bin_window_setting = None
frame_bin_color_setting = None
bin_width = 400
bin_height = 100
bin_x = 500
bin_y = 0
mouse_x, mouse_y = 0, 0
window_set = False
open_set = False
open_after_starting = False
color_set = False
events_can_happen = True
moving = False
color = (0, 0, 0)
alpha = 1


def listen():
    def show():
        create_bin()
        return False

    with keyboard.GlobalHotKeys({'<ctrl>+<alt>+c': show}) as listener:
        listener.join()


def create_bin():
    global bin_name, have_bin_flag, bin_width, bin_height, bin_x, bin_y, alpha, color
    if not have_bin_flag:
        have_bin_flag = True
        window_bin = tk.Tk()
        window_bin.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))
        window_bin.overrideredirect(True)
        window_bin.config(background='#%02x%02x%02x' % color)
        window_bin.attributes('-topmost', True)
        window_bin.attributes('-alpha', alpha)
        bin_name = window_bin

        windnd.hook_dropfiles(window_bin, func=dragged_files)
        window_bin.bind('<Button-3>', get_menu)
        window_bin.bind('<Double-Button-1>', show)
        window_bin.bind('<B1-Motion>', move_bin)
        window_bin.bind('<Button-1>', get_mouse)

        window_bin.mainloop()
    else:
        mb.showwarning('已创建', '您已经创建过回收站了！')


def get_mouse(event):
    global mouse_x, mouse_y
    mouse_x = event.x
    mouse_y = event.y


def move_bin(event):
    global bin_name, bin_width, bin_height, bin_x, bin_y, mouse_x, mouse_y
    bin_x = event.x-mouse_x+bin_name.winfo_x()
    bin_y = event.y-mouse_y+bin_name.winfo_y()
    bin_name.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))


def remove_bin():
    global bin_name, have_bin_flag
    if bin_name and have_bin_flag:
        bin_name.destroy()
        have_bin_flag = False
        bin_name = None


def dragged_files(files):
    answer = mb.askyesno('确认', '您确定删除该文件吗？')
    if answer:
        for item in files:
            try:
                os.remove(item.decode('gbk'))
            except BaseException:
                shutil.rmtree(item.decode('gbk'))


def show(event):
    bin_name.attributes('-alpha', 1)


def get_menu(event):
    global bin_name, moving

    def give_args_to_alpha():
        change_alpha(bin_name, mouse_x, mouse_y)

    def give_args_to_settings():
        settings(bin_name, mouse_x, mouse_y)

    mouse_x = event.x_root
    mouse_y = event.y_root
    menubar = tk.Menu(bin_name, tearoff=False)
    if not moving:
        menubar.add_command(label='隐藏', command=remove_bin)
    menubar.add_command(label='混合', command=give_args_to_alpha)
    menubar.add_command(label='设置', command=give_args_to_settings)
    menubar.add_command(label='退出', command=quit_bin)
    menubar.post(mouse_x, mouse_y)


def change_alpha(master, x, y):
    global have_alpha_flag, alpha

    def confirm():
        global have_alpha_flag, alpha
        func = scale_alpha.get()
        func /= 100
        if func == 0:
            func = 0.01
        alpha = func
        master.attributes('-alpha', func)
        have_alpha_flag = False
        window_choose.destroy()
        if func == 0.01:
            window_reminder = tk.Tk()
            window_reminder.geometry('300x100+{0}+{1}'.format(x, y))
            label_reminder = tk.Label(window_reminder, text='回收站不见啦！双击左键可恢复。',
                                      font=('Microsoft YaHei', 13))
            label_reminder.place(x=20, y=35)
            window_reminder.mainloop()

    def move_alpha(event):
        new_x = event.x - mouse_x + window_choose.winfo_x()
        new_y = event.y - mouse_y + window_choose.winfo_y()
        window_choose.geometry('300x100+{0}+{1}'.format(new_x, new_y))

    if not have_alpha_flag:
        have_alpha_flag = True
        window_choose = tk.Toplevel(master)
        window_choose.title('透明度')
        window_choose.geometry('300x100+{0}+{1}'.format(x, y))
        window_choose.attributes('-topmost', True)
        window_choose.overrideredirect(True)

        scale_alpha = tk.Scale(window_choose, label='透明度', from_=0, to=100, orient=tk.HORIZONTAL,
                               length=270, showvalue=True, resolution=1)
        scale_alpha.set(100*alpha)
        scale_alpha.place(x=10, y=0)
        button_confirm = tk.Button(window_choose, text='确定', command=confirm)
        button_confirm.place(x=130, y=70)

        window_choose.bind('<B3-Motion>', move_alpha)
        window_choose.bind('<Button-3>', get_mouse)


def settings(master, x, y):
    def func(*args):
        global window_set, open_set, frame_bin_open_setting, frame_bin_window_setting, \
            frame_bin_color_setting, color_set, open_after_starting, events_can_happen

        def open_itself():
            global open_after_starting
            open_after_starting = var_open.get()
            path = os.getcwd()
            if var_open.get():
                os.popen('reg.exe add HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run '
                         '/v RecycleBin /t reg_sz /d {0}\\RecycleBin.exe'.format(path))
            else:
                os.popen('reg.exe delete HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'
                         ' /v RecycleBin /f')

        def change_width(arg):
            global bin_width
            bin_width = int(arg)
            bin_name.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))

        def change_height(arg):
            global bin_height
            bin_height = int(arg)
            bin_name.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))

        def choose_color():
            global color, bin_name
            chooses = cc.askcolor(parent=window_settings, color='#%02x%02x%02x' % color)
            color = (int(chooses[0][0]), int(chooses[0][1]), int(chooses[0][2]))
            bin_name.config(background='#%02x%02x%02x' % color)

        def change_events_can_happen():
            global events_can_happen
            events_can_happen = var_events.get()

        res = combobox_choose.get()
        if res == '窗口设置':
            if open_set:
                frame_bin_open_setting.destroy()
                open_set = False
            elif color_set:
                frame_bin_color_setting.destroy()
                color_set = False
            if not window_set:
                window_set = True
                frame_bin_window_setting = tk.Frame(window_settings)
                frame_bin_window_setting.pack()
                scale_bin_width = tk.Scale(frame_bin_window_setting, label='长度', from_=50, to=1450,
                                           orient=tk.HORIZONTAL, showvalue=True, resolution=1, command=change_width,
                                           length=500)
                scale_bin_width.set(bin_width)
                scale_bin_width.pack()

                scale_bin_height = tk.Scale(frame_bin_window_setting, label='宽度', from_=50, to=800,
                                            orient=tk.HORIZONTAL, showvalue=True, resolution=1, command=change_height,
                                            length=500)
                scale_bin_height.set(bin_height)
                scale_bin_height.pack()

        elif res == '系统选项':
            if window_set:
                frame_bin_window_setting.destroy()
                window_set = False
            elif color_set:
                frame_bin_color_setting.destroy()
                color_set = False
            if not open_set:
                open_set = True
                frame_bin_open_setting = tk.Frame(window_settings)
                frame_bin_open_setting.pack()

                var_open = tk.BooleanVar()
                var_open.set(open_after_starting)
                checkbutton_open = tk.Checkbutton(frame_bin_open_setting, text='开机自启', variable=var_open,
                                                  onvalue=True, offvalue=False, width=15, height=2,
                                                  command=open_itself, font=('Microsoft YaHei', 15))
                checkbutton_open.pack()
                var_events = tk.BooleanVar()
                var_events.set(events_can_happen)
                checkbutton_events = tk.Checkbutton(frame_bin_open_setting, text='随机事件', variable=var_events,
                                                    onvalue=True, offvalue=False, width=15, height=2,
                                                    command=change_events_can_happen,
                                                    font=('Microsoft YaHei', 15))
                checkbutton_events.pack()

        elif res == '窗口颜色':
            if window_set:
                frame_bin_window_setting.destroy()
                window_set = False
            elif open_set:
                frame_bin_open_setting.destroy()
                open_set = False
            if not color_set:
                color_set = True
                frame_bin_color_setting = tk.Frame(window_settings)
                frame_bin_color_setting.pack()

                button_color = tk.Button(frame_bin_color_setting, text='选择颜色', font=('Microsoft YaHei', 15),
                                         command=choose_color)
                button_color.pack()

    def quit_setting():
        global open_set, window_set, color_set
        open_set = False
        window_set = False
        color_set = False
        window_settings.destroy()

    def move_setting(event):
        new_x = event.x - mouse_x + window_settings.winfo_x()
        new_y = event.y - mouse_y + window_settings.winfo_y()
        window_settings.geometry('500x400+{0}+{1}'.format(new_x, new_y))

    window_settings = tk.Toplevel(master)
    window_settings.title('设置')
    window_settings.geometry('500x400+{0}+{1}'.format(x, y))
    window_settings.attributes('-topmost', True)
    window_settings.overrideredirect(True)

    var_choose = tk.StringVar()
    combobox_choose = ttk.Combobox(window_settings, textvariable=var_choose, width=50)
    combobox_choose.pack()
    button_confirm = tk.Button(window_settings, text='确认', font=('Microsoft YaHei', 15), command=quit_setting)
    button_confirm.place(x=230, y=350)

    combobox_choose['value'] = ('窗口设置', '系统选项', '窗口颜色')
    combobox_choose.current(0)

    combobox_choose.bind('<<ComboboxSelected>>', func)
    window_settings.bind('<B3-Motion>', move_setting)
    window_settings.bind('<Button-3>', get_mouse)


def quit_bin():
    global pid_list
    answer = mb.askyesno('确认', '您确定退出吗？')
    if answer:
        for item in pid_list:
            os.popen('taskkill.exe /pid:{0} /f'.format(item))


def move_event(binname):
    global bin_width, bin_height, bin_x, bin_y, moving
    moving = True
    direction = 'right'
    count = 0
    move_count = 0
    while count <= 100:
        if binname.winfo_x() <= binname.winfo_screenwidth()-bin_width and direction == 'right':
            count += 1
            while move_count < 35:
                move_count += 1
                bin_width += 2
                binname.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))
                time.sleep(0.001)
            while 35 <= move_count < 70:
                move_count += 1
                bin_x += 2
                bin_width -= 2
                binname.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))
                time.sleep(0.001)
            if move_count == 70:
                move_count = 0
        else:
            direction = 'left'
        if binname.winfo_x() >= -10 and direction == 'left':
            count += 1
            while move_count < 35:
                move_count += 1
                bin_width += 2
                bin_x -= 2
                binname.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))
                time.sleep(0.001)
            while 35 <= move_count < 70:
                move_count += 1
                bin_width -= 2
                binname.geometry('{0}x{1}+{2}+{3}'.format(bin_width, bin_height, bin_x, bin_y))
                time.sleep(0.001)
            if move_count == 70:
                move_count = 0
        else:
            direction = 'right'
    else:
        moving = False
        return


def color_event(binname):
    global color
    color_list = []
    for item in range(256):
        color_list.append(item)
    color = (random.choice(color_list), random.choice(color_list), random.choice(color_list))
    binname.config(background='#%02x%02x%02x' % color)


class ListenThread(Thread):
    """监听线程"""
    def __init__(self):
        super().__init__()

    def run(self):
        listen()


if __name__ == '__main__':
    events_list = [1, 2]
    pid_list = []
    listen_thread = ListenThread()
    listen_thread.start()
    task_list = os.popen('tasklist.exe')
    for item in task_list:
        if 'RecycleBin.exe' in item:
            lst1 = item.split(' C')
            lst2 = lst1[0].split()
            pid_list.append(lst2[1])
    while True:
        count_sec = 0
        time.sleep(1)
        while events_can_happen and bin_name is not None:
            while bin_name is not None and count_sec < 300 and events_can_happen:
                count_sec += 1
                time.sleep(1)
            if count_sec != 300:
                break
            event_num = random.choice(events_list)
            if event_num == 1:
                move_event(bin_name)
                count_sec = 0
                break
            elif event_num == 2:
                color_event(bin_name)
                count_sec = 0
                break
