
from sympy import symbols, sympify, diff, Symbol


import math

def newton_raphson(funcion_str, valor_inicial, tolerancia=1e-6, max_iter=1000):
    x = symbols('x')
    historial = []

    try:
        f = sympify(funcion_str)
        f_derivada = diff(f, x)
        f_func = lambda val: float(f.subs(x, val).evalf())
        f_prime_func = lambda val: float(f_derivada.subs(x, val).evalf())
    except Exception as e:
        return None, f"Error al interpretar la función: {str(e)}", []

    xi = float(valor_inicial)

    for i in range(1, max_iter + 1):
        try:
            f_xi = f_func(xi)
            f_prime_xi = f_prime_func(xi)
        except Exception as e:
            return None, f"Error al evaluar funciones: {str(e)}", historial

        if f_prime_xi == 0:
            return None, "Derivada igual a 0. No se puede continuar.", historial

        xi_nuevo = xi - f_xi / f_prime_xi
        error_relativo = abs((xi_nuevo - xi) / xi_nuevo) if xi_nuevo != 0 else abs(xi_nuevo - xi)

        # Generar fórmula en LaTeX
        formula_tex = (
            f"x_{{{i}}} = {xi:.6f} - \\frac{{{f_xi:.6f}}}{{{f_prime_xi:.6f}}} = {xi_nuevo:.6f} \\\\ "
            f"\\text{{Error}} = \\left| \\frac{{{xi_nuevo:.6f} - {xi:.6f}}}{{{xi_nuevo:.6f}}} \\right| = {error_relativo:.6f}"
        )
        
        historial.append({
            "iteracion": i,
            "xi": round(xi, 6),
            "f(xi)": round(f_xi, 6),
            "f'(xi)": round(f_prime_xi, 6),
            "xi_nuevo": round(xi_nuevo, 6),
            "error": round(error_relativo, 6),
            "formula_tex": formula_tex
        })

        if error_relativo < tolerancia:
            return round(xi_nuevo, 6), None, historial

        xi = xi_nuevo

    return None, "No se alcanzó convergencia dentro del máximo de iteraciones.", historial
