from src.runtime import Runtime, XSEvaluator
from src.ast_gen import XScriptAST, parser

code = """
local a = {a: 10}
print(a.a)
"""
ast = XScriptAST().transform(parser.parse(code))

xs = XSEvaluator()
xs.evaluate_ast(ast)