import sys
import re

__author__ = 'Jerry'


TRUE = ":^)"
FALSE = ":^("
truefalse = [TRUE, FALSE]


def is_token_literal(token):
    return str(token).startswith('\'') and str(token).endswith('\'')


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
    labels = {}

    # Element = {"return_address":, "variables": {"var_name": var_value, ...}}
    call_stack = []
    # Element = anything
    return_stack = []

    # Identifier restrictions
    keywords = ["mfw", "be", "like", "done", "implying", "is", "and", "or", "not", "inb4", "from", "to", "by", "thank",
                "wew", "wewlad", "tfw"]

    def __init__(self):
        pass

    def add_global_variable(self, var_name, var_value):
        if var_value is not None and len(var_name) > 0 and var_name[0].isalpha() and var_name.isalnum() \
                and var_name not in self.keywords:
            self.global_variables[var_name] = var_value
            return True
        else:
            return False

    def add_variable(self, var_name, var_value):
        if var_value is not None and len(var_name) > 0 and var_name[0].isalpha() and var_name.isalnum() \
                and var_name not in self.keywords and len(self.call_stack) > 0:
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
                and func_name not in self.functions and func_name not in self.keywords:
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
            local_vars = self.get_local_variables()
            split_tokens = []
            for t in src_tokens:
                if is_token_literal(t):
                    split_tokens.append(t)
                else:
                    # Replace :^)/:^( with true/false since parentheses will be split from the tokens
                    t = t.replace(TRUE, "True")
                    t = t.replace(FALSE, "False")
                    split_tokens.extend([t for t in re.split("(\(|\)|\*|/|\+|\-|%|<=|>=|<|>|\")", t) if len(t) > 0])
            result = ""
            if len(split_tokens) == 1:
                t = split_tokens[0]
                if is_float(t) or t == "True" or t == "False":
                    result = t
                elif is_token_literal(t):   # Strip single quotes
                    result = t[1:-1]
                elif t == "wew" and len(self.return_stack) > 0:
                    result = self.return_stack.pop()
                elif t in local_vars:
                    result = local_vars[t]
                elif t in self.global_variables:
                    result = self.global_variables[t]
                else:
                    raise GreentextError
            elif len(split_tokens) > 1:
                i = 0
                while i < len(split_tokens):
                    t = split_tokens[i]
                    if is_float(t) or is_token_literal(t) or \
                            t in ["True", "False", "(", ")", "*", "/", "+", "-", "%", "<", ">", "<=", ">="]:
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
                    elif t in local_vars:
                        split_tokens[i] = str(local_vars[t])
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

    def parse_signature(self, split_tokens, allow_exprs):
        # DFA to check function signature syntax
        # noinspection PyPep8Naming
        ST_START, ST_LPAREN, ST_ID, ST_COMMA, ST_RPAREN = 0, 1, 2, 3, 4

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
        # Parse function definitions, create symbol table for functions, generate branching operations

        line_tokens = []
        line_address = 0
        main_address = -1
        is_in_func_def = False
        is_in_main_def = False

        statements_stack = []

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

            if len(statements_stack) > 0:
                statement = statements_stack[-1]
            else:
                statement = None

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
                    if statement is not None:
                        if "implying" in statement:
                            print_error("missing done implying", line_address)
                        elif "inb4" in statement:
                            print_error("missing done inb4", line_address)
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

            elif tokens[0] == "implying":
                statements_stack.append({"implying": line_address})     # keep address of 'if'

            elif tokens == ["or", "not"]:
                if statement is not None and "implying" in statement:
                    self.labels[statement["implying"]] = line_address + 1       # map branch from 'if' -> 'else'
                    statements_stack[-1]["or_not"] = line_address               # keep address of 'else'
                else:
                    print_error("unexpected or not", line_address)
                    return

            elif tokens == ["done", "implying"]:
                if statement is not None and "implying" in statement:
                    if "or_not" in statement:
                        self.labels[statement["or_not"]] = line_address + 1     # map branch from 'else' -> 'end if'
                    else:
                        self.labels[statement["implying"]] = line_address + 1   # if no 'else', branch from 'if' -> 'end if'
                    statements_stack.pop()
                else:
                    print_error("unexpected done implying", line_address)
                    return

            elif tokens[0] == "inb4":
                statements_stack.append({"inb4": line_address})                 # keep address of loop start

            elif tokens == ["done", "inb4"]:
                if statement is not None and "inb4" in statement:
                    self.labels[line_address] = statement["inb4"]               # map branch from loop end -> loop start
                    self.labels[statement["inb4"]] = line_address + 1           # map branch from loop start -> loop end
                    statements_stack.pop()
                else:
                    print_error("unexpected done inb4", line_address)
                    return

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
        if len(statements_stack) > 0:
            if statements_stack[-1][0] == "implying":
                print_error("missing done implying at EOF", -1)
            elif statements_stack[-1][0] == "inb4":
                print_error("missing done inb4 at EOF", -1)
            return

        # print self.labels       # debug line

        # Second pass
        # Interpret/execute code

        loop_stack = []

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
                # print self.call_stack  # debug line
                # Returning from function call
                if len(self.call_stack) > 1:
                    if tokens_len > 1:
                        return_val = self.parse_expression(tokens[1:])
                        if return_val is not None:
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
                        local_vars = self.get_local_variables()
                        func_params = self.parse_signature(split_tokens[1:], True)
                        for i in range(0, len(func_params)):
                            p = func_params[i]
                            if is_token_literal(p):
                                func_params[i] = p[1:-1]
                            if p in local_vars:
                                func_params[i] = local_vars[p]
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

            # Syntax: >implying boolean_expression
            elif tokens[0] == "implying":
                result = self.parse_expression(tokens[1:])
                if result == TRUE:          # continue execution
                    pass
                elif result == FALSE:       # branch to 'else' block or 'end if'
                    line_address = self.labels[line_address]
                    continue
                else:
                    print_error("bad expression", line_address)
                    return

            elif tokens == ["or", "not"]:
                line_address = self.labels[line_address]                    # branch to 'end if'
                continue

            elif tokens == ["done", "implying"]:
                pass

            # Syntax: >inb4 i from start to end (by step)
            elif tokens[0] == "inb4":
                try:
                    # DFA to check loop syntax & process loop arguments
                    # noinspection PyPep8Naming
                    ST_START, ST_VAR, ST_FROM, ST_FROM_VAL, ST_TO, ST_TO_VAL, ST_BY, ST_BY_VAL = \
                        0, 1, 2, 3, 4, 5, 6, 7

                    expr_tokens = []
                    counter_var = ""
                    step_val = 1
                    state = ST_START
                    for t in tokens[1:]:
                        if state == ST_START:                   # i
                            state = ST_VAR
                            counter_var = t
                            expr_tokens.append(t)
                        elif state == ST_VAR:
                            if t == "from":                     # i from
                                state = ST_FROM
                                expr_tokens = []
                            else:                               # i ...
                                expr_tokens.append(t)
                        elif state == ST_FROM:                  # i from x
                            state = ST_FROM_VAL
                            expr_tokens.append(t)
                        elif state == ST_FROM_VAL:
                            if t == "to":                       # i from x to
                                state = ST_TO
                                start_val = self.parse_expression(expr_tokens)
                                expr_tokens = []
                                if start_val is not None and start_val not in truefalse:
                                    start_val = int(start_val)
                                else:
                                    raise GreentextError
                            else:                               # i from x x
                                expr_tokens.append(t)
                        elif state == ST_TO:                    # i from x to y
                            state = ST_TO_VAL
                            expr_tokens.append(t)
                        elif state == ST_TO_VAL:
                            if t == "by":                       # i from x to y by
                                state = ST_BY
                                end_val = self.parse_expression(expr_tokens)
                                expr_tokens = []
                                if end_val is not None and end_val not in truefalse:
                                    end_val = int(end_val)
                                else:                           # i from x to y y
                                    raise GreentextError
                            else:
                                expr_tokens.append(t)
                        elif state == ST_BY:                    # i from x to y by z
                            state = ST_BY_VAL
                            expr_tokens.append(t)
                        elif state == ST_BY_VAL:                # i from x to y by z z
                            expr_tokens.append(t)
                        else:
                            raise GreentextError

                    if state == ST_VAR:                         # while loop
                        result = self.parse_expression(expr_tokens)
                        if result not in truefalse:
                            raise GreentextError
                    else:
                        if state == ST_TO_VAL:                      # i from x to y
                            end_val = self.parse_expression(expr_tokens)
                            if end_val is not None and end_val not in truefalse:
                                end_val = int(end_val)
                            else:
                                raise GreentextError
                        elif state == ST_BY_VAL:                    # i from x to y by z
                            step_val = self.parse_expression(expr_tokens)
                            if step_val is not None and step_val not in truefalse:
                                step_val = int(step_val)
                            else:
                                raise GreentextError
                        else:
                            raise GreentextError

                        if len(loop_stack) == 0 or loop_stack[-1] != line_address:  # if first iteration of loop, declare loop counter
                            loop_stack.append(line_address)
                            if not self.add_variable(counter_var, start_val):
                                print_error("bad variable", line_address)
                                return
                        elif loop_stack[-1] == line_address:        # if not first iteration of loop, increment loop counter
                            self.add_variable(counter_var, self.get_local_variables()[counter_var] + 1)

                        counter_val = self.get_local_variables()[counter_var]
                        if step_val > 0:
                            result = TRUE if counter_val < end_val else FALSE
                        else:
                            result = TRUE if counter_val > end_val else FALSE
                        if result == FALSE:
                            loop_stack.pop()

                    if result == FALSE:
                        line_address = self.labels[line_address]    # branch to loop end
                        continue
                except GreentextError:
                    print_error("bad inb4 syntax", line_address)
                    return

            elif tokens == ["done", "inb4"]:
                line_address = self.labels[line_address]        # branch to loop start
                continue

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

if __name__ == "__main__":
    Parser().main()
