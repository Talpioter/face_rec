#!/usr/bin/env python
#coding:utf-8
import os.path
import time
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import recognition
import uuid
import random
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 防止CPU出问题
from tornado.options import define, options
define("port", default=8080, help="run on the given port", type=int)

imgtempdir = './tmp/'


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class UserHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        if self.request.files:
            file_name = "%s" % uuid.uuid1()
            print(file_name)
            self.write("OK")
            params = self.request.files['file'][0]['body']
            strtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            imgfilename = os.path.join(imgtempdir, strtime + str(random.randint(10000, 99999)) + '.jpg')
            with open(imgfilename, 'wb') as obj:
                obj.write(params)

            result = recognition.face_reconition.image_array_align_data(imgfilename)
            print(result)

            self.render("user.html", jsondata=result)
            self.set_header('Content-Type', 'application/json; charset=UTF-8')


handlers = [(r"/", IndexHandler), (r"/user", UserHandler)]

template_path = os.path.join(os.path.dirname(__file__), "template")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers, template_path)

    # HTTPServer是一个单线程非阻塞HTTP服务器，执行HTTPServer一般要回调Application对象，并提供发送响应的接口
    http_server = tornado.httpserver.HTTPServer(app)

    # 建立了单进程的http服务
    http_server.listen(options.port)

    # 表示可以接收来自HTTP的请求了
    tornado.ioloop.IOLoop.instance().start()