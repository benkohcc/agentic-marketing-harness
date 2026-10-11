"""Safe evaluator for MARKETING.md audience rules.

Grammar (deliberately tiny): names, numbers, strings, true/false/null, lists,
comparisons, + - * /, `in`, and/or/not, parentheses. Nothing else parses.

    evaluate("(orders_12m >= 3 and aov > 180) or allocation_list == true", customer)
"""
import ast

_ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Name, ast.Load, ast.Constant,
    ast.List, ast.Tuple,
)
_CONSTANTS = {"true": True, "false": False, "null": None, "True": True, "False": False, "None": None}


class RuleError(ValueError):
    pass


def _normalise(src: str) -> str:
    # YAML authors write `true`/`null`; Python wants True/None. Replace as whole words only.
    import re
    return re.sub(r"\b(true|false|null)\b", lambda m: {"true": "True", "false": "False", "null": "None"}[m.group(1)], src)


def compile_rule(src: str):
    try:
        tree = ast.parse(_normalise(src), mode="eval")
    except SyntaxError as e:
        raise RuleError(f"rule does not parse: {src!r} ({e.msg})")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise RuleError(f"rule uses disallowed syntax {type(node).__name__}: {src!r}")
    return compile(tree, "<rule>", "eval")


class _Attrs(dict):
    """Missing attribute → None, so `x > 3` on a missing x is False rather than an error."""
    def __missing__(self, key):
        return None


def evaluate(src: str, customer: dict) -> bool:
    code = compile_rule(src)
    env = _Attrs(customer)
    try:
        return bool(eval(code, {"__builtins__": {}}, env))  # noqa: S307 — AST-whitelisted above
    except TypeError:
        # comparing None with a number etc. — treat as not matching
        return False


def member(audience: dict, customer: dict) -> bool:
    """True when the customer matches `rule` and none of `exclusion_rules`."""
    rule = audience.get("rule")
    if not rule:
        raise RuleError(f"audience {audience.get('id')} has no `rule`")
    if not evaluate(rule, customer):
        return False
    for ex in audience.get("exclusion_rules", []) or []:
        if evaluate(ex, customer):
            return False
    return True
