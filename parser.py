import sys

__author__ = 'Jerry'


def parse(lines):
    variables = {}
    callstack = []

    linecount = 0
    while linecount < len(lines):
        tokens = lines[linecount].split()
        # print tokens
        tokenslen = len(tokens)
        if tokenslen == 0:
            continue
        if (tokens[0] == "mfw") and (tokenslen > 1):
            for token in tokens[1:]:
                if (token.startswith('\'') and token.endswith('\'')) \
                        or (token.startswith('\"') and token.endswith('\"')):
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
                # elif tokens[0] == "implying":

        elif tokens[0] == "inb4":
            if (tokenslen == 8) and (tokens[2] == "from") and (tokens[4] == "to") and (tokens[6] == "by"):
                variables[tokens[1]] = int(tokens[3])
                callstack.append({"linepos": linecount,
                                  "counter": tokens[1],
                                  "start": int(tokens[3]),
                                  "end": int(tokens[5]),
                                  "step": int(tokens[7])})
        elif (tokens[0] == "done") and (tokenslen > 1):
            if tokens[1] == "inb4":
                call = callstack[-1]
                variables[call["counter"]] += call["step"]
                if (call["step"] > 0 and variables[call["counter"]] < call["end"]) \
                        or (call["step"] < 0 and variables[call["counter"]] > call["end"]):
                    linecount = call["linepos"]
                else:
                    del variables[call["counter"]]
                    callstack.pop()


        linecount += 1


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
