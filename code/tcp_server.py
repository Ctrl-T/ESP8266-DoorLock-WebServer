import socket
import app_config
import time
from datetime import datetime
import requests
import json
import threading
import re
import csv
import schedule

# 当前门锁客户端
tcp_client = None

# 获取当前门锁客户端
def get_client():
    global tcp_client
    return tcp_client

# 设置当前门锁客户端
def set_client(C):
    global tcp_client
    if tcp_client is not None:
        old_client = tcp_client
        old_client.close()
    tcp_client = C

# TCP服务器线程
class TCPListener(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        s = socket.socket()  # 创建 socket 对象
        host = '0.0.0.0'  # 获取本地主机名
        port = self.port  # 设置端口
        s.bind((host, port))  # 绑定端口
        set_keepalive_linux(s) # 保活
        s.listen(5)  # 等待客户端连接
        print(f'{get_local_time()}: V3.0 服务器启动')
        pushplus("服务器启动")
        while True:
            c, addr = s.accept()  # 建立客户端连接          
            if c.recv(1024) == b'Hello from ESP8266':
                set_client(c) # 保存连接
                print(f'{get_local_time()}: 门锁上线')
                pushplus("门锁上线")
                TCPHolder(app_config.Port, c).start() # 以新连接创建TCP监听线程
            else:
                pushplus('端口受到攻击')
                c.close()


class TCPHolder(threading.Thread):
    name_openers = ['finger', 'nfc', 'web']
    re_log = re.compile(r'\[(.*)\] success:(\d+) fail:(\d+)')
    fieldnames = ['date', 'finger-success', 'finger-fail', 'nfc-success', 'nfc-fail', 'web-success', 'web-fail']
    def __init__(self, port, client):
        threading.Thread.__init__(self)
        self.port = port
        self.client = client

    def run(self):
        print(f'{get_local_time()}: 等待门锁发送数据')
        while True:
            try:
                by = self.client.recv(1024)
                if len(by) == 0:
                    pushplus("门锁掉线")
                    raise Exception("终端掉线")
                print(f'{get_local_time()}: 接收数据{by}')
                pushplus(f'接收数据 {by}')
                data_recvd = by.decode("utf-8")
                # self.write_log(data_recvd)
                if (re.match(r'-log-.*-/log-', data_recvd, re.S|re.M)):
                    self.write_log(data_recvd)
            except BaseException as e:
                pushplus(f'等待接收数据出错，关闭连接，原因:{str(e)}')
                print(f'{get_local_time()}: 等待接收数据出错，关闭连接，原因:{str(e)}')
                if get_client() == self.client:
                    set_client(None)
                self.client.close()
                return

    def write_log(self, data_recvd):
        pushplus(f'原始数据：{data_recvd}')
        logs = self.re_log.findall(data_recvd)
        pushplus(f'正则结果：{logs}')
        dict_log = {'date': datetime.now().strftime('%Y/%m/%d')}
        for i in range(len(logs)):
            dict_log[logs[i][0] + '-success'] = logs[i][1]
            dict_log[logs[i][0] + '-fail'] = logs[i][2]
        pushplus(str(dict_log))
        with open('door_log.csv', 'a', newline='') as f:
            log_writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if f.tell() == 0:
                log_writer.writeheader()
            log_writer.writerow(dict_log)
            
            
def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
    
def get_local_time():
    return datetime.now().strftime('%Y/%m/%d %H:%M:%S')

def pushplus(content, title = "来自服务器的消息"):
    token = 'd97a25a23cd7480599fc8a4836a0c44d'
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content
    }
    body=json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type':'application/json'}
    requests.post(url, data=body, headers=headers)

def collect_log():
    global tcp_client
    if tcp_client is None:
        return
    tcp_client.send("LOG\n".encode())


class LogCollector(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        schedule.every().day.at('23:50').do(collect_log)
        # schedule.every(1).minutes.do(collect_log)
        while True:
            schedule.run_pending()
            time.sleep(1)
