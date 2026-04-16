from flask import Flask, render_template,request
from datetime import datetime
app = Flask(__name__)
import random

@app.route("/")
def index():
    link="<h1>歡迎進入巴嚕的網站首頁2</h1>"
    link+="<a href=/mis>課程</a><hr>"
    link+="<a href=/today>今天日期</a><hr>"
    link+="<a href=/about>關於巴嚕</a><hr>"
    link+="<a href=/welcome?u=巴嚕&dep=資管A班>歡迎光臨</a><hr>"
    link+="<a href=/account>帳號密碼</a><hr>"
    link+="<a href=/math>數學計算機</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    return link


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math")
def math():
    return render_template("math.html")

    

@app.route("/mis")
def course():
    return '<h1>資訊管理導論</h1><a href="/">回到網站首頁</a>'

@app.route("/welcome", methods = ["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x,dep = y)

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)




@app.route("/today")
def today():
    now = datetime.now()
    year = str(now.year)
    month =str(now.month)
    day = str(now.day)
    now = year +"年"+month+"月"+day+"日"
    return render_template("today.html", datetime = str(now))
@app.route("/about")
def about():
	return render_template("MIS2A.html")

if __name__ == "__main__":
    app.run(debug=True)
