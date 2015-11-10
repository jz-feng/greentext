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


def print_error(message, line_address):
    if line_address == -1:
        print "wtf:", message
    else:
        print "wtf:", message, "at line", line_address + 1


class Parser:

    variables = {}
    functions = {}

    def __init__(self):
        pass

    def add_variable(self, var_name, var_value):
        if var_value is not None and len(var_name) > 0 and var_name[0].isalpha() and var_name.isalnum():
            self.variables[var_name] = var_value
            return True
        else:
            print "wtf can't be this"
            return False

    def add_function(self, func_name, func_params, start_address):
        if len(func_name) > 0 and func_name[0].isalpha() and func_name.isalnum():
            # Check for duplicate params
            if len(func_params) != len(set(func_params)):
                return False

            for p in func_params:
                if not(len(p) > 0 and p[0].isalpha() and p.isalnum()):
                    return False
            self.functions[func_name] = {"params": func_params, "start_address": start_address, "return_address": 0}
            return True
        else:
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
            return None

    def parse(self, lines):

        # First pass
        # Tokenize and clean input
        # Parse function definitions, create symbol table for functions

        line_tokens = []
        line_address = 0
        main_address = -1
        is_in_func_def = False

        while line_address < len(lines):
            tokens = lines[line_address].split()

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

            tokens_len = len(tokens)

            # Skip processing for blank lines (but keep them)
            if tokens_len == 0:
                line_tokens.append(tokens)
                line_address += 1
                continue

            if tokens[0] == "memes":
                is_in_func_def = True
                main_address = line_address + 1

            elif tokens[0] == "wewlad":
                try:
                    if tokens_len < 2:
                        raise StandardError
                    if is_in_func_def:
                        print_error("can't wewlad inside wewlad", line_address)
                        return

                    is_in_func_def = True
                    func_params = []
                    split_tokens = []
                    for t in tokens[1:]:
                        split_tokens.extend([t for t in re.split("(\(|\)|,)", t) if len(t) > 0])

                    func_name = split_tokens[0]
                    if len(split_tokens) == 1:
                        if not self.add_function(func_name, func_params, line_address):
                            raise StandardError
                    else:
                        # DFA to check function signature syntax
                        ST_START = 0
                        ST_LPAREN = 1
                        ST_ID = 2
                        ST_COMMA = 3
                        ST_RPAREN = 4
                        j = 1
                        state = ST_START
                        while j < len(split_tokens):
                            tok = split_tokens[j]
                            if state == ST_START and tok == "(":
                                state = ST_LPAREN
                            elif state == ST_LPAREN:
                                if tok == ")":
                                    state = ST_RPAREN
                                else:
                                    state = ST_ID
                                    func_params.append(tok)
                            elif state == ST_ID and tok == ",":
                                state = ST_COMMA
                            elif state == ST_ID and tok == ")":
                                state = ST_RPAREN
                            elif state == ST_COMMA:
                                state = ST_ID
                                func_params.append(tok)
                            else:
                                raise StandardError
                            j += 1
                        if state != ST_RPAREN:
                            raise StandardError
                        if not self.add_function(func_name, func_params, line_address):
                            raise StandardError
                except StandardError:
                    print_error("bad wewlad signature", line_address)
                    return

            elif tokens[0] == "tfw":
                if is_in_func_def:
                    is_in_func_def = False
                else:
                    print_error("bad tfw syntax", line_address)
                    return

            # Process global variable declarations
            if not is_in_func_def:
                if tokens[0] == "be":
                    if tokens_len == 2:
                        var_name = tokens[1]
                        self.add_variable(var_name, "")
                    elif tokens_len > 3 and tokens[2] == "like":
                        var_name = tokens[1]
                        var_value = self.parse_expression(tokens[3:])
                        self.add_variable(var_name, var_value)
                    else:
                        print_error("bad be syntax", line_address)
                        return

            line_tokens.append(tokens)
            line_address += 1

        if main_address == -1:
            print_error("no memes found", -1)
            return
        if is_in_func_def:
            print_error("missing tfw at EOF", -1)
            return

        # Second pass

        loop_stack = []
        condition_execution_stack = []
        condition_scope_stack = []
        func_stack = []

        line_address = main_address

        while line_address < len(line_tokens):
            tokens = line_tokens[line_address]

            tokens_len = len(tokens)

            # Skip processing for blank lines
            if tokens_len == 0:
                line_address += 1
                continue

            # Skip line if this is not the right conditional branch UNLESS for conditional statements
            if (condition_scope_stack != condition_execution_stack) \
                    and not ((tokens[0] == "implying")
                    or (tokens_len == 2 and tokens[0:2] == ["or", "not"])
                    or (tokens_len == 2 and tokens[0:2] == ["done", "implying"])):
                line_address += 1
                continue

            # Syntax: mfw token group 1, token group 2
            if tokens[0] == "mfw":
                tokens_group = []
                for token in tokens[1:]:
                    tokens_group.append(token)
                    if token.endswith(','):
                        tokens_group.append(tokens_group.pop()[:-1])    # remove comma from last token
                        result = self.parse_expression(tokens_group)
                        if result is not None:
                            print result,
                        else:
                            print_error("bad expression", line_address)
                            return
                        tokens_group = []
                # if line ended without comma, print the rest as a token group
                if len(tokens_group) > 0:
                    result = self.parse_expression(tokens_group)
                    if result is not None:
                        print result,
                    else:
                        print_error("bad expression", line_address)
                        return
                # print newline
                print

            elif tokens[0] == "be":
                # Syntax: be var_name
                if tokens_len == 2:
                    var_name = tokens[1]
                    self.add_variable(var_name, "")
                # Syntax: be var_name like var_value or expression
                elif tokens_len > 3 and tokens[2] == "like":
                    var_name = tokens[1]
                    var_value = self.parse_expression(tokens[3:])
                    self.add_variable(var_name, var_value)
                else:
                    print_error("bad be syntax", line_address)

            elif tokens[0] == "wewlad" and tokens_len > 1:
                tokens

            elif tokens[0] == "memes":
                tokens

            elif tokens[0] == "tfw":
                tokens

            elif tokens[0] == "wew" and tokens_len > 1:
                try:
                    split_tokens = []
                    for t in tokens[1:]:
                        split_tokens.extend([t for t in re.split("(\(|\)|,)", t) if len(t) > 0])
                    print split_tokens
                    func_name = split_tokens[0]
                    call = self.functions[func_name]
                    print call

                    if len(split_tokens) == 1 and len(call["params"]) == 0:
                        self.functions[func_name]["return_address"] = line_address + 1
                        line_address = call["start_address"] + 1
                        continue
                    elif len(split_tokens) >= 3 and split_tokens[1] == "(" and split_tokens[-1] == ")":
                        args = []
                        for i in range(2, len(split_tokens) - 1):
                            if i == len(split_tokens) - 2:              # last param
                                args.append(split_tokens[i])
                            elif split_tokens[i + 1] == ",":            # other params must be followed by comma
                                args.append(split_tokens[i])
                            elif split_tokens[i] != ",":
                                raise StandardError
                        print args
                except StandardError:
                    print "wtf can't wew this"
                    return

            elif tokens[0] == "implying":
                condition_scope_stack.append(TRUE)

                result = self.parse_expression(tokens[1:])
                if result in truefalse:
                    condition_execution_stack.append(result)
                else:
                    print "wtf can't imply this"
                    return
                # print condition_scope_stack, condition_execution_stack, line_address  # debug line

            elif tokens_len == 2 and tokens[0] == "or" \
                    and (tokens[1] == "not") and (len(condition_scope_stack) > 0):
                condition_scope_stack[-1] = FALSE
                # print condition_scope_stack, condition_execution_stack, line_address  # debug line

            elif tokens[0] == "inb4":
                if tokens_len == 8 and tokens[2] == "from" and tokens[3].isdigit() and tokens[4] == "to" \
                        and tokens[5].isdigit() and tokens[6] == "by" and tokens[7].isdigit() \
                        and tokens[1] not in self.variables:
                    self.add_variable(tokens[1], int(tokens[3]))
                    loop_stack.append({"line_pos": line_address,
                                      "counter": tokens[1],
                                      "start": int(tokens[3]),
                                      "end": int(tokens[5]),
                                      "step": int(tokens[7])})
                else:
                    print "wtf can't inb4 this"
                    return

            elif tokens[0] == "done" and tokens_len > 1:
                if tokens[1] == "inb4" and len(loop_stack) > 0:
                    call = loop_stack[-1]
                    self.variables[call["counter"]] += call["step"]
                    if (call["step"] > 0 and self.variables[call["counter"]] < call["end"]) \
                            or (call["step"] < 0 and self.variables[call["counter"]] > call["end"]):
                        line_address = call["line_pos"]
                    else:
                        del self.variables[call["counter"]]
                        loop_stack.pop()
                elif tokens[1] == "implying" and len(condition_scope_stack) > 0:
                    condition_scope_stack.pop()
                    condition_execution_stack.pop()
                    # print condition_scope_stack, condition_execution_stack, line_address  # debug line

            else:
                print "wtf r u doing", line_address
                return

            line_address += 1

    def main(self):
        inputlines = []

        for line in sys.stdin:
            stripped_line = line.lstrip()
            if len(stripped_line) == 0:
                inputlines.append("")
            else:
                if stripped_line[0] == "#":
                    inputlines.append("")
                elif stripped_line[0] == ">":
                    inputlines.append(stripped_line[1:])
                else:
                    print "wtf do u even greentext"
                    return

        self.parse(inputlines)


Parser().main()
