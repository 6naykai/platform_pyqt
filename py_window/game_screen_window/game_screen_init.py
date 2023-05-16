from UI.UI_gamescreen import Ui_MainWindow


# 使用界面窗口：初始化类
class GameScreen_init(Ui_MainWindow):
    def __init__(self):
        super(GameScreen_init, self).__init__()
        self.setupUi(self)  # 引入UI界面
