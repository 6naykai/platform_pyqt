import csv
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from py_window import Login, Verify, GameScreen


# 窗口控制类——用于控制窗口切换
class Controller:
    def __init__(self):
        self.verify = None
        self.login = None
        self.gameScreen = None
        self.usertype = None
        self.remembered_path = 'remembered_account.csv'  # 记住密码的文件相对地址

    # 显示登陆与注册窗口
    def show_login(self):
        self.login = Login()
        if self.gameScreen:
            self.gameScreen.close()
        self.login.switch_window.connect(self.identify_Administrator_User)
        self.login.show()

    # 区分管理员与用户：若为管理员直接进入主页面，若为用户则进行验证
    def identify_Administrator_User(self):
        # 从remember文件中读取用户类型
        with open(self.remembered_path, "rt", encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[3] == "普通用户":
                    self.verify = Verify()
                    self.login.close()
                    self.verify.switch_window.connect(self.show_gameScreen)
                    self.verify.show()
                    csvfile.close()
                    return
                else:
                    self.show_gameScreen()
                    csvfile.close()
                    return

    # 显示GamingPlatform主页面
    def show_gameScreen(self):
        self.gameScreen = GameScreen()
        if self.login:
            self.login.close()
        if self.verify:
            self.verify.close()
        # 若收到返回信号则回到登陆页面
        self.gameScreen.switch_window.connect(self.show_login)
        self.gameScreen.show()


def main():
    # 创建应用
    app = QApplication(sys.argv)
    # 设置窗口icon
    app.setWindowIcon(QIcon('pic/favicon.ico'))
    # 控制窗口切换
    controller = Controller()
    controller.show_login()
    # 退出应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
