from rich import print

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

        print(ast)
        print("\n","·"*132,"\n")

        if not isinstance(ast, list):
            ast = [ast]
        self.run_block(ast)

    def run_block(self, ast):
        for astobject in ast:
            #print(astobject)
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

    def eval_function(self, fnname, arguments):
        function = self.defines.find_define(fnname)
        fn_arguments = function["value"]["arguments"]
        fn_block = function["value"]["block"]

        if function["type"] != "function":
            raise RuntimeError(f"define with name '{fnname}' is not callable.")
        
        self.defines.add_scope(fnname)
        if len(fn_arguments) > len(arguments):
            raise RuntimeError(f"the function '{fnname}' requires those arguments {fn_arguments}")
        elif len(arguments) > len(fn_arguments):
            raise RuntimeError(f"the function '{fnname}' only accepts {len(fn_arguments)} arguments, but you passed {len(arguments)}")

        for index, argument in enumerate(arguments):
            self.defines.set_define(fn_arguments[index], "variable", argument) # los argumentos ya estan parseados por el eval_expression
        
        self.run_block(fn_block)
        self.defines.remove_scope()

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
        
        if isinstance(callable_value, dict): 
            self.eval_function(function, self.eval_arguments(arguments))

        elif isinstance(callable_value, object):
            #print(self.eval_arguments(arguments))
            callable_value(*self.eval_arguments(arguments))

    def new_function(self, name, block, arguments=None, **_):
        self.defines.set_define(name, "function", {
            "arguments": arguments,
            "block": block,
        })
