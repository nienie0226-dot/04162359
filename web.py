import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore


def get_firestore_client():
    """建立 Firestore client；若未設定憑證則回傳 None。"""
    cred = None

    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
    else:
        firebase_config = os.getenv("FIREBASE_CONFIG")
        if not firebase_config:
            return None

        try:
            cred_dict = json.loads(firebase_config)
        except json.JSONDecodeError:
            return None

        cred = credentials.Certificate(cred_dict)

    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass

    return firestore.client()


def normalize_teacher(doc):
    return {
        "name": doc.get("name", ""),
        "lab": doc.get("lab", ""),
        "mail": doc.get("mail", ""),
    }


def load_teacher_data(db_client):
    """啟動時一次讀取資料庫，之後由系統內資料搜尋。"""
    if db_client is None:
        return [], "尚未設定 Firestore 連線，無法載入資料。"

    try:
        collection_names = ["靜宜資管2026a", "靜宜資管"]
        for name in collection_names:
            docs = [
                normalize_teacher(doc.to_dict())
                for doc in db_client.collection(name).get()
            ]
            if docs:
                return docs, None
        return [], "資料庫集合存在，但目前沒有可用資料。"
    except Exception as exc:
        return [], f"讀取 Firestore 時發生錯誤：{exc}"


def filter_teachers(all_teachers, keyword):
    keyword = keyword.strip().lower()
    if not keyword:
        return all_teachers

    return [
        teacher
        for teacher in all_teachers
        if keyword in str(teacher.get("name", "")).lower()
    ]


app = Flask(__name__)
db = get_firestore_client()
teachers_data, data_load_error = load_teacher_data(db)


@app.route("/")
def index():
    # 整合後的首頁
    link = "<h1>歡迎進入巴嚕的網站首頁2</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>關於巴嚕</a><hr>"
    link += "<a href='/welcome?u=巴嚕&dep=資管A班'>歡迎光臨</a><hr>"
    link += "<a href=/account>帳號密碼</a><hr>"
    link += "<a href=/math>數學計算機</a><hr>"
    link += "<a href=/read>讀取全部資料</a><hr>"
    link += "<a href=/search>老師查詢系統</a><hr>"
    link += "<a href=/sp1>sp1</a><hr>"
    return link


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))


@app.route("/welcome", methods=["GET"])
def welcome():
    # 相容兩種參數命名：新版 u/dep 與舊版 nick/school
    user = request.values.get("u") or request.values.get("nick", "")
    school = request.values.get("dep") or request.values.get("school", "")
    return render_template("welcome.html", name=user, school=school)


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form.get("user", "")
        pwd = request.form.get("pwd", "")
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd
        return result
    else:
        return render_template("account.html")


@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        try:
            x = float(request.form.get("x", 0))
            y = float(request.form.get("y", 0))
        except ValueError:
            return "請輸入有效數字"

        op = request.form.get("op", "")
        try:
            if op == "+":
                result = x + y
            elif op == "-":
                result = x - y
            elif op == "*":
                result = x * y
            elif op == "/":
                result = x / y
            else:
                result = "不支援的運算子"
        except ZeroDivisionError:
            result = "除數不可為 0"

        return f"{x} {op} {y} = {result}"
    else:
        return render_template("math.html")


@app.route("/read")
def read():
    if data_load_error and not teachers_data:
        return render_template(
            "read.html",
            docs=[],
            keyword="",
            error=data_load_error,
        )

    keyword = request.values.get("q", "").strip()
    docs = filter_teachers(teachers_data, keyword)
    return render_template(
        "read.html", docs=docs, keyword=keyword, error=data_load_error
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    keyword = request.form.get("teacher_keyword", "").strip()
    if not keyword:
        return render_template(
            "search-results.html",
            results=[],
            keyword=keyword,
            error=data_load_error,
        )

    results = filter_teachers(teachers_data, keyword)
    return render_template(
        "search-results.html",
        results=results,
        keyword=keyword,
        error=data_load_error if not teachers_data else None,
    )

@app.route("/sp1")
def sp1():
    R = ""
    url = "https://baluhw.vercel.app/about"
    Data = requests.get(url)
    Data.encoding ="utf-8" 
    print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")

    for item in result:
        R +=item + "<br>" +item.get("href") +"<br><br>"
    return R

if __name__ == "__main__":
    app.run()
