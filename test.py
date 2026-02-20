from src.ast_gen import XScriptAST, parser
from src.runtime import RunScript

code = open("test.xsc", "r")
parseado = parser.parse(code.read())

ast = XScriptAST()
generado = ast.transform(parseado)

rs = RunScript(generado)