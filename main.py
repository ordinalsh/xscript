from src.runtime import Runtime, XSEvaluator
from src.ast_gen import XScriptAST, parser

code = """
local x = 10
local y = 20

local z = x + y*2
"""
ast = XScriptAST().transform(parser.parse(code))

xs = XSEvaluator()
xs.evaluate_ast(ast)