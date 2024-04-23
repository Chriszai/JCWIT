import javalang

tokens = javalang.tokenizer.tokenize('Verifier.nondetBoolean();')
parser = javalang.parser.Parser(tokens)
tree = parser.parse_expression()
for path, node in tree:
    print(node)