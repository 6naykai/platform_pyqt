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
        self.headers_json = {"content-type": "application/json"}
        self.headers_file = {"content-filetype": "multipart/form-data"}

    def response_json(self, payload=None):
        """
        返回函数
        :param payload: 需要传入的参数,字典类型(可不传入)
        :return: 传回后端返回数据,字典型
        """
        if payload is not None:
            res = requests.post(self.url, json=payload, headers=self.headers_json).json()
        else:
            res = requests.post(self.url, headers=self.headers_json).json()
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
        暂时废弃,(因控件连接关系,必须放入类函数中构建)
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

    def uploadFile_response(self, filePath, fileName, fileType):
        """
        上传文件函数,返回状态和信息的字典
        :param fileType: 上传文件的文件类型
        :param fileName: 上传文件的文件名称
        :param filePath: 上传的文件所在的绝对路径
        :return: 字典
        """
        # 文件
        myfiles = {
            'file': open(filePath, 'rb')
        }
        # 文件备注: data=mydata
        mydata = {
            'fileName': fileName,
            'fileType': fileType
        }
        res = requests.post(self.url, headers=self.headers_file, data=mydata, files=myfiles).json()
        return res
