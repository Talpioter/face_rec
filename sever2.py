
#!/usr/bin/env python
#coding:utf-8
import os.path
import time
import cv2
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import logging
import recognition
import uuid
import base64
import random
import json
from tornado.escape import utf8, _unicode
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

            # file_raw = self.request.files["file"][0]["body"]
            # iamges = "m_%s.jpg" % file_name
            #
            # fin = open(iamges, "w")
            # print("success to open file")
            # fin.write(str(file_raw))
            # fin.close()

            # face_rec_reslut = recognition.face_reconition.images_to_vectors(file_name)

            self.write("OK")

            # params = json.loads(self.request.body.decode('utf-8'))
            params = self.request.files['file'][0]['body']
            print(type(params))
            print("图片提取成功！")
            # image_base64 = params["image_base64"]
            imgfile = base64.b64decode(params)
            print(type(imgfile))

            strtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            imgfilename = os.path.join(imgtempdir, strtime + str(random.randint(10000, 99999)) + '.jpg')
            with open(imgfilename, 'w') as obj:
                obj.write(imgfile)
            # logging.info('imgfilename : ' + imgfilename)
            # try:
            #     with open(imgfilename, 'w') as obj:
            #         obj.write(imgfile)
            # except:
            #     return {'message': 'write temp img file error'}
            #
            # img = cv2.imread(imgfile, 0)
            # cv2.imshow('image', img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # if 'image_base64' in params:
            #     image_base64 = params["image_base64"]
            # else:
            #     return {'message': 'no image_base64'}
            # # 从base64编码得到图像文件
            # try:
            #     imgfile = base64.b64decode(image_base64)
            # except:
            #     return{'message': 'base64.b64decode error'}

            #face_con_result = recognition.face_reconition.images_to_vectors(imgfile)

            self.render("user.html")
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            #
            # print(imgfile)
            # return imgfile

            # file_raw = self.request.files["file"][0]["body"]
            # print(type(file_raw))
            #
            # usr_home = os.path.expanduser('~')
            # file_name = "./src/tmp/m_%s.jpg" % file_name
            # print(file_name)

            # fin = open(file_name, "w")
            # print("success to open file")
            # fin.write(file_raw)
            # fin.close()

            # file_name = "%s" % uuid.uuid1()
            # file_raw = self.request.files["file"][0]["body"]
            # usr_home = os.path.expanduser('~')
            # file_name = usr_home + "./img/m_%s.jpg" % file_name
            # fin = open(file_name, "w")
            # fin.write(file_raw)
            # fin.close()

            # json_result = {"count": 2, "upperLeft_X": "861", "upperLeft_Y": "538", "lowerRight_X": "1004", "lowerRight_Y": "658"}
            # self.render("user.html", username=json_result, email=file_name, website=file_raw, language=usr_home)
            # self.set_header('Content-Type', 'application/json; charset=UTF-8')


handlers = [(r"/", IndexHandler), (r"/user", UserHandler)]

template_path = os.path.join(os.path.dirname(__file__), "template")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers, template_path)
    http_server = tornado.httpserver.HTTPServer(app)  # HTTPServer是一个单线程非阻塞HTTP服务器，执行HTTPServer一般要回调Application对象，并提供发送响应的接口
    http_server.listen(options.port)  # 建立了单进程的http服务
    tornado.ioloop.IOLoop.instance().start() # 表示可以接收来自HTTP的请求了。