import json
import requests
from util import url


class MyPost:
    def __init__(self, addr):
        """
        MyPost类构建
        :param addr: 后端接口url后缀
        """
        self.url = url + addr
        self.headers = {"content-type": "application/json"}

    def response(self, payload):
        """
        返回函数
        :param payload: 需要传入的参数,字典类型
        :return: 传回后端数据,字典型
        """
        res = requests.post(self.url, json=payload, headers=self.headers).json()
        # print(res)
        # print(res.text)
        # myjson = json.loads(res.text)  # data是向 api请求的响应数据，data必须是字符串类型的
        # print(myjson)
        # newjson = json.dumps(myjson, ensure_ascii=False)  # ensure_ascii=False 就不会用 ASCII 编码，中文就可以正常显示了
        # print(newjson)
        return res


