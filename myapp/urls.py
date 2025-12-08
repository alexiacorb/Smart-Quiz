from django.urls import path
from . import views
urlpatterns = [
    path('', views.login, name="login"),
        #Am adaugat un nou path pentru a putea accesa pagina de login din register
    path('login/', views.login, name="login"),
    path("register/", views.register, name="register"),
    path("home/", views.home, name='home'),
    path("classes/", views.classes, name='classes'),
    path("feedback/", views.feedback, name='feedback'),
    path("upcoming/", views.upcoming, name='upcoming'),
    path("logout/", views.logout_view, name='logout'),
]