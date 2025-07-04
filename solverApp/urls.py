from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .forms import LoginUsuarioForm
from .views import newton_raphson_view, CustomLoginView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

    
    # Página principal luego de login
    path('', views.menu_principal, name='menu'),

    # Login con vista personalizada
    path('login/', CustomLoginView.as_view(), name='login'),

    # Logout
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Registro de usuario personalizado
    path('register/', views.registro_usuario, name='register'),

    # Método de Newton-Raphson
     path('newton/', newton_raphson_view, name='vista_newton'),
     path('newton/<int:historial_id>/', newton_raphson_view, name='vista_newton_precargado'),

     path('integracion/', views.integracion_view, name='integracion_view'),
     path('integracion/<int:historial_id>/', views.integracion_view, name='integracion_view_precargado'),
     path('integracion-compuesta/', views.vista_integracion_compuesta, name='vista_integracion_compuesta'),

    # Login como invitado
     path('guest-login/', views.guest_login, name='guest_login'),

     path('perfil/', views.perfil_view, name='perfil'),

     # Vista de administrador
     path('admin-panel/', views.admin_panel_view, name='admin_panel'),
     path('admin-panel/usuarios/', views.admin_usuarios_view, name='admin_usuarios'),
     path('admin-panel/usuarios/<int:user_id>/', views.admin_usuario_detalle, name='admin_usuario_detalle'),
     path('admin-panel/usuarios/<int:user_id>/toggle-active/', views.admin_toggle_user_active, name='admin_toggle_user_active'),
     path('admin-panel/usuarios/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
     path('admin-panel/historial/', views.admin_historial_view, name='admin_historial'),
     path('admin-panel/historial/<int:historial_id>/delete/', views.admin_delete_historial, name='admin_delete_historial'),
     path('admin-panel/estadisticas/', views.admin_estadisticas_view, name='admin_estadisticas'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)