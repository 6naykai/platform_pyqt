import csv
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from UI.UI_login import Ui_MainWindow
from util import MyPost, mkcsv


# 登陆窗口类
class Login(Ui_MainWindow, QMainWindow):

    # 窗口切换信号
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(Login, self).__init__()
        self._tracking = None
        self._startPos = None
        self._endPos = None
        self.effect_shadow_pushButton_register = None
        self.effect_shadow_pushButton_login = None
        self.effect_shadow_label_2 = None
        self.effect_shadow_label = None
        self.setupUi(self)                  # 引入UI界面
        self.setWindowTitle("创意游戏平台")   # 设置窗口名
        self.connecter()                    # 连接按钮
        # 隐藏框
        self.setWindowFlags(Qt.FramelessWindowHint)     # 隐藏标题栏
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置背景透明
        self.widget_enroll.hide()                       # 隐藏注册页面
        # 添加阴影
        self.add_shadow()
        # 前端post处理
        self.post_login = MyPost('/user_table/login')
        self.post_register = MyPost('/user_table/register')
        # 记住密码功能实现
        self.remembered_account = []    # 载入记住密码的列表
        self.remembered_path = 'remembered_account.csv'   # 记住密码的文件相对地址
        self.remembered_init()  # 记住密码界面初始化

    # 连接按钮和对应的函数
    def connecter(self):
        self.pushButton_landing.clicked.connect(self.landing)           # 登陆页面
        self.pushButton_enroll.clicked.connect(self.enroll)             # 注册页面
        self.pushButton_login.clicked.connect(self.login)               # 登陆功能
        self.pushButton_register.clicked.connect(self.register)         # 注册功能

    # 显示登陆页面
    def landing(self):
        self.widget_enroll.hide()   # 隐藏注册页面
        # 注册页面切换按钮变灰
        self.pushButton_enroll.setStyleSheet(
            "border:none;"
            "color:rgb(186,186,186);"
        )
        # 登陆页面切换按钮变黑
        self.pushButton_landing.setStyleSheet(
            "border:none;"
            "color:black;"
        )
        self.widget_landing.show()  # 显示登陆页面

    # 显示注册页面
    def enroll(self):
        self.widget_landing.hide()  # 隐藏登陆页面
        # 登陆页面切换按钮变灰
        self.pushButton_landing.setStyleSheet(
            "border:none;"
            "color:rgb(186,186,186);"
        )
        # 注册页面切换按钮变黑
        self.pushButton_enroll.setStyleSheet(
            "border:none;"
            "color:black;"
        )
        self.widget_enroll.show()   # 显示注册页面
        # self.switch_window.emit()

    # 根据是否记住密码,在启动时显示账户信息
    def remembered_init(self):
        mkcsv(self.remembered_path)
        with open(self.remembered_path, "rt", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row is None:
                    return
                else:
                    if row[2] == 'True':
                        self.lineEdit_login_password.setText(row[1])
                        self.checkBox_rememberPassword.setChecked(True)
                    self.lineEdit_login_account.setText(row[0])

    # 将账户写入记住密码文件中的函数
    def write_remembered(self, account, password, remembered):
        with open(self.remembered_path, "w", newline='', encoding='utf-8-sig') as file:
            csv_writer = csv.writer(file, dialect="excel")
            cell = [account, password, remembered]
            csv_writer.writerow(cell)
        file.close()

    # 实现登陆功能
    def login(self):
        """
        登陆确认按钮出发函数,包括一些合法性的检测,账户信息的输入与记录
        """
        account = self.lineEdit_login_account.text()
        password = self.lineEdit_login_password.text()
        if str(account) == "":
            QMessageBox.warning(self, "注意", "账号不能为空")
        elif str(password) == "":
            QMessageBox.warning(self, "注意", "密码不能为空")
        else:
            response = self.post_login.response({"user_name": str(account), "user_secret": str(password)})
            if response["status"] == "成功":
                QMessageBox.information(self, "提示", "登陆成功")
                # 成功登陆后跳转到验证窗口
                self.switch_window.emit()
                # 将账户写入记住密码文件中
                self.write_remembered(account, password, self.checkBox_rememberPassword.isChecked())
                return  # 后续添加恢复账户可用输入错误机会(已实现,通过数据库进行隔离)
            else:
                # 若遍历完整个账户列表仍未查到该用户
                QMessageBox.warning(self, "注意", response['beizhu'])
            # 清空账户输入框和密码输入框
            self.lineEdit_login_account.clear()
            self.lineEdit_login_password.clear()

    # 实现注册功能
    def register(self):
        """
        注册确认按钮出发函数,包括一些合法性的检测,账户信息的输入与记录
        """
        # temp = {}       # 存放当前账户信息
        account = self.lineEdit_register_account.text()
        password = self.lineEdit_register_password.text()
        passwordConfirm = self.lineEdit_register_passwordConfirm.text()
        if str(account) == "":
            QMessageBox.warning(self, "注意", "账号不能为空!")
        elif str(password) == "":
            QMessageBox.warning(self, "注意", "密码不能为空!")
        elif password != passwordConfirm:
            QMessageBox.warning(self, "注意", "两次输入密码不一致!")
            self.lineEdit_register_password.clear()
            self.lineEdit_register_passwordConfirm.clear()
        else:
            response = self.post_register.response({"user_name": str(account), "user_secret": str(password)})
            if response["status"] == "成功":
                QMessageBox.information(self, "提示", "注册成功!")
            else:
                QMessageBox.information(self, "注意", "注册失败！请联系后端管理人员")
            # 注册成功则跳转回登陆页面,并清空注册框内容
            self.landing()
            self.lineEdit_register_account.clear()
            self.lineEdit_register_password.clear()
            self.lineEdit_register_passwordConfirm.clear()

    # 控件阴影添加
    def add_shadow(self):
        # label控件阴影添加
        self.effect_shadow_label = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow_label.setOffset(0, 0)                               # 偏移
        self.effect_shadow_label.setBlurRadius(25)                             # 阴影半径
        self.effect_shadow_label.setColor(Qt.gray)                             # 阴影颜色
        self.label.setGraphicsEffect(self.effect_shadow_label)                 # 将设置套用到label控件中
        # label_2控件阴影添加
        self.effect_shadow_label_2 = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow_label_2.setOffset(0, 0)
        self.effect_shadow_label_2.setBlurRadius(25)
        self.effect_shadow_label_2.setColor(Qt.gray)
        self.label_2.setGraphicsEffect(self.effect_shadow_label_2)
        # pushButton_login控件阴影添加
        self.effect_shadow_pushButton_login = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow_pushButton_login.setOffset(3, 3)                               # 偏移
        self.effect_shadow_pushButton_login.setBlurRadius(25)                             # 阴影半径
        self.effect_shadow_pushButton_login.setColor(Qt.gray)                             # 阴影颜色
        self.pushButton_login.setGraphicsEffect(self.effect_shadow_pushButton_login)      # 将设置套用到pushButton控件中
        # pushButton_register控件阴影添加
        self.effect_shadow_pushButton_register = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow_pushButton_register.setOffset(3, 3)
        self.effect_shadow_pushButton_register.setBlurRadius(25)
        self.effect_shadow_pushButton_register.setColor(Qt.gray)
        self.pushButton_register.setGraphicsEffect(self.effect_shadow_pushButton_register)

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
