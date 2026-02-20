class DefinesManager:
    def __init__(self):
        self.scopes = ["script"]
        self.defines = {}

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

        for astobject in ast:
            operation = getattr(self, astobject["op"])
            operation(**astobject)

    def eval_expression(self, expression: tuple | int | str) -> any:
        if not isinstance(expression, tuple): return expression

        match expression[0]:
            case "reference": # hace referencia a un objeto
                reference = self.defines.find_define(expression[1])

                if not reference: # verificar si existe la variable
                    raise RuntimeError(f"no reference with name {expression[1]} is defined on current scope.")
                
                return reference["value"] # devolver la referencia
            
            case "add":
                return self.eval_expression(expression[1]) + self.eval_expression(expression[2])
            
    def set(self, define, value, **_): 
        self.defines.set_define(define[1], "variable", self.eval_expression(value))
        print(self.defines.defines)
