
from sympy import symbols, sympify, diff, Symbol
import math

def newton_raphson(funcion_str, valor_inicial, tolerancia=1e-6, max_iter=100):
    """
    Método Newton-Raphson mejorado con mejor convergencia y validación
    """
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
    
    # Validar que el punto inicial sea válido
    try:
        f_inicial = f_func(xi)
        f_prime_inicial = f_prime_func(xi)
        if not (math.isfinite(f_inicial) and math.isfinite(f_prime_inicial)):
            return None, "El punto inicial no es válido para esta función", []
    except Exception as e:
        return None, f"Error al evaluar el punto inicial: {str(e)}", []

    # Variables para detectar oscilaciones y divergencia
    valores_anteriores = []
    min_cambio = float('inf')
    iteraciones_sin_mejora = 0
    
    for i in range(max_iter):
        try:
            f_xi = f_func(xi)
            f_prime_xi = f_prime_func(xi)
        except Exception as e:
            return None, f"Error al evaluar funciones en iteración {i}: {str(e)}", historial

        # Verificar si la derivada es muy pequeña (casi cero)
        if abs(f_prime_xi) < 1e-14:
            return None, f"Derivada muy pequeña ({f_prime_xi:.2e}) en iteración {i}. Posible extremo local.", historial

        # Calcular nuevo punto
        xi_nuevo = xi - f_xi / f_prime_xi
        
        # Verificar si el resultado es válido
        if not math.isfinite(xi_nuevo):
            return None, f"Resultado no válido en iteración {i}. Posible divergencia.", historial

        # Calcular diferentes tipos de error
        error_absoluto = abs(xi_nuevo - xi)
        error_relativo = abs((xi_nuevo - xi) / xi_nuevo) if abs(xi_nuevo) > 1e-14 else error_absoluto
        error_funcion = abs(f_xi)
        
        # Usar el menor de los errores relativos o absolutos según el caso
        error_efectivo = min(error_relativo, error_absoluto) if abs(xi_nuevo) > 1 else error_absoluto

        # Generar fórmula en LaTeX
        formula_tex = (
            f"x_{{{i+1}}} = {xi:.6f} - \\frac{{{f_xi:.6f}}}{{{f_prime_xi:.6f}}} = {xi_nuevo:.6f} \\\\ "
            f"\\text{{Error}} = {error_efectivo:.6f}"
        )
        
        historial.append({
            "iteracion": i,
            "xi": round(xi, 6),
            "f(xi)": round(f_xi, 6),
            "f'(xi)": round(f_prime_xi, 6),
            "xi_nuevo": round(xi_nuevo, 6),
            "error": round(error_efectivo, 6),
            "formula_tex": formula_tex
        })

        # Criterios de convergencia mejorados
        converged = False
        
        # 1. Error relativo/absoluto suficientemente pequeño
        if error_efectivo < tolerancia:
            converged = True
        
        # 2. Valor de la función muy cercano a cero
        if abs(f_xi) < tolerancia * 10:
            converged = True
        
        # 3. Cambio muy pequeño en x
        if error_absoluto < tolerancia * 1e-3:
            converged = True
            
        if converged:
            return round(xi_nuevo, 6), None, historial

        # Detección de problemas de convergencia
        
        # Detectar oscilaciones (saltando entre valores)
        if len(valores_anteriores) >= 3:
            # Verificar si estamos oscilando entre valores
            if any(abs(xi_nuevo - prev) < tolerancia * 10 for prev in valores_anteriores[-3:]):
                # Promedio de los últimos valores para estabilizar
                xi_nuevo = (xi_nuevo + xi + sum(valores_anteriores[-2:])) / 4
        
        # Detectar divergencia (valores que crecen rápidamente)
        if abs(xi_nuevo) > 1e10:
            return None, f"Divergencia detectada en iteración {i}. Intenta con un valor inicial diferente.", historial
        
        # Detectar convergencia lenta
        cambio_actual = abs(xi_nuevo - xi)
        if cambio_actual < min_cambio:
            min_cambio = cambio_actual
            iteraciones_sin_mejora = 0
        else:
            iteraciones_sin_mejora += 1
            
        # Si no hay mejora en muchas iteraciones, posible problema
        if iteraciones_sin_mejora > 10 and i > 15:
            return None, f"Convergencia muy lenta después de {i} iteraciones. Intenta con un valor inicial diferente.", historial
        
        # Guardar valores anteriores para detectar patrones
        valores_anteriores.append(xi)
        if len(valores_anteriores) > 5:
            valores_anteriores.pop(0)
            
        # ACTUALIZAR xi para la siguiente iteración
        xi = xi_nuevo

    return None, f"No se alcanzó convergencia después de {max_iter} iteraciones. Intenta con un valor inicial diferente o mayor tolerancia.", historial
