from lark import Lark
from lark.visitors import Transformer
from rich import print

grammar = """
?start: commands*
?commands: set | require | call | func | fi

?atom: CNAME | INTEGER | STRING
?expr: call
    | member
    | atom
    | expr "+" expr -> plus
    | expr "-" expr -> sub
    | expr "/" expr -> div
    | expr "*" expr -> mul

?args: expr ("," expr)*
arg_names: CNAME ("," CNAME)*
?member: expr "." CNAME
    
require: "require" STRING "as" CNAME
set: "local" CNAME "=" expr
call: expr "("args?")"
func: "fn" CNAME "{" commands* "}"
    | "fn" CNAME "(" arg_names ")" "{" commands* "}" -> func_args

condition: expr
          | condition "==" condition -> equ
          | condition "!=" condition -> nequ
          | condition ">" condition -> gt
          | condition "<" condition -> lt
          | condition ">=" condition -> gte
          | condition "<=" condition -> lte

fi: "if" condition "{" commands* "}"


%import common.CNAME
%import common.NUMBER -> INTEGER
%import common.ESCAPED_STRING -> STRING
%import common.WS

%ignore WS
"""

test_code = """
local a = 10
local b = 20
local c = a + b
local d = a+b+c*2

print(a,b,c,d)
"""

parser = Lark(grammar, parser="lalr")

class XScriptAST(Transformer):
    def start(self, items): return items

    # transformaciones para el AST
    def INTEGER(self, token): return int(token)
    def STRING(self, token): return token[1:-1]
    def CNAME(self, token): return ("reference", str(token))
    def member(self, items): return ("reference_group", *(item[1] for item in items))
    def arg_names(self, items): return [item[1] for item in items]
    def args(self, items): return list(items)

    # condiciones
    def condition(self, items): return items[0]
    def equ(self, items): return ("equ", items[0], items[1])
    def nequ(self, items): return ("nequ", items[0], items[1])
    def gt(self, items): return ("gt", items[0], items[1])
    def lt(self, items): return ("lt", items[0], items[1])
    def gte(self, items): return ("gte", items[0], items[1])
    def lte(self, items): return ("gte", items[0], items[1])

    # funciones, variables y llamadas
    def set(self, items): return {"op": "set", "define": items[0], "value": items[1]}
    def call(self, items): return {"op": "call", "function": items[0], "arguments": items[1]}
    def func(self, items): return {"op": "new_function", "name": items[0][1], "block": items[1:]}
    def func_args(self, items): return {"op": "new_function", "name": items[0][1], "arguments": items[1], "block": items[2:]}
    
    # flujos
    def fi(self, items):
        return {"op": "fi", "condition": items[0], "block": items[1:]}

    # expresiones
    def plus(self, items): return ("add", items[0], items[1])
    def sub(self, items): return ("sub", items[0], items[1])
    def mul(self, items): return ("mul", items[0], items[1])
    def div(self, items): return ("div", items[0], items[1])

print(XScriptAST().transform(parser.parse(test_code)))
