from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
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
    pasos = []
    h = (b - a) / n
    suma = funcion(a) + funcion(b)
    pasos.append(f"h = (b - a) / n = ({b} - {a}) / {n} = {h}")
    pasos.append(f"f({a}) = {funcion(a):.6f}")
    pasos.append(f"f({b}) = {funcion(b):.6f}")

    for i in range(1, n):
        xi = a + i*h
        fx = funcion(xi)
        suma += 2 * fx
        pasos.append(f"f({xi:.6f})*2 = {fx:.6f}*2 = {2*fx:.6f}")

    integral = (h / 2) * suma
    pasos.append(f"Integral ≈ (h / 2) * suma = ({h}/2) * {suma:.6f} = {integral:.6f}")
    return integral, pasos

# --------------------------
# MÉTODO DE SIMPSON 1/3
def metodoSimpson1(funcion, a, b, n):
    pasos = []

    if n % 2 != 0:
        return None, ["El método de Simpson 1/3 requiere que n sea par."]

    h = (b - a) / n
    suma = funcion(a) + funcion(b)
    pasos.append(f"h = (b - a) / n = ({b} - {a}) / {n} = {h}")
    pasos.append(f"f({a}) = {funcion(a):.6f}")
    pasos.append(f"f({b}) = {funcion(b):.6f}")

    for i in range(1, n):
        xi = a + i * h
        fx = funcion(xi)
        factor = 4 if i % 2 != 0 else 2
        suma += factor * fx
        pasos.append(f"{factor} * f({xi:.6f}) = {factor} * {fx:.6f} = {factor*fx:.6f}")

    integral = (h / 3) * suma
    pasos.append(f"Integral ≈ (h / 3) * suma = ({h}/3) * {suma:.6f} = {integral:.6f}")
    return integral, pasos

# --------------------------
# MÉTODO DE SIMPSON 3/8
def metodoSimpson2(funcion, a, b, n):
    pasos = []

    if n % 3 != 0:
        return None, ["El método de Simpson 3/8 requiere que n sea múltiplo de 3."]

    h = (b - a) / n
    suma = funcion(a) + funcion(b)
    pasos.append(f"h = (b - a) / n = ({b} - {a}) / {n} = {h}")
    pasos.append(f"f({a}) = {funcion(a):.6f}")
    pasos.append(f"f({b}) = {funcion(b):.6f}")

    for i in range(1, n):
        xi = a + i * h
        fx = funcion(xi)
        factor = 3 if i % 3 != 0 else 2
        suma += factor * fx
        pasos.append(f"{factor} * f({xi:.6f}) = {factor} * {fx:.6f} = {factor*fx:.6f}")

    integral = (3 * h / 8) * suma
    pasos.append(f"Integral ≈ (3h / 8) * suma = (3*{h}/8) * {suma:.6f} = {integral:.6f}")
    return integral, pasos

# --------------------------
# VISTA PRINCIPAL

@login_required
def integracion_view(request, historial_id=None):
    resultadoIntegral = None
    procedimiento = None
    error = None
    grafica = None
    funcion = None
    a = None
    b = None
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
        funcion = request.POST.get('funcion')
        metodo = int(request.POST.get("metodos_integracion", 0))
        limite_izquierdo = request.POST.get("input_limiteIzquierdo")
        limite_derecho = request.POST.get("input_limiteDerecho")
        intervalos = request.POST.get("input_intervalos")

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
                                    pasos="\n".join(procedimiento),
                                    tabla=tabla_html,
                                    expresion=funcion,
                                    grafica=grafica  
                                )

            except Exception as exc:
                error = f"Error en los datos ingresados: {str(exc)}"

    return render(request, 'Metodos/integracion.html', {
        'resultadoIntegral': resultadoIntegral,
        'procedimiento': procedimiento,
        'error': error,
        'grafica': grafica,
        'datos_precargados': datos_precargados
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
                    'funcion': historial.expresion or '',
                    'x0': x0_str,
                    'tolerancia': tolerancia_str,
                    'decimales': int(decimales_val) if decimales_val else 6,
                }
        except HistorialOperacion.DoesNotExist:
            error = "No se encontró el problema en el historial."

    if request.method == 'POST':
        funcion_str = request.POST.get('funcion', '').replace('^', '**')
        x0_str = request.POST.get('x0')
        tolerancia_str = request.POST.get('tolerancia')
        decimales_str = request.POST.get('decimales')

        if funcion_str and x0_str and tolerancia_str and decimales_str:
            try:
                x0 = float(x0_str)
                tolerancia = float(tolerancia_str)
                decimales = int(decimales_str)

                x = Symbol('x')

                # Limpiar y convertir la función
                expr = sympify(funcion_str, evaluate=True)
                derivada = diff(expr, x)
                derivada_str = str(derivada)
                funcion_original = str(expr)

                # Crear funciones evaluables
                f = lambdify(x, expr, modules=["math"])
                f_prime = lambdify(x, derivada, modules=["math"])

                # Verificar si se pueden evaluar los valores iniciales
                try:
                    f_val = f(x0)
                    f_prime_val = f_prime(x0)
                    float(f_val), float(f_prime_val)
                except Exception as eval_error:
                    raise ValueError("Error al evaluar funciones: " + str(eval_error))

                # Ejecutar Newton-Raphson
                resultado, error_valor, pasos = newton_raphson(funcion_str, x0, tolerancia)

                for paso in pasos:
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
                tabla_html += "<thead class='bg-cyan-900 text-cyan-300 uppercase font-semibold text-xs'><tr><th class='px-2 py-1'>Iteración</th><th>x₀</th><th>f(x₀)</th><th>f'(x₀)</th><th>x₁</th><th>Error</th></tr></thead><tbody>"
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

            except Exception as e:
                error = f"Error de entrada: {str(e)}"

    return render(request, 'Metodos/newton.html', {
        'resultado': resultado,
        'error': error,
        'procedimiento': procedimiento,
        'derivada_str': derivada_str,
        'funcion_original': funcion_original,
        'datos_precargados': datos_precargados
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
