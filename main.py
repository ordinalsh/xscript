from src.runtime import Runtime, XSEvaluator
from src.ast_gen import XScriptAST, parser

code = """
if true { print("es perfecto") }
"""
ast = XScriptAST().transform(parser.parse(code))

xs = XSEvaluator()
xs.evaluate_ast(ast)