
class RuntimeScript(object):
    def __init__(self):
        self.defines = {
            
        }
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
                    return self.defines[expr[1]]["value"]
                else: return None
            elif expr_type == "add":
                return self.evaluate_expression(expr[1]) + self.evaluate_expression(expr[2])
            elif expr_type == "sub":
                return self.evaluate_expression(expr[1]) - self.evaluate_expression(expr[2])
            elif expr_type == "mul":
                return self.evaluate_expression(expr[1]) * self.evaluate_expression(expr[2])
            elif expr_type == "div":
                return self.evaluate_expression(expr[1]) / self.evaluate_expression(expr[2])

    def evaluate_args(self, args:list):
        args_list = []

        for arg in args:
            args_list.append(self.evaluate_expression(arg))
        
        return args_list

    def set(self, define, value, **_): 
        self.defines[define[1]] = {"type": "variable", "value": self.evaluate_expression(value)}

    def call(self, function, arguments, **_): 
        print(function, self.evaluate_args(arguments))

rs = RuntimeScript()
rs.evaluate([
    {'op': 'set', 'define': ('reference', 'a'), 'value': 10},
    {'op': 'set', 'define': ('reference', 'b'), 'value': 20},
    {'op': 'set', 'define': ('reference', 'c'), 'value': ('add', ('reference', 'a'), ('reference', 'b'))},
    {'op': 'set', 'define': ('reference', 'd'), 'value': ('add', ('reference', 'a'), ('add', ('reference', 'b'), ('mul', ('reference', 'c'), 2)))},
    {'op': 'call', 'function': ('reference', 'print'), 'arguments': [('reference', 'a'), ('reference', 'b'), ('reference', 'c'), ('reference', 'd')]}
])
