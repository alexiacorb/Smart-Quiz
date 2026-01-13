from urllib import request
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login as auth_login
import calendar
from datetime import datetime, date, timedelta
#from myapp.models import Class, Test
from .models import Review, Class, Grade, Test, User
from .forms import ReviewForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .utils import extrage_raspunsuri, calculeaza_nota
import json
from django.utils.dateparse import parse_datetime

def scan_test(request, test_id):
    # Găsim testul specific
    test_obj = get_object_or_404(Test, id=test_id)
    class_obj = test_obj.class_obj

    # Verificăm dacă a fost deja predat (securitate extra)
    if Grade.objects.filter(test=test_obj, student=request.user).exists():
        return redirect('class_detail', class_id=class_obj.id)

    if request.method == 'POST':
        uploaded_image = request.FILES.get('test_image')
        
        if uploaded_image:
            # 1. Procesăm imaginea direct
            # Nota: În producție, salvează fișierul temporar pe disc pentru OpenCV
            import os
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            
            # Salvăm imaginea temporar
            path = default_storage.save(f'tmp/{uploaded_image.name}', ContentFile(uploaded_image.read()))
            full_path = os.path.join(default_storage.location, path)

            try:
                # 2. Apelăm logica ta de OCR
                rezultat_scanare = extrage_raspunsuri(full_path, 10) # Sau len(test_obj.correct_answers)

                if "error" in rezultat_scanare:
                     return render(request, 'features/scan_page.html', {
                        'test': test_obj, 
                        'error': rezultat_scanare['error']
                    })

                # 3. Calculăm nota pe baza grilei din Test
                raport = calculeaza_nota(rezultat_scanare, test_obj.correct_answers)

                # 4. Salvăm Nota
                Grade.objects.create(
                    student=request.user,
                    class_obj=class_obj,
                    test=test_obj,
                    grade=raport['nota'],
                    notes=f"Corecte: {raport['total_corecte']}",
                    scanned_image=uploaded_image # Salvăm și poza finală
                )
                
                # Ștergem fișierul temporar
                os.remove(full_path)

                return redirect('class_detail', class_id=class_obj.id)

            except Exception as e:
                return render(request, 'features/scan_page.html', {'test': test_obj, 'error': str(e)})

    # Dacă e GET, afișăm pagina de upload
    return render(request, 'features/scan_page.html', {'test': test_obj})

def create_test(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user != class_obj.teacher:
        return redirect('class_detail', class_id=class_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        date_str = request.POST.get('date')
        answers_json = request.POST.get('answers_json') 

        if title and date_str and answers_json:
            Test.objects.create(
                class_obj=class_obj,
                title=title,
                date=parse_datetime(date_str),
                correct_answers=json.loads(answers_json) 
            )
            return redirect('class_detail', class_id=class_id)

    return render(request, 'create_test.html', {'class_obj': class_obj})

def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')  
        else:
            return render(request, "login.html", {
                "error": "Invalid username or password."
            })

    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.profile.role = role
        user.profile.save()

        return redirect("login")

    return render(request, "register.html")

@login_required
def create_class(request):
    if request.method == "POST":
        if request.user.profile.role != "teacher":
            return HttpResponseForbidden("Only teachers can create classes.")

        name = request.POST.get("className")
        details = request.POST.get("details")

        new_class = Class.objects.create(
            teacher=request.user,
            name=name,
            details=details
        )

        return redirect("home")

    return redirect("home")

@login_required
def join_class(request):
    if request.method == "POST":
        if request.user.profile.role != "student":
            return HttpResponseForbidden("Only students can join classes.")

        class_code = request.POST.get("classCode")

        try:
            class_obj = Class.objects.get(code=class_code)
        except Class.DoesNotExist:
            return render(request, "home.html", {"error": "Invalid class code."})

        class_obj.students.add(request.user)
        return redirect("home")

    return redirect("home")



@login_required(login_url='login')
def home(request):
    if request.user.profile.role == "teacher":
        classes = request.user.classes_created.all()
    else:
        classes = request.user.classes_joined.all()

    return render(request, "home.html", {"classes": classes})


@login_required(login_url='login')
def classes(request):
    return render(request, "classes.html")


@login_required(login_url='login')
def class_detail(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    tests= class_obj.tests.all().order_by('-date')
    # Only the class teacher or a student enrolled in the class can view details
    if request.user != class_obj.teacher and request.user not in class_obj.students.all():
        return HttpResponseForbidden("You don't have permission to view this class.")
    if request.user.profile.role == 'student':
        for test in tests:
            test.has_scanned = Grade.objects.filter(
                test=test, 
                student=request.user
            ).exists()
    students = class_obj.students.all()
    return render(request, 'class_detail.html', {
        'class_obj': class_obj,
        'tests': tests,
        'students': students,
    })

@login_required(login_url='login')
def feedback(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback')
    else:
        form = ReviewForm()
    reviews = Review.objects.all().order_by('-date')
    return render(request, 'feedback.html', {'form': form, 'reviews': reviews})

class MockTest:
    def __init__(self, title, test_date, class_name):
        self.title = title
        self.date = test_date # Trebuie sa fie obiect de tip date()
        self.class_name = class_name

@login_required(login_url='login')
def upcoming(request):
    if request.user.profile.role == "teacher":
        classes = request.user.classes_created.all()
    else:
        classes = request.user.classes_joined.all()
    
    today = datetime.now()
    req_year = request.GET.get('year')
    req_month = request.GET.get('month')

    if req_year and req_month:
        start_year = int(req_year)
        start_month = int(req_month)
    else:
        start_year = today.year
        start_month = today.month

    fake_tests_db = [
        MockTest("Tehnologii Web", date(start_year, start_month, 5), "Tehnologii Web"),       # Ziua 5 luna 1
        MockTest("Tehnologii", date(start_year, start_month, 20), "Tehnologii Web"),           # Ziua 20 luna 1
        MockTest("Proiect SQL", date(start_year, start_month, 20), "Tehnologii Web"),      # Tot ziua 20 (2 puncte)
    ]
    
    next_m = start_month + 1 if start_month < 12 else 1
    next_y = start_year if start_month < 12 else start_year + 1
    
    fake_tests_db.append(MockTest("Test Recapitulare", date(next_y, next_m, 2), "Matematica")) # Ziua 2 luna 2

    calendars_data = []
    current_iter_year = start_year
    current_iter_month = start_month

    for i in range(2):
        cal_matrix = calendar.monthcalendar(current_iter_year, current_iter_month)
        month_name = calendar.month_name[current_iter_month]

        tests_in_this_month = []
        for t in fake_tests_db:
            if t.date.year == current_iter_year and t.date.month == current_iter_month:
                tests_in_this_month.append(t)
        
        tests_dict = {}
        for test in tests_in_this_month:
            day = test.date.day
            if day not in tests_dict:
                tests_dict[day] = []
            tests_dict[day].append(test)

        calendars_data.append({
            'year': current_iter_year,
            'month': current_iter_month,
            'month_name': month_name,
            'matrix': cal_matrix,
            'tests_dict': tests_dict,
        })

        current_iter_month += 1
        if current_iter_month > 12:
            current_iter_month = 1
            current_iter_year += 1

    prev_date = date(start_year, start_month, 1)
    if start_month == 1:
        prev_month = 12
        prev_year = start_year - 1
    else:
        prev_month = start_month - 1
        prev_year = start_year

    if start_month == 12:
        next_month = 1
        next_year = start_year + 1
    else:
        next_month = start_month + 1
        next_year = start_year

    context = {
        'classes': classes,
        'calendars_data': calendars_data,
        'today_day': today.day,
        'today_month': today.month,
        'today_year': today.year,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }
    
    return render(request, "upcoming.html", context)

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def my_grades(request,class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if request.user.profile.role != "student":
        return HttpResponseForbidden("Only students can view their grades.")
    
    grades = Grade.objects.filter(student=request.user).select_related('class_obj')
    
    return render(request, 'my_grades.html', {'class_obj': class_obj, 'grades': grades})


@login_required(login_url='login')
def class_grades(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user != class_obj.teacher:
        return HttpResponseForbidden("Only the class teacher can view student grades.")
    
    grades = Grade.objects.filter(class_obj=class_obj).select_related('student')
    students = class_obj.students.all()
    
    grades_dict = {grade.student.id: grade for grade in grades}
    
    student_grades = []
    for student in students:
        grade = grades_dict.get(student.id)
        student_grades.append({
            'student': student,
            'grade': grade
        })
    
    return render(request, 'class_grades.html', {
        'class_obj': class_obj,
        'student_grades': student_grades,
        'students': students,
    })


def student_grades_view(request, class_id, student_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.user != class_obj.teacher:
        return redirect('home') 
    
    student = get_object_or_404(User, id=student_id)
    grades = Grade.objects.filter(student=student, test__class_associated=class_obj).order_by('test__date')
    average = 0
    if grades:
        total = sum([g.grade for g in grades]) 
        average = total / len(grades)

    context = {
        'class_obj': class_obj,
        'student': student,
        'grades': grades,
        'average': average
    }
    
    return render(request, 'student_grades.html', context)

def class_students(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)

    # Only the class teacher or a student enrolled in the class can view details
    if request.user != class_obj.teacher and request.user not in class_obj.students.all():
        return HttpResponseForbidden("You don't have permission to view this class.")

    students = class_obj.students.all()

    return render(request, 'class_students.html', {
        'class_obj': class_obj,
        'students': students,
    })