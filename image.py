import easyocr
import cv2
from PIL import Image
from io import BytesIO
import base64
import time

def getIn_getOut(imgSrc):
    img = cv2.imread(imgSrc) # 이미지 불러오기
    height, width = img.shape[:2]
    img = cv2.resize(img, (int(width*0.75), int(height*0.75)), interpolation=cv2.INTER_AREA) # 이미지 축소
    img = cv2.copyMakeBorder(img, 150, 150, 150, 150, cv2.BORDER_CONSTANT, None, value = 0) # 이미지 검은색 테두리 추가

    reader = easyocr.Reader(['ko', 'en'], gpu=False)  # need to run only once to load model into memory #easyOCR 인식
    result = reader.readtext(img) # 글자 읽어오기

    num = str(result[0][-2]) # 글자를 저장할 변수
    print(num)
    return(num)

# 배열 반환
def webCam(imgSrc):
    # start=time.time()
    reader = easyocr.Reader(['ko', 'en'], gpu=False)  # need to run only once to load model into memory
    result = reader.readtext(imgSrc)
    nums = []
    for i in result:
        nums.append(str(i[1]))
    print(nums)
    return nums
    # print("time : ", time.time()-start)

def getImage(getImg):
    img = base64.b64decode(getImg)
    img = BytesIO(img)
    img = Image.open(img)
    img.save('test.jpg')  # 저장하는 코드
