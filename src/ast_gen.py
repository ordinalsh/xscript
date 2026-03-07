from lark import Lark
from lark.visitors import Transformer

grammar = open("grammar.lark", "r")
parser = Lark(grammar, parser="lalr")

class XScriptAST(Transformer):
    def start(self, items): return items

    # transformaciones para el AST
    def INTEGER(self, token): return int(token)
    def STRING(self, token): return token[1:-1]
    def CNAME(self, token): return ("reference", str(token))
    def dict_key(self, item): return (item[0][1], item[1])
    def dict(self, items): return dict(items)

    def member(self, items): return ("reference_group", *(item[1] for item in items))
    def arg_names(self, items): return [item[1] for item in items]
    def block(self, items): return items

    # condiciones
    def condition(self, items): return items[0]
    def equ(self, items): return ("equ", items[0], items[1])
    def nequ(self, items): return ("nequ", items[0], items[1])
    def gt(self, items): return ("gt", items[0], items[1])
    def lt(self, items): return ("lt", items[0], items[1])
    def gte(self, items): return ("gte", items[0], items[1])
    def lte(self, items): return ("gte", items[0], items[1])
    def andc(self, items): return ("and", items[0], items[1])
    def orc(self, items): return ("or", items[0], items[1])

    # funciones, variables y llamadas
    def set(self, items): return {"op": "set", "define": items[0], "value": items[1]}
    def call(self, items): return {"op": "call", "function": items[0], "arguments": items[1:]}
    def func(self, items): return {"op": "new_function", "name": items[0][1], "block": items[1:]}
    def func_args(self, items): return {"op": "new_function", "name": items[0][1], "arguments": items[1], "block": items[2:]}
    def ret(self, items): return {"op": "ret", "value": items[0]}

    # flujos
    def fi(self, items):
        child = items[2] if len(items) > 2 else None
        return {"op": "fi", "condition": items[0], "block": items[1], "child": child}

    def elfi(self, items):
        child = items[2] if len(items) > 2 else None
        return {"op": "elfi", "condition": items[0], "block": items[1], "child": child}

    def elsf(self, items):
        return {"op": "elsf", "block": items[0]}

    # expresiones
    def plus(self, items): return ("add", items[0], items[1])
    def sub(self, items): return ("sub", items[0], items[1])
    def mul(self, items): return ("mul", items[0], items[1])
    def div(self, items): return ("div", items[0], items[1])
    def call_on_expr(self, items): operation = items[0]; return ("call_expr" ,operation["function"][1], operation["arguments"])

