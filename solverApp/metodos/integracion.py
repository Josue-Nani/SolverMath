import math
from sympy import symbols, lambdify, sympify

def metodoTrapecio(funcion, a, b, n):
    """Método del Trapecio para integración numérica"""
    try:
        h = (b - a) / n
        procedimiento = []
        
        # Paso 1: Configuración
        procedimiento.append({
            'tipo': 'configuracion',
            'mensaje': f'Método del Trapecio con n={n} intervalos'
        })
        
        # Evaluar función en puntos
        evaluaciones = []
        suma = 0
        
        for i in range(n + 1):
            xi = a + i * h
            fxi = funcion(xi)
            
            if i == 0 or i == n:
                coef = 1
                contribucion = coef * fxi
            else:
                coef = 2
                contribucion = coef * fxi
            
            evaluaciones.append({
                'tipo': 'evaluacion',
                'indice': i,
                'x_valor': round(xi, 6),
                'f_valor': round(fxi, 6),
                'coeficiente': coef,
                'contribucion': round(contribucion, 6)
            })
            
            suma += contribucion
        
        # Agregar evaluaciones al procedimiento
        procedimiento.extend(evaluaciones)
        
        # Paso final: aplicar fórmula
        resultado = (h / 2) * suma
        
        procedimiento.append({
            'tipo': 'formula',
            'formula': f'I \\approx \\frac{{h}}{{2}} \\left[ f(a) + 2\\sum_{{i=1}}^{{n-1}} f(x_i) + f(b) \\right]'
        })
        
        procedimiento.append({
            'tipo': 'calculo',
            'calculo': f'I \\approx \\frac{{{h:.6f}}}{{2}} \\times {suma:.6f} = {resultado:.6f}'
        })
        
        return resultado, procedimiento
        
    except Exception as e:
        return None, [f'Error en el cálculo: {str(e)}']

def metodoSimpson1(funcion, a, b, n):
    """Método de Simpson 1/3 para integración numérica"""
    try:
        if n % 2 != 0:
            raise ValueError("El número de intervalos debe ser par para Simpson 1/3")
            
        h = (b - a) / n
        procedimiento = []
        
        # Paso 1: Configuración
        procedimiento.append({
            'tipo': 'configuracion',
            'mensaje': f'Método de Simpson 1/3 con n={n} intervalos'
        })
        
        # Evaluar función en puntos
        evaluaciones = []
        suma = 0
        
        for i in range(n + 1):
            xi = a + i * h
            fxi = funcion(xi)
            
            if i == 0 or i == n:
                coef = 1
            elif i % 2 == 1:  # índices impares
                coef = 4
            else:  # índices pares (excepto extremos)
                coef = 2
            
            contribucion = coef * fxi
            
            evaluaciones.append({
                'tipo': 'evaluacion',
                'indice': i,
                'x_valor': round(xi, 6),
                'f_valor': round(fxi, 6),
                'coeficiente': coef,
                'contribucion': round(contribucion, 6)
            })
            
            suma += contribucion
        
        # Agregar evaluaciones al procedimiento
        procedimiento.extend(evaluaciones)
        
        # Paso final: aplicar fórmula
        resultado = (h / 3) * suma
        
        procedimiento.append({
            'tipo': 'formula',
            'formula': f'I \\approx \\frac{{h}}{{3}} \\left[ f(a) + 4\\sum_{{impares}} f(x_i) + 2\\sum_{{pares}} f(x_i) + f(b) \\right]'
        })
        
        procedimiento.append({
            'tipo': 'calculo',
            'calculo': f'I \\approx \\frac{{{h:.6f}}}{{3}} \\times {suma:.6f} = {resultado:.6f}'
        })
        
        return resultado, procedimiento
        
    except Exception as e:
        return None, [f'Error en el cálculo: {str(e)}']

def metodoSimpson2(funcion, a, b, n):
    """Método de Simpson 3/8 para integración numérica"""
    try:
        if n % 3 != 0:
            raise ValueError("El número de intervalos debe ser múltiplo de 3 para Simpson 3/8")
            
        h = (b - a) / n
        procedimiento = []
        
        # Paso 1: Configuración
        procedimiento.append({
            'tipo': 'configuracion',
            'mensaje': f'Método de Simpson 3/8 con n={n} intervalos'
        })
        
        # Evaluar función en puntos
        evaluaciones = []
        suma = 0
        
        for i in range(n + 1):
            xi = a + i * h
            fxi = funcion(xi)
            
            if i == 0 or i == n:
                coef = 1
            elif i % 3 == 0:  # múltiplos de 3 (excepto extremos)
                coef = 2
            else:  # otros puntos
                coef = 3
            
            contribucion = coef * fxi
            
            evaluaciones.append({
                'tipo': 'evaluacion',
                'indice': i,
                'x_valor': round(xi, 6),
                'f_valor': round(fxi, 6),
                'coeficiente': coef,
                'contribucion': round(contribucion, 6)
            })
            
            suma += contribucion
        
        # Agregar evaluaciones al procedimiento
        procedimiento.extend(evaluaciones)
        
        # Paso final: aplicar fórmula
        resultado = (3 * h / 8) * suma
        
        procedimiento.append({
            'tipo': 'formula',
            'formula': f'I \\approx \\frac{{3h}}{{8}} \\left[ f(a) + 3\\sum_{{no-múltiplos-de-3}} f(x_i) + 2\\sum_{{múltiplos-de-3}} f(x_i) + f(b) \\right]'
        })
        
        procedimiento.append({
            'tipo': 'calculo',
            'calculo': f'I \\approx \\frac{{3 \\times {h:.6f}}}{{8}} \\times {suma:.6f} = {resultado:.6f}'
        })
        
        return resultado, procedimiento
        
    except Exception as e:
        return None, [f'Error en el cálculo: {str(e)}']

# Ejemplo de uso (comentado para no ejecutar)
# print(metodoTrapecio(lambda x: x**2, 0, 1, 4))