import sys

__author__ = 'Jerry'


def is_literal(token):
    return (token.startswith('\'') and token.endswith('\'')) or (token.startswith('\"') and token.endswith('\"'))


def is_float(token):
    try:
        float(token)
        return True
    except ValueError:
        return False


class Parser:

    variables = {}
    TRUE = ":^)"
    FALSE = ":^{"
    truefalse = [TRUE, FALSE]

    def __init__(self):
        pass

    def parse_boolean(self, tokens):
        keywords = ["is", "isn\'t", "<", ">", "<=", ">=", "and", "or", "not"]
        new_tokens = []

        for token in tokens:
            if token in keywords:
                new_tokens.append(token)
            else:
                if is_literal(token):
                    new_tokens.append(token[1:-1])
                elif token.isdigit():
                    new_tokens.append(int(token))
                elif is_float(token):
                    new_tokens.append(float(token))
                elif token in self.variables:
                    new_tokens.append(self.variables[token])
                else:
                    print "wtf can't read", token
                    return -1

        for i in range(0, len(new_tokens)):
            token = new_tokens[i]
            # print token

            try:
                prev_token = new_tokens[i - 1]
                next_token = new_tokens[i + 1]
            except IndexError:
                print "wtf can't read this"
                return -1

            if token == "is":
                return 1 if prev_token == next_token else 0
            elif token == "isn\'t":
                return 1 if prev_token != next_token else 0
            elif token == "<":
                return 1 if prev_token < next_token else 0
            elif token == ">":
                return 1 if prev_token > next_token else 0
            elif token == "<=":
                return 1 if prev_token <= next_token else 0
            elif token == ">=":
                return 1 if prev_token >= next_token else 0

    def parse_math(self, tokens):
        return 0

    def parse_expression(self, tokens):
        boolean_result = self.parse_boolean(tokens)
        if boolean_result == 1:
            return self.TRUE
        elif boolean_result == 0:
            return self.FALSE
        else:
            return self.parse_math(tokens)

    def parse(self, lines):

        call_stack = []
        condition_execution_stack = []
        condition_scope_stack = []

        line_count = 0

        while line_count < len(lines):
            tokens = lines[line_count].split()
            # print tokens
            tokenslen = len(tokens)

            # Skip blank lines
            if tokenslen == 0:
                continue

            # Skip line if this is not the right conditional branch UNLESS it's an "else" or "end if"
            if (condition_scope_stack != condition_execution_stack) \
                    and not (((tokenslen == 2) and (tokens[0] == "or") and (tokens[1] == "not"))
                             or ((tokenslen == 2) and (tokens[0] == "done") and (tokens[1] == "implying"))):
                line_count += 1
                continue

            if (tokens[0] == "mfw") and (tokenslen > 1):
                for token in tokens[1:]:
                    if is_literal(token):
                        print token[1:-1],
                    elif token.isdigit() or is_float(token):
                        print token,
                    elif token in self.variables:
                        print self.variables[token],
                print

            elif tokens[0] == "be":
                if tokenslen == 3:
                    if is_literal(tokens[2]):
                        self.variables[tokens[1]] = tokens[2][1:-1]
                    elif tokens[2] in self.variables:
                        self.variables[tokens[1]] = self.variables[tokens[2]]
                    elif tokens[2].isdigit():
                        self.variables[tokens[1]] = int(tokens[2])
                    elif is_float(tokens[2]):
                        self.variables[tokens[1]] = float(tokens[2])
                    else:
                        print "wtf can't be this"
                        return
                elif tokenslen > 3:
                    self.variables[tokens[1]] = self.parse_expression(tokens[2:])

            elif tokens[0] == "implying":
                condition_scope_stack.append(self.TRUE)

                # Single boolean argument
                if tokenslen == 2:
                    if is_literal(tokens[1]):
                        if tokens[1][1:-1] in self.truefalse:
                            condition_execution_stack.append(tokens[1][1:-1])
                    elif (tokens[1] in self.variables) and (self.variables[tokens[1]] in self.truefalse):
                        condition_execution_stack.append(self.variables[tokens[1]])

                # Boolean expression
                elif tokenslen > 2:
                    parse_result = self.parse_expression(tokens[1:])
                    if parse_result in self.truefalse:
                        condition_execution_stack.append(parse_result)
                    else:
                        print "wtf can't imply this"
                        return

                # print condition_scope_stack, condition_execution_stack

            elif (tokenslen == 2) and (tokens[0] == "or") and (tokens[1] == "not") and (len(condition_scope_stack) > 0):
                condition_scope_stack[-1] = self.FALSE
                # print condition_scope_stack, condition_execution_stack

            elif tokens[0] == "inb4":
                if (tokenslen == 8) and (tokens[2] == "from") and (tokens[4] == "to") and (tokens[6] == "by"):
                    self.variables[tokens[1]] = int(tokens[3])
                    call_stack.append({"linepos": line_count,
                                      "counter": tokens[1],
                                      "start": int(tokens[3]),
                                      "end": int(tokens[5]),
                                      "step": int(tokens[7])})
                else:
                    print "wtf can't inb4 this"
                    return

            elif (tokens[0] == "done") and (tokenslen > 1):
                if tokens[1] == "inb4" and len(call_stack) > 0:
                    call = call_stack[-1]
                    self.variables[call["counter"]] += call["step"]
                    if (call["step"] > 0 and self.variables[call["counter"]] < call["end"]) \
                            or (call["step"] < 0 and self.variables[call["counter"]] > call["end"]):
                        line_count = call["linepos"]
                    else:
                        del self.variables[call["counter"]]
                        call_stack.pop()
                elif tokens[1] == "implying" and len(condition_scope_stack) > 0:
                    condition_scope_stack.pop()
                    condition_execution_stack.pop()
                    # print condition_scope_stack, condition_execution_stack

            else:
                print "wtf r u doing"
                return

            line_count += 1

    def main(self):
        inputlines = []

        for line in sys.stdin:
            strippedline = line.lstrip()
            if len(strippedline) > 0:
                if strippedline[0] != '>':
                    print "do you even greentext"
                    return
                else:
                    inputlines.append(strippedline[1:])

        self.parse(inputlines)


Parser().main()