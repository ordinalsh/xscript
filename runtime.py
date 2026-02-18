
class RuntimeScript(object):
    def __init__(self):
        self.defines = {}
        self.native_calls = {}

    def evaluate(self, ast_list: list):
        astobj: dict

        for astobj in ast_list:
            operation = getattr(self, astobj["op"])
            operation(**astobj)

    def evaluate_expression(self, expr):
        if isinstance(expr, int): return expr
        elif isinstance(expr, str): return expr
        elif isinstance(expr, tuple):
            expr_type = expr[0]
            if expr_type == "reference":
                if expr[1] in self.defines:
                    return self.defines[expr[1]]
                else: return None

    def set(self, define, value, **_): 
        self.defines[define[1]] = self.evaluate_expression(value)

    def call(self, function, arguments, **_): 
        print(function, self.evaluate_expression(arguments[0]))

rs = RuntimeScript()
rs.evaluate([{'op': 'set', 'define': ('reference', 'a'), 'value': 10}, {'op': 'call', 'function': ('reference', 'print'), 'arguments': [('reference', 'a')]}])