from django.urls import path
from . import views
urlpatterns = [
    path('', views.login_user, name="login"),
    path('login/', views.login_user, name="login"),
    path("register/", views.register_view, name="register"),
    path("home/", views.home, name='home'),
    path("classes/", views.classes, name='classes'),
    path("feedback/", views.feedback, name='feedback'),
    path("upcoming/", views.upcoming, name='upcoming'),
    path("logout/", views.logout_view, name='logout'),
    path('create-class/', views.create_class, name='create_class'),
    path('join-class/', views.join_class, name='join_class'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('my-grades/', views.my_grades, name='my_grades'),
    path('class/<int:class_id>/grades/', views.class_grades, name='class_grades'),
]
