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

?condition: expr
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
fn loop {
    fn call_this_on_loop(string) { print(string) }
    call_this_on_loop("Hello world, this will be looped, depending on the engine that uses XScript")
}
"""

parser = Lark(grammar, parser="lalr")

class XScriptAST(Transformer):
    def start(self, items): return items

    def INTEGER(self, token): return int(token)
    def STRING(self, token): return token[1:-1]
    def CNAME(self, token): return ("reference", str(token))
    def member(self, items):
        # Usamos una "list comprehension" para extraer el segundo elemento (índice 1)
        return ("reference_group", *(item[1] for item in items))
    def arg_names(self, items):
        return [item[1] for item in items]

    def set(self, items): return {"set": items[0], "value": items[1]}
    def call(self, items): return {"call": items[0], "arguments": items[1:]}
    def func(self, items): return {"func": items[0][1], "block": items[1:]}
    def func_args(self, items): return {"func": items[0][1], "arguments": items[1], "block": items[2:]}
    
    def plus(self, items): return ("add", items[0], items[1])
    def sub(self, items): return ("sub", items[0], items[1])
    def mul(self, items): return ("mul", items[0], items[1])
    def div(self, items): return ("div", items[0], items[1])

print(XScriptAST().transform(parser.parse(test_code)))