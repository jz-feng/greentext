import sys
import re

__author__ = 'Jerry'


TRUE = ":^)"
FALSE = ":^("
truefalse = [TRUE, FALSE]


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
    functions = {}

    def __init__(self):
        pass

    def add_variable(self, var_name, var_value):
        if (len(var_name) > 0) and (var_name[0].isalpha()) and (var_name.isalnum()):
            self.variables[var_name] = var_value
            return True
        else:
            print "wtf can't be this"
            return False

    def add_function(self, func_name, func_args, line_pos):
        if (len(func_name) > 0) and (func_name[0].isalpha()) and (func_name.isalnum()):
            self.functions[func_name] = (func_args, line_pos)
            return True
        else:
            "wtf can't wewlad this"
            return False

    def parse_expression(self, src_tokens):
        try:
            split_tokens = []
            for t in src_tokens:
                # Replace :^)/:^( with true/false since parentheses will be split from the tokens
                t = t.replace("\":^)\"", "True")
                t = t.replace("\":^(\"", "False")
                split_tokens.extend([t for t in re.split("(\(|\)|\*|/|\+|\-|%|<|>|<=|>=)", t) if len(t) > 0])
            result = ""
            if len(split_tokens) == 1:
                t = split_tokens[0]
                if is_literal(t):
                    result = t[1:-1]
                elif is_float(t) or t == "True" or t == "False":
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
            print "wtf what kinda expression is this"
            return None

    def parse(self, lines):

        loop_stack = []
        condition_execution_stack = []
        condition_scope_stack = []
        func_stack = []

        line_count = 0

        while line_count < len(lines):
            tokens = lines[line_count].split()

            # Remove commented tokens
            i = 0
            while i < len(tokens):
                t = tokens[i]
                if '#' in t:
                    tokens[i] = t.partition('#')[0]
                    i += 1
                    break
                i += 1
            while len(tokens) > i:
                tokens.pop()

            # Filter out empty tokens
            tokens = [t for t in tokens if len(t) > 0]

            # print tokens # debug line
            tokens_len = len(tokens)

            # Skip blank lines
            if tokens_len == 0:
                continue

            # Skip line if this is not the right conditional branch UNLESS for conditional statements
            if (condition_scope_stack != condition_execution_stack) \
                    and not ((tokens[0] == "implying")
                    or (tokens_len == 2 and tokens[0:2] == ["or", "not"])
                    or (tokens_len == 2 and tokens[0:2] == ["done", "implying"])):
                line_count += 1
                continue

            # Syntax: mfw token group 1, token group 2
            if tokens[0] == "mfw" and tokens_len > 1:
                tokens_group = []
                for token in tokens[1:]:
                    tokens_group.append(token)
                    if token.endswith(','):
                        tokens_group.append(tokens_group.pop()[:-1])    # remove comma from last token
                        result = self.parse_expression(tokens_group)
                        if result is not None:
                            print result,
                        tokens_group = []
                # if line ended without comma, print the rest as a token group
                if len(tokens_group) > 0:
                    result = self.parse_expression(tokens_group)
                    if result is not None:
                        print result,
                # print newline
                print

            # Syntax: be var_name like var_value or expression
            elif tokens[0] == "be" and tokens_len > 3 and tokens[2] == "like":
                var_name = tokens[1]
                var_value = self.parse_expression(tokens[3:])
                if var_value is not None:
                    self.add_variable(var_name, var_value)
                else:
                    print "wtf can't be this"
                    return

            elif (tokens[0] == "wewlad") and (tokens_len > 1):
                func_name = tokens[1]
                func_args = []
                if (tokens_len > 2) and (tokens[2].startswith('(')) and (tokens[tokens_len - 1].endswith(')')):
                    for i in range(2, tokens_len - 1):
                        t = tokens[i]
                        if is_literal(t):
                            func_args.append(t[1:-1])
                        elif t.isdigit():
                            func_args.append(int(t))
                        elif is_float(t):
                            func_args.append(float(t))
                        elif t in self.variables:
                            func_args.append(self.variables[t])
                self.add_function(func_name, func_args, line_count)
                #func_stack.append({"name": func_name,
                #                   "args": func_args,
                #                   "line_pos": line_count})

            elif (tokens[0] == "wew") and (tokens_len > 1):
                print

            elif tokens[0] == "implying":
                condition_scope_stack.append(TRUE)

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
                if tokens_len == 8 and tokens[2] == "from" and tokens[3].isdigit() and tokens[4] == "to" \
                        and tokens[5].isdigit() and tokens[6] == "by" and tokens[7].isdigit() \
                        and tokens[1] not in self.variables:
                    self.add_variable(tokens[1], int(tokens[3]))
                    loop_stack.append({"line_pos": line_count,
                                      "counter": tokens[1],
                                      "start": int(tokens[3]),
                                      "end": int(tokens[5]),
                                      "step": int(tokens[7])})
                else:
                    print "wtf can't inb4 this"
                    return

            elif (tokens[0] == "done") and (tokens_len > 1):
                if tokens[1] == "inb4" and len(loop_stack) > 0:
                    call = loop_stack[-1]
                    self.variables[call["counter"]] += call["step"]
                    if (call["step"] > 0 and self.variables[call["counter"]] < call["end"]) \
                            or (call["step"] < 0 and self.variables[call["counter"]] > call["end"]):
                        line_count = call["line_pos"]
                    else:
                        del self.variables[call["counter"]]
                        loop_stack.pop()
                elif tokens[1] == "implying" and len(condition_scope_stack) > 0:
                    condition_scope_stack.pop()
                    condition_execution_stack.pop()
                    # print condition_scope_stack, condition_execution_stack, line_count
                elif tokens[1] == "wewlad" and len(func_stack) > 0:
                    call = func_stack[-1]

            else:
                print "wtf r u doing"
                return

            line_count += 1

    def main(self):
        inputlines = []

        for line in sys.stdin:
            stripped_line = line.lstrip()
            if len(stripped_line) > 0 and stripped_line[0] != '#':
                if stripped_line[0] == ">":
                    inputlines.append(stripped_line[1:])
                else:
                    print "wtf do u even greentext"
                    return

        self.parse(inputlines)


Parser().main()
