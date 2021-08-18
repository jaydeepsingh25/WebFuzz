from urllib.parse import parse_qs, urlparse
from xml import dom
import pycurl
import sys
import requests
from bs4 import BeautifulSoup
from utils.parser import HTMLParser
from utils.miner import GrammarMiner
import gramfuzz
import io
import argparse, sys
import re
parser=argparse.ArgumentParser()

parser.add_argument('--url', help='Website URL', required= True, type=str)
parser.add_argument('--method', help='Type of request: GET/POST', required=True, type=str)
parser.add_argument('--attack', help='Type of attack: SQLI/XSS', required=True, type=str)
parser.add_argument('--filtercode', help='Filter the status code', type = int)
parser.add_argument('--noofrequests', help='Number of requests, default value 20', type=int, default=20)

args=parser.parse_args()

 
class WebFuzz():
    def __init__(self, req_type, base_url):
        self.req_type = req_type
        self.base_url = base_url
        self.html_parser = HTMLParser()
        self.parseHTML()
        self.grammar_miner = GrammarMiner(self.html_parser, args.attack)
        self.grammar_urls = self.get_grammar_urls()
        domain = urlparse(self.base_url).netloc
        self.new_url = domain + "/" + self.html_parser.action
        #print(self.grammar_urls)

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
        urls = gram_fuzzer.gen(cat="url", num=args.noofrequests)
        return [url.decode() for url in urls]


    def output_result_info(self):
        print("==========================================================")
        print("\tWebFuzz Result Summary\t")
        print("==========================================================")
        print("Target URL: " + self.new_url)
        print("Request Type: " + self.req_type)
        print("Type of attack " + args.attack )
        print("Total Requests: "+ str(len(self.grammar_urls)))
        print("==========================================================")
        if args.attack == "SQLI":
            print("Response\t\tRequest Params")
        elif args.attack == "XSS":
            print("XSS Result\t\tRequest Params")

    def fuzz_injection_attack(self):
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
            response_code = c.getinfo(pycurl.HTTP_CODE)
            if args.filtercode != response_code:
                print(str(c.getinfo(pycurl.HTTP_CODE)) +"\t\t"+ req_output)
    
    def fuzz_xss_attack(self):
        for gen_url in self.grammar_urls:
            storage = io.BytesIO()
            c = pycurl.Curl()
            req_params = gen_url.split("?")[2]
            if self.req_type == "POST":
                c.setopt(c.URL, self.new_url)
                c.setopt(pycurl.POST, 1)
                c.setopt(pycurl.POSTFIELDS, req_params)
                #c.setopt(c.WRITEFUNCTION, storage.write)
            elif self.req_type == "GET":
                complete_url = self.new_url +"&"+ req_params
                c.setopt(c.URL, complete_url)
                c.setopt(pycurl.HTTPGET, 1)
                #c.setopt(c.WRITEFUNCTION, storage.write)
            c.setopt(pycurl.WRITEFUNCTION, storage.write)
            c.perform()
            content = storage.getvalue().decode('UTF-8')
            #xss_query = re.search('searchFor=(.+?)&goButton', req_params).group(1)
            reqex_string = self.grammar_miner.xss_field_name + "=(.+?)&" + self.grammar_miner.submit_field_name
            xss_query = re.search(reqex_string, req_params)
            if xss_query:
                xss_query_val = xss_query.group(1).strip()
                #param_dict = parse_qs(req_params)
                response_code = c.getinfo(pycurl.HTTP_CODE)
                xss_result = "FAIL"
                if response_code != args.filtercode: 
                    if xss_query_val in content:
                        xss_result = "SUCCESS"
                    #print(str(c.getinfo(pycurl.HTTP_CODE)) +"\t\t"+ xss_result + "\t\t" + xss_query_val)
                    print(xss_result + "\t\t" + xss_query_val)

    def run(self):
        self.output_result_info()
        if args.attack == "SQLI":
            self.fuzz_injection_attack()
        elif args.attack == "XSS":
            self.fuzz_xss_attack()
        

## http://testphp.vulnweb.com/userinfo.php
webFuzz = WebFuzz(args.method, args.url)
## webFuzz = WebFuzz("POST", "http://testphp.vulnweb.com/login.php", "SQLI")
webFuzz.run()

# http://localhost/mutillidae/index.php?page=login.php
# http://www.webscantest.com/login.php

# webFuzz = WebFuzz(sys.argv[1], sys.argv[2])
# https://brokencrystals.com/api/auth/login
# http://juice-shop.herokuapp.com/rest/user/login
# print(webFuzz.grammar_urls)
