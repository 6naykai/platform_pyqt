from copy import copy
# 下面这个必须导入，因为exec中用到了
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QMainWindow, QHeaderView

from util import MyPost
from .game_screen_init import GameScreen_init


# 使用界面窗口：用户管理类
class GameScreen_user(GameScreen_init, QMainWindow):
    def __init__(self):
        super(GameScreen_user, self).__init__()
        # 前端post设置
        self.post_usersSelectPassword = MyPost('/userAdmin/usersSelectPassword')
        self.post_usersSelectFlag = MyPost('/userAdmin/usersSelectFlag')
        self.post_userInsert = MyPost('/userAdmin/userInsert')
        self.post_userUpdatePassword = MyPost('/userAdmin/userUpdatePassword')
        self.post_userUpdateForbidden = MyPost('/userAdmin/userUpdateForbidden')
        self.post_userDelete = MyPost('/userAdmin/userDelete')
        # 用户表设置
        self.header_user = [""]  # 列表头,用于显示数据对应的行序号
        self.saveList_user = []  # 数据存储列表(数据库中内容)
        self.displayList_user = []  # 数据显示列表(表格中内容)
        self.comboBox_list_user = ["True", "False"]
        self.UsertableHeader_init()  # 初始化表头
        self.Userdata_init()  # 初始化数据
        # 连接信号
        self.connecter_user()

    # 连接按钮和对应的函数
    def connecter_user(self):
        self.pushButton_save.clicked.connect(self.save_user)
        self.pushButton_delete.clicked.connect(self.delete_user)
        self.pushButton_refresh.clicked.connect(self.refresh_user)
        self.pushButton_add.clicked.connect(self.add_user)
        self.table.itemChanged.connect(self._dataChanged_user)

    # 初始化表头和行列数
    def UsertableHeader_init(self):
        self.header_user = [""]  # 初始化列表头
        self.saveList_user = []  # 数据存储列表(数据库中内容)
        self.displayList_user = []  # 数据显示列表(表格中内容)
        # 设置表格有1行5列
        self.table.setColumnCount(3)  # 设置列数
        self.table.setRowCount(1)  # 设置行数
        # 设定“列标题”并将单元格设定为不可编辑
        userName = QTableWidgetItem("用户名")
        passWord = QTableWidgetItem("密码")
        banFlag = QTableWidgetItem("封禁标志")
        userName.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        passWord.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        banFlag.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(0, 0, userName)
        self.table.setItem(0, 1, passWord)
        self.table.setItem(0, 2, banFlag)
        # 隐藏列标题
        self.table.horizontalHeader().setVisible(False)
        # 设置表格头的伸缩模式，也就是让表格铺满整个QTableWidget控件
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # 初始化操作：即从后端获取用户数据
    def Userdata_init(self):
        # 获取sel语句的数据字典
        usersPassword = self.post_usersSelectPassword.response_json()
        usersFlag = self.post_usersSelectFlag.response_json()
        # 遍历数据字典
        index = 0
        for userName in usersPassword:
            item = (userName, usersPassword[userName], usersFlag[userName])
            self.User_newLine(index + 1, item=item)  # 表格新增1行
            self.displayList_user.append(item)  # 显示列表添加数据元组
            index += 1
        self.saveList_user = copy(self.displayList_user)
        self.update()

    # 表格新增一行函数
    def User_newLine(self, num, item=None):
        """
        :param num: 在对应序号处的序号画空白行
        :param item: 输入为对应数据
        """
        if self.lineEdit_num.text() == "" and item is None:
            QMessageBox.warning(self, "注意", "输入用户名不能为空!")
            return
        # 遍历展示列表看是否有重名的,若有则添加失败
        for user in self.displayList_user:
            if user[0] == self.lineEdit_num.text():
                QMessageBox.warning(self, "注意", "输入用户名不能重复!")
                self.lineEdit_num.clear()
                return
        self.table.insertRow(num)
        _0 = QTableWidgetItem("")
        _0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _1 = QTableWidgetItem("")
        _2 = QTableWidgetItem("")
        # 设置选择框true/false,批量化生产子控件
        exec('self.comboBox_fengjin{} = QtWidgets.QComboBox()'.format(num))
        exec('self.comboBox_fengjin{}.addItems(self.comboBox_list_user)'.format(num))
        exec('self.comboBox_fengjin{}.currentIndexChanged.connect(self._dataChanged_user)'.format(num))
        # comboBox_fengjin = QtWidgets.QComboBox()
        # comboBox_fengjin.addItems(self.comboBox_list_user)
        if item is not None:
            _0.setText(str(item[0]))
            _1.setText(str(item[1]))
            _2.setText(str(item[2]))
            # 根据数据库内容设置选择框默认值
            if str(item[2]) == "True":
                exec('self.comboBox_fengjin{}.setCurrentIndex(0)'.format(num))
                # exec('self.comboBox_fengjin{}.setStyleSheet("QComboBox{color:#ee0000}")'.format(num))
                # comboBox_fengjin.setCurrentIndex(0)  # 设置默认值
                # comboBox_fengjin.setStyleSheet("QComboBox{color:#ee0000}")  # 禁用则标红
            else:
                exec('self.comboBox_fengjin{}.setCurrentIndex(1)'.format(num))
                # comboBox_fengjin.setCurrentIndex(1)
        else:
            _0.setText(self.lineEdit_num.text())
            exec('self.comboBox_fengjin{}.setCurrentIndex(1)'.format(num))
            # comboBox_fengjin.setCurrentIndex(1)
            content = (self.lineEdit_num.text(), None, False)
            self.displayList_user.append(content)
            self.lineEdit_num.clear()
        self.table.setItem(num, 0, _0)
        self.table.setItem(num, 1, _1)
        self.table.setItem(num, 2, _2)
        exec('self.table.setCellWidget(num, 2, self.comboBox_fengjin{})'.format(num))
        # self.table.setItem(num, 2, comboBox_fengjin)
        # self.table.setCellWidget(num, 2, comboBox_fengjin)
        self.header_user.append(str(num))
        self.table.setVerticalHeaderLabels(self.header_user)
        self.update()

    # def _comboBoxChanged_user(self, row):
    #     text = self.table.cellWidget(row, 2).currentText()
    #     self.table.item(row, 2).setText(text)

    # 表格数据更改的函数
    def _dataChanged_user(self):
        """
        一旦检测到数据改变,则进行检查,
        选择添加新数据还是对原数据进行修改
        :return:
        """
        row_select = self.table.selectedItems()
        if len(row_select) == 0:
            return
        row = row_select[0].row()
        content = (self.table.item(row, 0).text(), self.table.item(row, 1).text(),
                   self.table.cellWidget(row, 2).currentText())
        if row <= len(self.displayList_user):
            print("修改行", content)
            self.displayList_user[row - 1] = content
        else:
            print("最新行", content)
            self.displayList_user[row - 1] = content

    # 刷新表格函数
    def refresh_user(self):
        self.UsertableHeader_init()  # 初始化表头
        self.Userdata_init()  # 初始化数据

    # 表格删除一行函数
    def delete_user(self):
        """
        若有选中行,点击删除后即可删除
        :return:
        """
        row_select = self.table.selectedItems()
        # 若没有选中行
        if len(row_select) == 0:
            return
        Id = row_select[0].row()
        if int(Id) <= len(self.displayList_user):
            print("删除一条数据")
            self.displayList_user.pop(Id - 1)
        self.header_user.pop()
        self.table.removeRow(row_select[0].row())
        self.table.setVerticalHeaderLabels(self.header_user)
        self.update()

    # 保存表格函数
    def save_user(self):
        """
        点击保存需要筛选出
        需要更新的数据
        需要删除的数据
        需要添加的数据
        """
        idList = [str(k[0]) for k in self.saveList_user]
        _idList = [str(k[0]) for k in self.displayList_user]
        print("点击保存")
        for item in self.displayList_user:
            if item not in self.saveList_user:
                print("存在修改数据")
                # 添加用户
                if item[0] not in idList:
                    if item[1] is None or item[1] == '':
                        QMessageBox.warning(self, "注意", "密码不能为空！" + "用户”" + item[0] + "“添加失败。")
                        continue
                    userInsertDict = {"userName": item[0], "userPassword": item[1], "userFlag": item[2]}
                    response = self.post_userInsert.response_json(userInsertDict)
                    if response["状态"] == "成功":
                        print("insert user: ", item)
                    else:
                        print("cant insert user: ", item)
                        QMessageBox.warning(self, "注意", response["提示信息"])
                # 更新用户
                else:
                    if item[1] is None or item[1] == '':
                        QMessageBox.warning(self, "注意", "密码不能为空！" + "用户”" + item[0] + "“更新失败。")
                        continue
                    self.post_userUpdatePassword.response_json({"userName": item[0], "newPassword": item[1]})
                    self.post_userUpdateForbidden.response_json({"userName": item[0], "newFlag": item[2]})
                    print("update user: ", item)
        for item in self.saveList_user:
            if item[0] not in _idList:
                self.post_userDelete.response_json({"userName": item[0]})
                print("delete user: ", item)
        # self.saveList_user = copy(self.displayList_user)
        # 调用刷新按钮函数,更新save列表等
        self.refresh_user()

    # 表格新增一行函数
    def add_user(self):
        self.table.setCurrentItem(None)
        self.User_newLine(len(self.displayList_user) + 1)
