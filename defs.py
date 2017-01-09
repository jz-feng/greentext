TRUE = ":^)"
FALSE = ":^("
truefalse = [TRUE, FALSE]

# Identifier restrictions
keywords = ["mfw", "be", "like", "done", "implying", "is", "and", "or", "not", "inb4", "from", "to", "by", "thank",
            "wew", "wewlad", "tfw"]


class GreentextError(SyntaxError):
    """Custom Greentext syntax error"""
