# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
import uuid
import tensorflow as tf
import src.facenet
import src.align.detect_face
import numpy as np
from scipy import misc
import os
import json
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # 防止CPU出问题


class face_recongition:
    def __init__(self):
        pass

    def prewhiten(self, x):
        mean = np.mean(x)
        std = np.std(x)
        std_adj = np.maximum(std, 1.0 / np.sqrt(x.size))
        y = np.multiply(np.subtract(x, mean), 1 / std_adj)
        return y

    # 根据路径获取该文件夹中所有的图片
    def get_image_paths(self, inpath):
        paths = []
        for file in os.listdir(inpath):
            if os.path.isfile(os.path.join(inpath, file)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')) is False:
                    continue

                paths.append(os.path.join(inpath, file))

        return (paths)

    # 将一个文件夹下的所有图片转化为json
    # 方法二：只能是传入文件夹 ，并存入数据库
    def images_to_vectors(self, inpath, outjson_path, modelpath):
            results = dict()

            with tf.Graph().as_default():
                with tf.Session() as sess:
                    src.facenet.load_model(modelpath)
                    # Get input and output tensors
                    images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
                    embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
                    phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

                    image_paths = self.get_image_paths(inpath)
                    for image_path in image_paths:
                        # 获取图片中的人脸数
                        img = misc.imread(os.path.expanduser(image_path), mode='RGB')
                        images = self.image_array_align_data(img, image_path)
            return images
                        # 判断是否检测出人脸 检测不出 就跳出此循环
                        # if images.shape[0] == 1: continue
                        # feed_dict = {images_placeholder: images, phase_train_placeholder: False}
                        #
                        # emb_array = sess.run(embeddings, feed_dict=feed_dict)
                        #
                        # filename_base, file_extension = os.path.splitext(image_path)
            #             for j in range(0, len(emb_array)):
            #                 results[filename_base + "_" + str(j)] = emb_array[j].tolist()
            #                 face_mysql_instant = face_mysql.face_mysql()
            #                 face_mysql_instant.insert_facejson(filename_base + "_" + str(j),
            #                                                    ",".join(str(li) for li in emb_array[j].tolist()))
            #
            # # All done, save for later!
            # json.dump(results, open(outjson_path, "w"))
            # 返回图像中所有人脸的向量

    def image_array_align_data(self, image_arr, image_path,  image_size=160, margin=32, gpu_memory_fraction=1.0,
                               detect_multiple_faces=True):
        minsize = 20  # minimum size of face
        threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        factor = 0.709  # scale factor

        print('Creating networks and loading parameters')
        with tf.Graph().as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
            sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            with sess.as_default():
                pnet, rnet, onet = src.align.detect_face.create_mtcnn(sess, None)

        img = image_arr
        # 返回边界框数组 （参数分别是输入图片,脸部最小尺寸,三个网络,阈值,factor不清楚）
        bounding_boxes, points = src.align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
        nrof_faces = bounding_boxes.shape[0]
        print("检测的人脸个数为：{}".format(nrof_faces))
        print(points)

        nrof_successfully_aligned = 0
        if nrof_faces > 0:
            det = bounding_boxes[:, 0:4]
            det_arr = []
            img_size = np.asarray(img.shape)[0:2]
            if nrof_faces > 1:
                if detect_multiple_faces:
                    for i in range(nrof_faces):
                        det_arr.append(np.squeeze(det[i]))
                else:
                    bounding_box_size = (det[:, 2] - det[:, 0]) * (det[:, 3] - det[:, 1])
                    img_center = img_size / 2
                    offsets = np.vstack(
                        [(det[:, 0] + det[:, 2]) / 2 - img_center[1], (det[:, 1] + det[:, 3]) / 2 - img_center[0]])
                    offset_dist_squared = np.sum(np.power(offsets, 2.0), 0)
                    index = np.argmax(
                        bounding_box_size - offset_dist_squared * 2.0)  # some extra weight on the centering
                    det_arr.append(det[index, :])
            else:
                det_arr.append(np.squeeze(det))

            images = np.zeros((nrof_faces, image_size, image_size, 3))
            for i, det in enumerate(det_arr):
                det = np.squeeze(det)
                bb = np.zeros(4, dtype=np.int32)
                bb[0] = np.maximum(det[0] - margin / 2, 0)
                bb[1] = np.maximum(det[1] - margin / 2, 0)
                bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
                bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
                print("左上角列坐标bb0={}" .format(bb[0]), "左上角行坐标bb1={}".format(bb[1]), "右下角列坐标bb2={}".format(bb[2]),
                      "右下角行坐标bb3={}".format(bb[3]))
                dic = {}
                dic['count'] = str(nrof_faces)
                dic['upperLeft_X'] = str(bb[1])
                dic['upperLeft_Y'] = str(bb[0])
                dic['lowerRight_X'] = str(bb[3])
                dic['lowerRight_Y'] = str(bb[2])

                feeds_json = json.dumps(dic)
                print(feeds_json)
        return feeds_json



if __name__ == "__main__":
    face_recongition = face_recongition()
    images_path = './img/img'
    # 模型地址
    modelpath = 'D://GithubProjects//facenet_facerecognition//models//20180402-114759'
    out_path = './img/pic.json'
    face_recongition.images_to_vectors(images_path, out_path, modelpath)
