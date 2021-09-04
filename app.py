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
from statistics import mean




app = Flask(__name__)
api = Api(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
datas = []

def make_reqs(link):
    try:
        data = requests.post('https://api-price-parse-v1.herokuapp.com/api/v1/parser', params=({'url': link}), verify=False).json()['price']
        if data > 0:
            datas.append({'link': link, 'price': data})
    except:
        pass

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
            "num": 30
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

        urls = []
        for i in organic_results:
            urls.append(i['link'])
        with ThreadPoolExecutor(max_workers=40) as executor:
            future_to_files = {executor.submit(make_reqs, url): url for url in urls}
        data_to_return = sorted(datas, key=lambda i: i['price'])
        length_to_mean = int(len(data_to_return))
        clean_data = []
        if len(data_to_return) > 4:
            for n,i in enumerate(data_to_return):
                if n >= length_to_mean - 2 and n <= length_to_mean:
                    clean_data.append(i)
            print(clean_data)
            return {"data": clean_data}, 200
        else:
            return {"data": "Not enough data to analyse..."}, 400




    pass


api.add_resource(ParseLink, '/')

if __name__ == '__main__':
    app.run(debug=True)
