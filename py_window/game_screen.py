import csv
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMessageBox
from .game_screen_window import GameScreen_music, GameScreen_game


# 使用界面窗口
class GameScreen(GameScreen_music, GameScreen_game):

    # 窗口切换信号
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(GameScreen, self).__init__()
        self._startPos = None
        self._tracking = None
        self._endPos = None
        self.setWindowTitle("创意游戏平台")  # 设置窗口名
        # 连接按钮
        self.connecter()
        # 用户名及身份设置：从remember文件中读取
        self.username = ""
        self.usertype = ""
        self.remembered_path = 'remembered_account.csv'  # 记住密码的文件相对地址
        self.account_init()
        # 界面初始化(根据用户身份)
        self.ui_init()
        # 权限管控
        self.account_permission()

    # 权限管控：根据用户身份显示不同页面
    def account_permission(self):
        self.listWidget.clear()
        user_list = ["音乐", "游戏"]
        user_admin_list = ["用户管理"]
        music_admin_list = ["音乐管理", "音乐下载"]
        game_admin_list = ["游戏管理"]
        model_admin_list = []
        root_list = ["音乐", "游戏", "音乐管理", "音乐下载", "游戏管理", "用户管理", "权限管理"]
        if self.usertype == "普通用户":
            self.listWidget.addItems(user_list)
        elif self.usertype == "用户管理员":
            self.listWidget.addItems(user_admin_list)
        elif self.usertype == "音乐管理员":
            self.listWidget.addItems(music_admin_list)
        elif self.usertype == "游戏管理员":
            self.listWidget.addItems(game_admin_list)
        elif self.usertype == "模型管理员":
            self.listWidget.addItems(model_admin_list)
        else:
            self.listWidget.addItems(root_list)
        # 设置listWidget当前选中条目为列表第1项
        self.listWidget.setCurrentItem(self.listWidget.item(0))

    # 账户信息初始化：设置用户名和用户类型
    def account_init(self):
        with open(self.remembered_path, "rt", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.username = row[0]
                self.usertype = row[3]
        csvfile.close()
        # 用户名与身份的界面初始化
        self.label_username.setText(self.username)
        self.label_usershuxing.setText(self.usertype)

    # 界面初始化
    def ui_init(self):
        # 隐藏框
        self.setWindowFlags(Qt.FramelessWindowHint)  # 隐藏标题栏
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置背景透明
        # 初始化系统初始界面
        self.widget_musics.hide()
        self.widget_games.hide()
        self.widget_users.hide()
        self.widget_quanxians.hide()
        self.widget_musics_management.hide()
        self.widget_musics_download.hide()
        self.widget_games_management.hide()
        if self.usertype == "普通用户":
            self.widget_musics.show()
        elif self.usertype == "用户管理员":
            self.widget_users.show()
        elif self.usertype == "音乐管理员":
            self.widget_musics_management.show()
        elif self.usertype == "游戏管理员":
            self.widget_games_management.show()
        elif self.usertype == "模型管理员":
            pass
        elif self.usertype == "系统管理员":
            self.widget_musics.show()

    # 连接按钮和对应的函数
    def connecter(self):
        self.listWidget.itemClicked.connect(self.onClickedListWidget)
        self.pushButton_backToStart.clicked.connect(self.back)
        pass

    # 列表切换按钮：用于切换主界面的不同widget
    def onClickedListWidget(self, item):
        text = item.text()
        self.widget_games.hide()
        self.widget_users.hide()
        self.widget_quanxians.hide()
        self.widget_musics.hide()
        self.widget_musics_management.hide()
        self.widget_musics_download.hide()
        self.widget_games_management.hide()
        self.player.pause()
        if text == "音乐":
            self.music_init()
            self.widget_musics.show()
        if text == "游戏":
            self.gameWidget_init()
            self.widget_games.show()
        if text == "用户管理":
            self.widget_users.show()
        if text == "权限管理":
            self.widget_quanxians.show()
        if text == "音乐管理":
            self.widget_musics_management.show()
        if text == "音乐下载":
            self.widget_musics_download.show()
        if text == "游戏管理":
            self.widget_games_management.show()
        print(text)

    # 返回登陆页面按钮
    def back(self):
        reply = QMessageBox.question(self, '提示', '确认退出？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 接收到确认关闭信号之后回到登陆页面
            self.switch_window.emit()
        else:
            pass

    # 重写移动事件——用控件拖重写鼠标事件
    # 重写鼠标移动事件
    def mouseMoveEvent(self, e: QMouseEvent):
        if self._tracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    # 重写鼠标点击事件
    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._startPos = QPoint(e.x(), e.y())
            self._tracking = True

    # 重写鼠标释放事件
    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._tracking = False
            self._startPos = None
            self._endPos = None
