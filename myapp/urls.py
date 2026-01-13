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
    path('class/<int:class_id>/my_grades/', views.my_grades, name='my_grades'),
    path('class/<int:class_id>/grades/', views.class_grades, name='class_grades'),
    path('class/<int:class_id>/students/', views.class_students, name='class_students'),
    path('test/<int:test_id>/scan/', views.scan_test, name='scan_test'),
    path('class/<int:class_id>/create_test/', views.create_test, name='create_test'),
    path('class/<int:class_id>/student/<int:student_id>/grades/', views.student_grades_view, name='student_grades_view'),    
        
    

]
