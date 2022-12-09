from flask import jsonify, Flask, request, make_response
import pymysql

# db: https://lucathree.github.io/python/day16/

OK = 200
BAD_REQUEST = 400

def dbcon():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='1234',
                           db='encore',
                           charset='utf8')

def commitDB(sql, vals):
    try:
        db = dbcon()
        cur = db.cursor()
        cur.execute(sql, vals)
        cur.commit()
    except Exception as e:
        return False
    finally:
        db.close()          # MySQL 연결 종료

    return True

def selectDB(sql, vals):
    ret = list()
    try:
        db = dbcon()
        cur = db.cursor()
        cur.execute(sql, vals)
        ret = cur.fetchall()
    except Exception as e:
        return False
    finally:
        db.close()          # MySQL 연결 종료

    return ret

app = Flask(__name__)

# app.route('/url', methods=['POST'])
# get과 post 둘 다 지원하려면 methods=['GET', 'POST']

@app.route('/signup', methods=['POST'])
def signUp():
    params = request.get_json()
    carNum = params['carNo']

    sql = "insert into user values(%s, %s, %s, %s)"
    vals = (params['carNo'], params['email'], params['password'], params['phone'])

    flag = commitDB(sql, vals)

    if(flag != True):
        return make_response(BAD_REQUEST)

    return make_response(OK)

@app.route('/login', methods=['POST'])
def login():
    # https://velog.io/@dacokim32/Flask-1Flask%EC%97%90%EC%84%9C-json%EB%8B%A4%EB%A3%A8%EA%B8%B0
    params = request.get_json()
    sql = "SELECT id FROM user WHERE user_id = %s AND user_password = %s"
    vals = (params['email'], params['password'])

    flag = commitDB(sql, vals)

    if (flag != True):
        return make_response(BAD_REQUEST)

    return make_response(OK)

@app.route('/status', methods=['POST'])
def status():
    params = request.get_json()
    sql = "SELECT car_num FROM users WHERE user_id = %s"
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
