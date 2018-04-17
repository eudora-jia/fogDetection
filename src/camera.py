#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time, queue
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import cv2
import numpy as np

class LocalCamera(QObject):
    """本地摄像头类"""
    refreshLocalCameraImgSignal = pyqtSignal()
    def __init__(self):
        super().__init__() 
        self.image = QImage()
        self.imgArray = np.array([]) 
        self.imageQueue = queue.Queue(maxsize = 10) 
        self.device = cv2.VideoCapture(0)
        self.getLocalCameraParam()
        
        print("本地摄像头就绪")
        print("分辨率:", self.height, self.width)
        
        self.localCameraTimer = Timer()    
        self.localCameraTimer.timeOutSignal.connect(self.getLocalCameraImg)
        
    def getLocalCameraParam(self):
        """获取摄像头参数"""
        if self.device.isOpened():
            ret, frame= self.device.read()      
            self.height, self.width, self.bytesPerComponent = frame.shape
            self.bytesPerLine = self.bytesPerComponent * self.width
            return self.width, self.height
        
    def getLocalCameraImg(self):
        """获取摄像头图像"""
        if self.device.isOpened():
            ret, frame = self.device.read()
            self.imgArray = frame         
            # 变换彩色空间顺序
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
            # 转为QImage对象
            self.image = QImage(frame.data, self.width, self.height, self.bytesPerLine, QImage.Format_RGB888) 
            self.imageQueue.put(self.image)
            self.refreshLocalCameraImgSignal.emit()

        
class Timer(QThread):
    """定时器线程"""
    timeOutSignal = pyqtSignal()
    def __init__(self, parent=None):
        super(Timer, self).__init__(parent)
        self.stopedFlag = False
        self.mutex = QMutex()
        
    def run(self):
        with QMutexLocker(self.mutex):
            self.stopedFlag= False
        while True:
            if self.stopedFlag:
                return
            self.timeOutSignal.emit()
            #100毫秒发送一次信号,10帧
            time.sleep(0.1)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopedFlag= True

    def isStoped(self):
        with QMutexLocker(self.mutex):
            return self.stopedFlag
            
            
            
            