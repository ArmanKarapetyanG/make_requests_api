from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
from serpapi import GoogleSearch
import ast
from lxml import etree
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from urllib.parse import urlparse
from string import whitespace
from concurrent.futures import ThreadPoolExecutor
import validators




app = Flask(__name__)
api = Api(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
datas = []

def make_reqs(link):
    try:
        data = requests.post('https://api-price-parse-v1.herokuapp.com/api/v1/parser', params=({'url': link}), verify=False, timeout=15).json()['price']
        if data > 0:
            return data
    except:
        return 0

class ParseLink(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)
        args = parser.parse_args()
        q = args['query']
        params = {
            "engine": "google",
            "q": q,
            "google_domain": "google.ru",
            "hl": "ru",
            "gl": "ru",
            "api_key": "df88d3ff9457c1010b4081ea4eb67f1f5b1fa2f544164e81267e472681f69e93",
            "num": 100
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results['organic_results']
        inline_shoping = results.get('shopping_results')
        if inline_shoping:
            for i in inline_shoping:
                datas.append({
                    'link': i['link'],
                    'price': i['extracted_price']
                })

        for i in organic_results:
            url = i['link']
            datas.append({"link": url, "price": make_reqs(url)})
            
        ret_d = sorted(datas, key = lambda i: i['price'])
        if len(ret_d) >= 3:
            data = [ret_d[0], ret_d[1],ret_d[2]]
            return {"data": data}, 200
        else:
            return {"data": "Not enough data to analyse..."}, 400




    pass


api.add_resource(ParseLink, '/')

if __name__ == '__main__':
    app.run(debug=True)
