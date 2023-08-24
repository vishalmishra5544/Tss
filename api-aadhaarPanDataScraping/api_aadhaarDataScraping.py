import numpy as np
import cv2
from PIL import Image
import os
import layoutparser as lp
from deskew import determine_skew
import imutils
import time
import multiprocessing
import pytesseract
import base64
import shutil

def ocrImgAadhaar(image):
    text = pytesseract.image_to_string(image, config= "--psm 10", lang= "eng")
    return text


def img2base64(segmentImage, imgType):
    retval, buffer = cv2.imencode(f".{imgType}", segmentImage)
    img2Text = base64.b64encode(buffer).decode('utf-8')
    return img2Text



def smallImgData(img, imgName, isRotated, aadhaarModel):
    temp = imgName.split(".")
    img = cv2.resize(img, (650, 550), cv2.INTER_AREA)
    layoutResult = aadhaarModel.detect(img)
    listBlocks = lp.Layout([b for b in layoutResult if b.type in ["YOB", "Gender", "Name", "Photo", "QR", "UID", "Header"]])
    aadhaarData = {}
    dic = {}
    segmentArray = []
    blockTypeArray = []
    for block in listBlocks:
        segmentImage = (block.pad(left=5, right=5, top=5, bottom=5).crop_image(img))
        blockType = block.type
        encodedImg = img2base64(segmentImage, temp[1])
        aadhaarData[blockType]= {"image": encodedImg}
        if blockType in ["YOB", "Gender", "Name", "UID"]:
            gray = cv2.cvtColor(segmentImage, cv2.COLOR_BGR2GRAY)
            segmentArray.append(gray)
            blockTypeArray.append(blockType)
        
    t1 = time.time()
    if len(segmentArray)>0:
        with multiprocessing.Pool(processes=len(segmentArray)) as pool:
            resultsPool = pool.map(ocrImgAadhaar, segmentArray)
            pool.close()
            pool.join()
            dic = dict(zip(blockTypeArray, resultsPool))

    print("Multip1ro results & time in AADHAAR: ", imgName, time.time()-t1)
    uidBlock = lp.Layout([b for b in layoutResult if b.type in ["UID"]])
    maskedAd = lp.draw_box(img, uidBlock, box_width = 1, box_alpha = 1)
    encodedImg = img2base64(np.array(maskedAd), temp[1])
    aadhaarData["maskedAd"] = {"image": encodedImg}

    for key in aadhaarData.keys():
        if key in dic:
            aadhaarData[key]['data'] = dic[key].strip().replace('\n', '').replace('\f', '')
    return aadhaarData



def rotateImage(img, rotationModel):
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



def imgPreprocess(aadhaarImg, imgName):
    pathDPI = f"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/api-aadhaarPanDataScraping/dpi300/{imgName}"
    img = cv2.resize(aadhaarImg, (600, 600), cv2.INTER_AREA)
    img = Image.fromarray(img)
    img.save(pathDPI,dpi=(300, 300))
    deskewedImage = imgDeskew(pathDPI)
    shutil.rmtree("/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/api-aadhaarPanDataScraping/dpi300", ignore_errors=True)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    dst = clahe.apply(deskewedImage)
    img = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    return img



def aadhaarDataext(aadhaarImg, imgName, aadhaarModel, rotationModel, cardType):
    if cardType == "big":
        aadhaarImg = imgPreprocess(aadhaarImg, imgName)
    imgRotated, isRotated = rotateImage(aadhaarImg, rotationModel)
    data = smallImgData(imgRotated, imgName, isRotated, aadhaarModel)
    return data

