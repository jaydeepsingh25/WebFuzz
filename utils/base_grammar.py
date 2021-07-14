base_grammar = '''

import gramfuzz
from gramfuzz.fields import *

class URef(Ref):
    cat = "url_def"
class UDef(Def):
    cat = "url_def"


Def("url",
    URef("action"),
    URef("query"),
    cat="url",
    sep="?"
    )

UDef("_string",
    String(min=1, max=10, charset=String.charset_alphanum),
    )

UDef("_password",
    Or("pass1","pass2","test"),
    )

UDef("_email",
    String(min=1, max=10, charset=String.charset_alphanum),
    "@",
    String(min=1, max=10, charset=String.charset_alphanum),
    ".",
    String(min=2, max=4, charset=String.charset_alpha)
    )
'''