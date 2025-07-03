from sympy import symbols, lambdify, sympify
import numpy as np

def metodoTrapecio(funcion, a, b, n):

    x = symbols('x')
    f = lambdify(x, sympify(funcion), 'math')

    h = (b - a) / n
    suma = f(a) + f(b)

    for i in range(1,n):
        xi = a + (i*h)
        suma += 2*f(xi)

    return (h/2) * suma

pasos = []
pasos.append(r"f(x) = x^2 \Rightarrow \int_{0}^{1} x^2 dx")

print(metodoTrapecio('x**2 + 9*x', 0, 1, 2))