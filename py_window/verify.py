from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QUrl
from PyQt5.QtGui import QMouseEvent, QIcon
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from UI.UI_verify import Ui_MainWindow
import random


# 验证窗口类
class Verify(Ui_MainWindow, QMainWindow):

    # 窗口切换信号
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(Verify, self).__init__()
        self._tracking = None
        self._startPos = None
        self._endPos = None
        self.effect_shadow_label = None
        self.setupUi(self)                  # 引入UI界面
        self.setWindowTitle("创意游戏平台")   # 设置窗口名
        self.connecter()                    # 连接按钮
        # 隐藏框
        self.setWindowFlags(Qt.FramelessWindowHint)     # 隐藏标题栏
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置背景透明
        # 添加阴影
        self.add_shadow()
        # 音频设置及初始化
        self.music_list = []
        self.music_index_dict = {}  # 音频媒体索引链接字典
        self.playlist = QMediaPlaylist(self)
        self.player = QMediaPlayer(self)
        self.music_init()
        self.player.durationChanged.connect(self.get_duration_func)     # 歌曲进度初始位置关联
        self.player.positionChanged.connect(self.get_position_func)     # 歌曲进度中途位置关联
        # 问题列表设置及初始化
        self.question_list = []
        self.question_init()
        # slider控件初始化
        self.horizontalSlider_volume.setRange(0, 100)       # 音量范围
        self.horizontalSlider_volume.setValue(100)          # 初始音量
        self.horizontalSlider_progress.setEnabled(False)    # 音乐进度初始化为不可用
        # 验证hash表设置及初始化
        self.verify_hashTable = {}
        self.hashTable_init()

    # 连接按钮和对应的函数
    def connecter(self):
        self.pushButton_play_pause.clicked.connect(self.music_play_pause)           # 播放音乐
        self.pushButton_verify.clicked.connect(self.verify)                         # 验证功能
        self.pushButton_questionChange.clicked.connect(self.question_change)        # 切换问题功能
        self.horizontalSlider_volume.valueChanged.connect(self.volume_change)       # 音量大小改变功能
        self.horizontalSlider_progress.sliderMoved.connect(self.progress_change)    # 歌曲进度改变功能
        self.pushButton_sound.clicked.connect(self.sound_change)                    # 静音功能
        self.pushButton_musicChange.clicked.connect(self.music_change)              # 切换歌曲功能

    # 播放与暂停音乐功能
    def music_play_pause(self):
        if self.player.state() == 1:
            self.player.pause()
            self.pushButton_play_pause.setIcon(QIcon('icons/play.png'))
        else:
            self.player.play()
            self.pushButton_play_pause.setIcon(QIcon('icons/pause.png'))

    # 静音功能
    def sound_change(self):
        if self.player.isMuted():
            self.player.setMuted(False)
            self.pushButton_sound.setIcon(QIcon('icons/sound_on'))
        else:
            self.player.setMuted(True)
            self.pushButton_sound.setIcon(QIcon('icons/sound_off'))

    # 切换问题功能——切换后问题不能与切换前相同
    def question_change(self):
        question = self.label_question.text()
        # 如果切换后与切换前相同,则继续切换
        while True:
            text = self.question_list[random.randint(0, len(self.question_list)-1)]
            if text == question:
                continue
            else:
                self.label_question.setText(text)
                break

    # 切换歌曲功能——切换后歌曲不能与切换前相同(直接切换为下一首)
    def music_change(self):
        if self.playlist.currentIndex() == self.playlist.mediaCount() - 1:
            self.playlist.setCurrentIndex(0)
        else:
            self.playlist.next()
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
                self.label_time.setText('{}:0{}'.format(minutes, seconds))
            else:
                self.label_time.setText('{}:{}'.format(minutes, seconds))

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

    # 实现验证功能
    def verify(self):
        # 根据音频媒体索引链接字典得到当前播放歌曲路径
        try:
            music = self.music_index_dict[str(self.playlist.currentIndex())]
        except KeyError:
            QMessageBox.warning(self, "注意", "请先听提示音频！")
            return
        # 根据label_question的text值得到question
        question = self.label_question.text()
        # 循环hash表找到匹配验证答案
        answer = ""
        for index in range(1, 7):
            if self.verify_hashTable[index][0] == music and self.verify_hashTable[index][1] == question:
                answer = self.verify_hashTable[index][2]
        print(answer)
        # 提取用户输入验证答案
        verify_answer = self.lineEdit_verify_answer.text()
        # 若用户输入验证答案正确,则给出提示信息并跳转客户端
        if verify_answer == answer:
            QMessageBox.information(self, "提示", "恭喜你，得到了哥哥的认可！")
            self.player.pause()
            self.player.pause()
            # 成功验证后跳转到使用界面窗口
            self.switch_window.emit()
        # 若用户输入验证答案错误,则给出提示信息并清空输入框
        else:
            QMessageBox.warning(self, "注意", "验证答案错误！")
            self.lineEdit_verify_answer.clear()

    # 音频初始化
    def music_init(self):
        self.player.setPlaylist(self.playlist)
        self.music_list = ['musics/verify_jntm.mp3',
                           'musics/verify_hugme.mp3']
        index = 0
        for music_path in self.music_list:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(music_path)))    # 媒体播放列表添加歌曲
            self.music_index_dict[str(index)] = str(music_path)                      # 音频媒体索引链接字典添加歌曲
            index += 1
        self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)    # 设置为顺序播放

    # 问题列表初始化
    def question_init(self):
        self.question_list = ["这首歌的歌名是？",
                              "哥哥的练习时长是多少？",
                              "哥哥的成名曲是什么？"]
        self.label_question.setText(self.question_list[random.randint(0, len(self.question_list)-1)])

    # 验证hash表初始化
    def hashTable_init(self):
        self.verify_hashTable = {0: ["歌曲", "问题", "答案"],
                                 1: ["musics/verify_hugme.mp3", "这首歌的歌名是？", "hug me"],
                                 2: ["musics/verify_jntm.mp3", "这首歌的歌名是？", "只因你太美"],
                                 3: ["musics/verify_hugme.mp3", "哥哥的练习时长是多少？", "两年半"],
                                 4: ["musics/verify_jntm.mp3", "哥哥的练习时长是多少？", "两年半"],
                                 5: ["musics/verify_hugme.mp3", "哥哥的成名曲是什么？", "只因你太美"],
                                 6: ["musics/verify_jntm.mp3", "哥哥的成名曲是什么？", "只因你太美"]}

    # 控件阴影添加
    def add_shadow(self):
        # label控件阴影添加
        self.effect_shadow_label = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow_label.setOffset(0, 0)                               # 偏移
        self.effect_shadow_label.setBlurRadius(25)                             # 阴影半径
        self.effect_shadow_label.setColor(Qt.gray)                             # 阴影颜色
        self.label.setGraphicsEffect(self.effect_shadow_label)                 # 将设置套用到label控件中

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

