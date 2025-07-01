import cv2
from PIL import Image
import onnxruntime
import numpy as np
import time
from utils.operation import YOLO,DrawRect

if __name__ == "__main__":
    video = cv2.VideoCapture(1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    onnx_path = ('ReqFile/best.onnx')
    yolo=YOLO(onnx_path=onnx_path)
    #onnx_sess = onnxruntime.InferenceSession(onnx_path)
    #onnx_session = onnxruntime.InferenceSession(onnx_path,providers=['CUDAExecutionProvider'])

    device = onnxruntime.get_device()
    print("current device:",device)
    while True:
        t1 = time.perf_counter()
        ret , img_cv = video.read()
        print(img_cv.shape)
        det_obj = yolo.decect_nms(img_cv)
        img_res = DrawRect(img_cv,det_obj)
        t2 = time.perf_counter()
        print(det_obj,'fps:',1.00/(t2-t1),t2-t1)
        cv2.imshow('Image', img_cv)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #yolo.output()
            #print("aaaa")
            break
    cv2.destroyAllWindows()
