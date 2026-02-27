from .modules.defines import Defines # El defines

class XSEvaluator(object):
    def __init__(self):
        self.defines = Defines()
        self.defines.set_object(1, "print", print)
        
        self.defines.set_object(2, "true", True) # booleanos como variables, es raro
        self.defines.set_object(2, "false", False) 

    def evaluate_ast(self, ast: list, no_stop_on_return: bool = True):
        if isinstance(ast, dict): ast = [ast]

        for command in ast:
            operation = getattr(self, command["op"], None)
            if operation:
                response = operation(**command)
                if response is not None and not no_stop_on_return:
                    return response
            else: raise RuntimeError(f"No operation named '{command['op']}' is available.")
        return None

    def evaluate_expression(self, expression):
        if isinstance(expression, (str, int, float, bool)): return expression

        if isinstance(expression, tuple):
            EXPR_OP = expression[0]

            if EXPR_OP == "add": return self.evaluate_expression(expression[1]) + self.evaluate_expression(expression[2])
            if EXPR_OP == "sub": return self.evaluate_expression(expression[1]) - self.evaluate_expression(expression[2])
            if EXPR_OP == "mul": return self.evaluate_expression(expression[1]) * self.evaluate_expression(expression[2])
            if EXPR_OP == "div": return self.evaluate_expression(expression[1]) / self.evaluate_expression(expression[2])
            if EXPR_OP == "reference": 
                XSObj = self.defines.find_define(expression[1])
                if not XSObj: return None

                if XSObj.kind == 2:
                    return XSObj.value
                else: raise RuntimeError("Can't return a reference as a variable if it has been defined as a function.")  
            if EXPR_OP == "call_expr":
                EXPR_FN_NAME = expression[1]
                EXPR_ARG_LIST = expression[2]

                return self.evaluate_function(EXPR_FN_NAME, EXPR_ARG_LIST)

        return None

    def evaluate_function(self, name, arguments):
        obj = self.defines.find_define(name)

        if not obj: raise RuntimeError(f"No define with name '{name}' is callable")

        # Evaluamos los argumentos antes de ejecutar la función
        evaluated_arguments = [self.evaluate_expression(arg) for arg in arguments]

        if obj.kind == 1: 
            return obj.value(*evaluated_arguments)
        elif obj.kind == 2:
            raise RuntimeError(f"No define with name '{name}' is callable")

        fn_arguments = obj.value["arguments"] or []
        fn_block = obj.value["block"]

        if len(fn_arguments) > len(evaluated_arguments):
            raise RuntimeError(f"the function '{name}' requires those arguments {fn_arguments}")
        elif len(evaluated_arguments) > len(fn_arguments):
            raise RuntimeError(f"the function '{name}' only accepts {len(fn_arguments)} arguments, but you passed {len(evaluated_arguments)}")
        
        self.defines.add_scope() # Añadimos nuevo stack
        for index, result in enumerate(evaluated_arguments):
            self.defines.set_object(2, fn_arguments[index], result) # Añadimos al scope el argumento con el nombre como una variable.

        response = self.evaluate_ast(fn_block, False) # Que devuelva cuando haya un return.
        self.defines.remove_scope() # Eliminamos del stack el scope.

        return response # Devolvemos la respuesta del AST

    def evaluate_condition(self, condition):
        """
            ("and", expr, expr)
            ("or", expr, expr)
            ("equ", expr, expr)
            ("nequ", expr, expr)
            ("gt", expr, expr)
            ("lt", expr, expr)
            ("gte", expr, expr)
            ("lte", expr, expr)
        """
        if isinstance(condition, tuple):
            EXPR_OP = condition[0]

            if EXPR_OP == "and": return self.evaluate_condition(condition[1]) and self.evaluate_condition(condition[2])
            if EXPR_OP == "or": return self.evaluate_condition(condition[1]) or self.evaluate_condition(condition[2])
            if EXPR_OP == "equ": return self.evaluate_expression(condition[1]) == self.evaluate_expression(condition[2])
            if EXPR_OP == "nequ": return self.evaluate_expression(condition[1]) != self.evaluate_expression(condition[2])
            if EXPR_OP == "gt": return self.evaluate_expression(condition[1]) > self.evaluate_expression(condition[2])
            if EXPR_OP == "lt": return self.evaluate_expression(condition[1]) < self.evaluate_expression(condition[2])
            if EXPR_OP == "gte": return self.evaluate_expression(condition[1]) >= self.evaluate_expression(condition[2])
            if EXPR_OP == "lte": return self.evaluate_expression(condition[1]) <= self.evaluate_expression(condition[2])
            if EXPR_OP == "reference": return self.evaluate_expression(condition[1])

        return None

    def fi(self, condition, block, child, **_):
        result = self.evaluate_condition(condition)

        if result: 
            return self.evaluate_ast(block, False)

        if child:
            if child["op"] == "elfi": return self.fi(**child)
            elif child["op"] == "elsf": return self.evaluate_ast(child["block"], False)

    def set(self, define, value, **_): 
        resultado = self.evaluate_expression(value)
        self.defines.set_object(2, define[1], resultado) # Agregar define como objeto tipo variable.
    
    def new_function(self, name, arguments=None, block=None, **_):
        self.defines.set_object(3,name,{
            "arguments":arguments,
            "block":block
        })

    def ret(self, value, **_): # Esencial hermano :)
        return self.evaluate_expression(value)

    def call(self, function, arguments, **_):
        name = function[1]
        self.evaluate_function(name, arguments)

class Runtime(object):
    ...