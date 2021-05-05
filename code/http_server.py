from flask_restful import Resource, reqparse, abort
import app_config
import threading
import time
from tcp_server import get_client

class HttpServer(Resource): 
    def post(self):
        tcp_client = get_client()
        parser = reqparse.RequestParser()
        parser.add_argument('data', type=str, required=True)
        args = parser.parse_args()
        if args['data'] != app_config.Token:
            abort(403, msg="Token错误!")
        if tcp_client is None:
            abort(404, msg="门锁不在线!")
        try:
            tcp_client.send('OPEN\n'.encode())
        except:
            old_client = tcp_client
            tcp_client = None
            old_client.close()
            abort(500, msg='向门锁发送数据出错!')
        return {'msg': '开锁成功!'}
