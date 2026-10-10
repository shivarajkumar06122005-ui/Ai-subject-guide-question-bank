import ast
import re
import sympy as sp
from app.services.reasoning_parser_service import parse_reasoning
from sympy.parsing.sympy_parser import parse_expr, implicit_multiplication_application


def _parse_math_expression(expression: str, symbol_locals=None):
    """
    Parse mathematical expressions with support for implicit multiplication.
    Example: 2x -> 2*x, 2(x+1) -> 2*(x+1)
    """
    return parse_expr(
        expression.replace("^", "**").strip(),
        local_dict=symbol_locals or {},
        transformations="all",
    )

def _extract_math_symbols(reasoning: str):
    """
    Detect symbolic variables used in mathematical reasoning.
    """
    symbols = set()

    for line in reasoning.splitlines():
        if "=" not in line:
            continue

        left, right = line.split("=", 1)

        try:
            left_expr = _parse_math_expression(left, symbol_locals={})
            right_expr = _parse_math_expression(right, symbol_locals={})

            symbols.update(left_expr.free_symbols)
            symbols.update(right_expr.free_symbols)
        except Exception:
            continue

    return sorted(symbols, key=lambda symbol: str(symbol))

def _verify_equation_system(lines, math_symbols, symbol_locals):
    """
    Verify and solve a system of mathematical equations.
    """
    equations = []

    for line in lines:
        if "=" not in line:
            return None

        left, right = line.split("=", 1)

        left_expr = _parse_math_expression(
            left,
            symbol_locals
        )
        right_expr = _parse_math_expression(
            right,
            symbol_locals
        )

        equations.append(sp.Eq(left_expr, right_expr))

    if len(equations) <= 1:
        return None

    solutions = sp.solve(
        equations,
        math_symbols,
        dict=True
    )

    return {
        "domain": "math",
        "status": "verified" if solutions else "failed",
        "confidence": 1.0,
        "verified_steps": [
            {
                "step": index,
                "text": line,
                "status": "verified"
            }
            for index, line in enumerate(lines, start=1)
        ],
        "failed_steps": [] if solutions else [
            {
                "step": 1,
                "text": lines[0],
                "reason": "The equation system has no verified solution."
            }
        ],
        "hint": (
            f"System verified successfully: {solutions}"
            if solutions
            else "The submitted equation system could not be solved."
        ),
    }

def _extract_domain_restrictions(expressions, math_symbols):
    """
    Extract values that make mathematical expressions undefined.
    Currently focuses on denominator restrictions.
    """
    restrictions = []

    for expr in expressions:
        denominator = sp.denom(expr)

        if denominator == 1:
            continue

        try:
            excluded = sp.solve(denominator, math_symbols, dict=True)

            for solution in excluded:
                for symbol, value in solution.items():
                    restrictions.append({
                        "symbol": str(symbol),
                        "excluded_value": str(value),
                        "reason": f"{symbol} cannot equal {value} because the denominator becomes zero.",
                    })
        except Exception:
            continue

    return restrictions

def _calculate_math_confidence(
    verified_steps: list,
    failed_steps: list,
    total_steps: int,
) -> float:
    """
    F1.9: Confidence in the verifier's evidence, not confidence
    that the student's reasoning is correct.
    """
    if total_steps <= 0:
        return 0.0

    if not failed_steps:
        return 1.0

    first_failure = failed_steps[0]

    if (
        first_failure.get("is_first_failure")
        and first_failure.get("operation_preserved") is False
        and first_failure.get("expected_right") is not None
    ):
        return 0.95

    if first_failure.get("domain_restrictions"):
        return 0.95

    if verified_steps:
        return 0.85

    return 0.70

def _build_math_evidence(
    verified_steps: list,
    failed_steps: list,
    total_steps: int,
) -> dict:
    """
    F1.10: Package structured evidence explaining
    why the deterministic verifier is confident.
    """
    if total_steps <= 0:
        return {
            "type": "insufficient_input",
            "level": "none",
            "summary": "No mathematical reasoning was submitted.",
        }

    if not failed_steps:
        return {
            "type": "symbolic_solution_set",
            "level": "high",
            "summary": (
                "All submitted mathematical steps preserve "
                "the same solution set."
            ),
        }

    first_failure = failed_steps[0]

    if (
        first_failure.get("is_first_failure")
        and first_failure.get("operation_preserved") is False
        and first_failure.get("expected_right") is not None
    ):
        return {
            "type": "transition_preservation",
            "level": "high",
            "summary": (
                "The verifier detected a solution-set change and "
                "computed the expected transformed right side."
            ),
        }

    if first_failure.get("domain_restrictions"):
        return {
            "type": "domain_restriction",
            "level": "high",
            "summary": (
                "The verifier identified a mathematical domain "
                "restriction affecting the submitted step."
            ),
        }

    if verified_steps:
        return {
            "type": "structural_verification",
            "level": "medium",
            "summary": (
                "Earlier steps were verified, but the failed step "
                "does not provide enough evidence for a stronger classification."
            ),
        }

    return {
        "type": "parsing_or_structure",
        "level": "medium",
        "summary": (
            "The submitted reasoning could not be fully verified "
            "from its mathematical structure."
        ),
    }

def _parse_integral_expression(text: str):
    """
    Parse an explicit indefinite integral.

    Supported form:
      integral(x^2, x) = x^3/3
    """
    if "=" not in text:
        return None

    left, expected = text.split("=", 1)
    left = left.strip()
    expected = expected.strip()

    match = re.fullmatch(
        r"integral\s*\(\s*(.*)\s*,\s*([A-Za-z_]\w*)\s*\)",
        left
    )

    if not match:
        return None

    expression = match.group(1).strip()
    variable = match.group(2)

    if not expression or not expected:
        return None

    return expression, variable, expected


def verify_integral_reasoning(reasoning: str) -> dict:
    """
    Deterministic indefinite-integral verification using SymPy.

    Two antiderivatives are considered equivalent when their
    difference simplifies to a constant.
    """
    lines = [
        line.strip()
        for line in reasoning.splitlines()
        if line.strip()
    ]

    verified_steps = []
    failed_steps = []

    for index, line in enumerate(lines, start=1):
        parsed = _parse_integral_expression(line)

        if parsed is None:
            failed_steps.append({
                "step": index,
                "text": line,
                "reason": (
                    "Could not parse the integral. Use the explicit "
                    "integral(expression, x) form."
                ),
            })
            continue

        expression_text, variable_name, expected_text = parsed

        try:
            variable = sp.Symbol(variable_name)

            expression = sp.sympify(
                expression_text.replace("^", "**"),
                locals={variable_name: variable}
            )

            expected = sp.sympify(
                expected_text.replace("^", "**"),
                locals={variable_name: variable}
            )

            actual = sp.integrate(expression, variable)

            difference = sp.simplify(
                sp.diff(expected - actual, variable)
            )

            if difference != 0:
                failed_steps.append({
                    "step": index,
                    "text": line,
                    "reason": (
                        "The submitted antiderivative does not match "
                        "symbolic integration."
                    ),
                    "expected_integral": str(actual),
                    "submitted_integral": str(expected),
                })
                continue

            verified_steps.append({
                "step": index,
                "text": line,
                "status": "verified",
                "integral": str(actual),
            })

        except Exception as exc:
            failed_steps.append({
                "step": index,
                "text": line,
                "reason": f"Could not parse this integral: {exc}",
            })

    if failed_steps:
        first_failed = failed_steps[0]

        return {
            "domain": "calculus",
            "status": "failed",
            "confidence": 1.0,
            "verified_steps": verified_steps,
            "failed_steps": failed_steps,
            "hint": (
                f"Step {first_failed['step']} needs reconstruction. "
                f"{first_failed['reason']}"
            ),
        }

    return {
        "domain": "calculus",
        "status": "verified",
        "confidence": 1.0,
        "verified_steps": verified_steps,
        "failed_steps": [],
        "hint": "All submitted integral steps were verified symbolically.",
    }

def is_calculus_reasoning(reasoning: str) -> bool:
    """
    Detect explicit derivative reasoning.
    MVP supports d/dx, diff(...), and Derivative(...).
    """
    calculus_markers = [
        "d/dx",
        "diff(",
        "Derivative(",
        "integral(",
    ]

    return any(marker in reasoning for marker in calculus_markers)


def _parse_derivative_expression(text: str):
    """
    Parse an explicit derivative expression into:
    (expression, variable, expected_result).

    Supported forms:
      d/dx (x^2) = 2*x
      diff(x^2, x) = 2*x
      Derivative(x^2, x) = 2*x
    """
    if "=" not in text:
        return None

    left, expected = text.split("=", 1)
    left = left.strip()
    expected = expected.strip()

    variable = None
    expression = None

    d_dx_match = re.fullmatch(
        r"d/d([A-Za-z_]\w*)\s*\((.*)\)",
        left
    )

    if d_dx_match:
        variable = d_dx_match.group(1)
        expression = d_dx_match.group(2).strip()

    else:
        function_match = re.fullmatch(
            r"(?:diff|Derivative)\s*\(\s*(.*)\s*,\s*([A-Za-z_]\w*)\s*\)",
            left
        )

        if function_match:
            expression = function_match.group(1).strip()
            variable = function_match.group(2)

    if not expression or not variable:
        return None

    return expression, variable, expected


def verify_calculus_reasoning(reasoning: str) -> dict:
    """
    Deterministic derivative verification using SymPy.
    """
    lines = [
        line.strip()
        for line in reasoning.splitlines()
        if line.strip()
    ]


    if any(line.startswith("integral(") for line in lines):
        return verify_integral_reasoning(reasoning)

    verified_steps = []
    failed_steps = []

    for index, line in enumerate(lines, start=1):
        parsed = _parse_derivative_expression(line)

        if parsed is None:
            failed_steps.append({
                "step": index,
                "text": line,
                "reason": (
                    "Could not parse the derivative. Use an explicit "
                    "d/dx(...), diff(..., x), or Derivative(..., x) form."
                ),
            })
            continue

        expression_text, variable_name, expected_text = parsed

        try:
            variable = sp.Symbol(variable_name)

            expression = sp.sympify(
                expression_text.replace("^", "**"),
                locals={variable_name: variable}
            )

            expected = sp.sympify(
                expected_text.replace("^", "**"),
                locals={variable_name: variable}
            )

            actual = sp.diff(expression, variable)

            difference = sp.simplify(actual - expected)

            if difference != 0:
                failed_steps.append({
                    "step": index,
                    "text": line,
                    "reason": "The derivative result does not match SymPy verification.",
                    "expected_derivative": str(actual),
                    "submitted_derivative": str(expected),
                })
                continue

            verified_steps.append({
                "step": index,
                "text": line,
                "status": "verified",
                "derivative": str(actual),
            })

        except Exception as exc:
            failed_steps.append({
                "step": index,
                "text": line,
                "reason": f"Could not parse this derivative: {exc}",
            })

    if failed_steps:
        first_failed = failed_steps[0]

        return {
            "domain": "calculus",
            "status": "failed",
            "confidence": 1.0,
            "verified_steps": verified_steps,
            "failed_steps": failed_steps,
            "hint": (
                f"Step {first_failed['step']} needs reconstruction. "
                f"{first_failed['reason']}"
            ),
        }

    return {
        "domain": "calculus",
        "status": "verified",
        "confidence": 1.0,
        "verified_steps": verified_steps,
        "failed_steps": [],
        "hint": "All submitted derivative steps were verified symbolically.",
    }

def verify_math_reasoning(reasoning: str) -> dict:
    """
    Deterministic mathematical verification using SymPy.

    Verifies each equation and checks that consecutive steps
    preserve the same solution set.
    """

    lines = [
        line.strip()
        for line in reasoning.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "domain": "math",
            "status": "invalid",
            "confidence": 1.0,
            "verified_steps": [],
            "failed_steps": [],
            "hint": "Enter at least one mathematical reasoning step.",
        }

    verified_steps = []
    failed_steps = []
    previous_equation = None

    math_symbols = _extract_math_symbols(reasoning)
    symbol_locals = {str(symbol): symbol for symbol in math_symbols}

    # Treat multi-variable equations as simultaneous systems.
    # Single-variable multi-line equations are normally sequential
    # reasoning steps and must reach the transition verifier below.
    unique_symbol_count = len(math_symbols)

    if unique_symbol_count > 1:
        system_result = _verify_equation_system(
            lines,
            math_symbols,
            symbol_locals
        )

        if system_result is not None:
            return system_result

    for index, line in enumerate(lines, start=1):
        try:
            if "=" not in line:
                failed_steps.append({
                    "step": index,
                    "text": line,
                    "reason": "The step does not contain an equation.",
                })
                continue

            left, right = line.split("=", 1)

            left_expr = _parse_math_expression(
                left,
                symbol_locals
            )
            right_expr = _parse_math_expression(
                right,
                symbol_locals
            )

            domain_restrictions = _extract_domain_restrictions(
                [left_expr, right_expr],
                math_symbols
            )

            current_solutions = sp.solve(
                sp.Eq(left_expr, right_expr),
                math_symbols,
                dict=True
            )

            invalid_domain_solutions = []

            for solution in current_solutions:
                for restriction in domain_restrictions:
                    symbol_name = restriction["symbol"]
                    excluded_value = restriction["excluded_value"]

                    if symbol_name in solution:
                        if str(solution[symbol_name]) == excluded_value:
                            invalid_domain_solutions.append(solution)

            if invalid_domain_solutions:
                failed_steps.append({
                    "step": index,
                    "text": line,
                    "reason": (
                        "The equation produces a solution that is excluded "
                        "by the original expression's domain restriction."
                    ),
                    "domain_restrictions": domain_restrictions,
                    "invalid_solutions": [
                        str(solution) for solution in invalid_domain_solutions
                    ],
                })
                continue

            if previous_equation is not None:
                previous_left, previous_right = previous_equation

                previous_solutions = sp.solve(
                    sp.Eq(previous_left, previous_right),
                    math_symbols,
                    dict=True
                )

                if current_solutions != previous_solutions:
                    left_change = sp.simplify(left_expr - previous_left)
                    right_change = sp.simplify(right_expr - previous_right)

                    expected_right = sp.simplify(
                        previous_right + left_change
                    )

                    failed_steps.append({
                        "step": index,
                        "text": line,
                        "reason": (
                            "This transformation changes the solution set "
                            "from the previous step."
                        ),
                        "previous_step": (
                            f"{previous_left} = {previous_right}"
                        ),
                        "left_change": str(left_change),
                        "right_change": str(right_change),
                        "expected_right": str(expected_right),
                        "operation_preserved": False,
                        "is_first_failure": True,
                    })
                    break

            if not current_solutions and domain_restrictions:
                failed_steps.append({
                    "step": index,
                    "text": line,
                    "reason": (
                        "The equation has no valid solution after applying "
                        "the original domain restrictions."
                    ),
                    "domain_restrictions": domain_restrictions,
                })
                continue

            verified_steps.append({
                "step": index,
                "text": line,
                "status": "verified",
                "solutions": [str(solution) for solution in current_solutions],
                "domain_restrictions": domain_restrictions,
            })

            previous_equation = (left_expr, right_expr)

        except Exception as exc:
            failed_steps.append({
                "step": index,
                "text": line,
                "reason": f"Could not parse this equation: {exc}",
            })

    if failed_steps:
        return {
            "domain": "math",
            "status": "failed",
            "confidence": _calculate_math_confidence(
                verified_steps,
                failed_steps,
                len(lines),
            ),
            "verified_steps": verified_steps,
            "failed_steps": failed_steps,
            "evidence": _build_math_evidence(
                verified_steps,
                failed_steps,
                len(lines),
            ),
            "hint": _build_math_hint(failed_steps[0]),
        }

    return {
        "domain": "math",
        "status": "verified",
        "confidence": _calculate_math_confidence(
            verified_steps,
            [],
            len(lines),
        ),
        "verified_steps": verified_steps,
        "failed_steps": [],
        "evidence": _build_math_evidence(
            verified_steps,
            [],
            len(lines),
        ),
        "hint": "All submitted mathematical reasoning steps preserve the solution set.",
    }


def is_trigonometric_reasoning(reasoning: str) -> bool:
    """
    Detect common trigonometric expressions/functions.
    """

    trig_markers = [
        "sin",
        "cos",
        "tan",
        "cot",
        "sec",
        "csc",
        "asin",
        "acos",
        "atan",
        "sinh",
        "cosh",
        "tanh",
    ]

    lowered = reasoning.lower()

    return any(marker in lowered for marker in trig_markers)


def verify_trigonometric_reasoning(reasoning: str) -> dict:
    """
    Deterministic trigonometric identity verification using SymPy.
    """

    lines = [
        line.strip()
        for line in reasoning.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "domain": "trigonometry",
            "status": "invalid",
            "confidence": 1.0,
            "verified_steps": [],
            "failed_steps": [],
            "hint": "Enter at least one trigonometric reasoning step.",
        }

    x = sp.Symbol("x", real=True)

    verified_steps = []
    failed_steps = []

    trig_locals = {
        "x": x,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "cot": sp.cot,
        "sec": sp.sec,
        "csc": sp.csc,
    }

    for index, line in enumerate(lines, start=1):
        try:
            if "=" not in line:
                failed_steps.append({
                    "step": index,
                    "text": line,
                    "reason": "The step does not contain an identity or equation.",
                })
                continue

            left, right = line.split("=", 1)

            left_expr = sp.sympify(
                left.replace("^", "**"),
                locals=trig_locals,
            )

            right_expr = sp.sympify(
                right.replace("^", "**"),
                locals=trig_locals,
            )

            difference = sp.trigsimp(
                sp.expand_trig(left_expr - right_expr)
            )

            if difference != 0:
                simplified_difference = sp.simplify(difference)

                if simplified_difference != 0:
                    failed_steps.append({
                        "step": index,
                        "text": line,
                        "reason": (
                            "The two sides are not symbolically equivalent "
                            "as a trigonometric identity."
                        ),
                    })
                    continue

            verified_steps.append({
                "step": index,
                "text": line,
                "status": "verified",
                "type": "trigonometric_identity",
            })

        except Exception as exc:
            failed_steps.append({
                "step": index,
                "text": line,
                "reason": f"Could not parse this trigonometric expression: {exc}",
            })

    if failed_steps:
        return {
            "domain": "trigonometry",
            "status": "failed",
            "confidence": 1.0,
            "verified_steps": verified_steps,
            "failed_steps": failed_steps,
            "hint": _build_math_hint(failed_steps[0]),
        }

    return {
        "domain": "trigonometry",
        "status": "verified",
        "confidence": 1.0,
        "verified_steps": verified_steps,
        "failed_steps": [],
        "hint": "All submitted trigonometric identities passed symbolic verification.",
    }


def is_inequality_reasoning(reasoning: str) -> bool:
    """
    Detect common inequality expressions.
    """

    inequality_markers = [
        ">=",
        "<=",
        ">",
        "<",
    ]

    return any(marker in reasoning for marker in inequality_markers)


def verify_inequality_reasoning(reasoning: str) -> dict:
    """
    Deterministic inequality verification using SymPy.

    Verifies each inequality step and checks that consecutive
    steps preserve the same solution region.
    """

    lines = [
        line.strip()
        for line in reasoning.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "domain": "inequality",
            "status": "invalid",
            "confidence": 1.0,
            "verified_steps": [],
            "failed_steps": [],
            "hint": "Enter at least one inequality reasoning step.",
        }

    x = sp.Symbol("x", real=True)

    verified_steps = []
    failed_steps = []
    previous_region = None

    for index, line in enumerate(lines, start=1):
        try:
            normalized = line.replace("^", "**")

            relation = None
            for operator in [">=", "<=", ">", "<"]:
                if operator in normalized:
                    relation = operator
                    break

            if relation is None:
                failed_steps.append({
                    "step": index,
                    "text": line,
                    "reason": "The step does not contain an inequality.",
                })
                continue

            left, right = normalized.split(relation, 1)

            left_expr = sp.sympify(
                left.strip(),
                locals=symbol_locals,
            )

            right_expr = sp.sympify(
                right.strip(),
                locals=symbol_locals,
            )

            if relation == ">":
                inequality = left_expr > right_expr
            elif relation == ">=":
                inequality = left_expr >= right_expr
            elif relation == "<":
                inequality = left_expr < right_expr
            else:
                inequality = left_expr <= right_expr

            current_region = sp.reduce_inequalities([inequality], x)

            if previous_region is not None:
                equivalent = sp.simplify(
                    sp.Equivalent(previous_region, current_region)
                )

                if equivalent != sp.true:
                    failed_steps.append({
                        "step": index,
                        "text": line,
                        "reason": (
                            "This transformation changes the solution "
                            "region from the previous step."
                        ),
                    })
                    continue

            verified_steps.append({
                "step": index,
                "text": line,
                "status": "verified",
                "solution_region": str(current_region),
            })

            previous_region = current_region

        except Exception as exc:
            failed_steps.append({
                "step": index,
                "text": line,
                "reason": f"Could not parse this inequality: {exc}",
            })

    if failed_steps:
        return {
            "domain": "inequality",
            "status": "failed",
            "confidence": 1.0,
            "verified_steps": verified_steps,
            "failed_steps": failed_steps,
            "hint": _build_math_hint(failed_steps[0]),
        }

    return {
        "domain": "inequality",
        "status": "verified",
        "confidence": 1.0,
        "verified_steps": verified_steps,
        "failed_steps": [],
        "hint": "All submitted inequality steps preserve the same solution region.",
    }

def verify_python_reasoning(reasoning: str) -> dict:
    """
    Deterministic Python syntax/structure verification using AST.
    """

    try:
        ast.parse(reasoning)

        return {
            "domain": "python",
            "status": "verified",
            "confidence": 1.0,
            "evidence": {
                "type": "python_syntax",
                "level": "high",
                "summary": "The submitted Python reasoning is syntactically valid.",
            },
            "verified_steps": [
                {
                    "step": 1,
                    "text": "Python syntax",
                    "status": "verified",
                }
            ],
            "failed_steps": [],
            "hint": "The submitted Python reasoning is syntactically valid.",
        }

    except SyntaxError as exc:
        return {
            "domain": "python",
            "status": "failed",
            "confidence": 1.0,
            "evidence": {
                "type": "python_syntax",
                "level": "high",
                "summary": "The submitted Python reasoning contains a syntax error.",
            },
            "verified_steps": [],
            "failed_steps": [
                {
                    "step": 1,
                    "text": "Python syntax",
                    "reason": str(exc)
                }
            ],
            "hint": "Check the syntax around the reported line and reconstruct that part of the solution.",
        }


def detect_domain(reasoning: str) -> str:
    """
    Lightweight deterministic domain detection.
    """

    python_patterns = [
        r"(?m)^\s*def\s+\w+\s*\(",
        r"(?m)^\s*import\s+\w+",
        r"(?m)^\s*from\s+\w+(\.\w+)*\s+import\s+",
        r"(?m)^\s*print\s*\(",
        r"(?m)^\s*for\s+\w+\s+in\s+",
        r"(?m)^\s*while\s+.+:",
        r"(?m)^\s*if\s+.+:",
        r"(?m)^\s*return\s+",
    ]

    if any(re.search(pattern, reasoning) for pattern in python_patterns):
        return "python"

    return "math"


def verify_reasoning(reasoning: str) -> dict:
    """
    Main deterministic F1 verification entry point.
    """

    if not reasoning.strip():
        return {
            "domain": "unknown",
            "status": "invalid",
            "confidence": 0.0,
            "evidence": {
                "type": "insufficient_input",
                "level": "none",
                "summary": "No reasoning was submitted for verification.",
            },
            "verified_steps": [],
            "failed_steps": [],
            "hint": "Submit reasoning before verification.",
        }

    if is_calculus_reasoning(reasoning):
        return verify_calculus_reasoning(reasoning)
    if is_trigonometric_reasoning(reasoning):
        return verify_trigonometric_reasoning(reasoning)

    if is_inequality_reasoning(reasoning):
        return verify_inequality_reasoning(reasoning)

    domain = detect_domain(reasoning)

    if domain == "python":
        return verify_python_reasoning(reasoning)

    # F1.5: Parse natural-language mathematical reasoning
    # before deterministic symbolic verification.
    natural_language_markers = [
    r"\bstart\b",
    r"\bsubtract\b",
    r"\badd\b",
    r"\bdivide\b",
    r"\bmultiply\b",
    r"\btherefore\b",
    r"\bbecause\b",
    r"\bsince\b",
    r"\bthen\b",
    r"\bso\b",
    r"\bgiven\b",
    r"\bassume\b",
    r"\blet\b",
    r"\bfirst\b",
    r"\bnext\b",
    r"\bfinally\b",
]

    is_natural_language_reasoning = any(
        re.search(marker, reasoning, re.IGNORECASE)
        for marker in natural_language_markers
    )

    if "=" in reasoning and (
        len(reasoning.splitlines()) == 1
        or any("=" not in line for line in reasoning.splitlines())
        or is_natural_language_reasoning
    ):
        parsed_reasoning = parse_reasoning(reasoning)

        parsed_steps = parsed_reasoning.get("steps", [])

        parsed_expressions = [
            step.get("expression", "").strip()
            for step in parsed_steps
            if step.get("expression", "").strip()
        ]

        if len(parsed_expressions) >= 2:
            reasoning = "\n".join(parsed_expressions)
    return verify_math_reasoning(reasoning)


def _build_math_hint(failed_step: dict) -> str:
    step_number = failed_step.get("step", "?")
    reason = failed_step.get(
        "reason",
        "This step could not be verified."
    )
    domain_restrictions = failed_step.get(
        "domain_restrictions",
        []
    )

    if domain_restrictions:
        restrictions = "; ".join(
            restriction.get(
                "reason",
                "A domain restriction applies."
            )
            for restriction in domain_restrictions
        )

        return (
            f"Step {step_number} needs reconstruction. "
            "Before continuing, check whether the original expression "
            f"allows the value you introduced. {restrictions} "
            "What restriction must remain true throughout the solution?"
        )

    previous_step = failed_step.get("previous_step")
    left_change = failed_step.get("left_change")
    right_change = failed_step.get("right_change")
    expected_right = failed_step.get("expected_right")

    if (
        previous_step
        and left_change is not None
        and right_change is not None
        and expected_right is not None
    ):
        return (
            f"Step {step_number} needs reconstruction. "
            f"Compare it with the previous step ({previous_step}). "
            f"The left side changed by {left_change}, so applying the "
            f"same operation to the right side would give {expected_right}. "
            f"Your right side changed by {right_change}. "
            "What operation did you intend to apply to both sides?"
        )

    if previous_step and left_change is not None and right_change is not None:
        return (
            f"Step {step_number} needs reconstruction. "
            f"Compare it with the previous step ({previous_step}). "
            f"The left side changed by {left_change}, while the right side "
            f"changed by {right_change}. "
            "What operation did you apply to one side, and did you apply "
            "the same operation to the other side?"
        )

    return (
        f"Step {step_number} needs reconstruction. "
        f"{reason} "
        "What changed from the previous step, and does that same "
        "operation preserve the solution?"
    )






























































