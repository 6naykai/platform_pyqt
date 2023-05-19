##################################################################
# 下载线程
##################################################################
import requests
from PyQt5.QtCore import QThread, pyqtSignal


class downloadThread(QThread):
    download_proess_signal = pyqtSignal(int)  # 创建信号

    def __init__(self, url, filesize, fileobj, buffer):
        super(downloadThread, self).__init__()
        self.url = url
        self.filesize = filesize
        self.fileobj = fileobj
        self.buffer = buffer
        self.proess = 0

    def run(self):
        try:
            rsp = requests.post(self.url, stream=True)  # 流下载模式
            offset = 0
            for chunk in rsp.iter_content(chunk_size=self.buffer):
                if not chunk: break
                self.fileobj.seek(offset)  # 设置指针位置
                self.fileobj.write(chunk)  # 写入文件
                offset = offset + len(chunk)
                proess = offset / int(self.filesize) * 100
                self.proess = int(proess)
                self.download_proess_signal.emit(int(proess))  # 发送信号
            #######################################################################
            self.fileobj.close()  # 关闭文件
            self.exit(0)  # 关闭线程

        except Exception as e:
            print(e)
