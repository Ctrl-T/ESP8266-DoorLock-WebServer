from flask import Flask
import app_config
from flask_restful import Api
from http_server import HttpServer
from tcp_server import TCPListener, LogCollector


app = Flask(__name__)
app.config.from_object(app_config)
api = Api(app)
api.add_resource(HttpServer, '/api/unlock')
TCPListener(app_config.Port).start()
LogCollector().start()