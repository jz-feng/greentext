import sys
import re

__author__ = 'Jerry'


TRUE = ":^)"
FALSE = ":^{"
truefalse = [TRUE, FALSE]


def is_literal(token):
    return (token.startswith('\'') and token.endswith('\'')) or (token.startswith('\"') and token.endswith('\"'))


def is_float(token):
    try:
        float(token)
        return True
    except ValueError:
        return False


def do_math_operation(operator, operand1, operand2):
    if operator == '+':
        return operand1 + operand2
    elif operator == '-':
        return operand1 - operand2
    elif operator == '*':
        return operand1 * operand2
    elif operator == '/':
        return operand1 / operand2
    elif operator == '%':
        return int(operand1) % int(operand2)
    else:
        raise ValueError


def do_boolean_operation(operator, operand1, operand2):
    if operator == "is":
        return TRUE if operand1 == operand2 else FALSE
    elif operator == "isn\'t":
        return TRUE if operand1 != operand2 else FALSE
    elif operator == "<":
        return TRUE if operand1 < operand2 else FALSE
    elif operator == ">":
        return TRUE if operand1 > operand2 else FALSE
    elif operator == "<=":
        return TRUE if operand1 <= operand2 else FALSE
    elif operator == ">=":
        return TRUE if operand1 >= operand2 else FALSE
    elif operand1 in truefalse and operand2 in truefalse:
        if operator == "and":
            return TRUE if (operand1 == TRUE and operand2 == TRUE) else FALSE
        elif operator == "or":
            return TRUE if (operand1 == TRUE or operand2 == TRUE) else FALSE
        elif operator == "not":
            return TRUE if operand1 == FALSE else FALSE
        else:
            return "invalid"
    else:
        return "invalid"


class Parser:

    standalone_bool_keywords = ["is", "isn\'t", "and", "or", "not"]
    embeddable_bool_keywords = ["<", ">", "<=", ">=", "(", ")"]

    variables = {}

    def __init__(self):
        pass

    def parse_expression(self, src_tokens):
        try:
            split_tokens = []
            for t in src_tokens:
                split_tokens.extend([t for t in re.split("(\(|\)|\*|/|\+|\-|%|<|>|<=|>=)", t) if len(t) > 0])
            result = ""
            if len(split_tokens) == 1:
                t = split_tokens[0]
                if is_literal(t):
                    result = t[1:-1]
                elif t.isdigit() or is_float(t):
                    result = t
                elif t in self.variables:
                    result = self.variables[t]
                else:
                    raise SyntaxError

            elif len(split_tokens) > 1:
                i = 0
                while i < len(split_tokens):
                    t = split_tokens[i]
                    if t == "is":
                        split_tokens[i] = "=="
                    elif t == "isn\'t":
                        split_tokens[i] = "!="
                    elif t == TRUE:
                        split_tokens[i] = "True"
                    elif t == FALSE:
                        split_tokens[i] = "False"
                    elif t in self.variables:
                        split_tokens[i] = str(self.variables[t])
                        i -= 1
                    i += 1
                # print split_tokens
                result = str(eval(" ".join(split_tokens)))
            if result == "True":
                return TRUE
            elif result == "False":
                return FALSE
            else:
                return result
        except SyntaxError:
            print "wtf can't read this"
            return None

    def parse(self, lines):

        call_stack = []
        condition_execution_stack = []
        condition_scope_stack = []

        line_count = 0

        while line_count < len(lines):
            tokens = lines[line_count].split()
            # print tokens
            tokens_len = len(tokens)

            # Skip blank lines and commented out lines
            if tokens_len == 0:
                continue

            # Skip line if this is not the right conditional branch UNLESS for conditional statements
            if (condition_scope_stack != condition_execution_stack) \
                    and not ((tokens[0] == "implying")
                    or ((tokens_len == 2) and (tokens[0] == "or") and (tokens[1] == "not"))
                    or ((tokens_len == 2) and (tokens[0] == "done") and (tokens[1] == "implying"))):
                line_count += 1
                continue

            if (tokens[0] == "mfw") and (tokens_len > 1):
                tokens_group = []
                for token in tokens[1:]:
                    tokens_group.append(token)
                    if token.endswith(','):
                        tokens_group.append(tokens_group.pop()[:-1])
                        result = self.parse_expression(tokens_group)
                        if result is not None:
                            print result,
                        tokens_group = []
                if len(tokens_group) > 0:
                    result = self.parse_expression(tokens_group)
                    if result is not None:
                        print result,
                print

            elif tokens[0] == "be":
                if tokens_len > 3 and tokens[2] == "like":
                    if is_literal(tokens[3]):
                        self.variables[tokens[1]] = tokens[3][1:-1]
                    elif tokens[3].isdigit() and tokens_len == 4:
                        self.variables[tokens[1]] = int(tokens[3])
                    elif is_float(tokens[3]) and tokens_len == 4:
                        self.variables[tokens[1]] = float(tokens[3])
                    elif tokens[3] in self.variables and tokens_len == 4:
                        self.variables[tokens[1]] = self.variables[tokens[3]]
                    else:
                        result = self.parse_expression(tokens[3:])
                        if result is not None:
                            self.variables[tokens[1]] = result

            elif tokens[0] == "implying":
                condition_scope_stack.append(TRUE)

                # Single boolean argument
                if tokens_len == 2:
                    if is_literal(tokens[1]):
                        if tokens[1][1:-1] in truefalse:
                            condition_execution_stack.append(tokens[1][1:-1])
                    elif (tokens[1] in self.variables) and (self.variables[tokens[1]] in truefalse):
                        condition_execution_stack.append(self.variables[tokens[1]])

                # Boolean expression
                elif tokens_len > 2:
                    result = self.parse_expression(tokens[1:])
                    if result in truefalse:
                        condition_execution_stack.append(result)
                    else:
                        print "wtf can't imply this"
                        return

                # print condition_scope_stack, condition_execution_stack, line_count

            elif (tokens_len == 2) and (tokens[0] == "or") \
                    and (tokens[1] == "not") and (len(condition_scope_stack) > 0):
                condition_scope_stack[-1] = FALSE
                # print condition_scope_stack, condition_execution_stack, line_count

            elif tokens[0] == "inb4":
                if (tokens_len == 8) and (tokens[2] == "from") and (tokens[4] == "to") and (tokens[6] == "by"):
                    self.variables[tokens[1]] = int(tokens[3])
                    call_stack.append({"linepos": line_count,
                                      "counter": tokens[1],
                                      "start": int(tokens[3]),
                                      "end": int(tokens[5]),
                                      "step": int(tokens[7])})
                else:
                    print "wtf can't inb4 this"
                    return

            elif (tokens[0] == "done") and (tokens_len > 1):
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
                    # print condition_scope_stack, condition_execution_stack, line_count

            else:
                print "wtf r u doing"
                return

            line_count += 1

    def main(self):
        inputlines = []

        for line in sys.stdin:
            stripped_line = line.lstrip()
            if len(stripped_line) > 0:
                if stripped_line[0] != '>':
                    print "do you even greentext"
                    return
                else:
                    inputlines.append(stripped_line[1:])

        self.parse(inputlines)


Parser().main()
