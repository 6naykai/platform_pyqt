import json
import requests
from util import url, music_storePath, game_storePath, downloadThread


class MyPost:
    def __init__(self, addr):
        """
        MyPost类构建
        :param addr: 后端接口url后缀
        """
        self.url = url + addr
        self.headers = {"content-type": "application/json"}

    def response_json(self, payload=None):
        """
        返回函数
        :param payload: 需要传入的参数,字典类型(可不传入)
        :return: 传回后端返回数据,字典型
        """
        if payload is not None:
            res = requests.post(self.url, json=payload, headers=self.headers).json()
        else:
            res = requests.post(self.url, headers=self.headers).json()
        # print(res)
        # print(res.text)
        # myjson = json.loads(res.text)  # data是向 api请求的响应数据，data必须是字符串类型的
        # print(myjson)
        # newjson = json.dumps(myjson, ensure_ascii=False)  # ensure_ascii=False 就不会用 ASCII 编码，中文就可以正常显示了
        # print(newjson)
        return res

    def download_music(self, musicName):
        r = requests.post(self.url, stream=True)
        storePath = music_storePath + musicName + '.mp3'
        f = open(storePath, "wb")
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
        return "{}下载完成".format(musicName)

    def download_game(self, gameName, progressbar):
        """
        暂时废弃
        :param gameName:
        :param progressbar:
        :return:
        """
        the_filesize = self.getContentLength()
        the_filepath = game_storePath + gameName + '.exe'
        the_fileobj = open(the_filepath, 'wb')
        #### 创建下载线程
        self.downloadThread = downloadThread(self.url, the_filesize, the_fileobj, buffer=10240)
        self.downloadThread.download_proess_signal.connect(progressbar.set_progressbar_value)
        self.downloadThread.start()

    def getContentLength(self):
        the_filesize = requests.post(self.url, stream=True).headers['Content-Length']
        return the_filesize
