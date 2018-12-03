
#!/usr/bin/env python
#coding:utf-8
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import face_mark_save
import uuid
import json

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class UserHandler(tornado.web.RequestHandler):

    def post(self):
        # if self.request.files:
        #     file_name = "%s" % uuid.uuid1()
        #     file_raw = self.request.files["file"][0]["body"]
        #     usr_home = os.path.expanduser('~')
        #     file_name = usr_home + "./img/m_%s.jpg" % file_name
        #     fin = open(file_name, "w")
        #     fin.write(file_raw)
        #     fin.close()

        # user_name = self.get_argument("username")
        # user_email = self.get_argument("email")
        # user_website = self.get_argument("website")
        # user_language = self.get_argument("language")
        #self.render("user.html", username=user_name, email=user_email, website=user_website, language=user_language)
        #
        json_result = {"count": 2, "upperLeft_X": "861", "upperLeft_Y": "538", "lowerRight_X": "1004", "lowerRight_Y": "658"}
        self.render("user.html", username=json_result, email=json_result, website=json_result, language=json_result)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        # self.write(json_result)
        # self.finish()


handlers = [(r"/", IndexHandler), (r"/user", UserHandler)]

template_path = os.path.join(os.path.dirname(__file__), "template")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers, template_path)
    http_server = tornado.httpserver.HTTPServer(app)  # HTTPServer是一个单线程非阻塞HTTP服务器，执行HTTPServer一般要回调Application对象，并提供发送响应的接口
    http_server.listen(options.port)  # 建立了单进程的http服务
    tornado.ioloop.IOLoop.instance().start() # 表示可以接收来自HTTP的请求了。