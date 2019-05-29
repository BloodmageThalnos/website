import datetime
import os
from urllib import request

def download():
    url = "http://littledva.cn/getmusic/19_summer/%E6%9D%80%E6%AD%BB%E9%82%A3%E4%B8%AA%E7%9F%B3%E5%AE%B6%E5%BA%84%E4%BA%BA.mp3"
    path = "./1.mp3"

    max_size = 50*1024*1024*8 # 50MB
    chunk_size = 1024*1024

    time = datetime.datetime.now()
    with request.urlopen(url) as fr:
        fw = open(path, mode="wb")
        tot_size = 0
        while True:
            chunk = fr.read(chunk_size)
            if not chunk:
                break
            fw.write(chunk)
            tot_size += chunk_size
            print('downloaded %d KB'%(tot_size//(1024*8)))
            if tot_size > max_size:
                fw.close()
                os.remove(path)
                return None, False
    cost_time = datetime.datetime.now() - time
    print("Speed: %d KB/s"%(tot_size/cost_time//(1024*8)))


download()