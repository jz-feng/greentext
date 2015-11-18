import sys
import re

__author__ = 'Jerry'


TRUE = ":^)"
FALSE = ":^("
truefalse = [TRUE, FALSE]


def is_token_literal(token):
    return token.startswith('\'') and token.endswith('\'')


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


def parse_literals(line):
    tokens = [t for t in re.split(r"(\")", line) if len(t) > 0]
    if len(tokens) > 0 and tokens[-1].endswith("\n"):   # Remove newline char
        tokens[-1] = tokens[-1][:-1]
    if len(tokens) > 1:
        is_literal = False
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if is_literal:
                if t == "\"":
                    if tokens[i - 1] != "\"":
                        tokens[i - 1] += "'"    # Suffix with single quote
                    is_literal = False
                else:
                    if tokens[i - 1] == "\"":
                        tokens[i] = "'" + t     # Prefix with single quote
                    else:
                        # Combine current token with previous token, remove current token, don't increment index
                        tokens[i - 1] = tokens[i - 1] + " " + t
                        del tokens[i]
                        i -= 1
            else:
                if t == "\"":
                    is_literal = True
            i += 1
    # Remove "s from tokens stream
    return [t for t in tokens if len(t) > 0 and t != "\""]


def parse_tokens(tokens):
    split_tokens = []
    for t in tokens:
        if is_token_literal(t):
            split_tokens.append(t)
        else:
            split_tokens.extend(t.split())
    return split_tokens


class GreentextError(SyntaxError):
    """Custom Greentext syntax error"""


class Parser:

    global_variables = {}
    functions = {}

    # Element = {"return_address":, "variables": {"var_name": var_value, ...}}
    call_stack = []
    # Element = anything
    return_stack = []

    def __init__(self):
        pass

    def add_global_variable(self, var_name, var_value):
        if var_value is not None and len(var_name) > 0 and var_name[0].isalpha() and var_name.isalnum():
            self.global_variables[var_name] = var_value
            return True
        else:
            return False

    def add_variable(self, var_name, var_value):
        if var_value is not None and len(var_name) > 0 and var_name[0].isalpha() and var_name.isalnum() \
                and len(self.call_stack) > 0:
            self.call_stack[-1]["variables"][var_name] = var_value
            return True
        else:
            return False

    def get_local_variables(self):
        if len(self.call_stack) > 0:
            return self.call_stack[-1]["variables"]
        else:
            return {}

    def add_function(self, func_name, func_params, start_address):
        if len(func_name) > 0 and func_name[0].isalpha() and func_name.isalnum()\
                and func_name not in self.functions:
            # Check for duplicate params
            if len(func_params) != len(set(func_params)):
                return False

            # Check params format
            for p in func_params:
                if not(len(p) > 0 and p[0].isalpha() and p.isalnum()):
                    return False

            self.functions[func_name] = {"params": func_params, "start_address": start_address + 1}
            return True
        else:
            return False

    def parse_expression(self, src_tokens):
        try:
            split_tokens = []
            for t in src_tokens:
                if is_token_literal(t):
                    split_tokens.append(t)
                else:
                    # Replace :^)/:^( with true/false since parentheses will be split from the tokens
                    t = t.replace(TRUE, "True")
                    t = t.replace(FALSE, "False")
                    split_tokens.extend([t for t in re.split("(\(|\)|\*|/|\+|\-|%|<|>|<=|>=|\")", t) if len(t) > 0])
            result = ""
            if len(split_tokens) == 1:
                t = split_tokens[0]
                if is_float(t) or t == "True" or t == "False":
                    result = t
                elif is_token_literal(t):   # Strip single quotes
                    result = t[1:-1]
                elif t == "wew" and len(self.return_stack) > 0:
                    result = self.return_stack.pop()
                elif t in self.get_local_variables():
                    result = self.get_local_variables()[t]
                elif t in self.global_variables:
                    result = self.global_variables[t]
                else:
                    raise GreentextError
            elif len(split_tokens) > 1:
                i = 0
                while i < len(split_tokens):
                    t = split_tokens[i]
                    if is_float(t) or is_token_literal(t) or \
                            t in ["True", "False", "(", ")", "*", "/", "+", "-", "%", "<", ">"]:
                        pass
                    elif t == "is":
                        split_tokens[i] = "=="
                    elif t == "isn\'t":
                        split_tokens[i] = "!="
                    elif t == TRUE:
                        split_tokens[i] = "True"
                    elif t == FALSE:
                        split_tokens[i] = "False"
                    elif t == "wew" and len(self.return_stack) > 0:
                        split_tokens[i] = self.return_stack.pop()
                    elif t in self.get_local_variables():
                        split_tokens[i] = str(self.get_local_variables()[t])
                        i -= 1
                    elif t in self.global_variables:
                        split_tokens[i] = str(self.global_variables[t])
                        i -= 1
                    else:
                        raise GreentextError
                    i += 1

                try:
                    result = str(eval(" ".join(split_tokens)))
                except (SyntaxError, TypeError, NameError):
                    return None
            if result == "True":
                return TRUE
            elif result == "False":
                return FALSE
            else:
                return result
        except GreentextError:
            return None

    # noinspection PyPep8Naming
    def parse_signature(self, split_tokens, allow_exprs):
        # DFA to check function signature syntax
        ST_START = 0
        ST_LPAREN = 1
        ST_ID = 2
        ST_COMMA = 3
        ST_RPAREN = 4

        params = []
        param_tokens = []
        state = ST_START
        for t in split_tokens:
            if state == ST_START and t == "(":      # (
                state = ST_LPAREN
            elif state == ST_LPAREN:
                if t == ")":                        # ( )
                    state = ST_RPAREN
                else:                               # ( abc
                    state = ST_ID
                    param_tokens.append(t)
            elif state == ST_ID:
                if t == "," or t == ")":            # ( abc , OR ( abc )
                    state = ST_COMMA if t == "," else ST_RPAREN
                    if allow_exprs:
                        param_result = self.parse_expression(param_tokens)
                        param_tokens = []
                        if param_result is not None:
                            params.append(param_result)
                        else:
                            raise GreentextError
                    else:
                        params.append(param_tokens[0])
                        param_tokens = []
                elif allow_exprs:                   # ( abc bcd
                    param_tokens.append(t)
                else:
                    raise GreentextError
            elif state == ST_COMMA:                 # ( abc , bcd
                state = ST_ID
                param_tokens.append(t)
            else:
                raise GreentextError
        if state != ST_RPAREN:
            raise GreentextError
        return params

    def parse(self, lines):

        # First pass
        # Tokenize and clean input
        # Parse function definitions, create symbol table for functions

        line_tokens = []
        line_address = 0
        main_address = -1
        is_in_func_def = False
        is_in_main_def = False

        while line_address < len(lines):
            # Extract string literals, store as tokens
            literals_tokens = parse_literals(lines[line_address])

            # Tokenize the rest of the line
            tokens = parse_tokens(literals_tokens)

            # Remove commented tokens
            i = 0
            while i < len(tokens):
                t = tokens[i]
                if not is_token_literal(t) and '#' in t:
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

            if tokens == ["be", "me"]:
                if is_in_func_def:
                    print_error("missing tfw before be me", line_address)
                    return
                is_in_main_def = True
                main_address = line_address + 1
                if not self.add_function("main", [], main_address):
                    print_error("duplicate be me", line_address)
                    return

            elif tokens[0] == "wewlad":
                try:
                    if tokens_len < 2:
                        raise GreentextError
                    if is_in_func_def:
                        print_error("can't wewlad inside wewlad", line_address)
                        return
                    if is_in_main_def:
                        print_error("don't forget to thank mr skeltal", line_address)
                        return

                    is_in_func_def = True
                    split_tokens = []
                    for t in tokens[1:]:
                        split_tokens.extend([t for t in re.split("(\(|\)|,)", t) if len(t) > 0])

                    func_name = split_tokens[0]
                    if len(split_tokens) == 1:
                        if not self.add_function(func_name, [], line_address):
                            raise GreentextError
                    else:
                        func_params = self.parse_signature(split_tokens[1:], False)
                        if not self.add_function(func_name, func_params, line_address):
                            raise GreentextError
                except GreentextError:
                    print_error("bad wewlad signature", line_address)
                    return

            elif tokens[0] == "tfw":
                if is_in_func_def:
                    is_in_func_def = False
                else:
                    print_error("unexpected tfw", line_address)
                    return

            elif tokens == ["thank", "mr", "skeltal"]:
                is_in_main_def = False

            # Process global variable declarations
            if not (is_in_func_def or is_in_main_def):
                if tokens[0] == "be":
                    if tokens_len == 2 and tokens[1] != "me":
                        var_name = tokens[1]
                        self.add_global_variable(var_name, "")
                    elif tokens_len > 3 and tokens[1] != "me" and tokens[2] == "like":
                        var_name = tokens[1]
                        var_value = self.parse_expression(tokens[3:])
                        if var_value is None:
                            print_error("bad expression", line_address)
                            return
                        if not self.add_global_variable(var_name, var_value):
                            print_error("bad variable", line_address)
                            return
                    else:
                        print_error("bad be syntax", line_address)
                        return

            line_tokens.append(tokens)
            line_address += 1

        if main_address == -1:
            print_error("be me not found", -1)
            return
        if is_in_func_def:
            print_error("missing tfw at EOF", -1)
            return
        if is_in_main_def:
            print_error("don't forget to thank mr skeltal", -1)
            return

        # Second pass
        # Interpret/execute code

        # Element = {"line_pos":, "counter":, "start":, "end":, "step":}
        loop_stack = []
        # Element = TRUE/FALSE
        condition_execution_stack = []
        # Element = TRUE/FALSE
        condition_scope_stack = []

        # Begin execution at main
        line_address = main_address
        self.call_stack.append({"return_address": -1, "variables": {}})

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
                    or (tokens == ["or", "not"])
                    or (tokens == ["done", "implying"])):
                line_address += 1
                continue

            # Syntax: >mfw token group 1, token group 2
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

            # Syntax: >be var_name like var_value/expression
            elif tokens[0] == "be":
                if tokens_len == 2 and tokens[1] != "me":
                    var_name = tokens[1]
                    self.add_variable(var_name, "")
                elif tokens_len > 3 and tokens[1] != "me" and tokens[2] == "like":
                    var_name = tokens[1]
                    var_value = self.parse_expression(tokens[3:])
                    if var_value is None:
                        print_error("bad expression", line_address)
                        return
                    if not self.add_variable(var_name, var_value):
                        print_error("bad variable", line_address)
                        return
                else:
                    print_error("bad be syntax", line_address)
                    return

            elif tokens[0] == "tfw":
                # Returning from function call
                if len(self.call_stack) > 1:
                    if tokens_len > 1:
                        return_val = self.parse_expression(tokens[1:])
                        if return_val is not None:
                            if len(self.return_stack) > 0:
                                self.return_stack[-1] = return_val
                            else:
                                self.return_stack.append(return_val)
                    line_address = self.call_stack.pop()["return_address"]
                    continue
                # Returning from main
                elif len(self.call_stack) == 1:
                    self.call_stack.pop()
                    return
                else:
                    print_error("unexpected tfw", line_address)
                    return

            elif tokens[0] == "wew":
                try:
                    if tokens_len < 2:
                        raise GreentextError

                    split_tokens = []
                    for t in tokens[1:]:
                        split_tokens.extend([t for t in re.split("(\(|\)|,)", t) if len(t) > 0])

                    func_name = split_tokens[0]
                    if func_name not in self.functions:
                        print_error("wewlad not found", line_address)
                        return
                    function = self.functions[func_name]

                    if len(split_tokens) == 1:
                        if len(function["params"]) == 0:
                            self.call_stack.append({"return_address": line_address + 1, "variables": {}})
                            line_address = function["start_address"]
                            continue
                        else:
                            raise GreentextError
                    else:
                        func_params = self.parse_signature(split_tokens[1:], True)
                        for i in range(0, len(func_params)):
                            p = func_params[i]
                            if is_token_literal(p):
                                func_params[i] = p[1:-1]
                            if p in self.get_local_variables():
                                func_params[i] = self.get_local_variables()[p]
                            elif p in self.global_variables:
                                func_params[i] = self.global_variables[p]

                        # print func_params
                        if len(function["params"]) == len(func_params):
                            variables = {}
                            for i in range(0, len(function["params"])):
                                variables[function["params"][i]] = func_params[i]
                            self.call_stack.append({"return_address": line_address + 1, "variables": variables})
                            line_address = function["start_address"]
                            continue
                        else:
                            raise GreentextError
                except GreentextError:
                    print_error("bad wew signature", line_address)
                    return

            # Syntax: >implying boolean_var/boolean_expression
            elif tokens[0] == "implying":
                condition_scope_stack.append(TRUE)

                result = self.parse_expression(tokens[1:])
                if result is None:
                    print_error("bad expression", line_address)
                    return
                if result in truefalse:
                    condition_execution_stack.append(result)
                else:
                    print_error("bad implying syntax", line_address)
                    return
                # print condition_scope_stack, condition_execution_stack, line_address  # debug line

            # Syntax: >or not
            elif tokens == ["or", "not"]:
                if len(condition_scope_stack) > 0:
                    condition_scope_stack[-1] = FALSE
                else:
                    print_error("unexpected or not", line_address)
                    return
                # print condition_scope_stack, condition_execution_stack, line_address  # debug line

            # Syntax: >inb4 i from start to end (by step)
            elif tokens[0] == "inb4":
                if tokens_len == 8 and tokens[2] == "from" and tokens[3].isdigit() and tokens[4] == "to" \
                        and tokens[5].isdigit() and tokens[6] == "by" and tokens[7].isdigit():
                    if not self.add_variable(tokens[1], int(tokens[3])):
                        print_error("bad variable", line_address)
                        return
                    loop_stack.append({"line_pos": line_address,
                                      "counter": tokens[1],
                                      "start": int(tokens[3]),
                                      "end": int(tokens[5]),
                                      "step": int(tokens[7])})
                else:
                    print_error("bad inb4 syntax", line_address)
                    return

            elif tokens == ["done", "inb4"]:
                if len(loop_stack) > 0:
                    call = loop_stack[-1]
                    self.add_variable(call["counter"], self.get_local_variables()[call["counter"]] + call["step"])
                    counter = self.get_local_variables()[call["counter"]]
                    if (call["step"] > 0 and counter < call["end"]) \
                            or (call["step"] < 0 and counter > call["end"]):
                        line_address = call["line_pos"]
                    else:
                        del self.call_stack[-1]["variables"][call["counter"]]
                        loop_stack.pop()
                else:
                    print_error("unexpected done inb4", line_address)
                    return

            elif tokens == ["done", "implying"]:
                if len(condition_scope_stack) > 0:
                    condition_scope_stack.pop()
                    condition_execution_stack.pop()
                    # print condition_scope_stack, condition_execution_stack, line_address  # debug line
                else:
                    print_error("unexpected done implying", line_address)
                    return

            elif tokens == ["thank", "mr", "skeltal"]:
                exit()

            # Undefined token
            else:
                print_error("what is this", line_address)
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
                    print_error("do you even greentext", -1)
                    return

        self.parse(inputlines)


Parser().main()
