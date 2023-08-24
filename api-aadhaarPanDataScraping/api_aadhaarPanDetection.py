import numpy as np
import cv2
from PIL import Image
import os
import shutil
import layoutparser as lp
from deskew import determine_skew
import pickle
from api_panDataScraping import pan1DataExt
from api_panDataScraping import pan2DataExt
from api_aadhaarDataScraping import aadhaarDataext
import base64
from fastapi import FastAPI
from pydantic import BaseModel
os.umask(0)

app = FastAPI()

bigModel = lp.models.Detectron2LayoutModel(
    config_path=r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/aadhaarPanDetectionModel/config.yaml",
    model_path=r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/aadhaarPanDetectionModel/model_final.pth",
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
    device="cuda",
    label_map={0: "aadhaar", 1: "panClass1", 2: "panClass2", 3: "bigAadhaar"}
    )



aadhaarModel = lp.models.Detectron2LayoutModel(
    config_path = r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/aadhaarModel/config.yaml",
    model_path = r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/aadhaarModel/model_final.pth",
    extra_config = ["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6],
    device = "cuda",
    label_map={0:"Gender",1: "Header", 2: "Name", 3: "Photo", 4: "QR", 5: "UID", 6: "YOB"}
    )



pick = open("/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/aadhaarModel/svmLinearModel.sav", "rb")
adRotationModel = pickle.load(pick)
pick.close()



pick = open("/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/panModel/panClass1Model/pan1svmlinear600x600.sav", "rb")
pan1RotationModel = pickle.load(pick)
pick.close()



pick = open("/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/panModel/panClass2Model/pan2svmlinear600x600.sav", "rb")
pan2RotationModel = pickle.load(pick)
pick.close()



panClass1Model = lp.models.Detectron2LayoutModel(
    config_path=r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/panModel/panClass1Model/config.yaml",
    model_path=r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/panModel/panClass1Model/model_final.pth",
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6],
    device="cuda",
    label_map={0: "dob", 1: "fathersname", 2: "header", 3: "name", 4: "pannum", 5: "photo", 6: "signature"}
    )



panClass2Model = lp.models.Detectron2LayoutModel(
    config_path=r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/panModel/panClass2Model/config.yaml",
    model_path=r"/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/aadhaarPanDataScraping/aiModels/panModel/panClass2Model/model_final.pth",
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6],
    device="cuda",
    label_map={0: "dob", 1: "fathersname", 2: "name", 3: "pannum", 4: "photo", 5: "signature"}
    )


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
    img = Image.fromarray(img)
    img = img.resize((650, 550))
    img.save(pathDPI, dpi=(300, 300))
    deskewedImage = imgDeskew(pathDPI)
    shutil.rmtree("/media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/api-aadhaarPanDataScraping/dpi300", ignore_errors=True)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    dst = clahe.apply(deskewedImage)
    dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    return dst



def aadhaarOrPan(img, imgName):
    height = img.shape[0]
    width = img.shape[1]
    layout = None
    aadhaarData = {}
    panData = {}
    cardType = "small"
    if height < width:
        img = cv2.resize(img, (650, 550), cv2.INTER_AREA)
        
    height = img.shape[0]
    width = img.shape[1]
    
    if height > 550:
        layout = bigModel.detect(img)
        cardType = "big"
    else:
        img = imgPreprocess(img, imgName)
        layout = bigModel.detect(img)

    listBlocks = [b for b in layout if b.type in [
        "aadhaar", "panClass1", "panClass2", "bigAadhaar"]]
    
    aadhaarData["isAadhaar"] = False
    panData["isPan"] = False
    if len(listBlocks)>0:
        for i, block in enumerate(listBlocks):
            temp = imgName.split(".")
            imgName = temp[0]+"_"+str(i)+"."+temp[1]
            blockType = block.type

            if blockType == "bigAadhaar":
                segmentImage = (block.pad(left=10, right=10,
                                top=10, bottom=10).crop_image(img))
                aadhaarData = aadhaarDataext(segmentImage, imgName, aadhaarModel, adRotationModel, cardType)
                aadhaarData["isAadhaar"] = True

            elif blockType == "aadhaar":
                segmentImage = (block.pad(left=10, right=10,
                                top=10, bottom=10).crop_image(img))
                aadhaarData = aadhaarDataext(segmentImage, imgName, aadhaarModel, adRotationModel, cardType)
                aadhaarData["isAadhaar"] = True

            elif blockType == "panClass1":
                segmentImage = (block.pad(left=10, right=10,
                                top=10, bottom=10).crop_image(img))
                panData = pan1DataExt(segmentImage, imgName, panClass1Model, pan1RotationModel, cardType)
                panData["isPan"] = True

            elif blockType == "panClass2":
                segmentImage = (block.pad(left=10, right=10,
                                top=10, bottom=10).crop_image(img))
                panData = pan2DataExt(segmentImage, imgName, panClass2Model, pan2RotationModel, cardType)
                panData["isPan"] = True

            else:
                pass
    
    else:
        aadhaarData["isAadhaar"] = False
        panData["isPan"]= False
    return aadhaarData, panData



def base64ToImg(imageData):
    os.makedirs("./dpi300", exist_ok=True)
    jpg_as_text = imageData.encode('utf-8')
    jpg_original = base64.b64decode(jpg_as_text)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    return img



def jsonResponse(requestId, imageData, imageType):
    img  = base64ToImg(imageData)
    imgName = f"{requestId}.{imageType.lower()}"
    aadhaarData, panData = aadhaarOrPan(img, imgName)
    isAadhaar = aadhaarData["isAadhaar"]
    isPan = panData["isPan"]
    del aadhaarData["isAadhaar"]
    del panData["isPan"]
    if isAadhaar == True and isPan == True:
        response = {
                "requestId": requestId,
                "isAadhaar": True,
                "isPan": True,
                "aadharDetails": aadhaarData,
                "panDetails": panData
        }

    elif isAadhaar:
        response = {
                "requestId": requestId,
                "isAadhaar": True,
                "aadharDetails": aadhaarData,
        }
        
    elif isPan:
        response = {
                "requestId": requestId,
                "isPan": True,
                "panDetails": panData,
        }
        
    else:
        response = {
                "requestId": requestId,
                "isAadhaar": False,
                "isPan": False,
            }
            
    return response





@app.post("/GetCardDetails/v1")
def get_card_details(request: dict):
    try:
        # Parse the request fields
        requestId = request.get("requestId")
        imageType = request.get("imageType")
        imageData = request.get("imageData")
        attachmentType = request.get("attachmentType")

        response = jsonResponse(requestId, imageData, imageType)
        return response
    except Exception as e: 
        response = {
                "requestId": requestId,
                "error": str(e)
            }
        return response
