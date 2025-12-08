from urllib import request
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
import calendar
from datetime import datetime, date, timedelta
#from myapp.models import Class, Test

from myapp.models import Review
from myapp.forms import ReviewForm

def login(request):
    return render(request, "login.html")
def register(request):
    return render(request, "register.html")
def home(request):
    return render(request, "home.html")
def classes(request):
    return render(request, "classes.html")
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
def upcoming(request):

    classes = [
        {'name': 'Tehnologii Web', 'details': 'Laborator de Tehnologii Web'},
    ]
    
    # 1. Determinam anul si luna de START (de la care incepem afisarea)
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
    
    # Calculam luna a 2-a pentru testele false
    next_m = start_month + 1 if start_month < 12 else 1
    next_y = start_year if start_month < 12 else start_year + 1
    
    fake_tests_db.append(MockTest("Test Recapitulare", date(next_y, next_m, 2), "Matematica")) # Ziua 2 luna 2

    calendars_data = []
    current_iter_year = start_year
    current_iter_month = start_month

    # Iteram de 2 ori (Luna Curenta + Urmatoarea)
    for i in range(2):
        cal_matrix = calendar.monthcalendar(current_iter_year, current_iter_month)
        month_name = calendar.month_name[current_iter_month]

        # --- FILTRARE MANUALA (In loc de Database Query) ---
        # Cautam in lista noastra fake testele care sunt in luna curenta a buclei
        tests_in_this_month = []
        for t in fake_tests_db:
            if t.date.year == current_iter_year and t.date.month == current_iter_month:
                tests_in_this_month.append(t)
        
        # Le punem in dictionar pe zile
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

    # Logica butoanelor Next/Prev ramane neschimbata
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
        'classes': classes, # Trimitem lista falsa
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

def logout_view(request):
    logout(request)
    return redirect('login')
