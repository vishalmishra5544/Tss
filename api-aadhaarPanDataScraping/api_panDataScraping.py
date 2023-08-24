import numpy as np
import cv2
from PIL import Image
import os
import layoutparser as lp
from deskew import determine_skew
import imutils
import time
import multiprocessing
import base64
import pytesseract
import shutil

def ocrImgPAN(image):
    text = pytesseract.image_to_string(image, config= "--psm 10", lang= "eng")
    return text

def img2base64(segmentImage, imgType):
    _, buffer = cv2.imencode(f".{imgType}", segmentImage)
    img2Text = base64.b64encode(buffer).decode('utf-8')
    return img2Text

def pan1ImgData(img, imgName, panClass1Model, isRotated):
    temp = imgName.split(".")
    img = cv2.resize(img, (650, 550), cv2.INTER_AREA)
    layout = panClass1Model.detect(img)
    listBlocks = lp.Layout([b for b in layout if b.type in ["dob", "fathersname", "name", "header", "pannum", "photo", "signature"]])
    dic = {}
    panData = {}
    segmentArray = []
    blockTypeArray = []
    for block in listBlocks:
        segmentImage = (block.pad(left=5, right=5, top=5, bottom=5).crop_image(img))
        blockType = block.type
        encodedImg = img2base64(segmentImage, temp[1])
        panData[blockType]= {"image": encodedImg}
        if blockType in ["dob", "fathersname", "name", "pannum"]:
            gray = cv2.cvtColor(segmentImage, cv2.COLOR_BGR2GRAY)
            threshold = 67
            ret, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
            grayWhiteImg = cv2.bitwise_not(thresh)
            blurred = cv2.GaussianBlur(grayWhiteImg, (3, 3), cv2.BORDER_DEFAULT)
            segmentArray.append(blurred)
            blockTypeArray.append(blockType)


    t1 = time.time()
    if len(segmentArray)>0:
        with multiprocessing.Pool(processes=len(segmentArray)) as pool:            
            # pool = multiprocessing.Pool(processes=len(segmentArray))
            resultsPool = pool.map(ocrImgPAN, segmentArray)
            pool.close()
            pool.join()
            dic = dict(zip(blockTypeArray, resultsPool))

    for key in panData.keys():
        if key in dic:
            panData[key]['data'] = dic[key].strip().replace('\n', '').replace('\f', '')
    print("Multip1ro results & time in class 1: ", imgName, time.time()-t1)
    return panData



def pan2ImgData(img, imgName, panClass2Model, isRotated):
    temp = imgName.split(".")
    img = cv2.resize(img, (650, 550), cv2.INTER_AREA)
    layout = panClass2Model.detect(img)
    listBlocks = lp.Layout([b for b in layout if b.type in ["dob", "fathersname", "name", "pannum", "photo", "signature"]])
    dic = {}
    panData = {}
    segmentArray = []
    blockTypeArray = []
    for block in listBlocks:
        segmentImage = (block.pad(left=5, right=5, top=5, bottom=5).crop_image(img))
        blockType = block.type
        encodedImg = img2base64(segmentImage, temp[1])
        panData[blockType]= {"image": encodedImg}
        if blockType in ["dob", "fathersname", "name", "pannum"]:
            gray = cv2.cvtColor(segmentImage, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (3, 3), cv2.BORDER_DEFAULT)
            segmentArray.append(blurred)
            blockTypeArray.append(blockType)

            
    t1 = time.time()
    if len(segmentArray)>0:
        with multiprocessing.Pool(processes=len(segmentArray)) as pool:
            # pool = multiprocessing.Pool(processes=len(segmentArray))
            resultsPool = pool.map(ocrImgPAN, segmentArray)
            pool.close()
            pool.join()
            dic = dict(zip(blockTypeArray, resultsPool))
    for key in panData.keys():
        if key in dic:
            panData[key]['data'] = dic[key].strip().replace('\n', '').replace('\f', '')
    print("Multip1ro results & time in class 2: ", imgName, time.time()-t1)
    return panData



def rotateImageClass1(img, rotationModel):
    try:
        adImg = cv2.resize(img, (600, 600), cv2.INTER_AREA)
        imgFlatten = np.array(adImg).flatten()
        prediction = rotationModel.predict(list([imgFlatten]))
        imgRotated = imutils.rotate_bound(adImg, prediction[0])
        isRotated = True
        return imgRotated, isRotated
        
    except Exception:
        isRotated = False
        return img, isRotated



def rotateImageClass2(img, rotationModel):
    try:
        adImg = cv2.resize(img, (600, 600), cv2.INTER_AREA)
        imgFlatten = np.array(adImg).flatten()
        prediction = rotationModel.predict(list([imgFlatten]))
        imgRotated = imutils.rotate_bound(adImg, prediction[0])
        isRotated = True
        return imgRotated, isRotated
        
    except Exception:
        isRotated = False   
        return img, isRotated


def imgDeskew(img, background = (0, 0, 0)):
    img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    angle = determine_skew(img)
    oldWidth, oldHeight = img.shape[:2]
    width = abs(np.sin(np.radians(angle)) * oldHeight) + abs(np.cos(np.radians(angle)) * oldWidth)
    height = abs(np.sin(np.radians(angle)) * oldWidth) + abs(np.cos(np.radians(angle)) * oldHeight)
    imgCenter = tuple(np.array(img.shape[1::-1]) / 2)
    rotMat = cv2.getRotationMatrix2D(imgCenter, angle, 1.0)
    rotMat[1, 2] += (width - oldWidth) / 2
    rotMat[0, 2] += (height - oldHeight) / 2
    img = Image.fromarray(cv2.warpAffine(img, rotMat, (int(round(height)), int(round(width))), borderValue=background))
    result = np.array(img)
    return result



def imgPreprocess(img, imgName):
    pathDPI = f"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/api-aadhaarPanDataScraping/dpi300/{imgName}"
    img = cv2.resize(img, (600, 600), cv2.INTER_AREA)
    img = Image.fromarray(img)
    img.save(pathDPI,dpi=(300, 300))
    deskewedImage = imgDeskew(pathDPI)
    shutil.rmtree("/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/api-aadhaarPanDataScraping/dpi300", ignore_errors=True)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    dst = clahe.apply(deskewedImage)
    img = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    return img



def pan1DataExt(img, imgName, panClass1Model, pan1RotationModel, cardType):
    if cardType == "big":
        img = imgPreprocess(img, imgName)
    img, isRotated = rotateImageClass1(img, pan1RotationModel)
    data = pan1ImgData(img, imgName, panClass1Model, isRotated)
    return data



def pan2DataExt(img, imgName, panClass2Model, pan2RotationModel, cardType):
    if cardType == "big":
        img = imgPreprocess(img, imgName)
    img, isRotated = rotateImageClass2(img, pan2RotationModel)
    data = pan2ImgData(img, imgName, panClass2Model, isRotated)
    return data
