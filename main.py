from flask import jsonify, Flask, request, make_response
import pymysql

# dbw: https://lucathree.github.io/python/day16/

OK = 200
BAD_REQUEST = 400

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

def selectDB(sql, vals):
    db = dbcon()
    cur = db.cursor()
    cur.execute(sql, vals)
    ret = cur.fetchone()
    db.close()          # MySQL 연결 종료

    return ret

app = Flask(__name__)

# app.route('/url', methods=['POST'])
# get과 post 둘 다 지원하려면 methods=['GET', 'POST']

@app.route('/signup', methods=['POST'])
def signUp():
    params = request.get_json()
    carNum = params['carNo']

    sql = "insert into member values(%s, %s, %s, %s, 0)"
    vals = (params['carNo'], params['email'], params['password'], params['phone'])

    flag = commitDB(sql, vals)

    if(flag == False):
        return make_response("fail")

    return make_response("OK")

@app.route('/login', methods=['POST'])
def login():
    # https://velog.io/@dacokim32/Flask-1Flask%EC%97%90%EC%84%9C-json%EB%8B%A4%EB%A3%A8%EA%B8%B0
    params = request.get_json()
    sql = "SELECT * FROM member WHERE member_id = %s AND member_password = %s"
    vals = (params['email'], params['password'])

    flag = selectDB(sql, vals)

    data = {
        "carNo": flag[0],
        "email": flag[1],
        "password": flag[2],
        "phone": flag[3]
    }

    if (flag == False):
        return make_response("FAIL")

    return make_response(data)

#-------------------------------------------------------------------

@app.route('/mypark', methods=['GET'])
def status():
    params = request.get_json()
    sql = "SELECT car_num FROM member WHERE member_id = %s"
    flag = selectDB(sql, params['email'])

    if (flag == False):
        return make_response(BAD_REQUEST)

    sql = "SELECT * FROM users WHERE car_num = %s"

@app.route('/status', methods=['POST'])
def status():
    params = request.get_json()
    sql = "SELECT car_num FROM member WHERE member_id = %s"
    flag = selectDB(sql, params['email'])

    if (flag == False):
        return make_response(BAD_REQUEST)

    sql = "SELECT * FROM users WHERE car_num = %s"



@app.route('/update', methods=['POST'])
def updatePark():
    return make_response(OK)



# https://scribblinganything.tistory.com/620


if __name__ == '__main__':          # 현재 파일 실행 시 개발용 웹 서버 구동
    app.run(debug=True, port=80, host='0.0.0.0')
