class DefinesManager:
    def __init__(self):
        self.scopes = ["script"]
        self.defines = {
            "script": {
                "print": {"type": "function", "value": print}
            }
        }

    def set_define(self, name, type, value):
        scope = self.scopes[-1]

        if not scope in self.defines:
            self.defines[scope] = {}
        self.defines[scope][name] = {"type": type, "value": value}
    
    def free_define(self, name):
        if not name in self.defines[self.scopes[-1]]:
            raise RuntimeError(f"no define with name {name} found in the current scope")
        del self.defines[self.scopes[-1]][name]

    def find_define(self, name):
        for scope in reversed(self.scopes):
            definition = self.defines[scope].get(name)
            if definition is not None:
                return definition
        return None
    
    def add_scope(self, name_scope):
        self.scopes.append(name_scope)

    def remove_scope(self):
        scope_name = self.scopes[-1]
        if scope_name == "script":
            raise RuntimeError("cant remove scope with the name script, reserved.")
        self.scopes.pop()


class RunScript(object):
    def __init__(self, ast):
        self.defines = DefinesManager()

        if not isinstance(ast, list):
            ast = [ast]

        for astobject in ast:
            operation = getattr(self, astobject["op"])
            operation(**astobject)

    def eval_expression(self, expression: tuple | int | str) -> any:
        if not isinstance(expression, tuple): return expression

        match expression[0]:
            case "reference": # hace referencia a un objeto
                reference = self.defines.find_define(expression[1])

                if not reference: # verificar si existe la variable
                    raise RuntimeError(f"no reference with name '{expression[1]}' is defined on current scope.")
                
                return reference["value"] # devolver la referencia
            
            case "add": return self.eval_expression(expression[1]) + self.eval_expression(expression[2]) # sumar
            case "sub": return self.eval_expression(expression[1]) - self.eval_expression(expression[2]) # restar
            case "div": return self.eval_expression(expression[1]) / self.eval_expression(expression[2]) # dividir
            case "mul": return self.eval_expression(expression[1]) * self.eval_expression(expression[2]) # multiplicar
    
    def eval_arguments(self, args: list): return list(map(self.eval_expression, args))        
    
    def set(self, define, value, **_): 
        self.defines.set_define(define[1], "variable", self.eval_expression(value))
        print(self.defines.defines)

    def call(self, function, arguments, **_):
        function = function[1]

        callable_define = self.defines.find_define(function)
        if not callable_define:
            raise RuntimeError(f"no define with name '{function}' that can be callable.")
        
        callable_type = callable_define["type"]
        callable_value = callable_define["value"]
        if callable_type != "function": 
            raise RuntimeError(f"no define with name '{function}' that can be callable.")
        
        if isinstance(callable_value, list): ...
        elif isinstance(callable_value, object):
            print(self.eval_arguments(arguments))
            callable_value(*self.eval_arguments(arguments))
