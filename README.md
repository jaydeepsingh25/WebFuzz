# WebFuzz

* The tool can be executed as python script from command line and it supports the following arguments:
	* Mandatory Arguments:
	    * --url: it determines the url of the web application.
	    * --method: it defines the method i.e GET or POST
		* --attack: it defines whether the attack is sql-injection or xss. (Valid Values: SQLI or XSS)
	* Optional Arguments:
		* --filtercode: it filters the response code of the response given by the webfuzzer
		* --noofrequests: it defines the number of request that the fuzzer will hit (Default value: 20)

* A sample command to run WebFuzz from the command line would be: 
	* python WebFuzz.py --url=http://testphp.vulnweb.com/login.php --method=POST --attack=SQLI --filtercode=302 --noofrequests=30