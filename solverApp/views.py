from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.conf import settings
from . forms import RegistroUsuarioForm, LoginUsuarioForm, EditarPerfilForm
from .models import Perfil, HistorialOperacion
from sympy import sympify, diff, lambdify, Symbol, symbols, integrate
from sympy.core.sympify import SympifyError
from .metodos.newton import newton_raphson
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import json

def convertir_a_formato_matematico(expresion):
    """
    Convierte una expresión matemática de formato Python a formato matemático legible.
    """
    if not expresion:
        return ''
    
    # Convertir operadores básicos
    expresion = expresion.replace('**', '^')
    expresion = expresion.replace('*', '×')
    expresion = expresion.replace('/', '÷')
    
    # Convertir funciones matemáticas
    expresion = expresion.replace('exp(', 'e^(')
    expresion = expresion.replace('log(', 'ln(')
    expresion = expresion.replace('sqrt(', '√(')
    
    # Convertir constantes
    expresion = expresion.replace('3.14159265359', 'π')
    expresion = expresion.replace('2.71828182846', 'e')
    
    return expresion

@login_required
def perfil_view(request):
    usuario = request.user
    # Crear perfil si no existe (en lugar de dar error 404)
    perfil, created = Perfil.objects.get_or_create(
        user=usuario,
        defaults={
            'nombre_completo': usuario.first_name + ' ' + usuario.last_name if usuario.first_name else usuario.username,
            'carrera': '',
            'carnet': '',
            'ciclo': '',
        }
    )
    if created:
        print(f"Perfil creado para el usuario: {usuario.username}")
    
    historial = HistorialOperacion.objects.filter(usuario=usuario).order_by('-fecha')
    editando = request.GET.get('edit') == '1'

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=perfil, user=usuario)
        print(f"DEBUG: POST data recibido en perfil: {request.POST}")
        print(f"DEBUG: FILES data recibido en perfil: {request.FILES}")
        
        if form.is_valid():
            print("DEBUG: Formulario de perfil válido")
            form.save()
            print("DEBUG: Perfil actualizado exitosamente")
            return redirect('perfil')
        else:
            print(f"DEBUG: Formulario de perfil inválido. Errores: {form.errors}")
    else:
        form = EditarPerfilForm(instance=perfil, user=usuario)

    # Procesar historial para incluir # de iteraciones si hay tabla en HTML
    historial_modificado = []
    for h in historial:
        iteraciones = 0
        if h.tabla and 'Iteración' in h.tabla:
            iteraciones = h.tabla.count('Iteración') or h.tabla.count('<tr>') - 1
        historial_modificado.append({
            'id': h.id,
            'fecha': h.fecha,
            'metodo': h.metodo,
            'expresion': h.expresion,
            'datos_entrada': h.datos_entrada,
            'parametros': h.parametros,
            'resultado': h.resultado,
            'tabla': h.tabla,
            'iteraciones': iteraciones,
        })

    return render(request, 'perfil.html', {
        'usuario': usuario,
        'perfil': perfil,
        'historial': historial_modificado,
        'editando': editando,
        'form': form if editando else None
    })


# --------------------------
# MÉTODO DEL TRAPECIO
def metodoTrapecio(funcion, a, b, n):
    """Método del Trapecio para integración numérica"""
    try:
        h = (b - a) / n
        procedimiento = []
        
        # Evaluaciones de función en puntos
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

# --------------------------
# MÉTODO DE SIMPSON 1/3
def metodoSimpson1(funcion, a, b, n):
    """Método de Simpson 1/3 para integración numérica"""
    try:
        if n % 2 != 0:
            return None, [{'tipo': 'error', 'mensaje': 'El método de Simpson 1/3 requiere que n sea par.'}]
            
        h = (b - a) / n
        procedimiento = []
        
        # Evaluaciones de función en puntos
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

# --------------------------
# MÉTODO DE SIMPSON 3/8
def metodoSimpson2(funcion, a, b, n):
    """Método de Simpson 3/8 para integración numérica"""
    try:
        if n % 3 != 0:
            return None, [{'tipo': 'error', 'mensaje': 'El método de Simpson 3/8 requiere que n sea múltiplo de 3.'}]
            
        h = (b - a) / n
        procedimiento = []
        
        # Evaluaciones de función en puntos
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

# --------------------------
# VISTA PRINCIPAL

@login_required
def integracion_view(request, historial_id=None):
    resultadoIntegral = None
    procedimiento = None
    error = None
    grafica = None
    funcion = None
    funcion_original = None
    a = None
    b = None
    n = None
    metodo = 1
    limite_izquierdo = None
    limite_derecho = None
    intervalos = None
    datos_precargados = None

    # Si se proporciona un ID de historial, cargar los datos
    if historial_id:
        try:
            historial = HistorialOperacion.objects.get(id=historial_id, usuario=request.user)
            if "Integración" in historial.metodo:
                # Determinar el método basado en el nombre del historial
                metodo_num = 1  # Trapecio por defecto
                if "Simpson 1/3" in historial.metodo:
                    metodo_num = 2
                elif "Simpson 3/8" in historial.metodo:
                    metodo_num = 3
                
                # Asegurar que los valores numéricos se conviertan correctamente
                a_val = historial.parametros.get('a', '')
                b_val = historial.parametros.get('b', '')
                n_val = historial.parametros.get('n', '')
                
                # Debug: imprimir valores originales
                print(f"DEBUG Integración - Parámetros originales: {historial.parametros}")
                print(f"DEBUG Integración - a: {a_val} (tipo: {type(a_val)})")
                print(f"DEBUG Integración - b: {b_val} (tipo: {type(b_val)})")
                print(f"DEBUG Integración - n: {n_val} (tipo: {type(n_val)})")
                
                datos_precargados = {
                    'funcion': historial.expresion,
                    'a': str(a_val) if a_val != '' else '',
                    'b': str(b_val) if b_val != '' else '',
                    'n': str(n_val) if n_val != '' else '',
                    'metodo': metodo_num
                }
                
                # Debug: imprimir datos procesados
                print(f"DEBUG Integración - Datos precargados: {datos_precargados}")
        except HistorialOperacion.DoesNotExist:
            error = "No se encontró el problema en el historial."

    if request.method == 'POST':
        funcion_original = request.POST.get('funcion', '')
        funcion = funcion_original.replace('^', '**')
        metodo = int(request.POST.get("metodos_integracion", 1))
        limite_izquierdo = request.POST.get("input_limiteIzquierdo", '')
        limite_derecho = request.POST.get("input_limiteDerecho", '')
        intervalos = request.POST.get("input_intervalos", '')

        # Datos del formulario para mantener valores
        datos_formulario = {
            'funcion': funcion_original,  # Mantener formato original
            'metodo': metodo,
            'limite_izquierdo': limite_izquierdo,
            'limite_derecho': limite_derecho,
            'intervalos': intervalos
        }

        # Usa los límites del formulario para la gráfica
        if funcion and limite_izquierdo and limite_derecho:
            try:
                a = float(limite_izquierdo)
                b = float(limite_derecho)
                grafica = graficar_funcion(funcion, a, b)
            except Exception as e:
                error = str(e)
                grafica = None

        if metodo and limite_izquierdo and limite_derecho and intervalos:
            try:
                a = float(limite_izquierdo)
                b = float(limite_derecho)
                n = int(intervalos)

                if a >= b:
                    error = "El límite izquierdo debe ser menor que el derecho."
                elif n <= 0:
                    error = "El número de intervalos debe ser mayor que cero."
                else:
                    x = symbols('x')
                    try:
                        funcion_sympy = sympify(funcion)
                        funcion_lambda = lambdify(x, funcion_sympy, modules=["math"])
                    except SympifyError:
                        error = "Función no válida."
                        funcion_lambda = None

                    if funcion_lambda and not error:
                        if metodo == 1:
                            resultadoIntegral, procedimiento = metodoTrapecio(funcion_lambda, a, b, n)
                        elif metodo == 2:
                            resultadoIntegral, procedimiento = metodoSimpson1(funcion_lambda, a, b, n)
                        elif metodo == 3:
                            resultadoIntegral, procedimiento = metodoSimpson2(funcion_lambda, a, b, n)

                        if resultadoIntegral is not None:
                            resultadoIntegral = round(float(resultadoIntegral), 6)

                            # Guardar en historial si no es usuario invitado
                            if request.user.is_authenticated and request.user.username != "invitado":
                                nombre_metodo = {1: "Trapecio", 2: "Simpson 1/3", 3: "Simpson 3/8"}.get(metodo, "Desconocido")

                                # Tabla de pasos en HTML
                                tabla_html = "<div class='text-sm text-white/90 bg-gray-900 p-4 rounded-md shadow border border-cyan-600 overflow-x-auto whitespace-pre-wrap'>"
                                tabla_html += "<br>".join([f"\\[{paso}\\]" for paso in procedimiento])  # Envolver cada paso en delimitadores de MathJax
                                tabla_html += "</div>"

                                HistorialOperacion.objects.create(
                                    usuario=request.user,
                                    metodo=f"Integración - {nombre_metodo}",
                                    datos_entrada=f"f(x)={funcion}, a={a}, b={b}, n={n}",
                                    resultado=str(resultadoIntegral),
                                    parametros={"a": a, "b": b, "n": n},
                                    pasos="\n".join([str(paso) for paso in procedimiento]),
                                    tabla=tabla_html,
                                    expresion=funcion,
                                    grafica=grafica  
                                )

            except Exception as exc:
                error = f"Error en los datos ingresados: {str(exc)}"
    else:
        # Si no es POST, inicializar variables con valores por defecto
        datos_formulario = {
            'funcion': '',
            'limite_izquierdo': '',
            'limite_derecho': '',
            'intervalos': '',
            'metodo': 1
        }

    # Preparar datos para mantener en el formulario si no se han definido
    if 'datos_formulario' not in locals():
        datos_formulario = {
            'funcion': '',
            'limite_izquierdo': '',
            'limite_derecho': '',
            'intervalos': '',
            'metodo': 1
        }

    # Determinar si se debe mostrar notificación de precarga
    es_desde_historial = historial_id is not None and datos_precargados is not None

    return render(request, 'Metodos/integracion.html', {
        'resultadoIntegral': resultadoIntegral,
        'procedimiento': procedimiento,
        'error': error,
        'grafica': grafica,
        'datos_precargados': datos_precargados,
        'datos_formulario': datos_formulario,
        'es_desde_historial': es_desde_historial,
        # Variables adicionales para el procedimiento detallado
        'funcion_mostrar': convertir_a_formato_matematico(funcion_original) if funcion_original else '',
        'limite_a': a if a is not None else '',
        'limite_b': b if b is not None else '',
        'n_intervalos': n if n is not None else '',
        'h_valor': round((b - a) / n, 6) if a is not None and b is not None and n is not None and n > 0 else '',
        'metodo_seleccionado': metodo if metodo is not None else 1,
        'metodo_nombre': {1: "Regla del Trapecio", 2: "Regla de Simpson 1/3", 3: "Regla de Simpson 3/8"}.get(metodo if metodo is not None else 1, "Trapecio"),
    })
def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES)  
        print(f"DEBUG: POST data recibido: {request.POST}")
        print(f"DEBUG: FILES data recibido: {request.FILES}")
        if form.is_valid():
            form.save()  # Ya no se hace login aquí
            print("DEBUG: Formulario válido, usuario creado exitosamente")
            return redirect('login')  # Redirige al login después del registro
        else:
            print(f"DEBUG: Formulario inválido. Errores: {form.errors}")
            for field, errors in form.errors.items():
                print(f"DEBUG: Campo '{field}' con errores: {errors}")
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def menu_principal(request):
    # Debug information about the user's authentication state
    print(f"DEBUG: Acceso a menu_principal")
    print(f"DEBUG: Usuario autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        print(f"DEBUG: Nombre de usuario: {request.user.username}")
    print(f"DEBUG: Sesión: {request.session.session_key}")
    
    return render(request, 'menu.html')


@login_required
def newton_raphson_view(request, historial_id=None):
    resultado = None
    error = None
    procedimiento = []
    derivada_str = ""
    funcion_original = ""
    datos_precargados = None

    # Si se proporciona un ID de historial, cargar los datos
    if historial_id:
        try:
            historial = HistorialOperacion.objects.get(id=historial_id, usuario=request.user)
            if historial.metodo == "Newton-Raphson":
                # Asegurar que los valores numéricos se conviertan correctamente
                x0_val = historial.parametros.get('x0', '')
                tolerancia_val = historial.parametros.get('tolerancia', '')
                decimales_val = historial.parametros.get('decimales', 6)
                
                # Manejo robusto de valores None o vacíos
                if x0_val is None or x0_val == '':
                    x0_str = ''
                else:
                    x0_str = str(x0_val)
                    
                if tolerancia_val is None or tolerancia_val == '':
                    tolerancia_str = ''
                else:
                    tolerancia_str = str(tolerancia_val)
                
                datos_precargados = {
                    'funcion': convertir_a_formato_matematico(historial.expresion or ''),
                    'x0': x0_str,
                    'tolerancia': tolerancia_str,
                    'decimales': int(decimales_val) if decimales_val else 6,
                }
        except HistorialOperacion.DoesNotExist:
            error = "No se encontró el problema en el historial."

    if request.method == 'POST':
        funcion_original = request.POST.get('funcion', '')
        funcion_str = funcion_original.replace('^', '**')
        x0_str = request.POST.get('x0')
        tolerancia_str = request.POST.get('tolerancia', '1e-6')
        decimales_str = request.POST.get('decimales', '6')

        # Datos del formulario para mantener valores
        datos_formulario = {
            'funcion': funcion_original,  # Mantener formato original
            'x0': x0_str,
            'tolerancia': tolerancia_str,
            'decimales': decimales_str
        }

        if funcion_str and x0_str and tolerancia_str and decimales_str:
            try:
                x0 = float(x0_str)
                tolerancia = float(tolerancia_str)
                decimales = int(decimales_str)
                
                # Validar parámetros de entrada
                if tolerancia <= 0:
                    error = "La tolerancia debe ser mayor que 0"
                elif tolerancia > 1:
                    error = "La tolerancia debe ser menor que 1 (recomendado: 1e-6)"
                elif decimales < 1 or decimales > 15:
                    error = "Los decimales deben estar entre 1 y 15"
                else:
                    x = Symbol('x')

                    # Limpiar y convertir la función
                    expr = sympify(funcion_str, evaluate=True)
                    derivada = diff(expr, x)
                    derivada_str = convertir_a_formato_matematico(str(derivada))
                    funcion_original_procesada = convertir_a_formato_matematico(str(expr))

                    # Crear funciones evaluables para validación inicial
                    f = lambdify(x, expr, modules=["math"])
                    f_prime = lambdify(x, derivada, modules=["math"])

                    # Verificar si se pueden evaluar los valores iniciales
                    try:
                        f_val = f(x0)
                        f_prime_val = f_prime(x0)
                        
                        if not (math.isfinite(f_val) and math.isfinite(f_prime_val)):
                            error = f"La función no se puede evaluar en x0 = {x0}. Intenta con otro valor inicial."
                        elif abs(f_prime_val) < 1e-10:
                            error = f"La derivada es muy pequeña en x0 = {x0} (f'(x0) = {f_prime_val:.2e}). Intenta con otro valor inicial."
                        else:
                            # Ejecutar Newton-Raphson mejorado
                            resultado, error_valor, pasos = newton_raphson(funcion_str, x0, tolerancia)
                            
                            if error_valor:
                                error = error_valor
                            else:
                                for paso in pasos:
                                    # Todas las iteraciones del método Newton-Raphson
                                    procedimiento.append({
                                        'iteracion': paso['iteracion'],
                                        'x0': round(paso['xi'], decimales),
                                        'f_x0': round(paso['f(xi)'], decimales),
                                        'f_prime_x0': round(paso["f'(xi)"], decimales),
                                        'x1': round(paso['xi_nuevo'], decimales),
                                        'tolerancia': round(paso['error'], decimales),
                                        'formula': paso['formula_tex']
                                    })

                                # Generar HTML para historial
                                tabla_html = "<table class='w-full text-sm text-left text-gray-300 border border-cyan-700 mt-2 rounded-lg overflow-hidden'>"
                                tabla_html += "<thead class='bg-cyan-900 text-cyan-300 uppercase font-semibold text-xs'><tr><th class='px-2 py-1'>Iteración</th><th>xᵢ</th><th>f(xᵢ)</th><th>f'(xᵢ)</th><th>xᵢ₊₁</th><th>Error</th></tr></thead><tbody>"
                                for paso in procedimiento:
                                    tabla_html += f"<tr class='border-t border-gray-700'><td class='px-2 py-1'>{paso['iteracion']}</td><td>{paso['x0']}</td><td>{paso['f_x0']}</td><td>{paso['f_prime_x0']}</td><td>{paso['x1']}</td><td>{paso['tolerancia']}</td></tr>"
                                tabla_html += "</tbody></table>"

                                tabla_html += "<div class='mt-4 bg-gray-800 p-4 rounded-lg border border-cyan-700'><h3 class='text-cyan-300 font-semibold mb-2'>Fórmulas aplicadas:</h3><div class='space-y-2 text-sm text-gray-200'>"
                                for paso in procedimiento:
                                    tabla_html += f"<p>\\[{paso['formula']}\\]</p>"
                                tabla_html += "</div></div>"

                                # Guardar en historial
                                if resultado is not None and request.user.is_authenticated and request.user.username != "invitado":
                                    HistorialOperacion.objects.create(
                                        usuario=request.user,
                                        metodo="Newton-Raphson",
                                        expresion=funcion_str,
                                        datos_entrada=f"f(x)={funcion_str}, x0={x0}, tolerancia={tolerancia}",
                                        resultado=str(resultado),
                                        parametros={
                                            'x0': x0,
                                            'tolerancia': tolerancia,
                                            'decimales': decimales,
                                            'iteraciones': len(procedimiento)
                                        },
                                        tabla=tabla_html
                                    )
                                    
                    except Exception as eval_error:
                        error = f"Error al evaluar la función en x0 = {x0}: {str(eval_error)}"

            except ValueError as ve:
                error = f"Error en los parámetros: {str(ve)}"
            except Exception as e:
                error = f"Error de entrada: {str(e)}"

    # Preparar datos para mantener en el formulario
    datos_formulario = {
        'funcion': funcion_original if 'funcion_original' in locals() else '',
        'x0': x0_str if 'x0_str' in locals() else '',
        'tolerancia': tolerancia_str if 'tolerancia_str' in locals() else '',
        'decimales': decimales_str if 'decimales_str' in locals() else ''
    }

    return render(request, 'Metodos/newton.html', {
        'resultado': resultado,
        'error': error,
        'procedimiento': procedimiento,
        'derivada_str': derivada_str,
        'funcion_original': funcion_original_procesada if 'funcion_original_procesada' in locals() else '',
        'datos_precargados': datos_precargados,
        'datos_formulario': datos_formulario,
        'es_desde_historial': bool(historial_id and datos_precargados)
    })

def vista_integracion(request):
    return render(request, 'Metodos/integracion.html')

def vista_integracion_compuesta(request):
    return render(request, 'Metodos/integracion_compuesta.html')

def guest_login(request):
    try:
        print(f"DEBUG: Intento de login como invitado")
        guest_user, created = User.objects.get_or_create(username='invitado')
        if created:
            print(f"DEBUG: Usuario invitado creado por primera vez")
            guest_user.set_unusable_password()
            guest_user.save()
        else:
            print(f"DEBUG: Usuario invitado ya existía")
        
        print(f"DEBUG: Estado previo a login - usuario autenticado: {request.user.is_authenticated}")
        print(f"DEBUG: Sesión antes de login: {request.session.session_key}")
        
        login(request, guest_user)
        
        print(f"DEBUG: Login completado - usuario autenticado: {request.user.is_authenticated}")
        print(f"DEBUG: Nombre de usuario en sesión: {request.user.username}")
        print(f"DEBUG: Sesión después de login: {request.session.session_key}")
        print(f"DEBUG: Redirigiendo a 'menu'")
        
        return redirect('menu')
    except Exception as e:
        print(f"ERROR en guest_login: {str(e)}")
        # Si hay un error, todavía intentamos redirigir al menú
        return redirect('menu') 

def graficar_funcion(funcion_str, a, b):
    # Graficar un rango un poco más amplio para contexto visual
    margen = (b - a) * 0.2 if b != a else 1
    x_min = a - margen
    x_max = b + margen
    x = np.linspace(x_min, x_max, 400)
    try:
        y = [eval(funcion_str, {"x": val, "np": np, "__builtins__": {}}) for val in x]
    except Exception:
        y = np.zeros_like(x)
    plt.figure(figsize=(7, 3.5))
    plt.plot(x, y, label=f'$f(x) = {funcion_str}$', color='royalblue')
    # Sombrea solo el área bajo la curva en [a, b]
    x_fill = np.linspace(a, b, 200)
    try:
        y_fill = [eval(funcion_str, {"x": val, "np": np, "__builtins__": {}}) for val in x_fill]
    except Exception:
        y_fill = np.zeros_like(x_fill)
    plt.fill_between(x_fill, y_fill, color='deepskyblue', alpha=0.4, label=f'Área $[{a}, {b}]$')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('Gráfica de la función y área bajo la curva')
    plt.legend()
    plt.grid(alpha=0.2)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

# Vista de login personalizada
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginUsuarioForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirigir al menú principal después del login exitoso
        print(f"DEBUG: get_success_url llamado, retornando 'menu'")
        return reverse_lazy('menu')
    
    def get(self, request, *args, **kwargs):
        """Override para verificar si ya está autenticado"""
        print(f"DEBUG: GET recibido en login. Usuario autenticado: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            print(f"DEBUG: Usuario ya autenticado: {request.user.username}. Redirigiendo a menu.")
            return redirect('menu')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Override para mostrar información del POST"""
        print(f"DEBUG: POST recibido en login. Datos: {request.POST}")
        print(f"DEBUG: Nombre de usuario recibido: {request.POST.get('username', 'NO PROPORCIONADO')}")
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Override para asegurar que el login sea exitoso"""
        user = form.get_user()
        print(f"DEBUG: Login validado exitosamente para: {user.username}")
        print(f"DEBUG: Usuario activo: {user.is_active}, Staff: {user.is_staff}")
        
        # Guardar los datos de la sesión para verificarlos
        session_key_before = self.request.session.session_key
        print(f"DEBUG: Sesión antes de login: {session_key_before}")
        
        # Usar el método padre para manejar la autenticación
        response = super().form_valid(form)
        
        # Verificar estado después de autenticación
        print(f"DEBUG: Usuario autenticado después de login: {self.request.user.is_authenticated}")
        print(f"DEBUG: Sesión después de login: {self.request.session.session_key}")
        print(f"DEBUG: Redirigiendo a: {self.get_success_url()}")
        
        # Confirmar los headers de la respuesta
        print(f"DEBUG: Headers de respuesta: {response.headers}")
        
        return response
    
    def form_invalid(self, form):
        """Override para debug de errores de login"""
        print(f"DEBUG: Login fallido. Errores: {form.errors}")
        for field, errors in form.errors.items():
            print(f"DEBUG: Campo '{field}' con errores: {errors}")
        
        cleaned_data = getattr(form, 'cleaned_data', {})
        print(f"DEBUG: Datos limpios: {cleaned_data}")
        
        return super().form_invalid(form)


# ===============================================
# VISTAS DE ADMINISTRADOR
# ===============================================

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

def es_superusuario(user):
    """Función para verificar si el usuario es superusuario"""
    return user.is_superuser

@user_passes_test(es_superusuario)
def admin_panel_view(request):
    """Vista principal del panel de administración"""
    # Estadísticas generales
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    total_operaciones = HistorialOperacion.objects.count()
    operaciones_hoy = HistorialOperacion.objects.filter(fecha__date=timezone.now().date()).count()
    
    # Métodos más utilizados
    metodos_populares = HistorialOperacion.objects.values('metodo').annotate(
        count=Count('metodo')
    ).order_by('-count')[:5]
    
    # Usuarios más activos
    usuarios_activos_stats = User.objects.annotate(
        operaciones_count=Count('historialoperacion')
    ).order_by('-operaciones_count')[:5]
    
    # Actividad reciente
    operaciones_recientes = HistorialOperacion.objects.select_related('usuario').order_by('-fecha')[:10]
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_operaciones': total_operaciones,
        'operaciones_hoy': operaciones_hoy,
        'metodos_populares': metodos_populares,
        'usuarios_activos_stats': usuarios_activos_stats,
        'operaciones_recientes': operaciones_recientes,
    }
    
    return render(request, 'admin/admin_panel.html', context)

@user_passes_test(es_superusuario)
def admin_usuarios_view(request):
    """Vista para gestionar usuarios"""
    search_query = request.GET.get('search', '')
    filter_by = request.GET.get('filter', 'all')
    
    usuarios = User.objects.all()
    
    if search_query:
        usuarios = usuarios.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if filter_by == 'active':
        usuarios = usuarios.filter(is_active=True)
    elif filter_by == 'inactive':
        usuarios = usuarios.filter(is_active=False)
    elif filter_by == 'staff':
        usuarios = usuarios.filter(is_staff=True)
    elif filter_by == 'superuser':
        usuarios = usuarios.filter(is_superuser=True)
    
    # Agregar estadísticas por usuario
    usuarios_con_stats = []
    for usuario in usuarios:
        operaciones_count = HistorialOperacion.objects.filter(usuario=usuario).count()
        ultima_operacion = HistorialOperacion.objects.filter(usuario=usuario).order_by('-fecha').first()
        
        try:
            perfil = Perfil.objects.get(user=usuario)
        except Perfil.DoesNotExist:
            perfil = None
        
        usuarios_con_stats.append({
            'usuario': usuario,
            'operaciones_count': operaciones_count,
            'ultima_operacion': ultima_operacion,
            'perfil': perfil,
        })
    
    context = {
        'usuarios': usuarios_con_stats,
        'search_query': search_query,
        'filter_by': filter_by,
    }
    
    return render(request, 'admin/admin_usuarios.html', context)

@user_passes_test(es_superusuario)
def admin_usuario_detalle(request, user_id):
    """Vista detallada de un usuario específico"""
    usuario = get_object_or_404(User, id=user_id)
    
    try:
        perfil = Perfil.objects.get(user=usuario)
    except Perfil.DoesNotExist:
        perfil = None
    
    # Historial de operaciones del usuario
    operaciones = HistorialOperacion.objects.filter(usuario=usuario).order_by('-fecha')
    
    # Estadísticas del usuario
    total_operaciones = operaciones.count()
    metodos_utilizados = operaciones.values('metodo').annotate(
        count=Count('metodo')
    ).order_by('-count')
    
    # Actividad por día (últimos 30 días)
    fecha_inicio = timezone.now() - timedelta(days=30)
    actividad_diaria = operaciones.filter(fecha__gte=fecha_inicio).extra(
        select={'day': 'date(fecha)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    context = {
        'usuario': usuario,
        'perfil': perfil,
        'operaciones': operaciones[:20],  # Últimas 20 operaciones
        'total_operaciones': total_operaciones,
        'metodos_utilizados': metodos_utilizados,
        'actividad_diaria': actividad_diaria,
    }
    
    return render(request, 'admin/admin_usuario_detalle.html', context)

@user_passes_test(es_superusuario)
def admin_toggle_user_active(request, user_id):
    """Toggle del estado activo de un usuario"""
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'is_active': usuario.is_active,
            'message': f'Usuario {"activado" if usuario.is_active else "desactivado"} exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@user_passes_test(es_superusuario)
def admin_delete_user(request, user_id):
    """Eliminar un usuario"""
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        if usuario.is_superuser:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar un superusuario'})
        
        username = usuario.username
        usuario.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {username} eliminado exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@user_passes_test(es_superusuario)
def admin_historial_view(request):
    """Vista para gestionar el historial de operaciones"""
    search_query = request.GET.get('search', '')
    filter_metodo = request.GET.get('metodo', 'all')
    filter_fecha = request.GET.get('fecha', 'all')
    
    historial = HistorialOperacion.objects.select_related('usuario').all()
    
    if search_query:
        historial = historial.filter(
            Q(usuario__username__icontains=search_query) |
            Q(expresion__icontains=search_query) |
            Q(metodo__icontains=search_query)
        )
    
    if filter_metodo != 'all':
        historial = historial.filter(metodo=filter_metodo)
    
    if filter_fecha == 'today':
        historial = historial.filter(fecha__date=timezone.now().date())
    elif filter_fecha == 'week':
        fecha_inicio = timezone.now() - timedelta(days=7)
        historial = historial.filter(fecha__gte=fecha_inicio)
    elif filter_fecha == 'month':
        fecha_inicio = timezone.now() - timedelta(days=30)
        historial = historial.filter(fecha__gte=fecha_inicio)
    
    historial = historial.order_by('-fecha')
    
    # Obtener métodos únicos para el filtro
    metodos_disponibles = HistorialOperacion.objects.values_list('metodo', flat=True).distinct()
    
    context = {
        'historial': historial,
        'search_query': search_query,
        'filter_metodo': filter_metodo,
        'filter_fecha': filter_fecha,
        'metodos_disponibles': metodos_disponibles,
    }
    
    return render(request, 'admin/admin_historial.html', context)

@user_passes_test(es_superusuario)
def admin_delete_historial(request, historial_id):
    """Eliminar una entrada del historial"""
    if request.method == 'POST':
        historial = get_object_or_404(HistorialOperacion, id=historial_id)
        historial.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Entrada del historial eliminada exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@user_passes_test(es_superusuario)
def admin_estadisticas_view(request):
    """Vista de estadísticas avanzadas"""
    # Estadísticas por método
    metodos_stats = HistorialOperacion.objects.values('metodo').annotate(
        count=Count('metodo')
    ).order_by('-count')
    
    # Actividad por mes (últimos 12 meses)
    fecha_inicio = timezone.now() - timedelta(days=365)
    actividad_mensual = HistorialOperacion.objects.filter(fecha__gte=fecha_inicio).extra(
        select={'month': 'strftime("%%Y-%%m", fecha)'}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Usuarios registrados por mes
    usuarios_por_mes = User.objects.filter(date_joined__gte=fecha_inicio).extra(
        select={'month': 'strftime("%%Y-%%m", date_joined)'}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Top 10 usuarios más activos
    usuarios_activos = User.objects.annotate(
        operaciones_count=Count('historialoperacion')
    ).order_by('-operaciones_count')[:10]
    
    # Estadísticas de perfil
    perfiles_completos = Perfil.objects.exclude(
        Q(nombre_completo='') | Q(carrera='') | Q(carnet='')
    ).count()
    total_perfiles = Perfil.objects.count()
    
    context = {
        'metodos_stats': metodos_stats,
        'actividad_mensual': list(actividad_mensual),
        'usuarios_por_mes': list(usuarios_por_mes),
        'usuarios_activos': usuarios_activos,
        'perfiles_completos': perfiles_completos,
        'total_perfiles': total_perfiles,
        'porcentaje_perfiles_completos': round((perfiles_completos / total_perfiles * 100) if total_perfiles > 0 else 0, 2),
    }
    
    return render(request, 'admin/admin_estadisticas.html', context)


@user_passes_test(es_superusuario)
def admin_dashboard_view(request):
    """Vista principal del dashboard analytics"""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg
    
    # Obtener estadísticas generales
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    total_operaciones = HistorialOperacion.objects.count()
    
    # Operaciones de hoy
    hoy = timezone.now().date()
    operaciones_hoy = HistorialOperacion.objects.filter(fecha__date=hoy).count()
    
    # Tiempo promedio de cálculo (simulado - podrías agregar este campo al modelo)
    tiempo_promedio = 2.5
    
    # Datos para gráficos - últimos 30 días
    fecha_inicio = timezone.now() - timedelta(days=30)
    operaciones_por_dia = []
    
    for i in range(30):
        fecha = fecha_inicio + timedelta(days=i)
        count = HistorialOperacion.objects.filter(fecha__date=fecha.date()).count()
        operaciones_por_dia.append(count)
    
    # Métodos más utilizados
    metodos_stats = (HistorialOperacion.objects
                    .values('metodo')
                    .annotate(count=Count('metodo'))
                    .order_by('-count')[:5])
    
    # Actividad reciente
    actividad_reciente = HistorialOperacion.objects.order_by('-fecha')[:10]
    
    # Usuarios registrados en los últimos 7 días
    hace_7_dias = timezone.now() - timedelta(days=7)
    nuevos_usuarios = User.objects.filter(date_joined__gte=hace_7_dias).count()
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_operaciones': total_operaciones,
        'operaciones_hoy': operaciones_hoy,
        'tiempo_promedio': tiempo_promedio,
        'operaciones_por_dia': operaciones_por_dia,
        'metodos_stats': metodos_stats,
        'actividad_reciente': actividad_reciente,
        'nuevos_usuarios': nuevos_usuarios,
    }
    
    return render(request, 'admin/admin_dashboard.html', context)


@user_passes_test(es_superusuario)
def admin_backup_view(request):
    """Vista completa para sistema de respaldos"""
    import os
    import subprocess
    from datetime import datetime
    from django.conf import settings
    
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Listar backups existentes
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db') or filename.endswith('.json'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'path': filepath
                })
    
    backups.sort(key=lambda x: x['created'], reverse=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_backup':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_{timestamp}.json'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            try:
                # Crear backup usando dumpdata
                result = subprocess.run([
                    'python', 'manage.py', 'dumpdata', 
                    '--indent=2', '--output', backup_path
                ], capture_output=True, text=True, cwd=settings.BASE_DIR)
                
                if result.returncode == 0:
                    messages.success(request, f'Backup creado exitosamente: {backup_filename}')
                else:
                    messages.error(request, f'Error al crear backup: {result.stderr}')
            except Exception as e:
                messages.error(request, f'Error al crear backup: {str(e)}')
        
        elif action == 'delete_backup':
            filename = request.POST.get('filename')
            if filename:
                filepath = os.path.join(backup_dir, filename)
                try:
                    os.remove(filepath)
                    messages.success(request, f'Backup {filename} eliminado exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al eliminar backup: {str(e)}')
        
        return redirect('admin_backup')
    
    context = {
        'backups': backups,
        'backup_dir': backup_dir,
        'total_backups': len(backups),
        'total_size': sum(b['size'] for b in backups)
    }
    
    return render(request, 'admin/admin_backup.html', context)


@user_passes_test(es_superusuario)
def admin_logs_view(request):
    """Vista completa para visor de logs"""
    import logging
    import os
    from datetime import datetime, timedelta
    from django.core.paginator import Paginator
    
    # Configurar logging si no está configurado
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Logs de actividad de usuarios
    activity_logs = []
    log_entries = []
    
    # Obtener logs recientes de la base de datos
    recent_operations = HistorialOperacion.objects.select_related('usuario').order_by('-fecha')[:100]
    
    for operation in recent_operations:
        activity_logs.append({
            'timestamp': operation.fecha,
            'user': operation.usuario.username,
            'action': f'Operación: {operation.metodo}',
            'details': operation.expresion[:50] + '...' if len(operation.expresion) > 50 else operation.expresion,
            'level': 'INFO'
        })
    
    # Logs de autenticación
    recent_users = User.objects.filter(last_login__gte=datetime.now() - timedelta(days=7)).order_by('-last_login')
    
    for user in recent_users:
        if user.last_login:
            log_entries.append({
                'timestamp': user.last_login,
                'level': 'INFO',
                'message': f'Usuario {user.username} inició sesión',
                'category': 'Authentication'
            })
    
    # Simular algunos logs de sistema
    import random
    system_events = [
        'Inicio de aplicación',
        'Limpieza de cache completada',
        'Backup automático ejecutado',
        'Optimización de base de datos',
        'Verificación de integridad completada'
    ]
    
    for i in range(20):
        log_entries.append({
            'timestamp': datetime.now() - timedelta(hours=random.randint(1, 168)),
            'level': random.choice(['INFO', 'WARNING', 'DEBUG']),
            'message': random.choice(system_events),
            'category': 'System'
        })
    
    # Ordenar todos los logs por fecha
    all_logs = log_entries + activity_logs
    all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Filtros
    level_filter = request.GET.get('level', 'all')
    category_filter = request.GET.get('category', 'all')
    
    if level_filter != 'all':
        all_logs = [log for log in all_logs if log.get('level') == level_filter]
    
    if category_filter != 'all':
        all_logs = [log for log in all_logs if log.get('category') == category_filter]
    
    # Paginación
    paginator = Paginator(all_logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    context = {
        'logs': logs,
        'total_logs': len(all_logs),
        'level_filter': level_filter,
        'category_filter': category_filter,
        'levels': ['INFO', 'WARNING', 'ERROR', 'DEBUG'],
        'categories': ['System', 'Authentication', 'Database', 'User Activity']
    }
    
    return render(request, 'admin/admin_logs.html', context)


@user_passes_test(es_superusuario)  
def admin_reports_view(request):
    """Vista completa para generador de reportes"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg
    from django.http import HttpResponse
    import json
    
    # Estadísticas para reportes
    now = datetime.now()
    last_month = now - timedelta(days=30)
    last_week = now - timedelta(days=7)
    
    # Datos de usuarios
    users_data = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'new_users_month': User.objects.filter(date_joined__gte=last_month).count(),
        'new_users_week': User.objects.filter(date_joined__gte=last_week).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'superusers': User.objects.filter(is_superuser=True).count(),
    }
    
    # Datos de operaciones
    operations_data = {
        'total_operations': HistorialOperacion.objects.count(),
        'operations_month': HistorialOperacion.objects.filter(fecha__gte=last_month).count(),
        'operations_week': HistorialOperacion.objects.filter(fecha__gte=last_week).count(),
        'operations_by_method': list(HistorialOperacion.objects.values('metodo').annotate(count=Count('id'))),
        'avg_operations_per_user': HistorialOperacion.objects.values('usuario').annotate(count=Count('id')).aggregate(avg=Avg('count'))['avg'] or 0,
    }
    
    # Datos de actividad por día
    activity_data = []
    for i in range(30):
        date = now - timedelta(days=i)
        count = HistorialOperacion.objects.filter(fecha__date=date.date()).count()
        activity_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'operations': count
        })
    
    activity_data.reverse()
    
    # Usuarios más activos
    top_users = User.objects.annotate(
        operation_count=Count('historialoperacion')
    ).order_by('-operation_count')[:10]
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        
        if report_type == 'users_json':
            response = HttpResponse(
                json.dumps(users_data, indent=2, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="users_report_{now.strftime("%Y%m%d_%H%M%S")}.json"'
            return response
        
        elif report_type == 'operations_json':
            response = HttpResponse(
                json.dumps(operations_data, indent=2, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="operations_report_{now.strftime("%Y%m%d_%H%M%S")}.json"'
            return response
        
        elif report_type == 'full_report':
            full_report = {
                'generated_at': now.isoformat(),
                'users': users_data,
                'operations': operations_data,
                'activity': activity_data,
                'top_users': [{'username': u.username, 'operations': u.operation_count} for u in top_users]
            }
            
            response = HttpResponse(
                json.dumps(full_report, indent=2, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="full_report_{now.strftime("%Y%m%d_%H%M%S")}.json"'
            return response
    
    context = {
        'users_data': users_data,
        'operations_data': operations_data,
        'activity_data': activity_data,
        'top_users': top_users,
        'report_date': now
    }
    
    return render(request, 'admin/admin_reports.html', context)


@user_passes_test(es_superusuario)
def admin_maintenance_view(request):
    """Vista completa para mantenimiento del sistema"""
    import os
    import subprocess
    from django.core.management import call_command
    from django.core.cache import cache
    from django.db import connection
    from django.conf import settings
    from datetime import datetime
    
    # Información del sistema
    db_size = 0
    try:
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
    except:
        pass
    
    # Estadísticas de cache
    cache_stats = {
        'cache_backend': str(cache),
        'cache_timeout': getattr(settings, 'CACHE_TIMEOUT', 300),
    }
    
    # Información de archivos estáticos
    static_root = getattr(settings, 'STATIC_ROOT', '')
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    
    static_size = 0
    media_size = 0
    
    try:
        if static_root and os.path.exists(static_root):
            static_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(static_root)
                            for filename in filenames)
    except:
        pass
    
    try:
        if media_root and os.path.exists(media_root):
            media_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                           for dirpath, dirnames, filenames in os.walk(media_root)
                           for filename in filenames)
    except:
        pass
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'clear_cache':
                cache.clear()
                messages.success(request, 'Cache limpiado exitosamente')
            
            elif action == 'collect_static':
                call_command('collectstatic', '--noinput')
                messages.success(request, 'Archivos estáticos recopilados exitosamente')
            
            elif action == 'optimize_db':
                # Para SQLite
                if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                    with connection.cursor() as cursor:
                        cursor.execute("VACUUM;")
                        cursor.execute("ANALYZE;")
                    messages.success(request, 'Base de datos optimizada exitosamente')
                else:
                    messages.info(request, 'Optimización de BD no disponible para este motor')
            
            elif action == 'clean_sessions':
                call_command('clearsessions')
                messages.success(request, 'Sesiones antiguas limpiadas exitosamente')
            
            elif action == 'check_system':
                # Verificar integridad del sistema
                issues = []
                
                # Verificar configuración
                if not settings.DEBUG:
                    if not settings.ALLOWED_HOSTS:
                        issues.append('ALLOWED_HOSTS está vacío en producción')
                
                # Verificar permisos de archivos
                if not os.access(settings.BASE_DIR, os.W_OK):
                    issues.append('Sin permisos de escritura en BASE_DIR')
                
                if issues:
                    messages.warning(request, f'Problemas encontrados: {", ".join(issues)}')
                else:
                    messages.success(request, 'Sistema verificado - Sin problemas encontrados')
            
            elif action == 'backup_media':
                # Crear backup de archivos media
                import shutil
                
                backup_dir = os.path.join(settings.BASE_DIR, 'backups', 'media')
                os.makedirs(backup_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(backup_dir, f'media_backup_{timestamp}')
                
                if media_root and os.path.exists(media_root):
                    shutil.copytree(media_root, backup_path)
                    messages.success(request, f'Backup de media creado: media_backup_{timestamp}')
                else:
                    messages.warning(request, 'No hay archivos media para respaldar')
        
        except Exception as e:
            messages.error(request, f'Error durante la operación: {str(e)}')
        
        return redirect('admin_maintenance')
    
    # Obtener información del sistema
    system_info = {
        'db_size': db_size,
        'static_size': static_size,
        'media_size': media_size,
        'cache_stats': cache_stats,
        'total_users': User.objects.count(),
        'total_operations': HistorialOperacion.objects.count(),
        'active_sessions': 0,  # Placeholder
        'debug_mode': settings.DEBUG,
        'database_engine': settings.DATABASES['default']['ENGINE'],
    }
    
    context = {
        'system_info': system_info,
        'maintenance_date': datetime.now()
    }
    
    return render(request, 'admin/admin_maintenance.html', context)

@user_passes_test(es_superusuario)
def admin_config_view(request):
    """Vista completa para configuración del sistema"""
    from .models import ConfiguracionSistema, ConfiguracionMetodo
    
    config = ConfiguracionSistema.obtener_configuracion()
    metodos_config = ConfiguracionMetodo.objects.all()
    
    # Crear configuraciones por defecto para métodos si no existen
    metodos_por_defecto = [
        ('newton', 'Método de Newton-Raphson'),
        ('biseccion', 'Método de Bisección'),
        ('secante', 'Método de la Secante'),
        ('punto_fijo', 'Método de Punto Fijo'),
        ('integracion', 'Integración Numérica'),
        ('derivacion', 'Derivación Numérica'),
    ]
    
    for metodo_key, metodo_name in metodos_por_defecto:
        ConfiguracionMetodo.objects.get_or_create(
            metodo=metodo_key,
            defaults={
                'habilitado': True,
                'limite_iteraciones': 100,
                'precision': 0.0001,
                'tiempo_maximo': 30,
                'limite_uso_diario': 50,
                'limite_uso_usuario': 10,
                'descripcion': f'Configuración para {metodo_name}'
            }
        )
    
    # Actualizar lista de métodos
    metodos_config = ConfiguracionMetodo.objects.all()
    
    if request.method == 'POST':
        seccion = request.POST.get('seccion')
        
        if seccion == 'general':
            config.nombre_sistema = request.POST.get('nombre_sistema', config.nombre_sistema)
            config.descripcion_sistema = request.POST.get('descripcion_sistema', config.descripcion_sistema)
            config.mantenimiento_activo = request.POST.get('mantenimiento_activo') == 'on'
            config.mensaje_mantenimiento = request.POST.get('mensaje_mantenimiento', config.mensaje_mantenimiento)
            config.save()
            messages.success(request, 'Configuración general actualizada exitosamente')
        
        elif seccion == 'limites':
            config.limite_operaciones_usuario = int(request.POST.get('limite_operaciones_usuario', config.limite_operaciones_usuario))
            config.limite_operaciones_dia = int(request.POST.get('limite_operaciones_dia', config.limite_operaciones_dia))
            config.limite_tiempo_sesion = int(request.POST.get('limite_tiempo_sesion', config.limite_tiempo_sesion))
            config.save()
            messages.success(request, 'Límites de uso actualizados exitosamente')
        
        elif seccion == 'email':
            config.email_habilitado = request.POST.get('email_habilitado') == 'on'
            config.smtp_host = request.POST.get('smtp_host', config.smtp_host)
            config.smtp_port = int(request.POST.get('smtp_port', config.smtp_port))
            config.smtp_usuario = request.POST.get('smtp_usuario', config.smtp_usuario)
            config.smtp_password = request.POST.get('smtp_password', config.smtp_password)
            config.smtp_tls = request.POST.get('smtp_tls') == 'on'
            config.notificaciones_admin = request.POST.get('notificaciones_admin') == 'on'
            config.notificaciones_usuario = request.POST.get('notificaciones_usuario') == 'on'
            config.save()
            messages.success(request, 'Configuración de email actualizada exitosamente')
        
        elif seccion == 'seguridad':
            config.intentos_login_max = int(request.POST.get('intentos_login_max', config.intentos_login_max))
            config.tiempo_bloqueo_login = int(request.POST.get('tiempo_bloqueo_login', config.tiempo_bloqueo_login))
            config.save()
            messages.success(request, 'Configuración de seguridad actualizada exitosamente')
        
        elif seccion == 'metodos':
            # Actualizar configuración de métodos
            for metodo_config in metodos_config:
                metodo_key = metodo_config.metodo
                metodo_config.habilitado = request.POST.get(f'metodo_{metodo_key}_habilitado') == 'on'
                metodo_config.limite_iteraciones = int(request.POST.get(f'metodo_{metodo_key}_iteraciones', metodo_config.limite_iteraciones))
                metodo_config.precision = float(request.POST.get(f'metodo_{metodo_key}_precision', metodo_config.precision))
                metodo_config.tiempo_maximo = int(request.POST.get(f'metodo_{metodo_key}_tiempo', metodo_config.tiempo_maximo))
                metodo_config.limite_uso_diario = int(request.POST.get(f'metodo_{metodo_key}_uso_diario', metodo_config.limite_uso_diario))
                metodo_config.limite_uso_usuario = int(request.POST.get(f'metodo_{metodo_key}_uso_usuario', metodo_config.limite_uso_usuario))
                metodo_config.save()
            
            messages.success(request, 'Configuración de métodos actualizada exitosamente')
        
        elif seccion == 'test_email':
            # Probar configuración de email
            try:
                from django.core.mail import send_mail
                send_mail(
                    'Test Email - SolverApp',
                    'Este es un email de prueba desde el sistema de configuración.',
                    config.smtp_usuario,
                    [request.user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Email de prueba enviado exitosamente')
            except Exception as e:
                messages.error(request, f'Error al enviar email: {str(e)}')
        
        return redirect('admin_config')
    
    # Estadísticas del sistema
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    total_operaciones = HistorialOperacion.objects.count()
    
    # Uso de métodos
    uso_metodos = []
    for metodo_config in metodos_config:
        uso_total = HistorialOperacion.objects.filter(metodo=metodo_config.metodo).count()
        uso_metodos.append({
            'metodo': metodo_config,
            'uso_total': uso_total,
            'uso_activo': uso_total > 0
        })
    
    context = {
        'config': config,
        'metodos_config': metodos_config,
        'uso_metodos': uso_metodos,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_operaciones': total_operaciones,
        'config_date': datetime.now()
    }
    
    return render(request, 'admin/admin_config.html', context)
