# coding: utf-8
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tkinter as tk
from tkinter.filedialog import *
from tkinter import ttk
import main
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageColor
import time
import copy



# 支持多车牌识别
class Surface2(ttk.Frame):
    pic_path = ""
    viewhigh = 600
    viewwide = 600
    update_time = 0
    thread = None
    thread_run = False
    camera = None
    row = 0
    result_frame = None
    card_image_list = []
    card_rect_list = []
    temp_path = ""
    original_image = None
    keep_reference_for_tk = []

    def __init__(self, win):
        ttk.Frame.__init__(self, win)
        frame_left = ttk.Frame(self)
        frame_right1 = ttk.Frame(self)
        frame_right2 = ttk.Frame(self)
        self.result_frame = frame_right1;
        win.title("车牌识别")
        win.state("zoomed")
        self.pack(fill=tk.BOTH, expand=tk.YES, padx="5", pady="5")
        frame_left.pack(side=LEFT, expand=1, fill=BOTH)
        frame_right1.pack(side=TOP, expand=1, fill=tk.Y)
        frame_right2.pack(side=RIGHT, expand=0)
        ttk.Label(frame_left, text='原图：').pack(anchor="nw")

        from_pic_ctl = ttk.Button(frame_right2, text="来自图片", width=20, command=self.from_pic)
        # from_vedio_ctl = ttk.Button(frame_right2, text="来自摄像头", width=20, command=self.from_vedio)
        self.image_ctl = ttk.Label(frame_left)
        self.image_ctl.pack(anchor="nw")

        # from_vedio_ctl.pack(anchor="se", pady="5")
        from_pic_ctl.pack(anchor="se", pady="5")

    def add_result_frame(self, frame, result):
        if result is None:
            return
        ttk.Label(frame, text='车牌位置：').grid(column=0, row=self.row, sticky=tk.W)
        self.row += 1
        roi_ctl = ttk.Label(frame)
        roi_ctl.grid(column=0, row=self.row, sticky=tk.W)
        self.row += 1
        ttk.Label(frame, text='识别结果：').grid(column=0, row=self.row, sticky=tk.W)
        self.row += 1

        r_ctl = ttk.Label(frame, text="")
        r_ctl.grid(column=0, row=self.row, sticky=tk.W)
        self.row += 1

        ttk.Label(frame, text="准确率").grid(column=0, row=self.row, sticky=tk.W)
        self.row += 1
        precision_ctl = ttk.Label(frame, text="", width="20")
        precision_ctl.grid(column=0, row=self.row, sticky=tk.W)
        self.row += 1
        if result:
            imgtk_roi = ImageTk.PhotoImage(image=result['rect_image'])
            self.keep_reference_for_tk.append(imgtk_roi)
            roi_ctl.configure(image=imgtk_roi, state='enable')
            r_ctl.configure(text=result['result'])
            self.update_time = time.time()
            precision_ctl.configure(text=result['precision'])
        elif self.update_time + 8 < time.time():
            roi_ctl.configure(state='disabled')
            r_ctl.configure(text="")
            precision_ctl.configure(state='disabled')

    def clear_result_frame(self):
        self.keep_reference_for_tk.clear()
        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def get_imgtk(self, img_bgr):
        im = img_bgr
        imgtk = ImageTk.PhotoImage(image=im)
        wide = imgtk.width()
        high = imgtk.height()
        if wide > self.viewwide or high > self.viewhigh:
            wide_factor = self.viewwide / wide
            high_factor = self.viewhigh / high
            factor = min(wide_factor, high_factor)
            wide = int(wide * factor)
            if wide <= 0: wide = 1
            high = int(high * factor)
            if high <= 0: high = 1
            im = im.resize((wide, high), Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=im)
        return imgtk

    def from_pic(self):
        self.thread_run = False
        self.pic_path = askopenfilename(title="选择识别图片", filetypes=[("jpg图片", "*.jpg")])
        if self.pic_path:
            self.clear_result_frame()
            self.original_image = Image.open(self.pic_path)
            self.temp_path = self.pic_path
            while True:
                # 调用模型开始识别车牌
                result = main.start(self.temp_path)
                if result is not None:
                    rect_image = self.cut_pic(self.original_image, result['rect'])
                    result_in_frame = {'rect_image': rect_image,
                                       'result': result['pstr'],
                                       'precision': result['confidence']}
                    self.add_result_frame(self.result_frame, result_in_frame)
                else:
                    # self.compose_original_image()
                    # img_bgr = Image.open(self.temp_path)
                    img_bgr = Image.open(self.pic_path)
                    self.imgtk = self.get_imgtk(img_bgr)
                    self.image_ctl.configure(image=self.imgtk)
                    self.add_result_frame(self.result_frame, None)
                    break

    def cut_pic(self, image, rect):
        print(image.size)
        rect[2] = rect[0] + rect[2]
        rect[3] = rect[1] + rect[3]
        crop = image.crop(tuple(rect))
        # 将识别出来的车牌区域扣出并保存，然后涂黑，以便下次识别
        temp_rect = copy.copy(rect)
        for i in range(len(temp_rect)):
            temp_rect[i] = int(temp_rect[i])
        self.card_image_list.append(image.crop(temp_rect))
        self.card_rect_list.append(tuple(temp_rect))
        self.temp_path = "./temp.jpg"
        draw = ImageDraw.Draw(image)
        draw.rectangle(temp_rect, fill=ImageColor.getcolor("black", "RGB"))
        image.save(self.temp_path)
        return crop

    def compose_original_image(self):
        print("compose result image" + str(self.card_rect_list))
        image = Image.open(self.temp_path)
        for (rect_image, rect) in zip(self.card_image_list, self.card_rect_list):
            image.paste(rect_image, rect)
        image.save(self.temp_path)


def close_window():
    print("destroy")
    if surface.thread_run:
        surface.thread_run = False
        surface.thread.join(2.0)
    win.destroy()


if __name__ == '__main__':
    win = tk.Tk()

    surface = Surface2(win)
    win.protocol('WM_DELETE_WINDOW', close_window)
    win.mainloop()
