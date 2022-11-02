# api
@app.route("/api/member/", methods=["GET","PATCH"])
def api():
  data_null =json.dumps({
  "data":None
  }) 
  if "username" in session:
    if request.method == "GET":
      username = request.args.get("username","要查詢的會員帳號")
      connection = get_connection()
      mycursor = connection.cursor()
      mycursor.execute("select id, name, username from member where username = %s",(username,))
      message=mycursor.fetchall()
      if message != None:
        for api in message:
          data_api =json.dumps({
          "data":{
          "id":api[0],
          "name":api[1],
          "username":api[2]
          }
          }) 
          return data_api
    if request.method == "PATCH":
      print("標頭名稱",request.headers.get("application/json"))
  return data_null