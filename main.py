from src.runtime import Runtime, XSEvaluator
from src.ast_gen import XScriptAST, parser

code = """
fn test(a,b) {
    local result = a + b
    if result > 10 {
        return "mayor que diez"
    } else {
        return "menor que diez"
    }
    print("esto se imprime?")
}

local a = test(10, 20)
print(a)
"""
ast = XScriptAST().transform(parser.parse(code))

xs = XSEvaluator()
xs.evaluate_ast(ast)