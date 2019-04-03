import feedparser
from flask import Flask
from flask import render_template
from flask import request
import urllib
import json
import datetime 
from flask import make_response 

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
 			 'cnn': 'http://rss.cnn.com/rss/edition.rss',
			 'fox': 'http://feeds.foxnews.com/foxnews/latest',
			 'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc', 'city':'London,UK', 'currency_from':'GBP', 'currency_to':'USD'}


def get_value_with_fallback(key):
	#function to give the fallback value
	if request.args.get(key):
		return request.args.get(key)
	if request.cookies.get(key):
		return request.cookies.get(key)
	return DEFAULTS[key]

def get_news(publication):
	feed = feedparser.parse(RSS_FEEDS[publication])
	articles = feed['entries']
	return articles
	
def get_weather(city):
	api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=6c0afcea5e9296ebd6cd6cae41b54606"
	city = urllib.parse.quote(city)
	url = api_url.format(city)
	data = urllib.request.urlopen(url).read()
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather"):
		weather = {"description":parsed["weather"][0]["description"], "temperature":parsed["main"]["temp"], "city":parsed["name"]}
		return weather

def get_rate(currency_from, currency_to):
	api_url = "https://openexchangerates.org//api/latest.json?app_id=7c5ed59521774852a07a2c932d314170"
	all_currency = urllib.request.urlopen(api_url).read()
	parsed = json.loads(all_currency).get("rates")
	from_rate = parsed.get(currency_from.upper())
	to_rate = parsed.get(currency_to.upper()) 
	return (to_rate/from_rate,parsed.keys())


@app.route("/")
#function to display homepage of our website
def home():
	#fetching the available articles from that publication
	publication = get_value_with_fallback("publication")
	articles = get_news(publication)
	
	#fetching the weather based upon the city
	city = get_value_with_fallback("city")
	weather = get_weather(city)

	#fetching rates and currency conversion on the bases of currency_from and currency_to
	currency_from = get_value_with_fallback("currency_from")
	currency_to = get_value_with_fallback("currency_to")
	rate, currencies = get_rate(currency_from, currency_to)

	#setting up the cookies
	response = make_response(render_template("homepage.html", articles=articles, weather=weather, currency_from=currency_from, currency_to=currency_to, rate=rate, currencies=sorted(currencies) ))
	expires  = datetime.datetime.now()+datetime.timedelta(days=365)
	response.set_cookie("publication", publication, expires=expires)
	response.set_cookie("city", city, expires=expires)
	response.set_cookie("currency_from", currency_from, expires=expires)
	response.set_cookie("currency_to", currency_to, expires=expires)
	return response

if __name__ == "__main__":    
	app.run(port=5000, debug=True) 