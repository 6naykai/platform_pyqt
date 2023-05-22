import re
from copy import copy
# 下面这个必须导入，因为exec中用到了
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QMainWindow, QHeaderView, QFileDialog, QMessageBox
from util import MyPost
from .game_screen_init import GameScreen_init
from .game_screen_game import GameScreen_game


# 使用界面窗口：游戏管理类
class GameScreen_gameManagement(GameScreen_game):
    def __init__(self):
        super(GameScreen_gameManagement, self).__init__()
        # 前端post设置
        self.post_gamesSelectGamePath = MyPost('/gameAdmin/gamesSelectGamePath')
        self.post_gamesSelectIsAdded = MyPost('/gameAdmin/gamesSelectIsAdded')
        self.post_gameUpdateIsAdded = MyPost('/gameAdmin/gameUpdateIsAdded')
        self.post_gameDelete = MyPost('/gameAdmin/gameDelete')
        self.post_gameUpload = MyPost('/gameAdmin/gameUpload')
        # 游戏表的设置
        self.header_game = [""]  # 列表头,用于显示数据对应的行序号
        self.saveList_game = []  # 游戏表的数据存储列表(数据库中内容)
        self.displayList_game = []  # 游戏表的数据显示列表(表格中内容)
        self.tableHeader_init_game()  # 初始化表头
        self.data_init_game()  # 初始化数据
        # 连接信号
        self.connecter_gameManagement()

    # 连接按钮和对应的函数
    def connecter_gameManagement(self):
        self.pushButton_save_game.clicked.connect(self.save_game)
        self.pushButton_delete_game.clicked.connect(self.delete_game)
        self.pushButton_refresh_game.clicked.connect(self.refresh_game)
        self.pushButton_add_game.clicked.connect(self.add_game)
        self.table_game.itemChanged.connect(self._dataChanged_game)

    # 初始化表头和行列数
    def tableHeader_init_game(self):
        self.header_game = [""]  # 初始化列表头
        self.saveList_game = []  # 游戏表的数据存储列表(数据库中内容)
        self.displayList_game = []  # 游戏表的数据显示列表(表格中内容)
        # 设置表格有1行3列
        self.table_game.setColumnCount(3)  # 设置列数
        self.table_game.setRowCount(1)  # 设置行数
        # 设定“列标题”并将单元格设定为不可编辑
        gameName = QTableWidgetItem("游戏名称")
        gamePath = QTableWidgetItem("游戏路径")
        game_isAccretion = QTableWidgetItem("是否添加至游戏库")
        gameName.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        gamePath.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        game_isAccretion.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table_game.setItem(0, 0, gameName)
        self.table_game.setItem(0, 1, gamePath)
        self.table_game.setItem(0, 2, game_isAccretion)
        # 隐藏列标题
        self.table_game.horizontalHeader().setVisible(False)
        # 设置表格头的伸缩模式，也就是让表格铺满整个QTableWidget控件
        self.table_game.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # 初始化操作：即从数据库加载数据
    def data_init_game(self):
        # 获取sel语句的数据列表
        gamesPath = self.post_gamesSelectGamePath.response_json()
        gamesIsAdded = self.post_gamesSelectIsAdded.response_json()
        # 遍历数据字典
        data = []
        for gameName in gamesPath:
            file_path = gamesPath[gameName]
            # rfind获取游戏相对路径
            game_path = file_path[file_path.rfind('/', 0, file_path.rfind('/') - 1) + 1:]
            # print(game_path)
            item = (gameName, game_path, gamesIsAdded[gameName])
            data.append(item)
        # 遍历data列表
        # enumerate()函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
        for index, item in enumerate(data):
            self.game_newLine(index + 1, item=item)  # 表格新增1行
            self.displayList_game.append(item)  # 显示列表添加数据元组
        self.saveList_game = copy(self.displayList_game)
        self.update()

    # 表格新增一行函数
    def game_newLine(self, num, item=None, flag=False):
        """
        :param num: 在对应序号处的序号画空白行
        :param item: 输入为对应数据
        :param flag: 是否为新增数据
        """
        self.table_game.insertRow(num)
        _0 = QTableWidgetItem("")
        _0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _1 = QTableWidgetItem("")
        _1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _2 = QTableWidgetItem("")
        # 设置确认框true/false,默认为true,批量化生产子控件
        exec('self.checkBox_rukugame{} = QtWidgets.QCheckBox()'.format(num))
        exec('self.checkBox_rukugame{}.setChecked(True)'.format(num))
        exec('self.checkBox_rukugame{}.stateChanged.connect(self._dataChanged_game)'.format(num))
        if item is not None:
            _0.setText(str(item[0]))
            _1.setText(str(item[1]))
            # _2.setText(str(item[2]))
            # _2.setCheckState(Qt.Unchecked)
            # 根据数据库内容设置确认框默认值
            if str(item[2]) == "False":
                # _2.setCheckState(Qt.Unchecked)
                exec('self.checkBox_rukugame{}.setChecked(False)'.format(num))
            # 若为新增,则显示列表新增
            if flag:
                self.displayList_game.append(item)
        else:
            return  # 与添加游戏按钮关联(采用正则关联content,已解决)
        self.table_game.setItem(num, 0, _0)
        self.table_game.setItem(num, 1, _1)
        self.table_game.setItem(num, 2, _2)
        exec('self.table_game.setCellWidget(num, 2, self.checkBox_rukugame{})'.format(num))
        self.header_game.append(str(num))
        self.table_game.setVerticalHeaderLabels(self.header_game)
        self.update()

    # 表格数据更改的函数
    def _dataChanged_game(self):
        """
        一旦检测到数据改变,则进行检查,
        选择添加新数据还是对原数据进行修改
        :return:
        """
        row_select = self.table_game.selectedItems()
        if len(row_select) == 0:
            return
        row = row_select[0].row()
        content = (self.table_game.item(row, 0).text(), self.table_game.item(row, 1).text(),
                   self.table_game.cellWidget(row, 2).isChecked())
        if row <= len(self.displayList_game):
            print("修改行", content)
            self.displayList_game[row - 1] = content
        else:
            print("最新行", content)
            self.displayList_game[row - 1] = content

    # 刷新表格函数
    def refresh_game(self):
        self.tableHeader_init_game()  # 初始化表头
        self.data_init_game()  # 初始化数据

    # 表格删除一行函数
    def delete_game(self):
        """
        若有选中行,点击删除后即可删除
        :return:
        """
        row_select = self.table_game.selectedItems()
        # 若没有选中行
        if len(row_select) == 0:
            return
        Id = row_select[0].row()
        print(self.displayList_game[Id - 1])
        if int(Id) <= len(self.displayList_game):
            print("删除一条数据")
            self.displayList_game.pop(Id - 1)
        self.header_game.pop()
        self.table_game.removeRow(row_select[0].row())
        self.table_game.setVerticalHeaderLabels(self.header_game)
        self.update()

    # 保存表格函数
    def save_game(self):
        """
        点击保存需要筛选出
        需要更新的数据
        需要删除的数据
        需要添加的数据
        """
        idList = [str(k[0]) for k in self.saveList_game]
        _idList = [str(k[0]) for k in self.displayList_game]
        print("点击保存")
        for item in self.displayList_game:
            if item not in self.saveList_game:
                print("存在修改数据")
                if item[0] not in idList:
                    print("insert game")
                else:
                    gameUpdatePath = self.post_gameUpdateIsAdded.response_json({'gameName': item[0],
                                                                                'newIsAdded': item[2]})["更新游戏路径"]
                    # re.findall正则获取游戏uuid
                    gameUuid = re.findall(r'(.+?)\.exe', re.findall(r'[^\\/:*?"<>|\r\n]+$', gameUpdatePath)[0])[0]
                    # print(gameUuid)
                    gameUuid = gameUuid.replace('-', '_')
                    # **首先判断是否已创建了子控件**
                    if gameUuid in self.gamesDict:
                        # 再判断是否显示
                        if item[2]:
                            exec('self.widget_{}.show()'.format(gameUuid))
                        else:
                            exec('self.widget_{}.hide()'.format(gameUuid))
                    else:
                        # 创建子控件
                        self.gameWidget_init()
                    print("update game", item)
        for item in self.saveList_game:
            if item[0] not in _idList:
                gamePath = self.post_gameDelete.response_json({'gameName': item[0]})["删除游戏路径"]
                # re.findall正则获取游戏uuid
                gameUuid = re.findall(r'(.+?)\.exe', re.findall(r'[^\\/:*?"<>|\r\n]+$', gamePath)[0])[0]
                # print(gameUuid)
                gameUuid = gameUuid.replace('-', '_')
                exec('self.widget_{}.hide()'.format(gameUuid))
                print("delete game", item)
        # self.saveList_game = copy(self.displayList_game)
        # 调用刷新按钮函数,更新save列表等
        self.refresh_game()

    # 表格新增一行函数
    def add_game(self):
        # 获取游戏文件路径
        file = QFileDialog.getOpenFileName(self, "请选择要添加的游戏文件", "games", "All Files (*)")
        print(file)
        if file == ('', ''):
            return  # 没取到文件则直接返回
        file_path = file[0]
        # re.findall正则获取游戏名称
        game_name = re.findall(r'(.+?)\.exe', re.findall(r'[^\\/:*?"<>|\r\n]+$', file_path)[0])[0]
        print(game_name)
        # # rfind获取游戏相对路径
        # game_path = file_path[file_path.rfind('/', 0, file_path.rfind('/') - 1) + 1:]
        # print(game_path)
        game_path = file[0]  # 使用绝对路径进行上传
        print(game_path)
        # 将游戏上传至后端
        upload_response = self.post_gameUpload.uploadFile_response(game_path, game_name, "exe")
        if upload_response["状态"] == "失败":
            QMessageBox.warning(self, "注意", upload_response["提示信息"])
        else:
            QMessageBox.information(self, "提示", upload_response["提示信息"])

        # # 添加一行游戏
        # content = (game_name, game_path, True)
        # self.table_game.setCurrentItem(None)
        # self.game_newLine(len(self.displayList_game) + 1, content, True)

        # 更新游戏显示界面
        self.gameWidget_init()
        # 调用刷新按钮函数,更新save列表等
        self.refresh_game()
