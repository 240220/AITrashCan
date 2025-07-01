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
    model = YOLO(model=r'yolo11s.pt')
    #model.predict(source=0,save=True,show=True,device=0)
    model.train(data=r'data_01_split.yaml',
                imgsz=640,
                epochs=60,
                batch=4,
                workers=0,
                device=0,
                optimizer='SGD',
                close_mosaic=50,
                resume=False,
                project='runs/train',
                name='exp',
                single_cls=False,
                cache=False,
                )
    # export
    # path = model.export(format="onnx",opset=11)