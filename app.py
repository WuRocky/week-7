from mysql.connector import pooling
from mySQL import MySQLPassword
from flask import *
import requests
import json
app=Flask(
  __name__,
  static_folder="public",
  static_url_path="/"
)
app.secret_key="test"

def get_connection():
  connection = pooling.MySQLConnectionPool(
    pool_name="python_pool",
    pool_size=10,
    pool_reset_session=True,
    host="localhost",
    user="root",
    password=MySQLPassword(),
    database='website'
    )
  return connection.get_connection()

# 首頁
@app.route("/")
def index():
  return render_template("index.html")

# 註冊
@app.route("/signup", methods=["POST"])
def signup():
  try:
    connection = get_connection()
    mycursor = connection.cursor()
    name=request.form["name"]
    username=request.form["username"]
    password=request.form["password"]
    mycursor.execute("select username from member where username = %s LIMIT 1",(username,))
    reuslt=mycursor.fetchone()

    if reuslt != None:
      return redirect("/error?message=帳號已經被註冊")
    mycursor.execute("insert into member(name, username, password) values(%s, %s, %s)",(name,username,password))
    connection.commit()
    return redirect("/")
  except:
    print("Unexpected Error")
  finally:
    mycursor.close()
    connection.close()


# 登入
@app.route("/signin", methods=["POST"])
def signin():
  try:
    connection = get_connection()
    mycursor = connection.cursor()
    username=request.form["signinUsername"]
    password=request.form["signinPassword"]
    mycursor.execute("select id,name,username,password from member where username = %s and password =%s LIMIT 1",(username,password,))
    reuslt=mycursor.fetchone()
    if reuslt == None:
      return redirect("/error?message=帳號或密碼輸入錯誤")
    session["username"]=username
    session["password"]=password
    session["id"]=reuslt[0]
    session["name"]=reuslt[1]
    return redirect("/member")
  except:
    print("Unexpected Error")
  finally:
    mycursor.close()
    connection.close()


# 會員頁面
@app.route("/member")
def member():
  try:
    connection = get_connection()
    mycursor = connection.cursor()
    sqlMessage = "select a.name , b.content \
    from member as a \
    inner join message as b \
    on a.id = b.member_id"
    if "username" in session:
      data = session["name"]
      mycursor.execute(sqlMessage)
      message=mycursor.fetchall()
      return render_template("member.html",name=data,message=message)
    return redirect("/")
  except:
    print("Unexpected Error")
  finally:
    mycursor.close()
    connection.close()


# 聊天對話
@app.route("/message", methods=["POST"])
def message():
  try:
    connection = get_connection()
    mycursor = connection.cursor()
    content = request.form["content"]
    mycursor.execute("insert into message(member_id, content) values(%s, %s)",(session["id"],content))
    sqlMessage = "select a.name , b.content \
    from member as a \
    inner join message as b \
    on a.id = b.member_id"
    mycursor.execute(sqlMessage)
    message=mycursor.fetchall()
    connection.commit()
    return render_template("member.html",name=session["name"],message=message) 
  except: 
    print("Unexpected Error")
  finally:
    mycursor.close()
    connection.close()


# 錯誤頁面
@app.route("/error")
def error():
  data=request.args.get("message","自訂錯誤訊息")
  return render_template("error.html",message=data)

# 登出
@app.route("/signout")
def signout():
  del session["username"],session["id"],session["name"]
  return redirect("/")

# api
@app.route("/api/member/", methods=["PATCH","GET"])
def api():
  try:
    connection = get_connection()
    mycursor = connection.cursor()
    data_null =json.dumps({
    "data":None
    }) 
    error_updat_name =json.dumps({
    "error":True
    }) 
    if request.method == "GET":
      if "username" in session:
        username = request.args.get("username","要查詢的會員帳號")
        mycursor.execute("select id, name, username from member where username = %s",(username,))
        sql_data=mycursor.fetchall()
        if sql_data != None:
          for api in sql_data:
            data_api =json.dumps({
            "data":{
            "id":api[0],
            "name":api[1],
            "username":api[2]
            }
            }) 
            return data_api
      return data_null
    if request.method == "PATCH":
      if "username" in session:
        request_API = request.json
        updata_neame =request_API["name"]
        request_header = request.headers["Content-Type"]
        print(request_header)
        success__updata_name={
        "ok":True
        }

        mycursor.execute("update member set name = %s where id = %s",(updata_neame,session["id"],))
        connection.commit()
        if mycursor.rowcount != None:
          return success__updata_name
      return error_updat_name
  except: 
    print("Unexpected Error")
  finally:
    mycursor.close()
    connection.close()


if __name__ == "__main__": 
  app.run(port=3000,debug=True)

