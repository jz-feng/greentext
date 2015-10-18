import sys

__author__ = 'Jerry'


def is_literal(token):
    return (token.startswith('\'') and token.endswith('\'')) or (token.startswith('\"') and token.endswith('\"'))


def parse(lines):
    TRUE = ":^)"
    FALSE = ":^{"
    truefalse = [TRUE, FALSE]

    variables = {}
    call_stack = []
    condition_execution_stack = []
    condition_stack = []

    line_count = 0

    while line_count < len(lines):
        tokens = lines[line_count].split()
        # print tokens
        tokenslen = len(tokens)

        # Skip blank lines
        if tokenslen == 0:
            continue

        # Skip line if this is not the right conditional branch UNLESS it's an "else" or "end if"
        if (condition_stack != condition_execution_stack) \
                and not (((tokenslen == 2) and (tokens[0] == "or") and (tokens[1] == "not"))
                         or ((tokenslen == 2) and (tokens[0] == "done") and (tokens[1] == "implying"))):
            line_count += 1
            continue

        if (tokens[0] == "mfw") and (tokenslen > 1):
            for token in tokens[1:]:
                if is_literal(token):
                    print token[1:len(token) - 1],
                elif token in variables:
                    print variables[token],
            print

        elif tokens[0] == "be":
            if tokenslen == 3:
                if tokens[2].isdigit():
                    variables[tokens[1]] = int(tokens[2])
                else:
                    try:
                        variables[tokens[1]] = float(tokens[2])
                    except ValueError:
                        variables[tokens[1]] = tokens[2]
                # elif tokenslen > 3:
                # for i in range(1, tokenslen, 1):

        elif tokens[0] == "implying":
            condition_stack.append(TRUE)
            if tokenslen == 2:
                if is_literal(tokens[1]):
                    if tokens[1] in truefalse:
                        condition_execution_stack.append(tokens[1])
                else:
                    if (tokens[1] in variables) and (variables[tokens[1]] in truefalse):
                        condition_execution_stack.append(variables[tokens[1]])
            # print condition_stack, condition_execution_stack

        elif (tokenslen == 2) and (tokens[0] == "or") and (tokens[1] == "not") and (len(condition_stack) > 0):
            condition_stack[-1] = FALSE
            # print condition_stack, condition_execution_stack

        elif tokens[0] == "inb4":
            if (tokenslen == 8) and (tokens[2] == "from") and (tokens[4] == "to") and (tokens[6] == "by"):
                variables[tokens[1]] = int(tokens[3])
                call_stack.append({"linepos": line_count,
                                  "counter": tokens[1],
                                  "start": int(tokens[3]),
                                  "end": int(tokens[5]),
                                  "step": int(tokens[7])})

        elif (tokens[0] == "done") and (tokenslen > 1):
            if tokens[1] == "inb4" and len(call_stack) > 0:
                call = call_stack[-1]
                variables[call["counter"]] += call["step"]
                if (call["step"] > 0 and variables[call["counter"]] < call["end"]) \
                        or (call["step"] < 0 and variables[call["counter"]] > call["end"]):
                    line_count = call["linepos"]
                else:
                    del variables[call["counter"]]
                    call_stack.pop()
            elif tokens[1] == "implying" and len(condition_stack) > 0:
                condition_stack.pop()
                condition_execution_stack.pop()
                # print condition_stack, condition_execution_stack

        line_count += 1


def main():
    inputlines = []

    for line in sys.stdin:
        strippedline = line.lstrip()
        if len(strippedline) > 0:
            if strippedline[0] != '>':
                print "do you even greentext"
                return
            else:
                inputlines.append(strippedline[1:])

    parse(inputlines)


main()
