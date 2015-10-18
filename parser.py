import sys
__author__ = 'Jerry'


def main():
    variables = {}

    for line in sys.stdin:
        if line[0] != '>':
            print "do you even greentext"
            return

        tokens = line[1:].split()
        # print tokens
        tokenslen = len(tokens)

        if tokens[0] == "mfw":
            if tokenslen > 1:
                if tokens[1].startswith('\'') and tokens[1].endswith('\''):
                    print tokens[1][1:len(tokens[1]) - 1]
                elif tokens[1] in variables:
                    print variables[tokens[1]]

        elif tokens[0] == "be":
            if tokenslen == 3:
                variables[tokens[1]] = tokens[2]


main()
