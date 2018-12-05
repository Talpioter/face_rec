# -*- coding:utf-8 -*-
import json
import tensorflow as tf
import src.facenet
import src.align.detect_face
import numpy as np
from scipy import misc
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 防止CPU出问题


class face_reconition:
    def __init__(self):
        pass

    def image_array_align_data(image_arr, image_size=160, margin=32, gpu_memory_fraction=1.0,
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

        # 一定要把颜色通道标明，否则bounding_boxes会报 'str' object has no attribute 'shape' 错误
        img = misc.imread(image_arr, mode='RGB')
        bounding_boxes, _ = src.align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
        nrof_faces = bounding_boxes.shape[0]

        print("检测的人脸个数为：{}".format(nrof_faces))

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

            facedic = {}
            facedic['count'] = nrof_faces
            for i, det in enumerate(det_arr):
                det = np.squeeze(det)
                bb = np.zeros(4, dtype=np.int32)
                bb[0] = np.maximum(det[0] - margin / 2, 0)
                bb[1] = np.maximum(det[1] - margin / 2, 0)
                bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
                bb[3] = np.minimum(det[3] + margin / 2, img_size[0])

                facedic['face%s_' % i + 'upperLeft_X'] = str(bb[1])
                facedic['face%s_' % i + 'upperLeft_Y'] = str(bb[0])
                facedic['face%s_' % i + 'lowRight_X'] = str(bb[3])
                facedic['face%s_' % i + 'lowRight_Y'] = str(bb[2])

                print("bb0=" + str(bb[0]), "bb1=" + str(bb[1]), "bb2=" + str(bb[2]), "bb3=" + str(bb[3]))

        faceresult = json.dumps(facedic)
        print(faceresult)
        return faceresult
