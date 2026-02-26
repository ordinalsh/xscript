from src.runtime import Runtime, XSEvaluator
from src.ast_gen import XScriptAST, parser

code = """
fn num {
    local x = 10
    local y = 20
    local z = x + y*2

    print(z)
}

num()
print(z)
"""
ast = XScriptAST().transform(parser.parse(code))

xs = XSEvaluator()
xs.evaluate_ast(ast)