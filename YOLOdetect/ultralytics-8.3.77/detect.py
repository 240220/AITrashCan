# -*- coding: utf-8 -*-
"""
@Auth ： 挂科边缘
@File ：detect.py
@IDE ：PyCharm
@Motto:学习新思想，争做新青年
@Email ：179958974@qq.com
"""

from ultralytics import YOLO

if __name__ == '__main__':

    # Load a model
    print("aabb")
    model = YOLO(model='runs/train/exp11/weights/best.pt')
    # for i in range(10):
    #    result = model("data/newdata/images/r24.jpg")
    # print(result)
    model.predict(source="0",save=True,show=True,device=0)

    # export
    # path = model.export(format="onnx",opset=11,simplify=True,nms=True)