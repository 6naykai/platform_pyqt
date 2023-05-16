import os
import re
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QHeaderView, QTableWidgetItem, QAbstractItemView
from .game_screen_init import GameScreen_init
from database.database_root import Database_root


# 使用界面窗口：音乐下载类
class GameScreen_musicDownload(GameScreen_init, QMainWindow):
    def __init__(self):
        super(GameScreen_musicDownload, self).__init__()
        self.song_author = None
        self.song_url = None
        self.song_name = None
        self.song_num = None
        self.header_musicDownload = None
        self.response_data = None
        # 数据库设置
        self.database_download = Database_root()
        # 设置表格头的伸缩模式，也就是让表格铺满整个QTableWidget控件
        self.tableWidget_music_download.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.connecter_musicDownload()
        # QTableWidget设置整行选中
        self.tableWidget_music_download.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget_music_download.setSelectionMode(QAbstractItemView.SingleSelection)

    # 连接按钮和对应的函数
    def connecter_musicDownload(self):
        self.pushButton_music_search.clicked.connect(self.get_KuWoMusic)
        self.tableWidget_music_download.itemSelectionChanged.connect(self.get_song_url)
        self.pushButton_music_download.clicked.connect(self.download_music)
        pass

    # 爬虫获取音乐信息
    def get_KuWoMusic(self):
        """
        获取qq音乐
        :return:
        """
        # 清空tableWidget表格数据
        self.tableWidget_music_download.setRowCount(0)
        self.tableWidget_music_download.clearContents()
        self.header_musicDownload = []
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept - encoding': 'gzip, deflate',
            'accept - language': 'zh - CN, zh;q = 0.9',
            'cache - control': 'no - cache',
            'Connection': 'keep-alive',
            'csrf': 'HH3GHIQ0RYM',
            'Referer': 'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.51 Safari/537.36',
            'Cookie': '_ga=GA1.2.218753071.1648798611; _gid=GA1.2.144187149.1648798611; _gat=1; '
                      'Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1648798611; '
                      'Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1648798611; kw_token=HH3GHIQ0RYM'
        }
        search_input = self.lineEdit_music_search.text()
        if len(search_input) > 0:
            search_url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?'
            search_data = {
                'key': search_input,
                'pn': '1',
                'rn': '80',
                'httpsStatus': '1',
                'reqId': '858597c1-b18e-11ec-83e4-9d53d2ff08ff'
            }
            try:
                self.response_data = requests.get(search_url, params=search_data, headers=headers, timeout=20).json()
                songs_data = self.response_data['data']['list']
                if int(self.response_data['data']['total']) <= 0:
                    QMessageBox.warning(self, "注意", "搜索: {} 不存在.".format(search_input))
                else:
                    for i in range(len(songs_data)):
                        print((songs_data[i]['artist'], songs_data[i]['name'],
                               songs_data[i]['album']))
                        self.newLine_musicDownload(i + 1, (songs_data[i]['artist'], songs_data[i]['name'],
                                                           songs_data[i]['album']))
                    self.tableWidget_music_download.setRowCount(len(songs_data))
            except TimeoutError:
                QMessageBox.warning(self, "注意", "搜索超时，请重新输入后再搜索！")
        else:
            QMessageBox.warning(self, "注意", "未输入需查询的歌曲或歌手，请输入后搜索！")

    # 表格新增一行函数
    def newLine_musicDownload(self, num, item=None):
        """
        :param num: 在对应序号处的序号画空白行
        :param item: 输入为对应数据
        """
        self.tableWidget_music_download.setRowCount(num)
        self.tableWidget_music_download.insertRow(num)
        _0 = QTableWidgetItem("")
        _0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _1 = QTableWidgetItem("")
        _1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        _2 = QTableWidgetItem("")
        _2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        if item is not None:
            _0.setText(str(item[0]))
            _1.setText(str(item[1]))
            _2.setText(str(item[2]))
        else:
            print(5)
            return
        self.tableWidget_music_download.setItem(num - 1, 0, _0)
        self.tableWidget_music_download.setItem(num - 1, 1, _1)
        self.tableWidget_music_download.setItem(num - 1, 2, _2)
        self.header_musicDownload.append(str(num))
        self.tableWidget_music_download.setVerticalHeaderLabels(self.header_musicDownload)
        self.update()

    # 爬虫获取下载音乐的地址url
    def get_song_url(self):
        """
        获取下载歌曲的地址
        :return:
        """
        row_select = self.tableWidget_music_download.selectedItems()
        if len(row_select) == 0:
            return
        self.song_num = row_select[0].row() + 1
        print(self.song_num)
        # 获取下载歌曲的地址
        if self.song_num is not None:
            songs_data = self.response_data['data']['list']
            songs_req_id = self.response_data['reqId']
            song_rid = songs_data[self.song_num - 1]['rid']
            music_url = 'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={}&type=convert_url3' \
                        '&httpsStatus=1&reqId={}' \
                .format(song_rid, songs_req_id)
            response_data = requests.get(music_url).json()
            self.song_url = response_data['data'].get('url')
            self.song_name = songs_data[self.song_num - 1]['name']
            self.song_author = songs_data[self.song_num - 1]['artist']
            print(self.song_url)
            print(self.song_name)
            print(self.song_author)
        else:
            QMessageBox.warning(self, "注意", "未选择要下载的歌曲，请选择")

    # 下载音乐
    def download_music(self):
        """
        下载音乐
        :return:
        """
        if not os.path.exists('./musics'):
            os.mkdir("./musics/")
        if self.song_num is not None:
            song_name = self.song_name + '--' + self.song_author + ".mp3"
            try:
                save_path = os.path.join('./musics/{}'.format(song_name)) \
                    .replace('\\', '/')
                true_path = os.path.abspath(save_path)
                resp = requests.get(self.song_url)
                with open(save_path, 'wb') as file:
                    file.write(resp.content)
                    print(true_path)
                    file_path = true_path
                    # re.findall正则获取音乐名称
                    music_name = re.findall(r'(.+?)\.mp3', re.findall(r'[^\\/:*?"<>|\r\n]+$', file_path)[0])[0]
                    print(music_name)
                    music_path = 'musics/' + music_name + '.mp3'
                    self.database_download.insert("music_table", [music_name, music_path])
                    QMessageBox.information(self, "下载成功", '歌曲：%s\n保存地址：%s' % (self.song_name, music_path))
            except Exception:
                QMessageBox.warning(self, "注意", "未找到存放歌曲的文件夹")
        else:
            QMessageBox.warning(self, "注意", "未选择要下载的歌曲，请选择后下载")
