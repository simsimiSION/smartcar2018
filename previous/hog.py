import cv2
import numpy as np
from os.path import join


class hog():
    def __init__(self):
        # sift特征提取
        self.detect = cv2.xfeatures2d.SIFT_create()
        self.extract = cv2.xfeatures2d.SIFT_create()
        # flann匹配器
        flann_params = dict(algorithm=1, trees=5)
        matcher = cv2.FlannBasedMatcher(flann_params, {})
        # box训练器
        self.bow_kmeans_trainer = cv2.BOWKMeansTrainer(40)
        self.extract_bow = cv2.BOWImgDescriptorExtractor(self.extract, matcher)
        #训练特征
        for label in range(10):
            for i in range(30):
                self.bow_kmeans_trainer.add(self.extract_sift(self.getPath(i+1000*label)))

        voc = self.bow_kmeans_trainer.cluster()
        self.extract_bow.setVocabulary(voc)

        self.svm = dict()
        for label in range(10):
            self.svm[label] = cv2.ml.SVM_create()

        self.svm_train()




    #返回路径信息
    def getPath(self, num):
        return './data/' + str(num) + '.jpg'

    #读取图像并提取sift特征
    def extract_sift(self, fn):
        im = cv2.imread(fn, 0)
        return self.extract.compute(im, self.detect.detect(im))[1]

    #返回box特征
    def bow_features(self, im):
        return self.extract_bow.compute(im, self.detect.detect(im))

    #训练svm分类器
    def svm_train(self, LIMIT=45):
        for label in range(10):
            traindata = []
            trainlabel = []
            #添加正样本
            for i in range(LIMIT):
                traindata.extend(self.bow_features(cv2.imread(self.getPath(label*1000 + i))))
                trainlabel.append(1)
            #添加负样本
            for i in range(LIMIT):
                if int(i/5) == label:
                    pass
                else:
                    traindata.extend(self.bow_features(cv2.imread(self.getPath(int(i/5)*1000+i))))
                    trainlabel.append(-1)
            self.svm[label].train(np.array(traindata), cv2.ml.ROW_SAMPLE, np.array(trainlabel))

    #预测svm
    def predict(self, fn):
        pred = []
        output = 0
        for label in range(10):
            pred.append(self.svm[label].predict(self.bow_features(fn))[1][0][0])

        for i in range(10):
            if pred[i] > 0:
                output = i
                break
        return [output]



if __name__ == '__main__':
    im = cv2.imread('./data/4800.jpg')
    Hog = hog()
    print(Hog.predict(im))