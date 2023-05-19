import re
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow
import random
from .game_screen_init import GameScreen_init
from util import music_storePath, MyPost


# 使用界面窗口：音乐界面类
class GameScreen_music(GameScreen_init, QMainWindow):
    def __init__(self):
        super(GameScreen_music, self).__init__()
        # slider控件初始化
        self.horizontalSlider_volume.setRange(0, 100)  # 音量范围
        self.horizontalSlider_volume.setValue(100)  # 初始音量
        self.horizontalSlider_progress.setEnabled(False)  # 音乐进度初始化为不可用
        # 前端post设置
        self.post_musicInit = MyPost('/user/musicInit')
        # 音频设置及初始化
        self.musicsPath_list = []        # 音频前端绝对路径列表
        self.musicsName_list = []        # 音频名称列表
        self.music_index_dict = {}       # 音频媒体索引链接字典
        self.playlist = QMediaPlaylist(self)
        self.player = QMediaPlayer(self)
        self.music_init()
        # 关联按钮
        self.connecter_music()

    # 连接按钮和对应的函数
    def connecter_music(self):
        self.horizontalSlider_volume.valueChanged.connect(self.volume_change)  # 音量大小改变功能
        self.horizontalSlider_progress.sliderMoved.connect(self.progress_change)  # 歌曲进度改变功能
        self.pushButton_sound.clicked.connect(self.sound_change)  # 静音功能
        self.pushButton_musicChange.clicked.connect(self.music_change)  # 切换歌曲功能
        self.pushButton_musicRandomChange.clicked.connect(self.music_randomChange)  # 切换歌曲功能(随机)
        self.pushButton_play_pause.clicked.connect(self.music_play_pause)  # 播放音乐
        self.listWidget_music.doubleClicked.connect(self.list_play_func)

    # 音频初始化
    def music_init(self):
        # 初始化
        self.musicsPath_list = []  # 音频相对路径列表
        self.musicsName_list = []  # 音频名称列表
        self.music_index_dict = {}  # 音频媒体索引链接字典
        self.listWidget_music.clear()   # 清空音频显示列表
        self.player.setPlaylist(self.playlist)  # 设置play的播放列表为playlist
        # 获取前端音乐资源存储路径下的所有音乐路径和所有音乐名称
        musicsPath = os.listdir(music_storePath)
        musicsName = []
        for musicPath in musicsPath:
            # re.findall正则获取前端音乐路径对应的音乐名称
            music_name = re.findall(r'(.+?)\.mp3', re.findall(r'[^\\/:*?"<>|\r\n]+$', musicPath)[0])[0]
            musicsName.append(music_name)
        # 根据后端具体设置,来设置前端播放器播放内容
        response = self.post_musicInit.response_json()
        for musicName_flask, musicPath_flask in response.items():
            self.musicsName_list.append(musicName_flask)
            # 若前端已存在音乐文件,则直接写入播放器
            if musicName_flask in musicsName:
                musicPath_pyqt = music_storePath + musicName_flask + '.mp3'
                self.musicsPath_list.append(musicPath_pyqt)
            # 否则,从后端下载音乐到本地再进行写入
            else:
                postExtendPath = '/user/musicDownload/' + musicPath_flask
                post_downloadMusic = MyPost(postExtendPath)
                post_downloadMusic.download_music(musicName_flask)
                musicPath_pyqt_download = music_storePath + musicName_flask + '.mp3'
                self.musicsPath_list.append(musicPath_pyqt_download)
        # 设置前端播放器
        self.listWidget_music.addItems(self.musicsName_list)
        index = 0
        self.playlist.clear()
        for music_path in self.musicsPath_list:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(music_path)))  # 媒体播放列表添加歌曲
            self.music_index_dict[str(index)] = str(music_path)  # 音频媒体索引链接字典添加歌曲
            index += 1
        self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)  # 设置为顺序播放
        # 设置歌曲进度位置关联
        self.player.durationChanged.connect(self.get_duration_func)  # 歌曲进度初始位置关联
        self.player.positionChanged.connect(self.get_position_func)  # 歌曲进度中途位置关联

    # 播放与暂停音乐功能
    def music_play_pause(self):
        if self.player.state() == 1:
            self.player.pause()
            self.pushButton_play_pause.setIcon(QIcon('icons/play.png'))
        else:
            self.player.play()
            self.listWidget_music.setCurrentRow(self.playlist.currentIndex())
            self.pushButton_play_pause.setIcon(QIcon('icons/pause.png'))

    # 静音功能
    def sound_change(self):
        if self.player.isMuted():
            self.player.setMuted(False)
            self.pushButton_sound.setIcon(QIcon('icons/sound_on'))
        else:
            self.player.setMuted(True)
            self.pushButton_sound.setIcon(QIcon('icons/sound_off'))

    # 切换歌曲功能——切换后歌曲不能与切换前相同(直接切换为下一首)
    def music_change(self):
        if self.playlist.currentIndex() == self.playlist.mediaCount() - 1:
            self.playlist.setCurrentIndex(0)
            self.listWidget_music.setCurrentRow(0)  # 设置列表选中
        else:
            self.playlist.next()
            self.listWidget_music.setCurrentRow(self.playlist.currentIndex())
        # 根据当前播放信息更改播放图标
        if self.player.state() == 1:
            self.pushButton_play_pause.setIcon(QIcon('icons/pause.png'))
        else:
            self.pushButton_play_pause.setIcon(QIcon('icons/play.png'))

    # 切换歌曲功能——切换后歌曲不能与切换前相同(随机切换)
    def music_randomChange(self):
        randomint = random.randint(0, self.playlist.mediaCount() - 1)
        print(randomint)
        if self.playlist.currentIndex() == randomint:
            self.music_randomChange()
            return
        self.playlist.setCurrentIndex(randomint)
        self.listWidget_music.setCurrentRow(randomint)
        # 根据当前播放信息更改播放图标
        if self.player.state() == 1:
            self.pushButton_play_pause.setIcon(QIcon('icons/pause.png'))
        else:
            self.pushButton_play_pause.setIcon(QIcon('icons/play.png'))

    # 音量大小改变功能
    def volume_change(self, value):
        self.player.setVolume(value)
        if value == 0:
            self.pushButton_sound.setIcon(QIcon('icons/sound_off.png'))
        else:
            self.pushButton_sound.setIcon(QIcon('icons/sound_on.png'))

    # 歌曲进度改变功能
    def progress_change(self, value):
        self.player.setPosition(value)
        # 更新歌曲进度时间
        progress_time = self.horizontalSlider_progress.maximum() - value
        self.time_change(progress_time)

    # 更新时间显示
    def time_change(self, progress_time):
        seconds = int(progress_time / 1000)
        minutes = int(seconds / 60)
        seconds -= minutes * 60
        if minutes == 0 and seconds == 0:
            self.label_time.setText('--/--')
            self.pushButton_play_pause.setIcon(QIcon('icons/play.png'))
        else:
            if seconds < 10:
                self.label_time.setText('0{}:0{}'.format(minutes, seconds))
            else:
                self.label_time.setText('0{}:{}'.format(minutes, seconds))

    # 歌曲进度初始位置初始化
    def get_duration_func(self, progress_time):
        self.horizontalSlider_progress.setRange(0, progress_time)
        self.horizontalSlider_progress.setEnabled(True)
        self.time_change(progress_time)

    # 歌曲播放过程位置更改
    def get_position_func(self, play_time):
        self.horizontalSlider_progress.setValue(play_time)
        # 更新歌曲进度时间
        progress_time = self.horizontalSlider_progress.maximum() - play_time
        self.time_change(progress_time)

    def list_play_func(self):
        self.playlist.setCurrentIndex(self.listWidget_music.currentRow())
        self.player.play()
        self.pushButton_play_pause.setIcon(QIcon('icons/pause.png'))
