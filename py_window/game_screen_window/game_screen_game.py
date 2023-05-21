import os
import re
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from .game_screen_init import GameScreen_init
from util import MyPost, game_storePath, downloadThread
import threading


# 通过路径启动exe游戏
def runGame(gamePath):
    def runExe():
        # os.system(gamePath)
        subprocess.Popen([gamePath])
    return runExe


# 使用界面窗口：游戏界面类
class GameScreen_game(GameScreen_init, QMainWindow):
    def __init__(self):
        super(GameScreen_game, self).__init__()
        # 前端post设置
        self.post_gameInit = MyPost('/user/gameInit')
        # 根据游戏名称,记录游戏后端路径和游戏下载状态值
        self.gamesDict = {}  # 记录已创建控件的游戏和游戏下载路径,再次post的时候不再创建
        # 当前游戏
        # 游戏界面显示初始化
        self.gameWidget_init()
        # 连接已创建子控件游戏的按钮函数
        self.connecter_game()

    # 更新下载进度显示
    def downloadJindu_change(self, gameName):
        def jindu_change():
            if self.gamesDict[gameName][1]:
                return
            elif self.downloadThread.proess < 10:
                exec('self.label_{}_jindu.setText("{}")'.format(gameName, "  {}%".format(self.downloadThread.proess)))
            elif self.downloadThread.proess < 100:
                exec('self.label_{}_jindu.setText("{}")'.format(gameName, " {}%".format(self.downloadThread.proess)))
            else:
                exec('self.label_{}_jindu.setText("{}")'.format(gameName, "{}%".format(self.downloadThread.proess)))
                exec('self.label_{}_tishi.setText("{}")'.format(gameName, "下载完成"))
                exec('self.pushButton_game_{}.setStyleSheet("QPushButton{}QPushButton:pressed{}")'.format(gameName,
                                                                                                          '{background-color:rgb(214, 244, 249);border-radius:20px;border-image: url(:/icons/icons/play_game.png);}',
                                                                                                          '{background-color:rgb(103, 216, 217);padding-left:3px;padding-top:3px;}'))
                gamePath = game_storePath + gameName + '.exe'
                # exec('self.pushButton_game_{}.clicked.connect(lambda: runGame("{}"))'.format(gameName, gamePath))
                self.gamesDict[gameName] = [gamePath, True]
        return jindu_change

    # 通过路径下载exe游戏,已采用多线程处理(若已下载,则运行游戏)
    def downloadGame(self, gameName):
        # 定义触发函数
        def down():
            # gamePath_bendi = game_storePath + gameName + '.exe'
            # 若游戏已下载,则启动(已增加多线程)
            if self.gamesDict[gameName][1]:
                new_thread = threading.Thread(target=runGame(self.gamesDict[gameName][0]))
                new_thread.start()
                # os.system(self.gamesDict[gameName][0])
            # 若游戏未下载,则从后端下载
            else:
                # *********要进行路径路由转化*******
                gamePath = self.gamesDict[gameName][0].replace('/', '\\')
                postExtendPath = '/user/gameDownload/' + gamePath
                post_downloadGame = MyPost(postExtendPath)
                the_filesize = post_downloadGame.getContentLength()
                the_filepath = game_storePath + gameName + '.exe'
                the_fileobj = open(the_filepath, 'wb')
                #### 创建下载线程
                self.downloadThread = downloadThread(post_downloadGame.url, the_filesize, the_fileobj, buffer=10240)
                exec('self.label_{}_tishi.setText("{}")'.format(gameName, "游戏正在下载中，请不要退出"))
                exec('self.downloadThread.download_proess_signal.connect(self.downloadJindu_change("{}"))'.format(
                    gameName,
                    gameName))
                exec('self.downloadThread.download_proess_signal.connect(self.progressBar__{}.setValue)'.format(
                    gameName))
                # 设置游戏按键icon
                exec('self.pushButton_game_{}.setStyleSheet("QPushButton{}QPushButton:pressed{}")'.format(gameName,
                                                                                                          '{background-color:rgb(214, 244, 249);border-radius:20px;border-image: url(:/icons/icons/下载中.png);}',
                                                                                                          '{background-color:rgb(103, 216, 217);padding-left:3px;padding-top:3px;}'))
                self.downloadThread.start()

        return down

    # 连接按钮和对应的函数
    def connecter_game(self):
        for gameName, gameDataList in self.gamesDict.items():
            if gameDataList[1]:
                gamePath = game_storePath + gameName + '.exe'
                self.gamesDict[gameName] = [gamePath, True]
                eval('self.pushButton_game_{}.clicked.connect({})'.format(gameName,
                                                                          "self.downloadGame('{}')".format(
                                                                              gameName)))
                # exec('self.pushButton_game_{}.clicked.connect(lambda: runGame("{}"))'.format(gameName, gamePath))
            else:
                gamePath = gameDataList[0]
                self.gamesDict[gameName] = [gamePath, False]
                eval('self.pushButton_game_{}.clicked.connect({})'.format(gameName,
                                                                          "self.downloadGame('{}')".format(
                                                                              gameName)))

    # 根据数据库中是否添加游戏入库信息来显示游戏widget
    def gameWidget_init(self):
        # 获取前端游戏资源存储路径下的所有游戏路径和所有游戏名称
        gamesPath = os.listdir(game_storePath)
        gamesName = []
        for gamePath in gamesPath:
            # re.findall正则获取前端游戏路径对应的游戏名称
            game_name = re.findall(r'(.+?)\.exe', re.findall(r'[^\\/:*?"<>|\r\n]+$', gamePath)[0])[0]
            gamesName.append(game_name)
        # 根据后端具体设置,来设置前端游戏页面内容
        response = self.post_gameInit.response_json()
        for gameName_flask, gamePath_flask in response.items():
            # re.findall正则获取游戏uuid
            gameUuid = re.findall(r'(.+?)\.exe', re.findall(r'[^\\/:*?"<>|\r\n]+$', gamePath_flask)[0])[0]
            # print(gameUuid)
            gameUuid = gameUuid.replace('-', '_')
            # print(gameUuid)
            # 若字典中存在键,则跳过
            if gameUuid in self.gamesDict:
                continue
            if gameName_flask in gamesName:
                self.createGameUI_AlreadyDownload(gameUuid, gameName_flask)
                self.gamesDict[gameUuid] = [gamePath_flask, True]
            else:
                self.createGameUI_NotDownload(gameUuid, gameName_flask)
                self.gamesDict[gameUuid] = [gamePath_flask, False]
        # self.createGameUI_NotDownload("game101", "五子棋")
        # self.createGameUI_AlreadyDownload("game100", "aaa")
        self.hide_oldWidget()

    def hide_oldWidget(self):
        for i in range(11):
            exec('self.widget_game_{}.hide()'.format(i))
        self.widget_wuziqi.hide()
        self.widget_niao.hide()
        self.widget_eluosi.hide()
        self.widget_zoumigong.hide()
        self.widget_xiaoxiaole.hide()
        self.widget_tuixiangzi.hide()
        self.widget_pingpang.hide()
        self.widget_feiji.hide()
        self.widget_tanchishe.hide()
        self.widget_2048.hide()

    def createGameUI_AlreadyDownload(self, gameNum, gameName):
        exec('self.widget_{} = QtWidgets.QWidget(self.scrollAreaWidgetContents_3)'.format(gameNum))
        exec('self.widget_{}.setMinimumSize(QtCore.QSize(0, 121))'.format(gameNum))
        exec('self.widget_{}.setMaximumSize(QtCore.QSize(16777215, 121))'.format(gameNum))
        exec('self.widget_{}.setStyleSheet(".QWidget{}\n)'.format(gameNum,
                                                                  '{"\n"background-color: qlineargradient(x1:0, y0:0, x2:1, y2:0,stop:0 rgb(225, 245, 249), stop:1 rgb(155, 230, 237));"\n"border-radius:20px;"\n"color: rgb(255, 255, 255);"\n"}"'))
        exec('self.widget_{}.setObjectName("widget_{}")'.format(gameNum, gameNum))
        exec('self.widget_{}_iconxia = QtWidgets.QWidget(self.widget_{})'.format(gameNum, gameNum))
        exec('self.widget_{}_iconxia.setGeometry(QtCore.QRect(24, 24, 113, 73))'.format(gameNum))
        exec('self.widget_{}_iconxia.setStyleSheet("")'.format(gameNum))
        exec('self.widget_{}_iconxia.setObjectName("widget_{}_iconxia")'.format(gameNum, gameNum))
        exec('self.label_{}_icon = QtWidgets.QLabel(self.widget_{}_iconxia)'.format(gameNum, gameNum))
        exec('self.label_{}_icon.setGeometry(QtCore.QRect(30, 5, 64, 64))'.format(gameNum))
        # 设置游戏icon
        exec('self.label_{}_icon.setStyleSheet("border-image: url(:/youxi/images/icon.ico);")'.format(gameNum))
        exec('self.label_{}_icon.setText("")'.format(gameNum, gameName))
        exec('self.label_{}_icon.setObjectName("label_{}_icon")'.format(gameNum, gameNum))
        exec('self.pushButton_game_{} = QtWidgets.QPushButton(self.widget_{})'.format(gameNum, gameNum))
        exec('self.pushButton_game_{}.setGeometry(QtCore.QRect(660, 30, 64, 64))'.format(gameNum))
        # 设置游戏按键icon
        exec('self.pushButton_game_{}.setStyleSheet("QPushButton{}QPushButton:pressed{}")'.format(gameNum,
                                                                                                  '{background-color:rgb(214, 244, 249);border-radius:20px;border-image: url(:/icons/icons/play_game.png);}',
                                                                                                  '{background-color:rgb(103, 216, 217);padding-left:3px;padding-top:3px;}'))
        exec('self.pushButton_game_{}.setText("")'.format(gameNum))
        exec('self.pushButton_game_{}.setObjectName("pushButton_game_{}")'.format(gameNum, gameNum))
        exec('self.layoutWidget1 = QtWidgets.QWidget(self.widget_{})'.format(gameNum))
        exec('self.layoutWidget1.setGeometry(QtCore.QRect(162, 25, 481, 72))')
        exec('self.layoutWidget1.setObjectName("layoutWidget1")')
        exec('self.horizontalLayout_{} = QtWidgets.QHBoxLayout(self.layoutWidget1)'.format(gameNum))
        exec('self.horizontalLayout_{}.setContentsMargins(0, 0, 0, 0)'.format(gameNum))
        exec('self.horizontalLayout_{}.setObjectName("horizontalLayout_{}")'.format(gameNum, gameNum))
        exec('self.verticalLayout_{} = QtWidgets.QVBoxLayout()'.format(gameNum))
        exec('self.verticalLayout_{}.setSpacing(2)'.format(gameNum))
        exec('self.verticalLayout_{}.setObjectName("verticalLayout_{}")'.format(gameNum, gameNum))
        exec('self.label_{} = QtWidgets.QLabel(self.layoutWidget1)'.format(gameNum))
        exec('font = QtGui.QFont()')
        exec('font.setPointSize(16)')
        exec('font.setBold(True)\nfont.setWeight(75)\nself.label_{}.setFont(font)'.format(gameNum))
        exec('self.label_{}.setStyleSheet("color: rgb(22, 54, 53);text-align:centre;")'.format(gameNum))
        exec('self.label_{}.setAlignment(QtCore.Qt.AlignCenter)'.format(gameNum))
        exec('self.label_{}.setObjectName("label_{}")'.format(gameNum, gameNum))
        # 设置游戏名称
        exec('self.label_{}.setText("{}")'.format(gameNum, gameName))
        exec('self.verticalLayout_{}.addWidget(self.label_{})'.format(gameNum, gameNum))
        exec('self.label_{}_tishi = QtWidgets.QLabel(self.layoutWidget1)'.format(gameNum))
        exec('font = QtGui.QFont()\nfont.setBold(False)\nfont.setWeight(50)\nself.label_{}_tishi.setFont(font)'.format(
            gameNum))
        exec('self.label_{}_tishi.setStyleSheet("color: rgb(22, 54, 53)")'.format(gameNum))
        exec('self.label_{}_tishi.setObjectName("label_{}_tishi")'.format(gameNum, gameNum))
        # 设置提示信息
        exec('self.label_{}_tishi.setText("{}")'.format(gameNum, "下载完成"))
        exec('self.verticalLayout_{}.addWidget(self.label_{}_tishi)'.format(gameNum, gameNum))
        exec('self.progressBar__{} = QtWidgets.QProgressBar(self.layoutWidget1)'.format(gameNum))
        exec('self.progressBar__{}.setStyleSheet("QProgressBar::chunk {}QProgressBar{}")'.format(gameNum,
                                                                                                 '{border-top-left-radius:8px;border-bottom-left-radius:8px;background-color: rgb(103, 216, 217);}',
                                                                                                 '{border-radius:8px;background-color: rgb(223, 223, 223);}'))
        # 设置下载进度值
        exec('self.progressBar__{}.setProperty("value", 100)'.format(gameNum))
        exec('self.progressBar__{}.setTextVisible(False)'.format(gameNum))
        exec('self.progressBar__{}.setObjectName("progressBar__{}")'.format(gameNum, gameNum))
        exec('self.verticalLayout_{}.addWidget(self.progressBar__{})'.format(gameNum, gameNum))
        exec('self.horizontalLayout_{}.addLayout(self.verticalLayout_{})'.format(gameNum, gameNum))
        exec('self.label_{}_jindu = QtWidgets.QLabel(self.layoutWidget1)'.format(gameNum))
        exec('font = QtGui.QFont()\nfont.setPointSize(17)\nfont.setBold(True)\nfont.setWeight(75)')
        exec('self.label_{}_jindu.setFont(font)'.format(gameNum))
        exec('self.label_{}_jindu.setStyleSheet("color: rgb(43, 101, 103);")'.format(gameNum))
        exec(
            'self.label_{}_jindu.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)'.format(
                gameNum))
        exec('self.label_{}_jindu.setObjectName("label_{}_jindu")'.format(gameNum, gameNum))
        # 设置进度值
        exec('self.label_{}_jindu.setText("{}")'.format(gameNum, "100%"))
        exec('self.horizontalLayout_{}.addWidget(self.label_{}_jindu)'.format(gameNum, gameNum))
        exec('self.verticalLayout_15.addWidget(self.widget_{})'.format(gameNum))

    def createGameUI_NotDownload(self, gameNum, gameName):
        exec('self.widget_{} = QtWidgets.QWidget(self.scrollAreaWidgetContents_3)'.format(gameNum))
        exec('self.widget_{}.setMinimumSize(QtCore.QSize(0, 121))'.format(gameNum))
        exec('self.widget_{}.setMaximumSize(QtCore.QSize(16777215, 121))'.format(gameNum))
        exec('self.widget_{}.setStyleSheet(".QWidget{}\n)'.format(gameNum,
                                                                  '{"\n"background-color: qlineargradient(x1:0, y0:0, x2:1, y2:0,stop:0 rgb(225, 245, 249), stop:1 rgb(155, 230, 237));"\n"border-radius:20px;"\n"color: rgb(255, 255, 255);"\n"}"'))
        exec('self.widget_{}.setObjectName("widget_{}")'.format(gameNum, gameNum))
        exec('self.widget_{}_iconxia = QtWidgets.QWidget(self.widget_{})'.format(gameNum, gameNum))
        exec('self.widget_{}_iconxia.setGeometry(QtCore.QRect(24, 24, 113, 73))'.format(gameNum))
        exec('self.widget_{}_iconxia.setStyleSheet("")'.format(gameNum))
        exec('self.widget_{}_iconxia.setObjectName("widget_{}_iconxia")'.format(gameNum, gameNum))
        exec('self.label_{}_icon = QtWidgets.QLabel(self.widget_{}_iconxia)'.format(gameNum, gameNum))
        exec('self.label_{}_icon.setGeometry(QtCore.QRect(30, 5, 64, 64))'.format(gameNum))
        # 设置游戏icon
        exec('self.label_{}_icon.setStyleSheet("border-image: url(:/youxi/images/icon.ico);")'.format(gameNum))
        exec('self.label_{}_icon.setText("")'.format(gameNum, gameName))
        exec('self.label_{}_icon.setObjectName("label_{}_icon")'.format(gameNum, gameNum))
        exec('self.pushButton_game_{} = QtWidgets.QPushButton(self.widget_{})'.format(gameNum, gameNum))
        exec('self.pushButton_game_{}.setGeometry(QtCore.QRect(660, 30, 64, 64))'.format(gameNum))
        # 设置游戏按键icon
        exec('self.pushButton_game_{}.setStyleSheet("QPushButton{}QPushButton:pressed{}")'.format(gameNum,
                                                                                                  '{background-color:rgb(214, 244, 249);border-radius:20px;border-image: url(:/icons/icons/下载.png);}',
                                                                                                  '{background-color:rgb(103, 216, 217);padding-left:3px;padding-top:3px;}'))
        exec('self.pushButton_game_{}.setText("")'.format(gameNum))
        exec('self.pushButton_game_{}.setObjectName("pushButton_game_{}")'.format(gameNum, gameNum))
        exec('self.layoutWidget1 = QtWidgets.QWidget(self.widget_{})'.format(gameNum))
        exec('self.layoutWidget1.setGeometry(QtCore.QRect(162, 25, 481, 72))')
        exec('self.layoutWidget1.setObjectName("layoutWidget1")')
        exec('self.horizontalLayout_{} = QtWidgets.QHBoxLayout(self.layoutWidget1)'.format(gameNum))
        exec('self.horizontalLayout_{}.setContentsMargins(0, 0, 0, 0)'.format(gameNum))
        exec('self.horizontalLayout_{}.setObjectName("horizontalLayout_{}")'.format(gameNum, gameNum))
        exec('self.verticalLayout_{} = QtWidgets.QVBoxLayout()'.format(gameNum))
        exec('self.verticalLayout_{}.setSpacing(2)'.format(gameNum))
        exec('self.verticalLayout_{}.setObjectName("verticalLayout_{}")'.format(gameNum, gameNum))
        exec('self.label_{} = QtWidgets.QLabel(self.layoutWidget1)'.format(gameNum))
        exec('font = QtGui.QFont()')
        exec('font.setPointSize(16)')
        exec('font.setBold(True)\nfont.setWeight(75)\nself.label_{}.setFont(font)'.format(gameNum))
        exec('self.label_{}.setStyleSheet("color: rgb(22, 54, 53);text-align:centre;")'.format(gameNum))
        exec('self.label_{}.setAlignment(QtCore.Qt.AlignCenter)'.format(gameNum))
        exec('self.label_{}.setObjectName("label_{}")'.format(gameNum, gameNum))
        # 设置游戏名称
        exec('self.label_{}.setText("{}")'.format(gameNum, gameName))
        exec('self.verticalLayout_{}.addWidget(self.label_{})'.format(gameNum, gameNum))
        exec('self.label_{}_tishi = QtWidgets.QLabel(self.layoutWidget1)'.format(gameNum))
        exec('font = QtGui.QFont()\nfont.setBold(False)\nfont.setWeight(50)\nself.label_{}_tishi.setFont(font)'.format(
            gameNum))
        exec('self.label_{}_tishi.setStyleSheet("color: rgb(22, 54, 53)")'.format(gameNum))
        exec('self.label_{}_tishi.setObjectName("label_{}_tishi")'.format(gameNum, gameNum))
        # 设置提示信息
        exec('self.label_{}_tishi.setText("{}")'.format(gameNum, "游戏未下载"))
        exec('self.verticalLayout_{}.addWidget(self.label_{}_tishi)'.format(gameNum, gameNum))
        exec('self.progressBar__{} = QtWidgets.QProgressBar(self.layoutWidget1)'.format(gameNum))
        exec('self.progressBar__{}.setStyleSheet("QProgressBar::chunk {}QProgressBar{}")'.format(gameNum,
                                                                                                 '{border-top-left-radius:8px;border-bottom-left-radius:8px;background-color: rgb(103, 216, 217);}',
                                                                                                 '{border-radius:8px;background-color: rgb(223, 223, 223);}'))
        # 设置下载进度值
        exec('self.progressBar__{}.setProperty("value", 0)'.format(gameNum))
        exec('self.progressBar__{}.setTextVisible(False)'.format(gameNum))
        exec('self.progressBar__{}.setObjectName("progressBar__{}")'.format(gameNum, gameNum))
        exec('self.verticalLayout_{}.addWidget(self.progressBar__{})'.format(gameNum, gameNum))
        exec('self.horizontalLayout_{}.addLayout(self.verticalLayout_{})'.format(gameNum, gameNum))
        exec('self.label_{}_jindu = QtWidgets.QLabel(self.layoutWidget1)'.format(gameNum))
        exec('font = QtGui.QFont()\nfont.setPointSize(17)\nfont.setBold(True)\nfont.setWeight(75)')
        exec('self.label_{}_jindu.setFont(font)'.format(gameNum))
        exec('self.label_{}_jindu.setStyleSheet("color: rgb(43, 101, 103);")'.format(gameNum))
        exec(
            'self.label_{}_jindu.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)'.format(
                gameNum))
        exec('self.label_{}_jindu.setObjectName("label_{}_jindu")'.format(gameNum, gameNum))
        # 设置进度值
        exec('self.label_{}_jindu.setText("{}")'.format(gameNum, "  0%"))
        exec('self.horizontalLayout_{}.addWidget(self.label_{}_jindu)'.format(gameNum, gameNum))
        exec('self.verticalLayout_15.addWidget(self.widget_{})'.format(gameNum))
