from django.contrib import admin
from .models import Profile, Review, Class, Grade, Test

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('email', 'rating', 'date')
    search_fields = ('email',)
    list_filter = ('rating', 'date')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'code', 'created_at')
    search_fields = ('name', 'teacher__username')
    filter_horizontal = ('students',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_obj', 'grade', 'updated_at')
    search_fields = ('student__username', 'class_obj__name')
    list_filter = ('class_obj', 'updated_at')
    readonly_fields = ('updated_at',)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_obj', 'date', 'created_at')
    search_fields = ('title', 'class_obj__name')
    list_filter = ('class_obj', 'date')
    readonly_fields = ('created_at',)
