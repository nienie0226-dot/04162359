import requests
from bs4 import BeautifulSoup

url = "https://baluhw.vercel.app/about"
Data = requests.get(url)
Data.encoding ="utf-8" 
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.find(".filmListAllX li")

for item in result:
	print (item.find("img").get("alt"))
	print ("https://www.atmovies.com.tw"+item.find("a").get("href"))
	print()