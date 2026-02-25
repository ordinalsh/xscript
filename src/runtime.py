# TODO : Reescribir todo el Runtime Desde cero con el nuevo engine. Hacerlo mas modular y posiblemente, en futuras versiones transicion de Cython.
from .modules.defines import Defines, XSObject

class XSEvaluator(object):
    def __init__(self):
        self.defines = Defines()

    def evaluate_ast(self, ast: list) -> any:
        for command in ast:
            operation = getattr(self, command["op"], None)
            if operation:
                response = operation(**command)
                if response: return response
            else: raise RuntimeError(f"No operation named '{command["op"]}' is avaliable.")

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

                if XSObj.kind == 2: return self.evaluate_expression(XSObj.value)
                else: raise RuntimeError("Can't return a reference as a variable if it has been defined as a function.")  

        return None

    def set(self, define, value, **_): self.defines.set_object(2, define[1], self.evaluate_expression(value)) # Agregar define como objeto tipo variable.

class Runtime(object):
    ...