from io import BytesIO

import cv2
import onnxruntime
import numpy as np
from PIL import Image
import time

from sympy import classify_ode

from utils.orientation import non_max_suppression, tag_images, rescale_boxes

def DrawRect(img,det):
    img_Res = img
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(len(det)):
        img_Res = cv2.rectangle(img_Res, (det[i]['crop'][0], det[i]['crop'][1]),
                                (det[i]['crop'][2], det[i]['crop'][3]), (255, 0, 0), 2)
        img_Res = cv2.putText(img_Res, det[i]['classes']+str(det[i]['confidence']), (det[i]['crop'][0], det[i]['crop'][1]), font, 0.5,
                              (0, 0, 0), 1)
    return img_Res

class ONNXModel(object):
    def __init__(self, onnx_path):
        """
        :param onnx_path:
        """
        # so = onnxruntime.SessionOptions()
        # so.enable_profiling = True
        self.onnx_session = onnxruntime.InferenceSession(onnx_path,providers=[
            ("CUDAExecutionProvider", {
                "cudnn_conv_algo_search": "HEURISTIC",
                "cudnn_conv_use_max_workspace": '1',
                "cudnn_conv1d_pad_to_nc1d": '1'
            })])
        providers = self.onnx_session.get_providers()
        print("available providers:", providers)
        # self.onnx_session = onnxruntime.InferenceSession(onnx_path,providers=['CUDAExecutionProvider'])
        self.input_name = self.get_input_name(self.onnx_session)
        self.output_name = self.get_output_name(self.onnx_session)

        # print("input_name:{}".format(self.input_name))
        # print("output_name:{}".format(self.output_name))

    def get_output_name(self, onnx_session):
        """
        output_name = onnx_session.get_outputs()[0].name
        :param onnx_session:
        :return:
        """
        output_name = []
        for node in onnx_session.get_outputs():
            output_name.append(node.name)
        return output_name

    def get_input_name(self, onnx_session):
        """
        input_name = onnx_session.get_inputs()[0].name
        :param onnx_session:
        :return:
        """
        input_name = []
        for node in onnx_session.get_inputs():
            input_name.append(node.name)
        return input_name

    def get_input_feed(self, input_name, image_numpy):
        """
        input_feed={self.input_name: image_numpy}
        :param input_name:
        :param image_numpy:
        :return:
        """
        input_feed = {}
        for name in input_name:
            input_feed[name] = image_numpy
        return input_feed

    def to_numpy(self, file, shape, gray=False):
        if isinstance(file, np.ndarray):
            img = Image.fromarray(file)
        elif isinstance(file, bytes):
            img = Image.open(BytesIO(file))
            pass
        else:
            img = Image.open(file)

        widht, hight = shape
         # 改变大小 并保证其不失真
        img = img.convert('RGB')
        if gray:
            img = img.convert('L')
        img = img.resize((widht, hight), Image.ANTIALIAS)

        # 转换成矩阵
        image_numpy = np.array(img) # (widht, hight, 3)
        if gray:
            image_numpy = np.expand_dims(image_numpy,0)
            image_numpy = image_numpy.transpose(0, 1, 2)
        else:
            image_numpy = image_numpy.transpose(2,0,1) # 转置 (3, widht, hight)
        image_numpy = np.expand_dims(image_numpy,0)
        # 数据归一化
        image_numpy = image_numpy.astype(np.float32) / 255.0
        return image_numpy


class YOLO(ONNXModel):
    def __init__(self, onnx_path="ReqFile/yolov5n-7-k5.onnx"):
        super(YOLO, self).__init__(onnx_path)
        # 训练所采用的输入图片大小
        self.img_size = 640
        self.img_size_h = self.img_size_w = self.img_size
        self.batch_size = 1
        self.num_classes = 13
        self.classes = ['Battery',
                        'Medicine',
                        'Paper cup',
                        'Plastic bottle',
                        'Can',
                        'Potato',
                        'White radish',
                        'Carrot',
                        'Ceramic tile',
                        'Pebble',
                        'Brick',
                        'pepper',
                        'tomato']

    def to_numpy(self, img):
        img_size_h = img_size_w = self.img_size
        def letterbox_image(image, size):
            iw, ih = image.size
            w, h = size
            scale = min(w / iw, h / ih)
            nw = int(iw * scale)
            nh = int(ih * scale)

            image = image.resize((nw, nh), Image.BICUBIC)
            new_image = Image.new('RGB', size, (128, 128, 128))
            new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))
            return new_image

        resized = letterbox_image(img, (img_size_w, img_size_h))
        img_in = np.transpose(resized, (2, 0, 1)).astype(np.float32)  # HWC -> CHW
        img_in = np.expand_dims(img_in, axis=0)
        img_in /= 255.0
        return img_in

    def filter_Detections(self,results, thresh=0.5):
        # if model is trained on 1 class only
        if len(results[0]) == 5:
            # filter out the detections with confidence > thresh
            considerable_detections = [detection for detection in results if detection[4] > thresh]
            considerable_detections = np.array(considerable_detections)
            return considerable_detections

        # if model is trained on multiple classes
        else:
            # t1=time.perf_counter()
            """A = []
            for detection in results:
                class_id = detection[4:].argmax()
                confidence_score = detection[4:].max()
                new_detection = np.append(detection[:4], [class_id, confidence_score])
                if new_detection[-1] > thresh:
                    A.append(new_detection)
            A = np.array(A)
            t2=time.perf_counter()
            print(t2-t1)
            """
            A = []
            l=len(results[0])-4
            for detection in results:
                class_id = 0
                confidence_score = detection[4]
                j=1
                while j<l:
                    if detection[j+4]>confidence_score:
                        class_id=j
                        confidence_score = detection[j+4]
                    j=j+1
                #class_id = detection[4:].argmax()
                #confidence_score = detection[4:].max()
                if confidence_score > thresh:
                    A.append([detection[0],detection[1],detection[2],detection[3],class_id,confidence_score])
            A = np.array(A)
            # t2 = time.perf_counter()
            # print(t2 - t1)
            return A

    def NMS(self,results, thresh=0.5):
        res_ = sorted(results,key=lambda x: (x[5],x[4]),reverse=True)
        res = []
        def area(a):
            xx1 = a[0]
            yy1 = a[1]
            xx2 = a[2]
            yy2 = a[3]
            s = (xx2 - xx1) * (yy2 - yy1)
            return s
        def intersec(a,b):
            xx1 = max(min(a[0], a[2]), min(b[0], b[2]))
            yy1 = max(min(a[1], a[3]), min(b[1], b[3]))
            xx2 = min(max(a[0], a[2]), max(b[0], b[2]))
            yy2 = min(max(a[1], a[3]), max(b[1], b[3]))
            dx=max(xx2-xx1,0)
            dy=max(yy2-yy1,0)
            return dx*dy
        while len(res_) > 0:
            cur = res_.pop(0)
            res.append(cur)
            ss = area(cur)
            res_ = [i for i in res_ if i[4]!=cur[4] or intersec(i,cur)/(ss+area(i)-intersec(i,cur)) < thresh]
        return res

    def rescale(self, boxes,original_shape):
        """ Rescales bounding boxes to the original shape """
        current_dim=self.img_size
        orig_h, orig_w = original_shape
        scale = min(current_dim / orig_h, current_dim / orig_w)
        pad_x = max(orig_h - orig_w, 0) * scale/2
        pad_y = max(orig_w - orig_h, 0) * scale/2
        for box in boxes:
            x1 = ((box[0] - pad_x) - box[2] / 2) / scale
            x2 = ((box[0] - pad_x) + box[2] / 2) / scale
            y1 = ((box[1] - pad_y) - box[3] / 2) / scale
            y2 = ((box[1] - pad_y) + box[3] / 2) / scale
            box[:4] = [x1,y1,x2,y2]
        return boxes
    def rescale_nms(self, boxes,original_shape,thresh=0.3):
        """ Rescales bounding boxes to the original shape """
        current_dim=self.img_size
        orig_h, orig_w = original_shape
        scale = min(current_dim / orig_h, current_dim / orig_w)
        pad_x = max(orig_h - orig_w, 0) * scale/2
        pad_y = max(orig_w - orig_h, 0) * scale/2
        res = []
        for box in boxes:
            if box[4] >= thresh:
                x1 = (box[0] - pad_x) / scale
                x2 = (box[2] - pad_x) / scale
                y1 = (box[1] - pad_y) / scale
                y2 = (box[3] - pad_y) / scale
                box[:4] = [x1,y1,x2,y2]
                res.append(box)
        return res
    def decect(self, img_cv):
        img_size_h = img_size_w = self.img_size
        # 图片转换为矩阵
        img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        image_numpy = self.to_numpy(img)
        input_feed = self.get_input_feed(self.input_name, image_numpy)
        # t1 = time.perf_counter()
        outputs = self.onnx_session.run(self.output_name, input_feed=input_feed)
        # t2 = time.perf_counter()
        results = outputs[0][0]
        results = results.transpose()
        results=self.filter_Detections(results)
        results=self.rescale(results,img_cv.shape[:2])
        results=self.NMS(results)
        res = []
        for cur in results :
            box = [int(cur[0]),int(cur[1]),int(cur[2]),int(cur[3])]
            res.append(
                {
                    "crop":box,
                    "classes" : str(cur[4]),
                    "confidence" : cur[5]
                }
            )
        # t3=time.perf_counter()
        # print(t2-t1,t3-t2)
        return res
    def decect_nms(self, img_cv):
        # time.sleep(0.5)
        img_size_h = img_size_w = self.img_size
        # 图片转换为矩阵
        img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        image_numpy = self.to_numpy(img)
        input_feed = self.get_input_feed(self.input_name, image_numpy)
        # t1 = time.perf_counter()
        outputs = self.onnx_session.run(self.output_name, input_feed=input_feed)
        # t2 = time.perf_counter()
        results = outputs[0][0]
        results=self.rescale_nms(results,img_cv.shape[:2])
        res = []
        for cur in results :
            box = [int(cur[0]),int(cur[1]),int(cur[2]),int(cur[3])]
            res.append(
                {
                    "crop":box,
                    "classes" : self.classes[int(cur[5])],
                    "confidence" : cur[4]
                }
            )
        # t3=time.perf_counter()
        # print(t2-t1,t3-t2)
        return res
    def output(self):
        profile_file = self.onnx_session.end_profiling()
        print(profile_file)
        return