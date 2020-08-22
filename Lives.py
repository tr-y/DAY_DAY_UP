import requests
import re, json
import sys
import os
os.system('python ./venv/file_name.py')
from ffmpy3 import FFmpeg
import speech_recognition as sr
import sys
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# 取消注释可以去掉出现的警告


class LiveVideoDownload(object):
    def __init__(self, up_id, size, filename='None.flv'):
        self.up_id = up_id
        self.size_all = size
        self.filename = filename
        self.roomIdRegex = r'"//live\.bilibili\.com/{.*?}"'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}

    def getRoomId(self):
        url = 'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={}'.format(self.up_id)
        self.Referer = 'https://space.bilibili.com/{}/'.format(self.up_id)
        self.headers['Host'] = 'api.live.bilibili.com'
        self.headers['Referer'] = self.Referer
        response = requests.get(url=url, headers=self.headers).json()
        room_id = response['data']['roomid']
        return room_id

    def getJsonFile(self, room_id):
        url = 'https://api.live.bilibili.com/room/v1/Room/playUrl?cid={}'.format(room_id)
        content = requests.get(url=url, headers=self.headers).text
        return content

    def extract(self):
        room_id = self.getRoomId()
        data = self.getJsonFile(room_id)
        data_json = json.loads(data)
        download_url = data_json['data']['durl'][0]['url']
        host = download_url[8:].split('/')[0]
        return download_url, host

    def download(self):
        content = self.extract()
        url, host = content
        headers = self.headers
        headers['host'] = host
        headers['referer'] = self.Referer

        # 下载
        size = 0
        chunk_size = 1024
        response = requests.get(url, headers=headers, stream=True, verify=False)
        with open(self.filename, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                file.flush()
                if self.size_all > 0:
                    sys.stdout.write('  [下载进度]:%.2fMB/%.2fMB' % (
                    float(size / 10 / (self.size_all * 1024 * 1024) * 100), self.size_all) + '\r')
                    if size > self.size_all * 1024 * 1024:
                        break
                else:
                    sys.stdout.write('  [下载进度]:%.2fMB' % float(size / 1024 / 1024) + '\r')
        print('下载完成')



if __name__ == '__main__':
    up_id = '434565011'  # uid 号
    size_MB = 30  # size_MB=0 无限制下载，size_MB >0, 下载量为 [size_MB] MB
    filename = 'aky.flv'  # 下载文件名
    liveVideo = LiveVideoDownload(up_id=up_id,
                                  size=size_MB,
                                  filename=filename)
    liveVideo.download()

    #转换文件
    filepath = r"D:\project\python\Voice_Translate\\"  # 添加路径
    os.chdir(filepath)
    # os.path.nornmpath(filepath)
    # filename= os.listdir() #得到文件夹下的所有文件名称
    #
    outputpath = r"D:\project\python\Voice_Translate\enviroment\au\\"  # 添加路径
    os.chdir(outputpath)
    changefile = filepath + "aky.flv"
    outputfile = outputpath + "aky.wav"
    ff = FFmpeg(
        inputs={changefile: None},
        outputs={outputfile: ' -ab 128k -f wav'}
    )
    # ff.cmd
    ff.run()
    #将音频转成文字
    r = sr.Recognizer()

    harvards = sr.AudioFile('D:\project\python\Voice_Translate\enviroment/au/aky.wav')

    with harvards as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.record(source)
    text = r.recognize_google(audio, language='cmn-Hans-CN', show_all=True)
    print(text)