import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, make_response, jsonify


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
    link += "<a href=/movie>找電影</a><hr>"
    link += "<a href=/movie2>讀取開眼電影即將上映影片，寫入Firestore</a><hr>"
    link += "<a href=/movie3>查詢關鍵字</a><hr>"
    link += "<a href=/road>十大肇事路口</a><hr>"
    link += "<a href=/weather>查詢天氣</a><hr>"
    link += "<a href=/rate>本週新片進DB</a><hr>"
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
    R = "<a href='/'>回到首頁</a><br><hr>"

    url = "https://baluhw.vercel.app/about"
    Data = requests.get(url)
    Data.encoding ="utf-8" 
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")
    print(result)

    for item in result:
        R +=item.text + "<br>" +item.get("href") +"<br><br>"
    return R

@app.route("/movie")
def movie():
    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")

#根據你圖片中的選取器邏輯
    result = sp.select(".filmListAllX li")

    R = "<h1>即將上映電影清單</h1>"
    R += "<a href='/'>回到首頁</a><br><hr>"

    for item in result:
        try:
            # 抓取電影名稱 (從 img 的 alt 屬性)
            name = item.find("img").get("alt")
            # 抓取連結 (補上完整網址)
            link = "https://www.atmovies.com.tw/" + item.find("a").get("href")

#組合 HTML 字串
            R += f"🎬 <b>{name}</b><br>"
            R += f"🔗 <a href='{link}' target='_blank'>電影介紹連結</a><br><br>"
        except:
            # 防止部分 li 結構不完整導致報錯
            continue

    return R
@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    

    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    # 處理 GET 請求：顯示輸入關鍵字的表單
    if request.method == "GET":
        html = """
        <h1>電影關鍵字查詢系統</h1>
        <a href='/'>回到首頁</a><hr>
        <form action='/movie3' method='POST'>
            請輸入電影名稱關鍵字：
            <input type='text' name='keyword' required>
            <button type='submit'>搜尋</button>
        </form>
        """
        return html

    # 處理 POST 請求：接收關鍵字並去 Firestore 查詢
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        
        if not keyword:
            return "請輸入關鍵字！ <br><br><a href='/movie3'>返回搜尋頁</a>"

        if db is None:
            return "資料庫連線失敗，無法查詢。"

        try:
            # 取得 Firestore 中「電影」集合的所有資料
            docs = db.collection("電影").get()
            
            # 建立一個空陣列來存放比對成功的結果
            results = []
            for doc in docs:
                movie_data = doc.to_dict()
                title = movie_data.get("title", "")
                
                # 如果關鍵字包含在電影名稱內，就加入結果清單
                if keyword.lower() in title.lower():
                    results.append(movie_data)

            # 組合查詢結果的 HTML
            result_html = f"<h1>查詢結果：包含「{keyword}」的電影</h1>"
            result_html += "<a href='/movie3'>重新查詢</a> | <a href='/'>回到首頁</a><hr>"

            if not results:
                result_html += f"找不到任何名稱包含「{keyword}」的電影。"
                return result_html

            # 將有找到的電影一筆一筆列出來
            for m in results:
                result_html += f"🎬 <b>{m.get('title')}</b><br>"
                result_html += f"📅 上映日期：{m.get('showDate')} | ⏱️ 片長：{m.get('showLength')} 分鐘<br>"
                result_html += f"🔗 <a href='{m.get('hyperlink')}' target='_blank'>查看開眼電影介紹</a><br>"
                if m.get('picture'):
                    result_html += f"<img src='{m.get('picture')}' width='150'><br>"
                result_html += "<br><hr>"
                
            return result_html

        except Exception as exc:
            return f"查詢時發生錯誤：{exc}"

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/road")
def road():
    R = ""
    url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
    
    # 建議加入 timeout 避免網頁卡死
    Data = requests.get(url, timeout=10)
    JsonData = json.loads(Data.text)
    
    for item in JsonData:
        # 在結尾加上 <br>，網頁才會換行
        R += item["路口名稱"] + "，總共發生 " + item["總件數"] + "件事故<br>"
        
    return R +"<a href='/'>回到首頁</a><br><hr>"



@app.route("/weather_query")
def weather_query():
    # 建立一個簡單的 HTML 表單介面
    html = """
    <h2>縣市天氣查詢系統</h2>
    <a href="/">回到首頁</a>
    <hr>
    <form action="/weather" method="get">
        請輸入縣市名稱：<input type="text" name="city" placeholder="例如：臺中市">
        <button type="submit">搜尋</button>
    </form>
    """
    return html

@app.route("/weather", methods=["GET", "POST"])
def weather():
    # 1. 如果是第一次進入，或是沒有帶參數，先顯示查詢表單
    city = request.values.get("city")
    if not city:
        html = """
        <h2>縣市天氣查詢系統</h2>
        <a href="/">回到首頁</a>
        <hr>
        <form action="/weather" method="get">
            請輸入縣市名稱：<input type="text" name="city" placeholder="例如：臺中市" required>
            <button type="submit">搜尋</button>
        </form>
        """
        return html

    # 2. 如果有帶 city 參數，則執行爬蟲邏輯
    city = city.replace("台", "臺")
    city_encoded = quote(city)
    
    # 你的 API URL (參考 image_1ea25b.png 的邏輯)
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName={city_encoded}"
    
    try:
        Data = requests.get(url, timeout=10)
        json_data = json.loads(Data.text)
        
        # 取得氣象描述 (datasetDescription)
        weather_title = json_data["records"]["datasetDescription"]
        
        # 取得該城市的第一筆天氣資料
        location_data = json_data["records"]["location"][0]
        
        # 天氣現象 (Weather Element 0)
        weather_state = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        # 降雨機率 (Weather Element 1)
        rain_prob = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        
        R = f"<h1>{weather_title}</h1>"
        R += f"<h3>城市：{city}</h3>"
        R += f"目前天氣：<b>{weather_state}</b><br>"
        R += f"降雨機率：<b>{rain_prob}%</b><br><br>"
        
    except Exception as e:
        R = f"<h1>查詢失敗</h1>"
        R += f"找不到「{city}」的資料，請確認輸入是否正確（如：臺南市）。<br>"
        # R += f"Debug 訊息：{e}<br>" # 除錯用

    R += "<a href='/weather'>重新查詢</a> | <a href='/'>回到首頁</a>"
    return R

@app.route('/webhook', methods=['POST'])
def webhook():
    # 接收 Dialogflow 傳來的 JSON
    req = request.get_json(silent=True, force=True)
    
    # 取得 Dialogflow 抓到的參數 (普遍級、保護級等)
    target_rate = req.get('queryResult').get('parameters').get('rate')
    
    # 到 Firestore 查詢對應分級的電影
    collection_ref = db.collection("本週新片含分級")
    # 這裡的 "rate" 要對應你資料庫裡的欄位名稱
    docs = collection_ref.where("rate", "==", target_rate).stream()

    movie_titles = []
    for doc in docs:
        movie_titles.append(doc.to_dict().get("title"))

    # 組合回覆內容
    if movie_titles:
        reply = f"我是聶運安開發的機器人，幫您找到以下{target_rate}電影：\n" + "、".join(movie_titles)
    else:
        reply = f"哎呀，本週好像沒有{target_rate}的電影耶。"

    # 依照 Dialogflow 的格式回傳
    info = "我是聶運安開發的電影聊天機器人,您選擇的電影分級是：" +
    rate + "，相關電影：\n"
    return jsonify({"fulfillmentText": reply})
    
 
if __name__ == "__main__":
    app.run()
