import base64
from flask import Flask, request, make_response, jsonify
import datetime as dt
import pymysql
from PIL import Image
from io import BytesIO
from image import getIn_getOut, webCam, getImage
import json

# dbw: https://lucathree.github.io/python/day16/

GAS = 0

def dbcon():
    return pymysql.connect(host='localhost',
                           port=3306,
                           user='iotuser',
                           password='iotuser123456',
                           db='iot',
                           charset='utf8')

def commitDB(sql, vals):
    db = dbcon()
    cur = db.cursor()
    cur.execute(sql, vals)
    db.commit()
    db.close()          # MySQL 연결 종료

    return True

def select1DB(sql):
    # result=list()
    db = dbcon()
    cur = db.cursor()
    cur.execute(sql)
    ret = cur.fetchall()
    db.close()          # MySQL 연결 종료

    return ret

def select2DB(sql, vals):
    db = dbcon()
    cur = db.cursor()
    cur.execute(sql, vals)
    ret = cur.fetchone()
    db.close()          # MySQL 연결 종료

    return ret

app = Flask(__name__)

# app.route('/url', methods=['POST'])
# get과 post 둘 다 지원하려면 methods=['GET', 'POST']


# req
# {
#     "carNo": "String",
#     "email": "String",
#     "password": "String",
#     "phone": "String"
# }

@app.route('/user/signup', methods=['POST'])
def signUp():
    params = request.get_json()

    sql = "insert into member values(%s, %s, %s, %s, 0)"
    vals = (params['carNo'], params['email'], params['password'], params['phone'])

    flag = commitDB(sql, vals)

    if(flag == False):
        return make_response("FAIL")

    return make_response("OK")

# req
# {
#     "email": “String”,
#     "password": "String"
# }

# res
# {
#     "carNo": "String",
#     "email": "String",
#     "password": "String",
#     "phone": "String"
# }

@app.route('/user/login', methods=['POST'])
def login():
    # https://velog.io/@dacokim32/Flask-1Flask%EC%97%90%EC%84%9C-json%EB%8B%A4%EB%A3%A8%EA%B8%B0
    params = request.get_json()
    sql = "SELECT * FROM member WHERE member_id = %s AND member_password = %s"
    vals = (params['email'], params['password'])

    flag = select2DB(sql, vals)

    data = {
        "carNo": flag[0],
        "email": flag[1],
        "password": flag[2],
        "phone": flag[3]
    }

    if (flag == False):
        return make_response("FAIL")

    return make_response(data)

# res
# {
#     "getIn": "String",
#     "pay": int,                               -> ??
#     "parkingLoc": int,
#     "parkingStatus": int
# }
#

@app.route('/mypark', methods=['GET'])
def status():
    temp = str(request.args.get('carNo'))
    sql = "SELECT car_num, member_isparking FROM member WHERE car_num = %s"
    flag = select2DB(sql, temp)

    if (flag == False):
        return make_response("FAIL")

    if(flag[1] == 0):
        getIn = "-"
        pay = 0
        parkingLoc = 0
    else:
        sql1 = "SELECT car_num, parking_location, parking_in_date, parking_out_date FROM parking WHERE car_num = %s"
        db_result = select2DB(sql1, (flag[0],))
        # Tue, 01 Nov 2022 14:01:01
        getIn = str(db_result[2])[11:]
        parkingLoc = int(db_result[1])
        pay = 0

    sql2 = "SELECT car_num, parking_location FROM parking WHERE parking_out_date is null"
    park_result = select1DB(sql2)

    parkingStatus = len(park_result)

    data = {
        "getIn": getIn,
        "pay": pay,
        "parkingLoc": parkingLoc,
        "parkingStatus": parkingStatus
    }

    return make_response(data)

# res
# {
#     "no1": int,
#     "no2": int,
#     "no3": int,
#     "no4": int,
#     "no5": int,
#     "no6": int,
# }
# 0: 빈 주차자리
# 1: 이미 주차된 자리

@app.route('/parkingState', methods=['GET'])
def parkingState():

    sql = "SELECT parking_location FROM parking WHERE parking_out_date is null"
    park_result = select1DB(sql)

    if(park_result == None):
        data = {
            "no1": 0,
            "no2": 0,
            "no3": 0,
            "no4": 0,
            "no5": 0,
            "no6": 0
        }

        return make_response(data)

    arr = [0, 0, 0, 0, 0, 0]

    for i in range(len(park_result)):
        arr[int(park_result[i][0]) - 1] = 1

    data = {
        "no1": arr[0],
        "no2": arr[1],
        "no3": arr[2],
        "no4": arr[3],
        "no5": arr[4],
        "no6": arr[5]
    }

    return make_response(data)

## 좋은게 0, 나쁜게 1
@app.route('/gas', methods=['POST'])
def gasWithRaspberryPI():
    params = request.get_json()
    global GAS
    GAS = params['gas']
    print(GAS)
    return make_response("OK")

@app.route('/gas/status', methods=['GET'])
def gasWithApp():
    global GAS
    data = {
        "gas": GAS
    }
    return make_response(data)

#통계
@app.route('/statistics', methods=['GET'])
def analytics():
    temp = str(request.args.get('carNo'))
    sql = "SELECT car_num,sum(parking_fee) FROM parking WHERE car_num = %s"     #누적 요금
    flag = select2DB(sql, temp)

    if (flag == False):
        return make_response("FAIL")

    x = dt.datetime.now()

    sql = "SELECT car_num,count(*) FROM parking WHERE car_num = %s AND month(parking_in_date) = " + str(x.month)  # 누적 요금
    numUses = select2DB(sql, temp)

    if (numUses == False):
        return make_response("FAIL")

    data = {
        "pay": int(flag[1]),
        "numUses": numUses[1]
    }

    return make_response(data)


#-----------------------------------------------------------------------------------

@app.route('/image_webcam', methods=['POST'])
def parkingWithInfraredSensors():
    params = request.get_json()

    sql = "UPDATE member SET member_isparking = 1 WHERE car_num= %s and EXISTS (SELECT * FROM parking WHERE parking_out_date is null and member.car_num=parking.car_num)"

    getImage(params['img'])  # test.jpg로 저장
    img = webCam('test.jpg')   # 배열 return 받음
    cnt = 0

    for i in params['parking']:
        if(i == 1):
            db = commitDB(sql, img[cnt])
            if(db == False):
                return make_response("FAIL")
            cnt += 1

    return make_response("OK")

@app.route('/genInParking', methods=['POST'])
def getInPark():
    params = request.get_json()
    getImage(params['image'])
    out = getIn_getOut()        # 차 번호 받아옴

    sql = "INSERT INTO parking(car_num, parking_location, parking_in_date) VALUES(%s, '1', " + dt.datetime.now() + ")"

    flag = commitDB(sql, out)

    if(flag == False):
        return make_response("FAIL")

    return make_response(out)

@app.route('/genOutParking', methods=['POST'])
def getOutPark():
    params = request.get_json()
    getImage(params['image'])
    out = getIn_getOut('test.jpg')

    # 출차시간 업데이트
    sql = "UPDATE parking SET parking_out_date = " + dt.datetime.now() + "WHERE parking_out_date is null and car_num = %s"
    commitDB(sql, out)
    # 출차 했을 때, isparking 값 바꾸기
    sql2 = "UPDATE member SET member_isparking = 0 WHERE car_num = %s and NOT EXISTS(SELECT * FROM parking WHERE parking_out_date is null and member.car_num = parking.car_num)"
    commitDB(sql2, out)

    return make_response("OK")

@app.route('/image', methods=['POST'])
def index():
	json_data = request.get_json()
	# print(json_data['img'])
	# dict_data = json.loads(json_data)

	img = json_data['img']
	img = base64.b64decode(img)
	img = BytesIO(img)
	img = Image.open(img)
	img.save('test.jpg')

	return json_data



#
# @app.route('/update', methods=['POST'])
# def updatePark():
#     params = request.get_json()
#
#     sql = "SELECT * FROM member WHERE member_id = %s AND member_password = %s"
#     vals = (params['email'], params['password'])
#
#     flag = select2DB(sql, vals)
#
#     return make_response("OK")


# https://scribblinganything.tistory.com/620


if __name__ == '__main__':          # 현재 파일 실행 시 개발용 웹 서버 구동
    app.run(debug=True, port=8000, host='172.20.10.2')
