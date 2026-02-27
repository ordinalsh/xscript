from src.runtime import Runtime, XSEvaluator
from src.ast_gen import XScriptAST, parser

code = """
fn myNum(a) { return a }
local a = 10
local a = myNum(a) + 10

print(a)
"""
ast = XScriptAST().transform(parser.parse(code))

xs = XSEvaluator()
xs.evaluate_ast(ast)