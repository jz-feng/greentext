import sys
import os.path
from utils import *
from defs import *

__author__ = 'Jerry'


class Greentext:

    global_variables = {}
    functions = {}
    labels = {}

    # Element = {"return_address": num, "variables": {"var_name": value, ...}}
    call_stack = []

    # Element = anything
    return_stack = []

    # Input lines broken down into tokens
    line_tokens = []

    statements_stack = []
    loop_stack = []

    # (Line Counter) location in the source code of current execution/interpretation
    lc = 0

    # Offset the pointer location for functions for importing scripts
    offset = 0

    main_address = -1
    is_in_func_def = False
    is_in_main_def = False

    def __init__(self):
        pass

    # Util functions that depend on the runtime state

    def add_global_variable(self, var_name, var_value):
        if var_value is not None and len(var_name) > 0 and var_name[0].isalpha() and var_name.isalnum() \
                and var_name not in keywords:
            self.global_variables[var_name] = var_value
            return True
        else:
            return False

    def add_variable(self, var_name, var_value):
        if var_value is not None and len(var_name) > 0 and var_name[0].isalpha() and var_name.isalnum() \
                and var_name not in keywords and len(self.call_stack) > 0:
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
                and func_name not in self.functions and func_name not in keywords:
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

    def run(self, lines, imported):

        # First pass
        # Tokenize and clean input
        # Parse function definitions, create symbol table for functions, generate branching operations

        while self.lc < len(lines):
            # Extract string literals, store as tokens
            literals_tokens = extract_literals(lines[self.lc])

            # Tokenize the rest of the line
            tokens = extract_tokens(literals_tokens)

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
                self.line_tokens.append(tokens)
                self.lc += 1
                continue

            if len(self.statements_stack) > 0:
                statement = self.statements_stack[-1]
            else:
                statement = None

            if tokens[0] == "itt":
                if self.is_in_func_def:
                    error_and_quit("can't itt inside wewlad", self.lc)
                if self.is_in_main_def:
                    error_and_quit("can't itt inside be me", self.lc)
                importfile = tokens[1]
                if not os.path.isfile(importfile):
                    error_and_quit("can't find file for itt", self.lc)
                templc = self.lc
                tempoffset = self.offset
                self.read_input(open(importfile), True)
                self.offset = tempoffset + (self.lc-templc)
                self.lc = templc

            elif tokens == ["be", "me"]:
                if self.is_in_func_def:
                    error_and_quit("missing tfw before be me", self.lc)
                self.is_in_main_def = True
                self.main_address = self.lc + 1 + self.offset
                if not self.add_function("main", [], self.main_address):
                    error_and_quit("duplicate be me", self.lc)

            elif tokens[0] == "wewlad":
                try:
                    if tokens_len < 2:
                        raise GreentextError
                    if self.is_in_func_def:
                        error_and_quit("can't wewlad inside wewlad", self.lc)
                    if self.is_in_main_def:
                        error_and_quit("don't forget to thank mr skeltal", self.lc)
                    if statement is not None:
                        if "implying" in statement:
                            error_and_quit("missing done implying", self.lc)
                        elif "inb4" in statement:
                            error_and_quit("missing done inb4", self.lc)
                        return

                    self.is_in_func_def = True
                    split_tokens = []
                    for t in tokens[1:]:
                        split_tokens.extend([t for t in re.split("(\(|\)|,)", t) if len(t) > 0])

                    func_name = split_tokens[0]
                    if len(split_tokens) == 1:
                        if not self.add_function(func_name, [], self.lc + self.offset):
                            raise GreentextError
                    else:
                        func_params = self.parse_signature(split_tokens[1:], False)
                        if not self.add_function(func_name, func_params, self.lc + self.offset):
                            raise GreentextError
                except GreentextError:
                    error_and_quit("bad wewlad signature", self.lc)

            elif tokens[0] == "tfw":
                if self.is_in_func_def:
                    self.is_in_func_def = False
                else:
                    error_and_quit("unexpected tfw", self.lc)
                    return

            elif tokens == ["thank", "mr", "skeltal"]:
                self.is_in_main_def = False

            elif tokens[0] == "implying":
                self.statements_stack.append({"implying": self.lc + self.offset})     # keep address of 'if'

            elif tokens == ["or", "not"]:
                if statement is not None and "implying" in statement:
                    self.labels[statement["implying"]] = self.lc + 1 + self.offset      # map branch from 'if' -> 'else'
                    self.statements_stack[-1]["or_not"] = self.lc + self.offset         # keep address of 'else'
                else:
                    error_and_quit("unexpected or not", self.lc)

            elif tokens == ["done", "implying"]:
                if statement is not None and "implying" in statement:
                    if "or_not" in statement:
                        self.labels[statement["or_not"]] = self.lc + 1 + self.offset     # map branch from 'else' -> 'end if'
                    else:
                        self.labels[statement["implying"]] = self.lc + 1 + self.offset   # if no 'else', branch from 'if' -> 'end if'
                    self.statements_stack.pop()
                else:
                    error_and_quit("unexpected done implying", self.lc)

            elif tokens[0] == "inb4":
                self.statements_stack.append({"inb4": self.lc + self.offset})                 # keep address of loop start

            elif tokens == ["done", "inb4"]:
                if statement is not None and "inb4" in statement:
                    self.labels[self.lc + self.offset] = statement["inb4"]               # map branch from loop end -> loop start
                    self.labels[statement["inb4"]] = self.lc + 1 + self.offset           # map branch from loop start -> loop end
                    self.statements_stack.pop()
                else:
                    error_and_quit("unexpected done inb4", self.lc)

            # Process global variable declarations
            if not (self.is_in_func_def or self.is_in_main_def):
                if tokens[0] == "be":
                    if tokens_len == 2 and tokens[1] != "me":
                        var_name = tokens[1]
                        self.add_global_variable(var_name, "")
                    elif tokens_len > 3 and tokens[1] != "me" and tokens[2] == "like":
                        var_name = tokens[1]
                        var_value = self.parse_expression(tokens[3:])
                        if var_value is None:
                            error_and_quit("bad expression", self.lc)
                        if not self.add_global_variable(var_name, var_value):
                            error_and_quit("bad variable", self.lc)
                    else:
                        error_and_quit("bad be syntax", self.lc)

            self.line_tokens.append(tokens)
            self.lc += 1

        # If we have imported this code, don't run it
        if imported:
            return

        if self.main_address == -1:
            error_and_quit("be me not found", -1)
        if self.is_in_func_def:
            error_and_quit("missing tfw at EOF", -1)
        if self.is_in_main_def:
            error_and_quit("don't forget to thank mr skeltal", -1)
        if len(self.statements_stack) > 0:
            if self.statements_stack[-1][0] == "implying":
                error_and_quit("missing done implying at EOF", -1)
            elif self.statements_stack[-1][0] == "inb4":
                error_and_quit("missing done inb4 at EOF", -1)
            return

        # print self.labels       # debug line

        # Second pass
        # Interpret/execute code

        # Begin execution at main
        self.lc = self.main_address
        self.call_stack.append({"return_address": -1, "variables": {}})

        while self.lc < len(self.line_tokens):
            tokens = self.line_tokens[self.lc]

            tokens_len = len(tokens)

            # Skip processing for blank lines
            if tokens_len == 0:
                self.lc += 1
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
                            error_and_quit("bad expression", self.lc)
                        tokens_group = []
                # if line ended without comma, print the rest as a token group
                if len(tokens_group) > 0:
                    result = self.parse_expression(tokens_group)
                    if result is not None:
                        print result,
                    else:
                        error_and_quit("bad expression", self.lc)
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
                        error_and_quit("bad expression", self.lc)
                    if not self.add_variable(var_name, var_value):
                        error_and_quit("bad variable", self.lc)
                else:
                    error_and_quit("bad be syntax", self.lc)

            elif tokens[0] == "tfw":
                # print self.call_stack  # debug line
                # Returning from function call
                if len(self.call_stack) > 1:
                    if tokens_len > 1:
                        return_val = self.parse_expression(tokens[1:])
                        if return_val is not None:
                            self.return_stack.append(return_val)
                    self.lc = self.call_stack.pop()["return_address"]
                    continue
                # Returning from main
                elif len(self.call_stack) == 1:
                    self.call_stack.pop()
                    return
                else:
                    error_and_quit("unexpected tfw", self.lc)

            elif tokens[0] == "wew":
                try:
                    if tokens_len < 2:
                        raise GreentextError

                    split_tokens = []
                    for t in tokens[1:]:
                        split_tokens.extend([t for t in re.split("(\(|\)|,)", t) if len(t) > 0])

                    func_name = split_tokens[0]
                    if func_name not in self.functions:
                        error_and_quit("wewlad not found", self.lc)
                    function = self.functions[func_name]

                    if len(split_tokens) == 1:
                        if len(function["params"]) == 0:
                            self.call_stack.append({"return_address": self.lc + 1, "variables": {}})
                            self.lc = function["start_address"]
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
                            self.call_stack.append({"return_address": self.lc + 1, "variables": variables})
                            self.lc = function["start_address"]
                            continue
                        else:
                            raise GreentextError
                except GreentextError:
                    error_and_quit("bad wew signature", self.lc)

            # Syntax: >implying boolean_expression
            elif tokens[0] == "implying":
                result = self.parse_expression(tokens[1:])
                if result == TRUE:          # continue execution
                    pass
                elif result == FALSE:       # branch to 'else' block or 'end if'
                    self.lc = self.labels[self.lc]
                    continue
                else:
                    error_and_quit("bad expression", self.lc)

            elif tokens == ["or", "not"]:
                self.lc = self.labels[self.lc]                    # branch to 'end if'
                continue

            elif tokens == ["done", "implying"]:
                pass

            elif tokens[0] == "itt":
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

                        if len(self.loop_stack) == 0 or self.loop_stack[-1] != self.lc:  # if first iteration of loop, declare loop counter
                            self.loop_stack.append(self.lc)
                            if not self.add_variable(counter_var, start_val):
                                error_and_quit("bad variable", self.lc)
                        elif self.loop_stack[-1] == self.lc:        # if not first iteration of loop, increment loop counter
                            self.add_variable(counter_var, self.get_local_variables()[counter_var] + 1)

                        counter_val = self.get_local_variables()[counter_var]
                        if step_val > 0:
                            result = TRUE if counter_val < end_val else FALSE
                        else:
                            result = TRUE if counter_val > end_val else FALSE
                        if result == FALSE:
                            self.loop_stack.pop()

                    if result == FALSE:
                        self.lc = self.labels[self.lc]    # branch to loop end
                        continue
                except GreentextError:
                    error_and_quit("bad inb4 syntax", self.lc)

            elif tokens == ["done", "inb4"]:
                self.lc = self.labels[self.lc]        # branch to loop start
                continue

            elif tokens == ["thank", "mr", "skeltal"]:
                exit()

            # Undefined token
            else:
                error_and_quit("what is this", self.lc)

            self.lc += 1

    def main(self):
        self.read_input(sys.stdin, False)

    def read_input(self, inputfile, imported):
        inputlines = []

        for line in inputfile:
            stripped_line = line.lstrip()
            if len(stripped_line) == 0:
                inputlines.append("")
            else:
                if stripped_line[0] == "#":
                    inputlines.append("")
                elif stripped_line[0] == ">":
                    inputlines.append(stripped_line[1:])
                else:
                    error_and_quit("do you even greentext", -1)

        self.run(inputlines, imported)

if __name__ == "__main__":
    Greentext().main()
