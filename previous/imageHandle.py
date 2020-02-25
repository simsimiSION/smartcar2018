import cv2
import numpy as np
import matplotlib.pyplot as plt
from detect_img import mnist
from alexnet import alexnet
from hog import hog
from hog_knn import hog_knn

def imageRead(image_file, type=1, therehold=None):
    """
    :param image_file:
    :param type: 0 二值化 1 灰度 2彩色
    :return:
    """

    if type == 0:
        img = cv2.imread(image_file, cv2.IMREAD_COLOR)
    elif type == 1:
        img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
    elif type == 2:
        assert therehold != None
        img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img, therehold, 255, cv2.THRESH_BINARY)
    else:
        raise Exception('输入的图像类型有误')

    return img

def imageG2B(img, therehold):
    _, img = cv2.threshold(img, therehold, 255, cv2.THRESH_BINARY)
    return img

def imageShow(windows, imgs):
    assert len(windows) == len(imgs)

    for window, img in zip(windows, imgs):
        cv2.imshow('%s' % window, img)

def imageResize(img, size):
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)

def imagePerTransfer(img, src, dis, size=(300,300)):
# 自己选择要进行透视变换的点 [左上, 右上, 左下, 右下]
    src_array = np.array(src)
    dis_array = np.array(dis)
    M = cv2.getPerspectiveTransform(src_array, dis_array)
    dis_martix = cv2.warpPerspective(img, M, size)

    return dis_martix

def imageDilate(img, kernel=None):
    if kernel == None:
        kernel = np.zeros((5,5), dtype=np.uint8)
        kernel[1:4,1:4] = np.ones((3,3), dtype=np.uint8)

    dilated = cv2.dilate(img, kernel)

    return dilated

def imageErode(img, kernel=None):
    if kernel == None:
        kernel = np.zeros((5,5), dtype=np.uint8)
        kernel[1:4,1:4] = np.ones((3,3), dtype=np.uint8)

    eroded = cv2.erode(img, kernel)

    return eroded

def imageContours(img, reverse=True, area=4000, limit=[0.6, 1.6]):
    image = img.copy()
    _, image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)

    image, contours, hier = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in contours:
        #box  1 2
        #     0 3
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        if (box[3][0] - box[0][0]) * (box[0][1] - box[1][1]) >= area and \
                float ((box[3][0] - box[0][0]) / (box[0][1] - box[1][1])) > limit[0] and\
                float((box[3][0] - box[0][0]) / (box[0][1] - box[1][1])) < limit[1]:
            #cv2.drawContours(img_g, [box], 0, (0, 0, 255), 3)
            boxes.append(box)

    return boxes

def imageCountourHandle(img, countours):
    image_list = []

    def whiteHandle(image, therehold):
        BLACK = 0
        _, img = cv2.threshold(image, therehold, 255, cv2.THRESH_BINARY)

        height, width = image.shape
        up = down = left = right = 0
        #处理上边界
        for i in range(5):
            if sum(img[i,:] == BLACK) > int(width * 0.9):
                up = i
                break
            if  i == 4:
                up = i
        #处理下边界
        for i in range(5):
            if sum(img[height-i-1,:] == BLACK) > int(width * 0.9):
                down = height-i
                break
            if  i == 4:
                down = height-i
        # 处理左边界
        for i in range(5):
            if sum(img[:, i] == BLACK) > int(height * 0.9):
                left = i
                break
            if i == 4:
                left = i
        # 处理右边界
        for i in range(5):
            if sum(img[:, width-i-1] == BLACK) > int(height * 0.9):
                right = width-i
                break
            if i == 4:
                right = width-i
        return image[up:down,left:right]

    for index, contour in enumerate(contours):
        Xs = [i[0] for i in contour]
        Ys = [i[1] for i in contour]
        x1 = min(Xs)
        x2 = max(Xs)
        y1 = min(Ys)
        y2 = max(Ys)
        cropImg = img.copy()
        temp_img = imagePerTransfer(cropImg,
                                    np.float32([contour[1], contour[2], contour[0], contour[3]]),
                                    np.float32([[0, 0], [y2-y1, 0], [0, x2-x1], [y2-y1, x2-x1]]),
                                    (y2-y1,x2-x1))

        temp_img = whiteHandle(temp_img, 200)

        image_list.append(temp_img)

    return image_list

def imagePiexlDistrib(img):
    _, image = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
    height, width = image.shape

    WHITE = 255
    piexl_distrib = []
    for i in range(width):
        piexl_distrib.append(sum(image[:,i] == WHITE))

    return piexl_distrib

def imageSplitDueDistrib(img):
    LIMIT = 10
    INNER_LIMIT = 2

    distrib = imagePiexlDistrib(img)
    distrib_len = len(distrib)

    image_list = []
    status = count = left = right = dis_pointer =  0
    for index, pointer in enumerate(distrib):
        if pointer > LIMIT and status == 0:
            count += 1
            if count > INNER_LIMIT:
                status = 1
                count = 0
        if pointer < LIMIT and status == 1:
            count += 1
            if count > INNER_LIMIT:
                status = 2
                left = index - INNER_LIMIT
                count = 0
        if pointer > LIMIT and status == 2:
            count += 1
            if count > INNER_LIMIT:
                status = 3
                right = index - INNER_LIMIT
        if status == 3:
            dis_pointer = int((left + right)/2)
            break

    flag = 0
    if status == 3:
        image_temp = img[:,:dis_pointer]
        image_temp = imageResize(image_temp, (36, 36))
        image_list.append(image_temp)
        image_temp = img[:,dis_pointer:]
        image_temp = imageResize(image_temp, (36, 36))
        image_list.append(image_temp)
        flag = 1
    else:
        image_temp = imageResize(img, (36, 36))
        image_list.append(image_temp)


    return flag, image_list

def getMeanPiexl(image):
    #get image size
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    w, h = image.shape
    size = h * w

    #compute the mean piexl
    image_array = np.array(image).reshape(-1)
    image_array = sorted(image_array)
    mean_piexl = (image_array[0] + image_array[size-1] ) / 2

    return mean_piexl

def batchWithNoise(batch):
    imgs  = batch[0]
    label = batch[1]
    batch_len = len(label)

    new_batch_img = []
    new_batch = []

    for index, ori in enumerate(imgs):
        img = np.zeros((36,36), dtype=np.float)
        ori = np.array(ori).reshape((28,28))


        # img 36*36
       # img[4:28+4, 4:28+4] = ori[:,:]
        main_param = np.random.randint(0,6)
        inn_param = np.random.randint(0,2)
        param = np.random.randint(1,5)

        if main_param > 3:
            if inn_param == 1:
                if param == 1:
                    img[:2,:15]  = np.random.rand(2,15)
                    img[8:28+8, 4:28+4] = ori[:,:]
                elif param == 2:
                    img[:15,34:] = np.random.rand(15,2)
                    img[4:28+4,0:28+0] = ori[:,:]
                elif param == 3:
                    img[34:,:15] = np.random.rand(2,15)
                    img[0:28+0,4:28+4] = ori[:,:]
                elif param == 4:
                    img[:15,:2] = np.random.rand(15,2)
                    img[4:28+4,8:28+8] = ori[:,:]
                else:
                    img[4:28 + 4, 4:28 + 4] = ori[:, :]
            else:
                if param == 1:
                    img[:2, 20:] = np.random.rand(2, 16)
                    img[8:28 + 8, 4:28 + 4] = ori[:, :]
                elif param == 2:
                    img[20:, 34:] = np.random.rand(16, 2)
                    img[4:28 + 4, 0:28 + 0] = ori[:, :]
                elif param == 3:
                    img[34:, 20:] = np.random.rand(2, 16)
                    img[0:28 + 0, 4:28 + 4] = ori[:, :]
                elif param == 4:
                    img[20:, :2] = np.random.rand(16, 2)
                    img[4:28 + 4, 8:28 + 8] = ori[:, :]
                else:
                    img[4:28 + 4, 4:28 + 4] = ori[:, :]
        else:
            img[4:28 + 4, 4:28 + 4] = ori[:, :]



        img = img.reshape(-1)
        new_batch_img.append(img)

    new_batch.append(new_batch_img)
    new_batch.append(label)

    return tuple(new_batch)

def getProbably():
    pass






if __name__ == '__main__':
    Model = alexnet()#hog_knn()## #hog()#mnist()
    #cap = cv2.VideoCapture(0)
    #读取图像
    while True:
        #ret, img_file = cap.read()
        img_file = 'image/6.jpg'
        img_g = imageRead(img_file)
        #img_g = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        img_origin = img_g.copy()
        #生成灰度图像
        src = np.float32([[185,0], [420,0], [100,470], [500,470]])
        dis = np.float32([[0,0],[300,0],[0,300],[300,300]])
        img_g = imagePerTransfer(img_g, src, dis)
        #生成二值化图像
        img_b = imageG2B(img_g, 200)
        img_b = imageDilate(img_b)
        #找框框
        contours = imageContours(img_b, img_g)
        image_list = imageCountourHandle(img_g, contours)
        number_list = []

        font = cv2.FONT_HERSHEY_SIMPLEX

        for image, contour in zip(image_list, contours):
            double, imagesp = imageSplitDueDistrib(image)
            if double:
                _, im_1 = cv2.threshold(imagesp[0], 200, 255, cv2.THRESH_BINARY)
                _, im_2 = cv2.threshold(imagesp[1], 200, 255, cv2.THRESH_BINARY)
                number_list.append( Model.predict(im_1)[0] * 10 + Model.predict(im_2)[0])

                cv2.putText(img_g, str(Model.predict(im_1)[0] * 10 + Model.predict(im_2)[0]), (contour[0][0], contour[0][1]), font, 0.8,(0, 255, 0),2)
                cv2.drawContours(img_g, [contour], 0, (0, 0, 255), 3)
            else:
                _, im_1 = cv2.threshold(imagesp[0], 200, 255, cv2.THRESH_BINARY)
                number_list.append(Model.predict(im_1)[0])

                cv2.putText(img_g, str(Model.predict(im_1)[0]), (contour[0][0], contour[0][1]), font, 0.8, (0, 255, 0),2)
                cv2.drawContours(img_g, [contour], 0, (0, 0, 255), 3)


        imageShow(['origin','gray', 'bin' ], [img_origin, img_g, img_b])
        cv2.waitKey(1)












