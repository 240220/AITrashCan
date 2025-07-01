import tkinter as tk
import struct
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter.ttk import Style, Progressbar


from utils.operation import YOLO, DrawRect
# import serial
import cv2
import onnxruntime
import time
import threading
# from ffpyplayer.player import MediaPlayer
from pydub import AudioSegment
import simpleaudio as sa


def resize_img(img_pil, size):
	return img_pil.resize(size, Image.LANCZOS)


class MainPage:
	def __init__(self, root):
		self.root = root
		self.root.title('主页面')
		global yolo
		global cap
		global se
		cap = cv2.VideoCapture(0)
		yolo = YOLO(onnx_path='ReqFile/data03_03_15.onnx')
		img_cv = cv2.imread('ReqFile/c.jpg')
		yolo.decect(img_cv)
		# se = serial.Serial("/dev/ttyTHS1", 115200, timeout=1)
		Waiting(self.root)
	# VideoPlayTk(self.root)
	# DetectWindow(self.root)


# 开始界面
class Waiting:
	def __init__(self, root):
		self.root = root
		self.root.geometry("1280x800")
		self.Page = tk.Frame(self.root)
		self.Page.pack(fill=tk.BOTH, expand=True)
		# 创建打开文件按钮
		self.open_button = tk.Button(self.Page, text='开始', command=self.start)
		self.open_button.place(relx=0.2, rely=0.3, relheight=0.4, relwidth=0.6)
	
	def start(self):
		self.Page.destroy()
		VideoPlayTk(self.root)


# 主窗口
class VideoPlayTk:
	# 初始化函数
	def __init__(self, root):
		self.root = root
		self.Page = tk.Frame(self.root)
		self.Page.pack(fill=tk.BOTH, expand=True)
		# 创建一个画布用于显示视频帧
		self.canvas = tk.Canvas(self.Page, bg='black')
		self.canvas.pack(fill=tk.BOTH, expand=True)
		# 创建打开文件按钮
		self.open_button = tk.Button(self.Page, text='开始', command=self.open_file)
		self.open_button.pack(side=tk.LEFT)
		# 初始化播放器和播放状态标志
		self.audio_player = None
		self.video_player = None
		self.is_paused = False
		self.is_stopped = False
		self.find_trash = False
		self.open_file()
	
	# 打开文件的函数
	def open_file(self):
		# file_path = filedialog.askopenfilename()  # 弹出文件选择对话框
		file_path = 'source/trash0.mp4'
		self.audio_player = None
		self.video_player = None
		self.is_paused = False
		self.is_stopped = False
		self.find_trash = False
		self.start_video(file_path)  # 开始播放选择的视频文件
	
	# 开始播放视频的函数
	def start_video(self, file_path):
		self.video_player = cv2.VideoCapture(file_path)
		audio = AudioSegment.from_file(file_path, format="mp4")
		self.__slow_detect()
		self.play_video()  # 开始播放视频
		self.audio_player = sa.play_buffer(audio.raw_data, num_channels=audio.channels,
										   bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
	# 播放视频的函数
	def play_video(self):
		# if self.is_stopped:
		#    self.video_player = None  # 如果停止播放，则释放播放器资源
		#    return
		ret, frame = self.video_player.read()
		if frame is None:
			self.root.atter(10, self.open_file())
			return
		# 将帧图像转换为Tkinter PhotoImage并显示在画布上
		frm = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		# 将OpenCV图像转换为Pillow图像，然后转换为PhotoImage
		im = Image.fromarray(frm)
		# im = im.resize((1280, 720), Image.LANCZOS)
		photo = ImageTk.PhotoImage(image=im)
		self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
		self.canvas.image = photo  # 保持对PhotoImage的引用，防止被垃圾回收
		# 如果没有暂停，则继续播放下一帧
		if not self.is_stopped:
			self.root.after(25, self.play_video)  # 需要调整神秘常数
		else:
			self.video_player = None
	
	# 切换暂停状态的函数
	def video_stop(self):
		if not self.is_stopped:
			self.is_stopped = True
			self.audio_player.stop()
			self.Page.destroy()
			DetectWindow(self.root)
	def slow_detect(self):
		ret, img_cv = cap.read()
		det_obj = yolo.decect_nms(img_cv)
		if det_obj:
			self.find_trash = True
			if self.audio_player:
				self.video_stop()
		print(det_obj, self.find_trash)
	def __slow_detect(self):
		self.T = threading.Thread(target=self.slow_detect,args=())
		self.T.start()
		if self.find_trash == False:
			self.root.after(1000, self.__slow_detect)
		

class DetectWindow:
	def __init__(self, root):
		self.root = root
		self.Page = tk.Frame(self.root, width=450, height=250)
		self.Page.pack(fill=tk.BOTH, expand=True)
		# 创建一个画布用于显示视频帧
		self.canvas = tk.Canvas(self.Page, bg='black')
		self.canvas.place(x=0, y=0, relheight=1, relwidth=0.7)
		# 满载检测
		self.load_label = tk.Label(self.Page, text="满载检测：\n")
		self.load_label.place(relx=0.7, rely=0, relheight=0.3, relwidth=0.3)
		# 创建打开文本
		self.res_text = "识别结果：\n"
		self.res_label = tk.Label(self.Page, text=self.res_text)
		self.res_label.place(relx=0.7, rely=0.3, relheight=0.5, relwidth=0.3)
		# 返回按钮
		self.open_button = tk.Button(self.Page, text='返回', command=self.switch_window)
		self.open_button.place(relx=0.9, rely=0.8, relheight=0.2, relwidth=0.1)
		# 识出来按钮
		self.open_button = tk.Button(self.Page, text='压缩', command=self.extract)
		self.open_button.place(relx=0.7, rely=0.8, relheight=0.2, relwidth=0.2)
		# 初始化播放器和播放状态标志
		ret,self.res_img = cap.read()
		self.txtline = 0
		self.load = [0 ,0 ,0 ,0]
		self.cls_cnt = [0, 0, 0, 0]
		self.state = 1
		self.find_class = {
			"Battery": 0,
			"Medicine": 0,
			"Paper cup": 1,
			"Plastic bottle": 1,
			"Can": 1,
			"Potato": 2,
			"White radish": 2,
			"Carrot": 2,
			"Ceramic tile": 3,
			"Pebble": 3,
			"Brick": 3
		}
		self.las_det = []
		self.is_stopped = False
		self.__show()

	def show_txt(self, res):
		dic = {
		0: "有害垃圾  ",
		1: "可回收垃圾",
		2: "厨余垃圾  ",
		3: "其他垃圾  "
		}
		ss = str(res[0]) + '\t' + dic[res[1]] + '\t' + str(res[2]) + '\tOK!\n'
		self.res_text += ss
		self.res_label.config(text=self.res_text)
	
	def is_move(self, det_obj):
		cnt = 0
		def nms_check(box1, box2, thred=0.7):
			xx1 = max(min(box1[0], box1[2]), min(box2[0], box2[2]))
			xx2 = min(max(box1[0], box1[2]), max(box2[0], box2[2]))
			yy1 = max(min(box1[1], box1[3]), min(box2[1], box2[3]))
			yy2 = min(max(box1[1], box1[3]), max(box2[1], box2[3]))
			intersc = (xx2 - xx1) * (yy2 - yy1)
			ss = (box1[2] - box1[0]) * (box1[3] - box1[1]) + (box2[2] - box2[0]) * (box2[3] - box2[1])
			if float(intersc) / float(ss - intersc) > thred:
				return True
			return False
		
		for i in det_obj:
			for j in self.las_det:
				if i['classes'] == j['classes'] and nms_check(i['crop'], j['crop']):
					cnt += 1
		if cnt == len(det_obj):
			return True
		return False
	
	def extract(self):
		self.send_message(4,0,0,0)
	def send_message(self, cls, is_las, x, y):
		data_byte = struct.pack('HHBB', int(x), int(y), int(cls), int(is_las))
		# se.write(data_byte)
		self.state = 0
		# rec = se.read()
		rec = 0x20
		while not rec & 0x20:
			# se.write(data_byte)
			# rec = se.read()
			time.sleep(0.5)
		self.root.after(500, self.read_message)
	
	def read_message(self):
		rec_message = []
		# rec_message = se.readline()
		if rec_message:
			is_over = rec_message[0]
			print(is_over)
			ss="满载检测：\n"
			if is_over & 0x01:
				ss+="有害垃圾已满 \n"
			if is_over & 0x02:
				ss += "可回收垃圾已满 \n"
			if is_over & 0x04:
				ss += "厨余垃圾已满 \n"
			if is_over & 0x08:
				ss += "其他垃圾已满 \n"
			self.load_label.config(text=ss)
			if is_over & 0x10:
				self.state = 1
				return
		if self.state == 0:
			self.root.after(1000, self.read_message)
	
	def check_detect(self, det_obj):
		if self.state and self.is_move(det_obj):
			cls = self.find_class[det_obj[0]['classes']]
			x1 = det_obj[0]['crop'][0]
			y1 = det_obj[0]['crop'][1]
			x2 = det_obj[0]['crop'][2]
			y2 = det_obj[0]['crop'][3]
			xx = (x1+x2)/2
			yy = (y1+y2)/2
			self.txtline += 1
			self.cls_cnt[cls] += 1
			self.show_txt([self.txtline, cls, self.cls_cnt[cls]])
			self.send_message(cls, 1,xx,yy)
		self.las_det = det_obj
	def show_res(self):
		img_res = self.res_img
		if self.is_stopped:
			return
		frame = cv2.cvtColor(img_res, cv2.COLOR_BGR2RGB)
		# 将OpenCV图像转换为Pillow图像，然后转换为PhotoImage
		im = Image.fromarray(frame)
		im = im.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), Image.LANCZOS)
		photo = ImageTk.PhotoImage(image=im)
		self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
		self.canvas.image = photo  # 保持对PhotoImage的引用，防止被垃圾回收
	def __show(self):
		T = threading.Thread(target=self.fast_detect,args=())
		T.start()
		self.show_res()
		if not self.is_stopped:
			self.root.after(200,self.__show())
	def fast_detect(self):
		ret, img_cv = cap.read()
		
		det_obj = yolo.decect_nms(img_cv)
		print(det_obj)
		if len(det_obj) > 0:
			self.check_detect(det_obj)
		self.res_img = DrawRect(img_cv, det_obj)
	
	def switch_window(self):
		self.Page.destroy()
		self.is_stopped = True
		VideoPlayTk(self.root)


# 程序入口点
if __name__ == '__main__':
	root = tk.Tk()  # 创建Tkinter根窗口
	MainPage(root)  # 创建视频播放器应用
	root.mainloop()  # 进入Tkinter事件循环
