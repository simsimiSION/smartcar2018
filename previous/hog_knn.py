import cv2
from sklearn import neighbors

class hog_knn():
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
            for i in range(1,4):
                self.bow_kmeans_trainer.add(self.extract_sift(self.getPath(label, i)))

        voc = self.bow_kmeans_trainer.cluster()
        self.extract_bow.setVocabulary(voc)

        self.knn = neighbors.KNeighborsClassifier()
        self.knn_train()




    #返回路径信息
    def getPath(self, num, index):
        return 'digital/' + str(num)+ '_' + str(index) + '.jpg'

    # 读取图像并提取sift特征
    def extract_sift(self, fn):
        im = cv2.imread(fn, 0)
        return self.extract.compute(im, self.detect.detect(im))[1]

    # 返回box特征
    def bow_features(self, im):
        return self.extract_bow.compute(im, self.detect.detect(im))

    #训练knn分类器
    def knn_train(self, LIMIT=20):
        traindata = []
        trainlabel = []
        for label in range(10):
            for i in range(1,4):
                traindata.extend(self.bow_features(cv2.imread(self.getPath(label, i))))
                trainlabel.append(label)

        self.knn.fit(traindata, trainlabel)
        score = self.knn.score(traindata, trainlabel)



    #预测svm
    def predict(self, fn):
        return self.knn.predict(self.bow_features(fn))


if __name__ == '__main__':
    im = cv2.imread('digital/1_2.jpg')
    Hog = hog_knn()
    print(Hog.predict(im))
