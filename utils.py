import re

# Util functions that do not depend on the runtime state


def is_token_literal(token):
    return str(token).startswith('\'') and str(token).endswith('\'')


def is_float(token):
    try:
        float(token)
        return True
    except ValueError:
        return False


def error_and_quit(message, line_address):
    if line_address == -1:
        print ("wtf:", message)
    else:
        print ("wtf:", message, "at line", line_address + 1)
    exit()


def extract_literals(line):
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


def extract_tokens(tokens):
    split_tokens = []
    for t in tokens:
        if is_token_literal(t):
            split_tokens.append(t)
        else:
            split_tokens.extend(t.split())
    return split_tokens
