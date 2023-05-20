from copy import copy
# 下面这个必须导入，因为exec中用到了
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QMainWindow, QHeaderView

from util import MyPost
from .game_screen_init import GameScreen_init


# 使用界面窗口：权限管理类
class GameScreen_quanxian(GameScreen_init, QMainWindow):
    def __init__(self):
        super(GameScreen_quanxian, self).__init__()
        # 前端post设置
        self.post_accountsSelectPassword = MyPost('/rootAdmin/accountsSelectPassword')
        self.post_accountsSelectType = MyPost('/rootAdmin/accountsSelectType')
        self.post_accountInsert = MyPost('/rootAdmin/accountInsert')
        self.post_accountUpdatePassword = MyPost('/rootAdmin/accountUpdatePassword')
        self.post_adminUpdateType = MyPost('/rootAdmin/adminUpdateType')
        self.post_accountDelete = MyPost('/rootAdmin/accountDelete')
        # 管理员表设置
        self.header_quanxian = [""]             # 列表头,用于显示数据对应的行序号
        self.saveList_quanxian_user = []        # 用户表的数据存储列表(数据库中内容)
        self.saveList_quanxian_admin = []       # 管理员账户表的数据存储列表(数据库中内容)
        self.displayList_quanxian = []          # 数据显示列表(表格中内容)
        self.comboBox_list_quanxian = \
            ["普通用户", "音乐管理员", "游戏管理员", "用户管理员", "模型管理员"]  # 设置权限选择框中内容
        self.tableHeader_init_quanxian()        # 初始化表头
        self.data_init_quanxian()               # 初始化数据
        # 连接信号
        self.connecter_quanxian()

    # 连接按钮和对应的函数
    def connecter_quanxian(self):
        self.tablequanxian.itemChanged.connect(self._dataChanged_quanxian)
        self.pushButton_save1.clicked.connect(self.save_quanxian)
        self.pushButton_delete1.clicked.connect(self.delete_quanxian)
        self.pushButton_refresh1.clicked.connect(self.refresh_quanxian)
        self.pushButton_add1.clicked.connect(self.add_quanxian)

    # 初始化表头和行列数
    def tableHeader_init_quanxian(self):
        self.header_quanxian = [""]  # 初始化列表头
        self.saveList_quanxian_user = []  # 用户表的数据存储列表(数据库中内容)
        self.saveList_quanxian_admin = []  # 管理员账户表的数据存储列表(数据库中内容)
        self.displayList_quanxian = []  # 数据显示列表(表格中内容)
        # 设置表格有1行5列
        self.tablequanxian.setColumnCount(3)  # 设置列数
        self.tablequanxian.setRowCount(1)  # 设置行数
        # 设定“列标题”并将单元格设定为不可编辑
        accountName = QTableWidgetItem("账户名")
        accountPassword = QTableWidgetItem("账户密码")
        accountType = QTableWidgetItem("账户类型")
        accountName.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        accountPassword.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        accountType.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tablequanxian.setItem(0, 0, accountName)
        self.tablequanxian.setItem(0, 1, accountPassword)
        self.tablequanxian.setItem(0, 2, accountType)
        # 隐藏列标题
        self.tablequanxian.horizontalHeader().setVisible(False)
        # 设置表格头的伸缩模式，也就是让表格铺满整个QTableWidget控件
        self.tablequanxian.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # 初始化操作：即从数据库加载数据
    def data_init_quanxian(self):
        # 获取sel语句的数据列表
        accountsPassword = self.post_accountsSelectPassword.response_json()
        accountsType = self.post_accountsSelectType.response_json()
        # 遍历数据字典
        data = []
        for accountName in accountsPassword:
            item = (accountName, accountsPassword[accountName], accountsType[accountName])
            data.append(item)
        # 遍历data列表
        # enumerate()函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
        rootList = []
        adminList = []
        for index, item in enumerate(data):
            # 设置普通用户账户类型
            if item[2] == "普通用户":
                self.saveList_quanxian_user.append(item)  # 用户存储列表添加数据元组
            elif item[2] == "系统管理员":
                rootList.append(item)                     # 系统管理员填入
            else:
                adminList.append(item)                    # 其他管理员填入
        # 管理员存储列表添加数据元组
        self.saveList_quanxian_admin = copy(rootList + adminList)
        # 显示列表copy存储列表内容(管理员在前,普通用户在后)
        self.displayList_quanxian = copy(self.saveList_quanxian_admin + self.saveList_quanxian_user)
        for index, item in enumerate(self.displayList_quanxian):
            self.newLine_quanxian(index + 1, item=item)  # 表格新增1行
        self.update()   # 更新显示

    # 表格新增一行函数
    def newLine_quanxian(self, num, item=None):
        """
        :param num: 在对应序号处的序号画空白行
        :param item: 输入为对应数据
        """
        if self.lineEdit_num1.text() == "" and item is None:
            QMessageBox.warning(self, "注意", "输入账户名不能为空!")
            return
        # 遍历展示列表看是否有重名的,若有则添加失败
        for account in self.displayList_quanxian:
            if account[0] == self.lineEdit_num1.text():
                QMessageBox.warning(self, "注意", "输入账户名不能重复!")
                self.lineEdit_num1.clear()
                return
        self.tablequanxian.insertRow(num)
        _0 = QTableWidgetItem("")
        _0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _1 = QTableWidgetItem("")
        _2 = QTableWidgetItem("")
        # 系统管理员的特殊单元格设置
        if num == 1:
            _2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        else:
            # 设置选择框普通用户/音乐管理员/游戏管理员/用户管理员/模型管理员/系统管理员,批量化生产子控件
            exec('self.comboBox_type{} = QtWidgets.QComboBox()'.format(num))
            exec('self.comboBox_type{}.addItems(self.comboBox_list_quanxian)'.format(num))
            exec('self.comboBox_type{}.currentIndexChanged.connect(self._dataChanged_quanxian)'.format(num))
        if item is not None:
            _0.setText(str(item[0]))
            _1.setText(str(item[1]))
            _2.setText(str(item[2]))
            # 根据数据库内容设置选择框默认值
            if num == 1:
                pass
            elif item[2] == "音乐管理员":
                exec('self.comboBox_type{}.setCurrentIndex(1)'.format(num))
            elif item[2] == "游戏管理员":
                exec('self.comboBox_type{}.setCurrentIndex(2)'.format(num))
            elif item[2] == "用户管理员":
                exec('self.comboBox_type{}.setCurrentIndex(3)'.format(num))
            elif item[2] == "模型管理员":
                exec('self.comboBox_type{}.setCurrentIndex(4)'.format(num))
            else:
                exec('self.comboBox_type{}.setCurrentIndex(0)'.format(num))
        else:
            _0.setText(self.lineEdit_num1.text())
            exec('self.comboBox_type{}.setCurrentIndex(0)'.format(num))
            content = (self.lineEdit_num1.text(), None, "普通用户")
            self.displayList_quanxian.append(content)
            self.lineEdit_num1.clear()
        self.tablequanxian.setItem(num, 0, _0)
        self.tablequanxian.setItem(num, 1, _1)
        self.tablequanxian.setItem(num, 2, _2)
        if num == 1:
            pass
        else:
            exec('self.tablequanxian.setCellWidget(num, 2, self.comboBox_type{})'.format(num))
        self.header_quanxian.append(str(num))
        self.tablequanxian.setVerticalHeaderLabels(self.header_quanxian)
        self.update()

    # 表格数据更改的函数
    def _dataChanged_quanxian(self):
        """
        一旦检测到数据改变,则进行检查,
        选择添加新数据还是对原数据进行修改
        :return:
        """
        global content
        row_select = self.tablequanxian.selectedItems()
        if len(row_select) == 0:
            return
        row = row_select[0].row()
        try:
            content = (self.tablequanxian.item(row, 0).text(), self.tablequanxian.item(row, 1).text(),
                       self.tablequanxian.cellWidget(row, 2).currentText())
        except Exception:
            content = (self.tablequanxian.item(row, 0).text(), self.tablequanxian.item(row, 1).text(),
                       self.tablequanxian.item(row, 2).text())
        if row <= len(self.displayList_quanxian):
            print("修改行", content)
            self.displayList_quanxian[row - 1] = content
        else:
            print("最新行", content)
            self.displayList_quanxian.append(content)

    # 刷新表格函数
    def refresh_quanxian(self):
        self.tableHeader_init_quanxian()  # 初始化表头
        self.data_init_quanxian()  # 初始化数据

    # 表格删除一行函数
    def delete_quanxian(self):
        """
        若有选中行,点击删除后即可删除
        :return:
        """
        row_select = self.tablequanxian.selectedItems()
        # 若没有选中行
        if len(row_select) == 0:
            return
        Id = row_select[0].row()
        if int(Id) <= len(self.displayList_quanxian):
            print("删除一条数据")
            self.displayList_quanxian.pop(Id - 1)
        self.header_quanxian.pop()
        self.tablequanxian.removeRow(row_select[0].row())
        self.tablequanxian.setVerticalHeaderLabels(self.header_quanxian)
        self.update()

    # 保存表格函数
    def save_quanxian(self):
        """
        点击保存需要筛选出
        管理员表中需要更新的数据
        管理员表中需要删除的数据
        管理员表中需要添加的数据
        用户表中需要添加的数据
        用户表中需要删除的数据
        """
        user_nameList = [str(k[0]) for k in self.saveList_quanxian_user]
        admin_nameList = [str(k[0]) for k in self.saveList_quanxian_admin]
        _nameList = [str(k[0]) for k in self.displayList_quanxian]
        print("点击保存")
        # 判断是否存在修改或新增
        for item in self.displayList_quanxian:
            if item not in self.saveList_quanxian_admin + self.saveList_quanxian_user:
                print("存在修改数据")
                # 若修改的账户原来是管理员
                if item[0] in admin_nameList:
                    # 若该管理员被变更为普通用户,则在管理员表中剔除,在用户表中新增
                    if item[2] == "普通用户":
                        if item[1] is None or item[1] == '':
                            QMessageBox.warning(self, "注意", "密码不能为空！" + "账户”" + item[0] + "“更新失败。")
                            continue
                        self.post_accountDelete.response_json({"accountName": item[0],
                                                               "accountType": "非普通"})
                        self.post_accountInsert.response_json({"accountName": item[0],
                                                               "accountPassword": item[1],
                                                               "accountType": "普通用户"})
                        print('管理员' + item[0] + '变更为普通用户')
                    # 若未被变更为普通用户,则在管理员表中更新其内容
                    else:
                        if item[1] is None or item[1] == '':
                            QMessageBox.warning(self, "注意", "密码不能为空！" + "账户”" + item[0] + "“更新失败。")
                            continue
                        self.post_accountUpdatePassword.response_json({'accountName': item[0],
                                                                       'newPassword': item[1],
                                                                       'accountType': item[2]})
                        print(item[2])
                        self.post_adminUpdateType.response_json({'adminName': item[0],
                                                                 'adminType': item[2]})
                        print('管理员' + item[0] + '被更新')
                # 若修改的账户原来是普通用户
                elif item[0] in user_nameList:
                    # 若该用户未被设置成管理员,则在用户表中更新其内容
                    if item[2] == "普通用户":
                        if item[1] is None or item[1] == '':
                            QMessageBox.warning(self, "注意", "密码不能为空！" + "账户”" + item[0] + "“更新失败。")
                            continue
                        self.post_accountUpdatePassword.response_json({'accountName': item[0],
                                                                       'newPassword': item[1],
                                                                       'accountType': item[2]})
                        print('用户' + item[0] + '被更新')
                    # 若该用户被设置成管理员,则在用户表中剔除,在管理员表中新增
                    else:
                        if item[1] is None or item[1] == '':
                            QMessageBox.warning(self, "注意", "密码不能为空！" + "账户”" + item[0] + "“更新失败。")
                            continue
                        self.post_accountDelete.response_json({"accountName": item[0],
                                                               "accountType": "普通用户"})
                        self.post_accountInsert.response_json({"accountName": item[0],
                                                               "accountPassword": item[1],
                                                               "accountType": item[2]})
                        print('用户' + item[0] + '变更为' + item[2])
                # 找不到,则为新增账户
                else:
                    if item[1] is None or item[1] == '':
                        QMessageBox.warning(self, "注意", "密码不能为空！" + "账户”" + item[0] + "“添加失败。")
                        continue
                    self.post_accountInsert.response_json({"accountName": item[0],
                                                           "accountPassword": item[1],
                                                           "accountType": item[2]})
                    # 若新增的账户类型为普通用户,则在用户表中插入
                    if item[2] == "普通用户":
                        print('新增用户' + item[0])
                    # 若新增的账户类型为管理员,则在管理员账户表中插入
                    else:
                        print('新增管理员' + item[0])
        # 判断是否存在删除
        for item in self.saveList_quanxian_admin + self.saveList_quanxian_user:
            if item[0] not in _nameList:
                self.post_accountDelete.response_json({"accountName": item[0],
                                                       "accountType": item[2]})
                # 若删除的账户原来是普通用户,则在用户表中删除
                if item[2] == "普通用户":
                    print('删除用户' + item[0])
                # 若删除的账户原来是管理员,则在管理员表中删除
                else:
                    print('删除管理员' + item[0])
        # 调用刷新按钮函数,更新save列表等
        self.refresh_quanxian()

    # 表格新增一行函数
    def add_quanxian(self):
        self.tablequanxian.setCurrentItem(None)
        self.newLine_quanxian(len(self.displayList_quanxian) + 1)
