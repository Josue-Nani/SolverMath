# SolverMath - Métodos Numéricos

🧮 **SolverMath** es una aplicación web avanzada desarrollada en Django para resolver problemas de métodos numéricos de manera intuitiva y eficiente.

## ✨ Características Principales

### 🔍 **Método Newton-Raphson**
- Encuentra raíces de funciones matemáticas
- Visualización gráfica interactiva
- Análisis paso a paso del procedimiento
- Configuración personalizable de parámetros

### ∫ **Integración Numérica**
- Métodos del Trapecio y Simpson
- Cálculo de áreas bajo curvas
- Integración compuesta
- Visualización de resultados

### 👤 **Sistema de Usuarios**
- Registro y autenticación completa
- Perfiles personalizables con foto
- Historial completo de cálculos
- Funcionalidad de recarga de problemas anteriores

### 📊 **Características Avanzadas**
- Interfaz moderna con Tailwind CSS + DaisyUI
- Renderizado matemático con MathJax
- Gráficas interactivas con Matplotlib
- Exportación de resultados
- Responsive design

## 🚀 Tecnologías Utilizadas

- **Backend**: Django 5.2.2
- **Base de Datos**: SQLite (desarrollo) / MySQL (producción)
- **Frontend**: HTML5, Tailwind CSS, DaisyUI
- **Matemáticas**: SymPy, NumPy, Matplotlib
- **Renderizado**: MathJax, MathLive
- **Animaciones**: AOS (Animate On Scroll)

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Josue-Nani/SolverMath.git
cd SolverMath
```

### 2. Crear entorno virtual
```bash
python -m venv swag
# Windows
swag\\Scripts\\activate
# Linux/Mac
source swag/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

Visita `http://127.0.0.1:8000` en tu navegador.

## 🔧 Configuración

### Base de Datos
El proyecto está configurado para usar SQLite en desarrollo. Para producción con MySQL, modifica `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'solverans',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Variables de Entorno
Considera crear un archivo `.env` para variables sensibles:
```
SECRET_KEY=tu_clave_secreta
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 📚 Uso

### Newton-Raphson
1. Ingresa una función matemática (ej: `x**2 - 4`)
2. Define valor inicial, tolerancia y máximo de iteraciones
3. Ejecuta el cálculo y visualiza resultados

### Integración Numérica
1. Ingresa la función a integrar
2. Define límites de integración y número de subdivisiones
3. Selecciona el método (Trapecio/Simpson)
4. Visualiza el área calculada

### Gestión de Perfil
1. Registra una cuenta o inicia sesión
2. Personaliza tu perfil con foto y datos académicos
3. Consulta tu historial de cálculos
4. Recarga problemas anteriores con un clic

## 📁 Estructura del Proyecto

```
SolverMath/
├── solverANS/          # Configuración principal
├── solverApp/          # Aplicación principal
│   ├── models.py       # Modelos de datos
│   ├── views.py        # Lógica de vistas
│   ├── forms.py        # Formularios
│   ├── urls.py         # URLs de la app
│   ├── metodos/        # Algoritmos numéricos
│   ├── templates/      # Plantillas HTML
│   ├── static/         # Archivos estáticos
│   └── management/     # Comandos personalizados
├── media/              # Archivos subidos por usuarios
├── staticfiles/        # Archivos estáticos recolectados
└── requirements.txt    # Dependencias
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado con ❤️ para el curso de Métodos Numéricos

## 📞 Soporte

Si tienes preguntas o encuentras algún bug, por favor:
1. Revisa los [Issues existentes](https://github.com/Josue-Nani/SolverMath/issues)
2. Crea un nuevo Issue si es necesario
3. Proporciona información detallada del problema

---

⭐ **¡No olvides dar una estrella al proyecto si te fue útil!**
