import sys, cv2, threading
import mediapipe as mp
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QMovie
from PyQt5.QtMultimedia import QSound
from qt_material import apply_stylesheet
import random
import eyetest_variables as etv
import time
import webbrowser

etv.lowest_wrongtimes = -1
etv.level_now = 0.1
language_choice = 'English'

class Ui_MainWindow(QtCore.QObject):
    # signals for updating the message and image
    # avoid updating the GUI from a different thread
    update_message_signal = QtCore.pyqtSignal(str)
    update_distance_info_signal = QtCore.pyqtSignal(bool)
    update_image_signal = QtCore.pyqtSignal(QImage)
    startexam_signal = QtCore.pyqtSignal(bool)
    choose_pushbutton3_signal = QtCore.pyqtSignal(bool)
    choose_pushbutton4_signal = QtCore.pyqtSignal(bool)
    stop_gif_signal = QtCore.pyqtSignal(bool)
    quit_signal = QtCore.pyqtSignal(bool)  
    show_arrow_signal = QtCore.pyqtSignal(str)
    choose_desktop_signal = QtCore.pyqtSignal(bool)
    choose_laptop_signal = QtCore.pyqtSignal(bool)
    switch_leftcolumn_signal = QtCore.pyqtSignal(bool)
    switch_rightcolumn_signal = QtCore.pyqtSignal(bool)
    
    qsound = QSound("")

    def __init__(self):
        super().__init__()      
        self.round = 1              # round 1 for right eye, round 2 for left eye
        self.counter = 10           # time limit for every event
        self.testeye_now = 'right'  # right eye or left eye
        self.ocv = True             # open the camera or not
        self.teststart = False      # start the test or not
        self.pointstart = False     # start the pointing or not
        self.quitapp = True        # quit the application or not
        self.setsize = 100         # original size of the C image
        self.eye_xdistance = 0      # distance between two eyes
        self.imagedirection = ' '   # direction of the C image
        self.pointingdirection = '' # direction of the pointing
        self.lefteye = 0.0          # left eye vision
        self.righteye = 0.0         # right eye vision
        self.cap = None              
        self.column = 'left'        # left or right
        self.device = 'laptop'     # desktop or laptop

    # button for quit the application
    def quitButton_clicked(self):
        self.ocv = False        
        sys.exit()      

    # function for hide the start button
    def startexam(self, visibility):
        self.pushButton2.setVisible(not visibility)
        self.pushButton3.setVisible(not visibility)
        self.pushButton4.setVisible(not visibility)
        self.textEdit_6.setVisible(not visibility)
        self.label_2.setVisible(True)
        self.label_column.setVisible(not visibility)
        self.label_column2.setVisible(not visibility)
        self.pushButton5.setVisible(not visibility)
        self.pushButton6.setVisible(not visibility)
        self.label_glass.setVisible(not visibility)
        self.textEdit_5.setVisible(not visibility)
        self.textEdit_2.setVisible(not visibility)
        self.label_info.setStyleSheet("image: url(./glass2.png); border: 3px solid white;")
        self.label_leftcover.setVisible(True)
        self.label_rightcover.setVisible(True)
        self.label_leftcover.setStyleSheet("image: url(./leftcover.png);")
        self.label_rightcover.setStyleSheet("image: url(./openeye.png);")
        self.quitapp = False
        if language_choice == 'Chinese':
            self.textbox_final2.setText(f"視力檢查合格標準請參照下方表格\n\n\n本測驗為居家簡易檢測，數值僅供參考\n如有疑慮請至眼科進行進一步檢查\n\nVTABIRD關心您的視力健康")
            self.label_leftresult.setText("左眼")
            self.label_rightresult.setText("右眼")
            item00 = QtWidgets.QTableWidgetItem("年齡")
            item00.setTextAlignment(QtCore.Qt.AlignCenter)
            # set the item border color
            self.tableWidget.setItem(0, 0, item00)
            item01 = QtWidgets.QTableWidgetItem("4歲")
            item01.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 1, item01)
            item02 = QtWidgets.QTableWidgetItem("5歲")
            item02.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 2, item02)
            item03 = QtWidgets.QTableWidgetItem("6歲")
            item03.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 3, item03)
            item04 = QtWidgets.QTableWidgetItem("7歲或以上")
            item04.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 4, item04)
            item10 = QtWidgets.QTableWidgetItem("視力標準")
            item10.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 0, item10)
            item11 = QtWidgets.QTableWidgetItem("0.6")
            item11.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 1, item11)
            item12 = QtWidgets.QTableWidgetItem("0.7")
            item12.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 2, item12)
            item13 = QtWidgets.QTableWidgetItem("0.8")
            item13.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 3, item13)
            item14 = QtWidgets.QTableWidgetItem("0.9")
            item14.setTextAlignment(QtCore.Qt.AlignCenter)  
            self.tableWidget.setItem(1, 4, item14)       
        elif language_choice == 'English':
            self.textbox_final2.setText(f"Please refer to the table below for the standard\n\n\nThis test is a simple self-examination, the values are for reference only\nIf you have any concerns, please go to clinic for further examination\n\n\nVTABIRD cares about your vision health")
            self.label_leftresult.setText("Left Eye")
            self.label_rightresult.setText("Right Eye")
            item00 = QtWidgets.QTableWidgetItem("Age")
            item00.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 0, item00)
            item01 = QtWidgets.QTableWidgetItem("4 years")
            item01.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 1, item01)
            item02 = QtWidgets.QTableWidgetItem("5 years")
            item02.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 2, item02)
            item03 = QtWidgets.QTableWidgetItem("6 years")
            item03.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 3, item03)
            item04 = QtWidgets.QTableWidgetItem("7 years or above")
            item04.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(0, 4, item04)
            item10 = QtWidgets.QTableWidgetItem("Vision Standard")
            item10.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 0, item10)
            item11 = QtWidgets.QTableWidgetItem("0.6")
            item11.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 1, item11)
            item12 = QtWidgets.QTableWidgetItem("0.7")
            item12.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 2, item12)
            item13 = QtWidgets.QTableWidgetItem("0.8")
            item13.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 3, item13)
            item14 = QtWidgets.QTableWidgetItem("0.9")
            item14.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableWidget.setItem(1, 4, item14)        

    # hide every widget
    def hide_all(self):
        self.pushButton2.setVisible(False)
        self.pushButton3.setVisible(False)
        self.pushButton4.setVisible(False)
        self.label_2.setVisible(False)
        self.labelC.setVisible(False)
        self.textEdit.setVisible(False)
        self.textEdit_3.setVisible(False)
        self.pushButton.setVisible(False)
        self.textEdit_5.setVisible(False)
        self.label_arrow.setVisible(False)
        self.textbox_final2.setVisible(True)
        self.textEdit_2.setVisible(True)
        self.label_column.setVisible(False)
        self.label_column2.setVisible(False)
        self.label_leftresult.setVisible(True)
        self.label_rightresult.setVisible(True)
        self.leftresult.setVisible(True)
        self.rightresult.setVisible(True)
        self.quitapp = True
        
    
    #function for set the pushbutton3 black
    def choose_pushbutton3(self, visibility):
        global language_choice       
        self.pushButton3.setStyleSheet("font-size: 14pt; background-color: white;")
        self.pushButton4.setStyleSheet("font-size: 14pt; background-color: transparent;")
        language_choice = 'Chinese'
        self.textEdit_2.setText("手勢YA退出應用程式")
        self.textEdit_6.setText("手勢OK開始測試")
        self.textEdit_3.setText("歡迎使用VTABIRD！請選擇您的偏好語言後展示OK手勢。")
        self.pushButton5.setText("桌機")
        self.pushButton6.setText("筆電")

    # function to click event for github link
    def click_github(self):
        webbrowser.open('https://github.com/TKkusa/Project_Design_2')

    def click_youtube(self):
        webbrowser.open('https://www.youtube.com/channel/UCuypzy4Vy3qpLJAraQYRcTg')

    def choose_pushbutton4(self, visibility):
        global language_choice
        self.pushButton3.setStyleSheet("font-size: 14pt; background-color: transparent;")
        self.pushButton4.setStyleSheet("font-size: 14pt; background-color: white;")
        language_choice = 'English'
        self.textEdit_2.setText("Gesture YA to quit")
        self.textEdit_6.setText("Gesture OK to start")
        self.textEdit_3.setText("Please choose your language and device.")
        self.pushButton5.setText("Desktop")
        self.pushButton6.setText("Laptop")
    
    def choose_desktop(self):
        if self.device == 'laptop':
            self.device = 'desktop'
            self.setsize = 100
        self.pushButton5.setStyleSheet("font-size: 14pt; background-color: white;")
        self.pushButton6.setStyleSheet("font-size: 14pt; background-color: transparent;")
        

    def choose_laptop(self):
        if self.device == 'desktop':
            self.device = 'laptop'
            self.setsize = 100
        self.pushButton5.setStyleSheet("font-size: 14pt; background-color: transparent;")
        self.pushButton6.setStyleSheet("font-size: 14pt; background-color: white;")
        
    def switch_leftcolumn(self):

        self.label_column.setVisible(True)
        self.label_column2.setVisible(False)
    
    def switch_rightcolumn(self):

        self.label_column.setVisible(False)
        self.label_column2.setVisible(True)


    def show_arrow(self, direction):
        self.label_arrow.setVisible(True)
        if direction == 'up':
            self.label_arrow.setStyleSheet("image: url(./up.png); background-color: transparent; border: 3px solid cyan;")
        elif direction == 'down':
            self.label_arrow.setStyleSheet("image: url(./down.png); background-color: transparent; border: 3px solid cyan;")
        elif direction == 'left':
            self.label_arrow.setStyleSheet("image: url(./left.png); background-color: transparent; border: 3px solid cyan;")
        elif direction == 'right':
            self.label_arrow.setStyleSheet("image: url(./right.png); background-color: transparent; border: 3px solid cyan;")
        elif direction == 'pass':
            self.label_arrow.setStyleSheet("image: url(./pass.png); background-color: transparent; border: 3px solid cyan;")

    def stop_gif(self):
        self.loadingmovie.stop()
        self.label_loading.setVisible(False)
        self.label_loadingtext.setVisible(False)
        
    #function for screen to user distance information
    def eye_distance(self):
        global language_choice
        if self.eye_xdistance < 60:
            if language_choice == 'English':
                self.textEdit_5.setText("Please move closer to the camera.")
                self.textEdit_5.setStyleSheet("font-size: 14pt; background-color: transparent; color: yellow;")
            else:
                self.textEdit_5.setText("請靠近攝影機。")   
                self.textEdit_5.setStyleSheet("font-size: 14pt; background-color: transparent; color: yellow;")        
        elif self.eye_xdistance > 80:
            if language_choice == 'English':
                self.textEdit_5.setText("Please move away from the camera.")
                self.textEdit_5.setStyleSheet("font-size: 14pt; background-color: transparent; color: yellow;")
            else:
                self.textEdit_5.setText("請遠離攝影機。")
                self.textEdit_5.setStyleSheet("font-size: 14pt; background-color: transparent; color: yellow;")
        else:
            if language_choice == 'English':
                self.textEdit_5.setText("The distance is appropriate.")
                self.textEdit_5.setStyleSheet("font-size: 14pt; background-color: transparent; color: cyan;")
            else:
                self.textEdit_5.setText("距離適當。")
                self.textEdit_5.setStyleSheet("font-size: 14pt; background-color: transparent; color: cyan;") 

    # function for updating the message 
    def update_message(self, message):
        self.textEdit_3.setText(message)   
        self.label_arrow.setVisible(False)  
    

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # label for background image
        self.label_background = QtWidgets.QLabel(self.centralwidget)
        self.label_background.setGeometry(QtCore.QRect(0, -450, 1920, 1920))
        self.label_background.setObjectName("label_3")
        self.label_background.setStyleSheet("image: url(./background.png);")

        # change the icon of the window
        MainWindow.setWindowIcon(QtGui.QIcon('./icon.png'))

        # only close button available
        MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.FramelessWindowHint)

        # text box for time limit
        self.textEdit = QtWidgets.QPushButton(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(930, 630, 150, 150))
        font = QtGui.QFont()     
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setText("10")
        self.textEdit.setStyleSheet("font-size: 56pt; background-color: transparent;")

        # text box for eye distance
        self.textEdit_5 = QtWidgets.QPushButton(self.centralwidget)
        self.textEdit_5.setGeometry(QtCore.QRect(80, 730, 830, 50))
        font = QtGui.QFont()
        self.textEdit_5.setFont(font)
        self.textEdit_5.setObjectName("textEdit_5")
        self.textEdit_5.setText("")
        self.textEdit_5.setStyleSheet("font-size: 14pt; background-color: transparent;")
        self.update_distance_info_signal.connect(self.eye_distance)


        # text box for message
        self.textEdit_3 = QtWidgets.QPushButton(self.centralwidget)
        self.textEdit_3.setGeometry(QtCore.QRect(80, 800, 1000, 50))
        font = QtGui.QFont()
        self.textEdit_3.setObjectName("textEdit_3")
        self.textEdit_3.setText("Please wait for the camera.")
        self.textEdit_3.setStyleSheet("font-size: 14pt; background-color: transparent;")

        # label for image in the information part
        self.label_info = QtWidgets.QLabel(self.centralwidget)
        self.label_info.setGeometry(QtCore.QRect(50, 580, 1080, 400))
        self.label_info.setObjectName("label_info")
        self.label_info.setStyleSheet("image: url(./glass2.png); ")

        # label for image in gesture part
        self.label_gesture = QtWidgets.QLabel(self.centralwidget)
        self.label_gesture.setGeometry(QtCore.QRect(1150, 580, 580, 400))
        self.label_gesture.setObjectName("label_gesture")
        self.label_gesture.setStyleSheet("image: url(./glass3.png); ")

        # label for cover gesture hint left
        self.label_leftcover = QtWidgets.QLabel(self.centralwidget)
        self.label_leftcover.setGeometry(QtCore.QRect(1250, 650, 200, 200))
        self.label_leftcover.setObjectName("label_leftcover")
        self.label_leftcover.setVisible(False)

        # label for cover gesture hint right
        self.label_rightcover = QtWidgets.QLabel(self.centralwidget)
        self.label_rightcover.setGeometry(QtCore.QRect(1450, 650, 200, 200))
        self.label_rightcover.setObjectName("label_rightcover")
        self.label_rightcover.setVisible(False)
        
        # label for logo 
        self.label_logo = QtWidgets.QLabel(self.centralwidget)
        self.label_logo.setGeometry(QtCore.QRect(1740, 30, 170, 170))
        self.label_logo.setObjectName("label_logo")
        self.label_logo.setStyleSheet("image: url(./logo.png);")

        # label for long strip decoration
        self.label_strip = QtWidgets.QLabel(self.centralwidget)
        self.label_strip.setGeometry(QtCore.QRect(1740, 200, 170, 780))
        self.label_strip.setObjectName("label_strip")
        self.label_strip.setStyleSheet("image: url(./strip.png); ")
        self.label_strip.setVisible(True)
        
        # button for githublink
        self.button_github = QtWidgets.QPushButton(self.centralwidget)
        self.button_github.setGeometry(QtCore.QRect(1800, 230, 80, 80))
        self.button_github.setObjectName("button_github")
        self.button_github.setStyleSheet("image: url(./githublink.png); border: transparent;") 
        self.button_github.clicked.connect(self.click_github)

        # button for youtube link
        self.button_youtube = QtWidgets.QPushButton(self.centralwidget)
        self.button_youtube.setGeometry(QtCore.QRect(1770, 480, 80, 80))
        self.button_youtube.setObjectName("button_youtube")
        self.button_youtube.setStyleSheet("image: url(./youtubelink.png); border: transparent;")
        self.button_youtube.clicked.connect(self.click_youtube)


        # button for quit the application
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(1270, 800, 370, 50))
        font = QtGui.QFont()
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("quitButton")
        self.pushButton.setText("Gesture YA to quit ")
        self.pushButton.clicked.connect(self.quitButton_clicked)
        self.quit_signal.connect(self.quitButton_clicked)
        self.pushButton.setVisible(False)
        self.pushButton.setStyleSheet("font-size: 14pt;")

        #text box for how to quit the application
        self.textEdit_2 = QtWidgets.QPushButton(self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(1200, 800, 500, 50))
        font = QtGui.QFont()
        self.textEdit_2.setObjectName("textEdit_2")
        self.textEdit_2.setText("Gesture YA to quit ")
        self.textEdit_2.setVisible(True)
        self.textEdit_2.setStyleSheet("font-size: 14pt; background-color: transparent;")

        # text box for how to start the test
        self.textEdit_6 = QtWidgets.QPushButton(self.centralwidget)
        self.textEdit_6.setGeometry(QtCore.QRect(1200, 730, 500, 50))
        font = QtGui.QFont()
        self.textEdit_6.setObjectName("textEdit_6")
        self.textEdit_6.setText("Gesture OK to start ")
        self.textEdit_6.setStyleSheet("font-size: 14pt; background-color: transparent;")
        self.textEdit_6.setVisible(True)

        # label for arrow
        self.label_arrow = QtWidgets.QLabel(self.centralwidget)
        self.label_arrow.setGeometry(QtCore.QRect(1350, 650, 200, 200))
        self.label_arrow.setObjectName("label_arrow")
        self.label_arrow.setStyleSheet("image: url(./pass.png); background-color: transparent; border: 3px solid cyan;")
        self.label_arrow.setVisible(False)
        self.show_arrow_signal.connect(self.show_arrow)

        #label for left column
        self.label_column = QtWidgets.QLabel(self.centralwidget)
        self.label_column.setGeometry(QtCore.QRect(150, 170, 250, 300))
        self.label_column.setObjectName("label_column")
        self.label_column.setStyleSheet("background-color: black; border: 3px solid cyan;")
        self.label_column.setVisible(True)

        #label for right column
        self.label_column2 = QtWidgets.QLabel(self.centralwidget)
        self.label_column2.setGeometry(QtCore.QRect(500, 170, 250, 300))
        self.label_column2.setObjectName("label_column2")
        self.label_column2.setStyleSheet("background-color: black; border: 3px solid cyan;")
        self.label_column2.setVisible(False)

        # button for left eye result
        self.leftresult = QtWidgets.QPushButton(self.centralwidget)
        self.leftresult.setGeometry(QtCore.QRect(50, 100, 250, 150))
        self.leftresult.setObjectName("leftresult")
        self.leftresult.setText("Left Eye")
        self.leftresult.setStyleSheet("font-size: 56pt; background-color: transparent; border: 3px solid cyan;")
        self.leftresult.setVisible(False)

        # label for left eye result
        self.label_leftresult = QtWidgets.QLabel(self.centralwidget)
        self.label_leftresult.setGeometry(QtCore.QRect(50, 50, 100, 50))
        self.label_leftresult.setObjectName("label_leftresult")
        self.label_leftresult.setText("Left Eye")
        self.label_leftresult.setStyleSheet("font-size: 14pt; background-color: transparent; color: cyan;")
        self.label_leftresult.setVisible(False)

        # button for right eye result
        self.rightresult = QtWidgets.QPushButton(self.centralwidget)
        self.rightresult.setGeometry(QtCore.QRect(330, 100, 250, 150))
        self.rightresult.setObjectName("rightresult")
        self.rightresult.setText("Right Eye")
        self.rightresult.setStyleSheet("font-size: 56pt; background-color: transparent; border: 3px solid cyan;")
        self.rightresult.setVisible(False)

        # label for right eye result
        self.label_rightresult = QtWidgets.QLabel(self.centralwidget)
        self.label_rightresult.setGeometry(QtCore.QRect(330, 50, 100, 50))
        self.label_rightresult.setObjectName("label_rightresult")
        self.label_rightresult.setText("Right Eye")
        self.label_rightresult.setStyleSheet("font-size: 14pt; background-color: transparent; color: cyan;")
        self.label_rightresult.setVisible(False)


        # text box 2 for the final result
        self.textbox_final2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textbox_final2.setGeometry(QtCore.QRect(50, 300, 800, 250))
        font = QtGui.QFont()
        self.textbox_final2.setFont(font)
        self.textbox_final2.setObjectName("textEdit_7")
        self.textbox_final2.setText("")
        self.textbox_final2.setVisible(False)
        self.textbox_final2.setStyleSheet("font-size: 14pt; background-color: transparent;")

        # label for the camera
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(950, 50, 720, 480))

        # lable for loading gif
        self.label_loading = QtWidgets.QLabel(self.centralwidget)
        self.label_loading.setGeometry(QtCore.QRect(1250, 150, 200, 200))
        self.label_loading.setObjectName("label_loading")
        self.loadingmovie = QMovie("./loading.gif")
        self.label_loading.setMovie(self.loadingmovie)
        self.loadingmovie.start()
        self.stop_gif_signal.connect(self.stop_gif)

        # label for loading text
        self.label_loadingtext = QtWidgets.QLabel(self.centralwidget)
        self.label_loadingtext.setGeometry(QtCore.QRect(1150, 325, 500, 50))
        self.label_loadingtext.setObjectName("label_loadingtext")
        self.label_loadingtext.setText("Loading camera...")
        self.label_loadingtext.setStyleSheet("font-size: 25pt; color: cyan;")
        self.label_loadingtext.setVisible(True)

        # label for the frame image of the camera
        self.label_cameraframe = QtWidgets.QLabel(self.centralwidget)
        self.label_cameraframe.setGeometry(QtCore.QRect(710, -180, 1200, 1000))
        self.label_cameraframe.setObjectName("label_cameraframe")
        self.label_cameraframe.setStyleSheet("image: url(./cameraframe.png);")

        # label for whiteboard
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(50, 50, 830, 730))
        self.label_2.setObjectName("label_2")
        self.label_2.setStyleSheet("background-color: black; border: 3px solid white;")
        self.label_2.setVisible(False)

        # label for glass 
        self.label_glass = QtWidgets.QLabel(self.centralwidget)
        self.label_glass.setGeometry(QtCore.QRect(50, 50, 830, 500))
        self.label_glass.setObjectName("label_glass")
        self.label_glass.setStyleSheet("image: url(./glass1.png); ")
        self.label_glass.setVisible(True)


        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # connect the signals to the functions
        self.update_message_signal.connect(self.update_message)

        # button for starting
        self.pushButton2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton2.setGeometry(QtCore.QRect(1570, 720, 100, 50))
        font = QtGui.QFont()    
        self.pushButton2.setFont(font)
        self.pushButton2.setObjectName("StartButton")
        self.pushButton2.setText("Start")
        self.pushButton2.setStyleSheet("font-size: 14pt;") 
        self.startexam_signal.connect(self.startexam)
        self.pushButton2.setVisible(False)
        
        #button for change to Chinese
        self.pushButton3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton3.setGeometry(QtCore.QRect(200, 250, 150, 50))
        font = QtGui.QFont()
        self.pushButton3.setFont(font)
        self.pushButton3.setObjectName("ChineseButton")
        self.pushButton3.setText("中文")
        self.pushButton3.setStyleSheet("font-size: 14pt; background-color: transparent;")
        self.choose_pushbutton3_signal.connect(self.choose_pushbutton3)
        
        #button for change to English
        self.pushButton4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton4.setGeometry(QtCore.QRect(200, 350, 150, 50))
        font = QtGui.QFont()
        self.pushButton4.setFont(font)
        self.pushButton4.setObjectName("EnglishButton")
        self.pushButton4.setText("English")
        self.pushButton4.setStyleSheet("font-size: 14pt; background-color: white;")
        self.choose_pushbutton4_signal.connect(self.choose_pushbutton4)

        #button for choose desktop
        self.pushButton5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton5.setGeometry(QtCore.QRect(550, 250, 150, 50))
        font = QtGui.QFont()
        self.pushButton5.setFont(font)
        self.pushButton5.setObjectName("DesktopButton")
        self.pushButton5.setText("Desktop")
        self.pushButton5.setStyleSheet("font-size: 14pt; background-color: transparent;")
        self.choose_desktop_signal.connect(self.choose_desktop)

        #button for choose laptop
        self.pushButton6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton6.setGeometry(QtCore.QRect(550, 350, 150, 50))
        font = QtGui.QFont()
        self.pushButton6.setFont(font)
        self.pushButton6.setObjectName("LaptopButton")
        self.pushButton6.setText("Laptop")
        self.pushButton6.setStyleSheet("font-size: 14pt; background-color: white;")
        self.choose_laptop_signal.connect(self.choose_laptop)
        
        # label for the image of "C"
        self.labelC = QtWidgets.QLabel(self.centralwidget)
        self.labelC.setGeometry(QtCore.QRect(70, 70, 720, 480))

        # table for the vision standard
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(90, 600, 1000, 250))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setStyleSheet("font-size: 14pt; background-color: transparent; color: white; border: 3px solid cyan;")
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.setVisible(False)



        self.label_loading.raise_()
        self.label_loadingtext.raise_()
        self.label_cameraframe.raise_()
        self.label.raise_()
        self.label_logo.raise_()
        self.button_github.raise_()
        self.button_youtube.raise_()

        self.label_glass.raise_()
        self.label_column.raise_()
        self.label_column2.raise_()
        self.pushButton3.raise_()
        self.pushButton4.raise_()
        self.pushButton5.raise_()
        self.pushButton6.raise_()
        self.label_info.raise_()
        self.tableWidget.raise_()
        self.label_2.raise_()
        self.labelC.raise_()
        self.textEdit.raise_()
        self.textEdit_3.raise_()  
        self.textEdit_5.raise_()  
        self.label_gesture.raise_() 
        self.label_arrow.raise_()
        self.textEdit_2.raise_()
        self.textEdit_6.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1130, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        


        # timer for any event
        self.mytimer = QtCore.QTimer()
        self.mytimer.timeout.connect(self.onTimer)
        self.mytimer.start(1000)

        self.switch_leftcolumn_signal.connect(self.switch_leftcolumn)
        self.switch_rightcolumn_signal.connect(self.switch_rightcolumn)
    
    # function for the image
    def imageprocess(self):
        img = cv2.imread("./C.jpg")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        output_rotete_90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        output_rotete_180 = cv2.rotate(img, cv2.ROTATE_180)
        output_rotate_90_counterclockwise = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        rotate_pattern = random.randint(0, 3)
        if rotate_pattern == 0:
            img = output_rotete_90
            self.imagedirection = 'down'
        elif rotate_pattern == 1:
            img = output_rotete_180
            self.imagedirection = 'left'
        elif rotate_pattern == 2:
            img = output_rotate_90_counterclockwise
            self.imagedirection = 'up'
        else:
            img = img
            self.imagedirection = 'right'


        img = cv2.resize(img, (self.setsize, self.setsize))
        height, width, channel = img.shape
        bytesPerLine = channel * width
        

        qimg = QImage(img, width, height, bytesPerLine, QImage.Format_RGB888)
        canvas = QPixmap.fromImage(qimg)

        XBound = random.randint(70, 700)
        YBound = random.randint(-70, 450)
        
        self.labelC.setGeometry(QtCore.QRect(XBound, YBound, 720, 480))

        self.labelC.setPixmap(canvas)
 
    # eyetest flow event
    def onTimer(self):
        if self.teststart == True:
            self.counter = self.counter - 1
            self.textEdit.setText(str(self.counter))

            if self.counter == 0:
                self.labelC.setVisible(True)
                self.label_leftcover.setVisible(False)
                self.label_rightcover.setVisible(False)
                self.pointstart = True
                self.counter = 3

                self.vision_test()
                self.check_vision_level()
                self.imageprocess()

    # reset every value vision_correctimes dictionary to 0
    def reset_and_init(self):
        for level, times in etv.visionlevel_correctimes.items():
            etv.visionlevel_correctimes[level] = 0
        self.pointstart = False
        self.setsize = 100           
        self.imagedirection = ' '
        self.pointingdirection = ''
        self.round = 2
        self.counter = 11
        self.labelC.setVisible(False)
        self.label_arrow.setVisible(False)
        self.label_leftcover.setVisible(True)
        self.label_rightcover.setVisible(True)
        self.label_leftcover.setStyleSheet("image: url(./openeye.png);")
        self.label_rightcover.setStyleSheet("image: url(./rightcover.png);")
        etv.lowest_wrongtimes = -1
        etv.level_now = 0.1

    # vision test event handler
    def vision_test(self):
        if self.device == 'desktop':
            if etv.level_now == 0.1:     
                if self.pointingdirection == self.imagedirection:  
                    etv.visionlevel_correctimes[etv.level_now] += 1           
                    etv.level_now = 0.2 
                    self.setsize = 50
                else:
                    etv.lowest_wrongtimes += 1
                    self.setsize = 100
            elif etv.level_now == 0.2:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.3
                    self.setsize = 33                       
                else:
                    etv.level_now = 0.1
                    self.setsize = 100
            elif etv.level_now == 0.3:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.4
                    self.setsize = 25
                else:
                    etv.level_now = 0.2
                    self.setsize = 50
            elif etv.level_now == 0.4:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.5
                    self.setsize = 20
                else:
                    etv.level_now = 0.3
                    self.setsize = 33
            elif etv.level_now == 0.5:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.6
                    self.setsize = 17
                else:
                    etv.level_now = 0.4
                    self.setsize = 25
            elif etv.level_now == 0.6:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.7
                    self.setsize = 14
                else:
                    etv.level_now = 0.5
                    self.setsize = 20
            elif etv.level_now == 0.7:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.8
                    self.setsize = 12
                else:
                    etv.level_now = 0.6
                    self.setsize = 17
            elif etv.level_now == 0.8:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.9
                    self.setsize = 11
                else:
                    etv.level_now = 0.7
                    self.setsize = 14
            elif etv.level_now == 0.9:
                if self.pointingdirection == self.imagedirection:

                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 1.0
                    self.setsize = 10
                else:
                    etv.level_now = 0.8
                    self.setsize = 12
            elif etv.level_now == 1.0:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    self.setsize = 10
                else:
                    etv.level_now = 0.9
                    self.setsize = 11
        elif self.device == 'laptop':
            if etv.level_now == 0.1:     
                if self.pointingdirection == self.imagedirection:  
                    etv.visionlevel_correctimes[etv.level_now] += 1           
                    etv.level_now = 0.2 
                    self.setsize = 50
                else:
                    etv.lowest_wrongtimes += 1
                    self.setsize = 100
            elif etv.level_now == 0.2:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.3
                    self.setsize = 33                       
                else:
                    etv.level_now = 0.1
                    self.setsize = 100
            elif etv.level_now == 0.3:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.4
                    self.setsize = 25
                else:
                    etv.level_now = 0.2
                    self.setsize = 50
            elif etv.level_now == 0.4:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.5
                    self.setsize = 20
                else:
                    etv.level_now = 0.3
                    self.setsize = 33
            elif etv.level_now == 0.5:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.6
                    self.setsize = 17
                else:
                    etv.level_now = 0.4
                    self.setsize = 25
            elif etv.level_now == 0.6:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.7
                    self.setsize = 14
                else:
                    etv.level_now = 0.5
                    self.setsize = 20
            elif etv.level_now == 0.7:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.8
                    self.setsize = 12
                else:
                    etv.level_now = 0.6
                    self.setsize = 17
            elif etv.level_now == 0.8:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 0.9
                    self.setsize = 11
                else:
                    etv.level_now = 0.7
                    self.setsize = 14
            elif etv.level_now == 0.9:
                if self.pointingdirection == self.imagedirection:

                    etv.visionlevel_correctimes[etv.level_now] += 1
                    etv.level_now = 1.0
                    self.setsize = 10
                else:
                    etv.level_now = 0.8
                    self.setsize = 12
            elif etv.level_now == 1.0:
                if self.pointingdirection == self.imagedirection:
                    etv.visionlevel_correctimes[etv.level_now] += 1
                    self.setsize = 10
                else:
                    etv.level_now = 0.9
                    self.setsize = 11
            print(etv.visionlevel_correctimes)
            

    # check the vision level of two eyes
    def check_vision_level(self):
        global language_choice
        if self.round == 1:
            if etv.lowest_wrongtimes == 3:
                self.rightresult.setText("<0.1")
                if language_choice == 'English':
                    self.textEdit_3.setText("Round 2, please cover your right eye and point with your left hand.")       
                elif language_choice == 'Chinese':
                    self.textEdit_3.setText("第二輪，請遮住右眼，用左手指出缺口方向。")
                # initialize
                self.reset_and_init()
                self.testeye_now = 'left'
            for level, times in etv.visionlevel_correctimes.items():
                if times >= 3:
                    self.rightresult.setText(str(level))
                    self.righteye = level
                    if language_choice == 'English':
                        self.textEdit_3.setText("Round 2, please cover your right eye and point with your left hand.")
                    elif language_choice == 'Chinese':
                        self.textEdit_3.setText("第二輪，請遮住右眼，用左手指出缺口方向.")
                    # initialize
                    self.reset_and_init()
                    self.testeye_now = 'left'
        elif self.round == 2:    
            if etv.lowest_wrongtimes == 3:
                self.leftresult.setText("<0.1")
                self.hide_all()
                self.mytimer.stop()
                self.pointstart = False
                self.tableWidget.setVisible(True)
            for level, times in etv.visionlevel_correctimes.items():
                if times >= 3:
                    self.leftresult.setText(str(level))
                    self.lefteye = level
                    self.hide_all()
                    self.mytimer.stop()
                    self.pointstart = False
                    self.tableWidget.setVisible(True)

        

    # function for the camera
    def opencv(self):
        global language_choice
        self.cap = cv2.VideoCapture(0)

        mphands = mp.solutions.hands
        hands = mphands.Hands()
        
        mp_face_detection = mp.solutions.face_detection
        
        mpdraw = mp.solutions.drawing_utils
        handLmsStyle = mpdraw.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=2)
        handConStyle = mpdraw.DrawingSpec(color=(0, 255, 0), thickness=10, circle_radius=2)

        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            exit()
        else:
            self.update_message_signal.emit("Please choose your language and device.")
            self.stop_gif_signal.emit(True)
            

        # loop for the gesture recognition
        while self.ocv == True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # adapt the information of the frame
            frame = cv2.resize(frame, (800, 600))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # flip the frame
            frame = cv2.flip(frame, 1)
          
            result = hands.process(frame)

            imgheight = frame.shape[0]
            imgwidth = frame.shape[1]

            # face detection, get the distance between eyes
            if self.teststart == False:
                with mp_face_detection.FaceDetection(min_detection_confidence=0.6) as face_detection:
                    result_face = face_detection.process(frame)
                    if result_face.detections:
                        for detection in result_face.detections:
                            lefteye = int(detection.location_data.relative_keypoints[1].x * imgwidth), int(detection.location_data.relative_keypoints[1].y * imgheight)
                            righteye = int(detection.location_data.relative_keypoints[0].x * imgwidth), int(detection.location_data.relative_keypoints[0].y * imgheight)
                            self.eye_xdistance = lefteye[0] - righteye[0]
                            self.update_distance_info_signal.emit(True)
            
            if result.multi_hand_landmarks:
                for hand_idx, handLms in enumerate(result.multi_hand_landmarks):
                    # get the handness 
                    handness_label = "Left" if result.multi_handedness[hand_idx].classification[0].label == "Left" else "Right"  

                    # the information of every fingers
                    # thumb
                    thumb_tip = (handLms.landmark[4].x * imgwidth, handLms.landmark[4].y * imgheight)
                    thumb_base = (handLms.landmark[2].x * imgwidth, handLms.landmark[2].y * imgheight)
                    thumb_length = int(((thumb_tip[0] - thumb_base[0])**2 + (thumb_tip[1] - thumb_base[1])**2)**0.5)
                    horizental_distance_thumb = int(thumb_tip[0] - thumb_base[0])
                    vertical_distance_thumb = int(thumb_tip[1] - thumb_base[1])
                    
                    # index
                    index_finger_tip = (handLms.landmark[8].x * imgwidth, handLms.landmark[8].y * imgheight)
                    index_finger_base = (handLms.landmark[5].x * imgwidth, handLms.landmark[5].y * imgheight)   
                    index_length = int(((index_finger_tip[0] - index_finger_base[0])**2 + (index_finger_tip[1] - index_finger_base[1])**2)**0.5)
                    horizental_distance_index = int(index_finger_tip[0] - index_finger_base[0])
                    vertical_distance_index = int(index_finger_tip[1] - index_finger_base[1])

                    # middle
                    middle_finger_tip = (handLms.landmark[12].x * imgwidth, handLms.landmark[12].y * imgheight) 
                    middle_finger_base = (handLms.landmark[9].x * imgwidth, handLms.landmark[9].y * imgheight)
                    middle_length = int(((middle_finger_tip[0] - middle_finger_base[0])**2 + (middle_finger_tip[1] - middle_finger_base[1])**2)**0.5)
                    horizental_distance_middle = int(middle_finger_tip[0] - middle_finger_base[0])
                    vertical_distance_middle = int(middle_finger_tip[1] - middle_finger_base[1])

                    # ring
                    ring_finger_tip = (handLms.landmark[16].x * imgwidth, handLms.landmark[16].y * imgheight)
                    ring_finger_base = (handLms.landmark[13].x * imgwidth, handLms.landmark[13].y * imgheight)
                    ring_length = int(((ring_finger_tip[0] - ring_finger_base[0])**2 + (ring_finger_tip[1] - ring_finger_base[1])**2)**0.5)
                    horizental_distance_ring = int(ring_finger_tip[0] - ring_finger_base[0])
                    vertical_distance_ring = int(ring_finger_tip[1] - ring_finger_base[1])

                    # pinky
                    pinky_finger_tip = (handLms.landmark[20].x * imgwidth, handLms.landmark[20].y * imgheight)
                    pinky_finger_base = (handLms.landmark[17].x * imgwidth, handLms.landmark[17].y * imgheight)
                    pinky_length = int(((pinky_finger_tip[0] - pinky_finger_base[0])**2 + (pinky_finger_tip[1] - pinky_finger_base[1])**2)**0.5)
                    horizental_distance_pinky = int(pinky_finger_tip[0] - pinky_finger_base[0])
                    vertical_distance_pinky = int(pinky_finger_tip[1] - pinky_finger_base[1])


                    # Distance between thumb and index finger tip
                    distance_thumb_index = int(((thumb_tip[0] - index_finger_tip[0])**2 + (thumb_tip[1] - index_finger_tip[1])**2)**0.5)

                    # gesture YA for quit the application
                    if vertical_distance_index < -120 and vertical_distance_middle < -120 and vertical_distance_ring > -30 and vertical_distance_pinky > -30 and self.quitapp == True:
                        self.quit_signal.emit(True)   

                    # start when OK gesture
                    if distance_thumb_index < 30 and vertical_distance_middle < -100 and vertical_distance_ring < -100 and vertical_distance_pinky < -100 and self.teststart == False and self.eye_xdistance >= 60 and self.eye_xdistance <= 80:
                        self.teststart = True
                        self.startexam_signal.emit(True)
                        if language_choice == 'English':
                            self.update_message_signal.emit("Get ready, please cover left eye and point with your right hand.")
                        elif language_choice == 'Chinese':
                            self.update_message_signal.emit("準備好了嗎？請遮住左眼，用右手指出缺口方向。")  

                    # gesture for choosing the language and the device
                    if self.teststart == False :
                        if self.column == 'left':
                            if horizental_distance_index > 100:
                                self.column = 'right'
                                self.switch_rightcolumn_signal.emit(True)
                        elif self.column == 'right':
                            if horizental_distance_index < -90:
                                self.column = 'left'
                                self.switch_leftcolumn_signal.emit(True)
                                
                    if self.teststart == False:
                        if self.column == 'left':
                            if vertical_distance_index > 100:
                                self.choose_pushbutton4_signal.emit(True)
                            elif vertical_distance_index < -100:
                                self.choose_pushbutton3_signal.emit(True)
                        elif self.column == 'right':
                            if vertical_distance_index > 100:
                                self.choose_laptop_signal.emit(True)
                            elif vertical_distance_index < -100:
                                self.choose_desktop_signal.emit(True)                               

                    # gesture recognition, round 1 right hand
                    if index_length > 50 and self.pointstart == True:
                        if (handness_label == "Right" and self.round == 1) or (handness_label == "Left" and self.round == 2):
                            if vertical_distance_index < -80:
                                self.pointingdirection = 'up'
                                self.show_arrow_signal.emit('up')
                            elif vertical_distance_index > 80:
                                self.pointingdirection = 'down'
                                self.show_arrow_signal.emit('down')
                            elif horizental_distance_index < -50:
                                self.pointingdirection = 'left'
                                self.show_arrow_signal.emit('left')
                            elif horizental_distance_index > 50:
                                self.pointingdirection = 'right'
                                self.show_arrow_signal.emit('right')
                    elif index_length < 50 and self.pointstart == True:
                        self.pointingdirection = 'pass'
                        self.show_arrow_signal.emit('pass')


            # get the frame information
            height, width, channel = frame.shape
            bytesPerLine = channel * width

            # convert the frame to QImage
            qimg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qimg))
        
        self.cap.release()
        cv2.destroyAllWindows()

    # Add method to close the camera
    def close_camera(self):
        if self.cap is not None and self.cap.isOpened():
            self.ocv = False


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()

    main_ui = Ui_MainWindow()
    main_ui.setupUi(MainWindow)

    apply_stylesheet(app, theme='dark_cyan.xml') 

    vedio = threading.Thread(target=main_ui.opencv)
    vedio.start()
    MainWindow.showMaximized()

    # Connect the close event of the main window to close the camera
    MainWindow.closeEvent = main_ui.close_camera

    sys.exit(app.exec_())
