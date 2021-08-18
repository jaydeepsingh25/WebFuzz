from html.parser import HTMLParser
import gramfuzz
from gramfuzz.fields import *
from utils.base_grammar import base_grammar 

class GrammarMiner():
    def __init__(self, parser, attack):
        self.base_grammar = base_grammar
        self.attack_type = attack
        self.grammar_rules = self.create_new_rules(parser)

    def create_new_rules(self,html_parser):
        new_gram_rules = []
        action_gram_rule = 'UDef("action", Or("' + html_parser.action+'"))'
        new_gram_rules.append(action_gram_rule)

        req_params = ['URef("'+ key +'")' for key in html_parser.fields.keys()]
        query_gram_rule = 'UDef("query",'+ ",".join(req_params) + ",sep='&')"
        new_gram_rules.append(query_gram_rule)

        for field in html_parser.fields:
            field_name = field
            field_type = html_parser.fields[field_name]
            if field_type == "text" or field_type == "password":
                # new_gram_rules.append('UDef("'+field_name+'", Or("'+ field_name +'"), Or("test","admin","hello"), sep="=")')
                if self.attack_type == "SQLI":
                    new_gram_rules.append('UDef("'+field_name+'", Or("'+ field_name +'"), URef("_sql_string"), sep="=")')
                elif self.attack_type == "XSS":
                    self.xss_field_name = field_name
                    new_gram_rules.append('UDef("'+field_name+'", Or("'+ field_name +'"), URef("_xss_string"), sep="=")')
            if field_type == "submit":
                self.submit_field_name = field_name
                new_gram_rules.append('UDef("'+field_name+'", Or("'+ field_name +'"), Or("go"), sep="=")')
            # if field_type == "password":
                # new_gram_rules.append('UDef("'+field_name+'", Or("'+ field_name +'"), URef("_password"), sep="=")')
                # new_gram_rules.append('UDef("'+field_name+'", Or("'+ field_name +'"), URef("_sql_string"), sep="=")')
        new_rules_with_delimeter = "\n".join(new_gram_rules)
        new_grammar = "\n".join([base_grammar, new_rules_with_delimeter])
        # print(PAGE_GRAMMAR)
        with open('generated-grammar.py', 'w') as f:
            f.write(new_grammar)
        return new_grammar
