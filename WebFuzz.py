from urllib.parse import parse_qs, urlparse
from xml import dom
import pycurl
import sys
import requests
from bs4 import BeautifulSoup
from utils.parser import HTMLParser
from utils.miner import GrammarMiner
import gramfuzz

# def get_grammar_urls():
#     ## testphp.vulnweb.com
#     urls = ['uname=admin&pass=admin', 'uname=default&pass=default', 'uname=test&pass=test']
#     # ## webscantest
#     # #urls = ['login=test&passwd=test&submit_login=login', 'login=hello&passwd=admin&submit_login=login', 'login=admin&passwd=admin&submit_login=login']
#     # ## broken crystals
#     # # urls = ['user=hello&password=test&op=basic','user=test&password=test&op=basic','user=hello&password=test43526&op=basic', 'user=admin&password=admin&op=basic']
#     # ## juiceshop
#     # urls=['email=abc&password=def','email=test&password=test', "email=' or true -- & password=324" ] 
#     return urls
 
class WebFuzz():
    def __init__(self, req_type, base_url):
        self.req_type = req_type
        self.base_url = base_url
        self.html_parser = HTMLParser()
        self.parseHTML()
        self.grammar_miner = GrammarMiner(self.html_parser)
        self.grammar_urls = self.get_grammar_urls()
        domain = urlparse(self.base_url).netloc
        self.new_url = domain + "/"+ self.html_parser.action

    def parseHTML(self):
        html_text = requests.get(self.base_url).text
        soup = BeautifulSoup(html_text, "lxml")
        html_form = soup.body.find("form")
        self.html_parser.parseForm(html_form)
        # print(self.html_parser.action)
        # print(self.html_parser.fields)
    
    def get_grammar_urls(self):
        gram_fuzzer = gramfuzz.GramFuzzer()
        gram_fuzzer.load_grammar("generated-grammar.py")
        urls = gram_fuzzer.gen(cat="url", num=20)
        return [url.decode() for url in urls]


    def output_result_info(self):
        print("==========================================================")
        print("\tWebFuzz Result Summary\t")
        print("==========================================================")
        print("Target URL: " + self.new_url)
        print("Request Type: " + self.req_type)
        print("Total Requests: "+ str(len(self.grammar_urls)))
        print("==========================================================")
        print("Response\t\tRequest Params")
    
    def run(self):
        self.output_result_info()
        for gen_url in self.grammar_urls:
            c = pycurl.Curl()
            req_params = gen_url.split("?")[1]
            if self.req_type == "POST":
                c.setopt(c.URL, self.new_url)
                c.setopt(pycurl.POST, 1)
                c.setopt(pycurl.POSTFIELDS, req_params)
            elif self.req_type == "GET":
                complete_url = self.new_url +"?"+ req_params
                c.setopt(c.URL, complete_url)
                c.setopt(pycurl.HTTPGET, 1)
            c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
            c.perform()
            req_output = str(parse_qs(req_params))
            print(str(c.getinfo(pycurl.HTTP_CODE)) +"\t\t"+ req_output)

## http://testphp.vulnweb.com/userinfo.php

webFuzz = WebFuzz("POST", "http://testphp.vulnweb.com/login.php")
webFuzz.run()

# http://localhost/mutillidae/index.php?page=login.php
# http://www.webscantest.com/login.php

# webFuzz = WebFuzz(sys.argv[1], sys.argv[2])
# https://brokencrystals.com/api/auth/login
# http://juice-shop.herokuapp.com/rest/user/login
# print(webFuzz.grammar_urls)
