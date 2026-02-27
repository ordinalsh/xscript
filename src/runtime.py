# TODO : Reescribir todo el Runtime Desde cero con el nuevo engine. Hacerlo mas modular y posiblemente, en futuras versiones transicion de Cython.
from .modules.defines import Defines, XSObject

class XSEvaluator(object):
    def __init__(self):
        self.defines = Defines()
        self.defines.set_object(1, "print", print)

    def evaluate_ast(self, ast: list, no_stop_on_return: bool = True) -> any:
        if type(ast) is dict: ast = [ast]

        for command in ast:
            operation = getattr(self, command["op"], None)
            if operation:
                response = operation(**command)
                if response and not no_stop_on_return: return response
            else: raise RuntimeError(f"No operation named '{command["op"]}' is avaliable.")
        return None

    def evaluate_expression(self, expression):
        t = type(expression)
        if t is str or t is int: return expression

        if t is tuple:
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
        if obj.kind == 1: 
            return obj.value(*arguments)
        elif obj.kind == 2:
            raise RuntimeError(f"No define with name '{name}' is callable")

        fn_arguments = obj.value["arguments"] or []
        fn_block = obj.value["block"]

        if len(fn_arguments) > len(arguments):
            raise RuntimeError(f"the function '{name}' requires those arguments {fn_arguments}")
        elif len(arguments) > len(fn_arguments):
            raise RuntimeError(f"the function '{name}' only accepts {len(fn_arguments)} arguments, but you passed {len(arguments)}")
        
        self.defines.add_scope() # Añadimos nuevo stack
        for index,argument in enumerate(arguments):
            result = self.evaluate_expression(argument)
            self.defines.set_object(2, fn_arguments[index], result) # Añadimos al scope el argumento con el nombre como una variable.

        response = self.evaluate_ast(fn_block, False) # Que devuelva cuando haya un return.
        self.defines.remove_scope() # Eliminamos del stack el scope.

        return response # Devolvemos la respuesta del AST

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
        arguments = list(map(self.evaluate_expression, arguments))        
        name = function[1]
        obj = self.defines.find_define(name)

        if not obj: raise RuntimeError(f"No define with name '{name}' is callable")
        elif obj.kind == 2: raise RuntimeError(f"You can't call '{name}' because is a variable.")
        
        self.evaluate_function(name, arguments)
        

class Runtime(object):
    ...