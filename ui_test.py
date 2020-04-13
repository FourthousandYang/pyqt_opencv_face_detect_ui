import cv2
import numpy as np
import os,sys
import time
from datetime import datetime
import imutils
from configparser import ConfigParser
import face_recognition
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLineEdit,QFormLayout,QDesktopWidget
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QTimer
from PyQt5.QtGui import QPixmap,QColor, QPen,QPalette


  
port=0

logo_img = cv2.imread("NHRI_Logo.jpg", -1)
logo_img = cv2.resize( logo_img, (256,256))
facelist = [logo_img]*5



def rgb_face(image):
    global facelist,templist,distance
    X_face_locations = face_recognition.face_locations(image , model= 'hog')
    
    faces = []
    
    for y1,x2,y2,x1 in X_face_locations:
        
        
        
        
        faces.append((x1,y1,x2,y2))
        
        
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0,255), 2)
        
            
        
    return image,faces

def get_face(rgb_im,faces):
    global facelist
    if faces == []:
        return rgb_im
    for face in faces:
        
        (x1,y1,x2,y2) = face
        
        faceimg = cv2.resize( rgb_im[y1:y2,x1:x2], (256,256))
                                
        facelist.append(faceimg)
        facelist = facelist[-5:]
        




class RGBVideo(QtCore.QObject):
    
    image_rgb = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, camera_port=port, parent=None):
        super().__init__(parent)
        self.camera = cv2.VideoCapture(camera_port)
        self.width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print (self.width,self.height)
        self.timer = QtCore.QBasicTimer()

    def start_recording(self):
        self.timer.start(0, self)

    def timerEvent(self, event):
        if (event.timerId() != self.timer.timerId()):
            return

        read, data = self.camera.read()
        if read:
            
            self.image_rgb.emit(data)

class RecordMessage(QtCore.QObject):
    
    
    image_message = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        

        self.timer = QtCore.QBasicTimer()

    def start_recording(self):
        self.timer.start(0, self)

    def timerEvent(self, event):
        global facelist
        
        
        
        faces = np.hstack((facelist[4],facelist[3],facelist[2],facelist[1],facelist[0]))
        
        if (event.timerId() != self.timer.timerId()):
            return

        
        self.image_message.emit(faces)

class FaceDetectionWidget(QtWidgets.QWidget):
    def __init__(self,  parent=None):
        super().__init__(parent)
       
        self.image = QtGui.QImage()
        self._red = (0, 0, 255)
        self._width = 2
        self._min_size = (30, 30)

    

    def image_rgb_slot(self, image_rgb):
        
        
        
        image_rgb=cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
        
        image_temp = image_rgb.copy()
        
        image_rgb,faces = rgb_face(image_rgb)
        
        
        
        get_face(image_temp,faces)
        
        

        image_rgb=cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
       
        
        
        
        self.image = self.get_qimage(image_rgb)
        if self.image.size() != self.size():
            self.setFixedSize(self.image.size())

        self.update()
        
    

    def get_qimage(self, image: np.ndarray):
        height, width, colors = image.shape
        bytesPerLine = 3 * width
        QImage = QtGui.QImage

        image = QImage(image.data,
                       width,
                       height,
                       bytesPerLine,
                       QImage.Format_RGB888)

        image = image.rgbSwapped()
        return image

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()
        


class MessageWidget(QtWidgets.QWidget):
    def __init__(self,  parent=None):
        super().__init__(parent)
        
        self.image = QtGui.QImage()
        self._red = (0, 0, 255)
        self._width = 2
        self._min_size = (30, 30)

    

    def message_data_slot(self, image_message):

        
        
        self.image = self.get_qimage(image_message)
        if self.image.size() != self.size():
            self.setFixedSize(self.image.size())

        self.update()

    def get_qimage(self, image: np.ndarray):
        height, width, colors = image.shape
        bytesPerLine = 3 * width
        QImage = QtGui.QImage

        image = QImage(image.data,
                       width,
                       height,
                       bytesPerLine,
                       QImage.Format_RGB888)

        image = image.rgbSwapped()
        return image

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    
        self.initUI()
    def initUI(self):
        self.img = np.ndarray(())
        
        
        self.timer_id = 0
        self.label = QtWidgets.QLabel("")
        
        self.label_start = QtWidgets.QLabel("Start")
        
        
        self.label.setFont(QtGui.QFont("Roman times",30,QtGui.QFont.Bold))
        
        
        self.label.setAlignment(Qt.AlignCenter)
        
        
        
        
        
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        
        
        
        self.face_detection_widget = FaceDetectionWidget()
        
        self.message_widget = MessageWidget()
        
        
        
        
        # TODO: set video port
        
        
        self.rgb_video = RGBVideo()
        
        self.record_message = RecordMessage()

        
        
        image_rgb_slot = self.face_detection_widget.image_rgb_slot
        
        image_message_slot = self.message_widget.message_data_slot
        
        
        self.rgb_video.image_rgb.connect(image_rgb_slot)
        self.record_message.image_message.connect(image_message_slot)
        
        
        self.run_button = QtWidgets.QPushButton("Start",self)
        

        mainlayout = QtWidgets.QHBoxLayout()
        layout2 = QtWidgets.QVBoxLayout()
        messagelayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QHBoxLayout()
        layout1 = QtWidgets.QHBoxLayout()
        layout3 = QtWidgets.QVBoxLayout()
        
        
        

        layout.addWidget(self.face_detection_widget)
        
        
        
        
        layout2.addWidget(self.label,0,Qt.AlignTop)
        
        
        layout2.addWidget(self.run_button)
        
        
        
        layout1.addLayout(layout)
        
        
        layout3.addLayout(layout1)
        layout3.addWidget(self.message_widget)
        mainlayout.addLayout(layout3)
        mainlayout.addLayout(layout2)
        
        
        
        #self.thermal_video.start_recording()
        #self.rgb_video.start_recording()
        #self.record_message.start_recording()
        #self.timer()
        #self.openSlot()
        #self.openSlot1()
        
        self.run_button.clicked.connect(self.rgb_video.start_recording)
        self.run_button.clicked.connect(self.record_message.start_recording)
        self.run_button.clicked.connect(self.timer)
        
        
        self.setLayout(mainlayout)
        
    
        
        
    def timer(self):
        self.timer_id = self.startTimer(1000, timerType = QtCore.Qt.VeryCoarseTimer)

    
    def timerEvent(self, event):
        self.label.setText(time.strftime(" %Y年%m月%d日 \n\n %H:%M:%S"))
        
        
    


   
        
    

def main():

    
    app = QtWidgets.QApplication(sys.argv)
    screen = QDesktopWidget().screenGeometry()
    main_window = QtWidgets.QMainWindow()
    main_widget = MainWidget()
    main_window.setCentralWidget(main_widget)
    main_window.setGeometry(0, 0, 400, 400)
    #main_window.setWindowIcon(QtGui.QIcon("Logo.jpg"))
    main_window.setWindowTitle('UI Test')
    
    #main_window.resize(screen.width(),screen.height())
    
    #main_window.showFullScreen()
    
    main_window.show()
    sys.exit(app.exec_())





if __name__ == '__main__':

    #try:
        
    main()
        
    #except:
    #    print ("Can't get Cam")
    
    cv2.destroyAllWindows()        

