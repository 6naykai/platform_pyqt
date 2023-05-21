import re
from copy import copy
# 下面这个必须导入，因为exec中用到了
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QMainWindow, QHeaderView, QFileDialog, QMessageBox

from util import MyPost
from .game_screen_init import GameScreen_init


# 使用界面窗口：音乐管理类
class GameScreen_musicManagement(GameScreen_init, QMainWindow):
    def __init__(self):
        super(GameScreen_musicManagement, self).__init__()
        # 前端post设置
        self.post_musicsSelectMusicPath = MyPost('/musicAdmin/musicsSelectMusicPath')
        self.post_musicsSelectIsAccretion = MyPost('/musicAdmin/musicsSelectIsAccretion')
        self.post_musicUpdateIsAccretion = MyPost('/musicAdmin/musicUpdateIsAccretion')
        self.post_musicDelete = MyPost('/musicAdmin/musicDelete')
        self.post_musicUpload = MyPost('/musicAdmin/musicUpload')
        # 音乐表的设置
        self.header_music = [""]  # 列表头,用于显示数据对应的行序号
        self.saveList_music = []  # 音乐表的数据存储列表(数据库中内容)
        self.displayList_music = []  # 音乐表的数据显示列表(表格中内容)
        self.tableHeader_init_music()  # 初始化表头
        self.data_init_music()  # 初始化数据
        # 连接信号
        self.connecter_musicManagement()

    # 连接按钮和对应的函数
    def connecter_musicManagement(self):
        self.pushButton_save_music.clicked.connect(self.save_music)
        self.pushButton_delete_music.clicked.connect(self.delete_music)
        self.pushButton_refresh_music.clicked.connect(self.refresh_music)
        self.pushButton_add_music.clicked.connect(self.add_music)
        self.table_music.itemChanged.connect(self._dataChanged_music)

    # 初始化表头和行列数
    def tableHeader_init_music(self):
        self.header_music = [""]  # 初始化列表头
        self.saveList_music = []  # 音乐表的数据存储列表(数据库中内容)
        self.displayList_music = []  # 音乐表的数据显示列表(表格中内容)
        # 设置表格有1行3列
        self.table_music.setColumnCount(3)  # 设置列数
        self.table_music.setRowCount(1)  # 设置行数
        # 设定“列标题”并将单元格设定为不可编辑
        musicName = QTableWidgetItem("音乐名称")
        musicPath = QTableWidgetItem("音乐路径")
        music_isAccretion = QTableWidgetItem("是否添加至音乐库")
        musicName.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        musicPath.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        music_isAccretion.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table_music.setItem(0, 0, musicName)
        self.table_music.setItem(0, 1, musicPath)
        self.table_music.setItem(0, 2, music_isAccretion)
        # 隐藏列标题
        self.table_music.horizontalHeader().setVisible(False)
        # 设置表格头的伸缩模式，也就是让表格铺满整个QTableWidget控件
        self.table_music.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # 初始化操作：即从数据库加载数据
    def data_init_music(self):
        # 获取sel语句的数据列表
        musicsPath = self.post_musicsSelectMusicPath.response_json()
        musicsIsAccretion = self.post_musicsSelectIsAccretion.response_json()
        # 遍历数据字典
        data = []
        for musicName in musicsPath:
            file_path = musicsPath[musicName]
            # rfind获取音乐相对路径
            music_path = file_path[file_path.rfind('/', 0, file_path.rfind('/') - 1) + 1:]
            # print(music_path)
            item = (musicName, music_path, musicsIsAccretion[musicName])
            data.append(item)
        # 遍历data列表
        # enumerate()函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列
        for index, item in enumerate(data):
            self.Music_newLine(index + 1, item=item)  # 表格新增1行
            self.displayList_music.append(item)  # 显示列表添加数据元组
        self.saveList_music = copy(self.displayList_music)
        self.update()

    # 表格新增一行函数
    def Music_newLine(self, num, item=None, flag=False):
        """
        :param num: 在对应序号处的序号画空白行
        :param item: 输入为对应数据
        :param flag: 是否为新增数据
        """
        self.table_music.insertRow(num)
        _0 = QTableWidgetItem("")
        _0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _1 = QTableWidgetItem("")
        _1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _2 = QTableWidgetItem("")
        # 设置确认框true/false,默认为true,批量化生产子控件
        exec('self.checkBox_ruku{} = QtWidgets.QCheckBox()'.format(num))
        exec('self.checkBox_ruku{}.setChecked(True)'.format(num))
        exec('self.checkBox_ruku{}.stateChanged.connect(self._dataChanged_music)'.format(num))

        if item is not None:
            _0.setText(str(item[0]))
            _1.setText(str(item[1]))
            # _2.setText(str(item[2]))
            # _2.setCheckState(Qt.Unchecked)
            # 根据数据库内容设置确认框默认值
            if str(item[2]) == "False":
                # _2.setCheckState(Qt.Unchecked)
                exec('self.checkBox_ruku{}.setChecked(False)'.format(num))
            # 若为新增,则显示列表新增
            if flag:
                self.displayList_music.append(item)
        else:
            return  # 与添加音乐按钮关联(采用正则关联content,已解决)
        self.table_music.setItem(num, 0, _0)
        self.table_music.setItem(num, 1, _1)
        self.table_music.setItem(num, 2, _2)
        exec('self.table_music.setCellWidget(num, 2, self.checkBox_ruku{})'.format(num))
        self.header_music.append(str(num))
        self.table_music.setVerticalHeaderLabels(self.header_music)
        self.update()

    # 表格数据更改的函数
    def _dataChanged_music(self):
        """
        一旦检测到数据改变,则进行检查,
        选择添加新数据还是对原数据进行修改
        :return:
        """
        row_select = self.table_music.selectedItems()
        if len(row_select) == 0:
            return
        row = row_select[0].row()
        content = (self.table_music.item(row, 0).text(), self.table_music.item(row, 1).text(),
                   self.table_music.cellWidget(row, 2).isChecked())
        if row <= len(self.displayList_music):
            print("修改行", content)
            self.displayList_music[row - 1] = content
        else:
            print("最新行", content)
            self.displayList_music[row - 1] = content

    # 刷新表格函数
    def refresh_music(self):
        self.tableHeader_init_music()  # 初始化表头
        self.data_init_music()  # 初始化数据

    # 表格删除一行函数
    def delete_music(self):
        """
        若有选中行,点击删除后即可删除
        :return:
        """
        row_select = self.table_music.selectedItems()
        # 若没有选中行
        if len(row_select) == 0:
            return
        Id = row_select[0].row()
        if int(Id) <= len(self.displayList_music):
            print("删除一条数据")
            self.displayList_music.pop(Id - 1)
        self.header_music.pop()
        self.table_music.removeRow(row_select[0].row())
        self.table_music.setVerticalHeaderLabels(self.header_music)
        self.update()

    # 保存表格函数
    def save_music(self):
        """
        点击保存需要筛选出
        需要更新的数据
        需要删除的数据
        需要添加的数据
        """
        idList = [str(k[0]) for k in self.saveList_music]
        _idList = [str(k[0]) for k in self.displayList_music]
        print("点击保存")
        for item in self.displayList_music:
            if item not in self.saveList_music:
                print("存在修改数据")
                if item[0] not in idList:
                    # self.database_musicManagement.insert("music_table", [item[0], item[1]])
                    print("insert music")
                else:
                    self.post_musicUpdateIsAccretion.response_json({'musicName': item[0],
                                                                    'newIsAccretion': item[2]})
                    print("update music")
        for item in self.saveList_music:
            if item[0] not in _idList:
                self.post_musicDelete.response_json({'musicName': item[0]})
                print("delete music", item)
        # self.saveList_music = copy(self.displayList_music)
        # 调用刷新按钮函数,更新save列表等
        self.refresh_music()

    # 表格新增一行函数
    def add_music(self):
        # 获取音乐文件路径
        file = QFileDialog.getOpenFileName(self, "请选择要添加的音乐文件", "musics", "All Files (*)")
        print(file)
        if file == ('', ''):
            return  # 没取到文件则直接返回
        file_path = file[0]
        # re.findall正则获取音乐名称
        music_name = re.findall(r'(.+?)\.mp3', re.findall(r'[^\\/:*?"<>|\r\n]+$', file_path)[0])[0]
        print(music_name)
        # # rfind获取音乐相对路径
        # music_path = file_path[file_path.rfind('/', 0, file_path.rfind('/') - 1) + 1:]
        # print(music_path)
        music_path = file[0]    # 使用绝对路径进行上传
        print(music_path)
        # 将音乐上传至后端
        upload_response = self.post_musicUpload.uploadFile_response(music_path, music_name, "mp3")
        if upload_response["状态"] == "失败":
            QMessageBox.warning(self, "注意", upload_response["提示信息"])
        else:
            QMessageBox.information(self, "提示", upload_response["提示信息"])

        # # 添加一行音乐
        # content = (music_name, music_path, True)
        # self.table_music.setCurrentItem(None)
        # self.Music_newLine(len(self.displayList_music) + 1, content, True)

        # 调用刷新按钮函数,更新save列表等
        self.refresh_music()
