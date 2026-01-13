from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} Profile"


class Review(models.Model):
    email = models.EmailField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Class(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='classes_created'
    )
    
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    code = models.CharField(max_length=8, unique=True, editable=False)

    students = models.ManyToManyField(
        User,
        related_name='classes_joined',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.teacher.username})"

class Test(models.Model):
    class_obj = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='tests' 
    )
    title = models.CharField(max_length=100)
    date = models.DateTimeField()
    
    correct_answers = models.JSONField(default=dict) 
    
    model_file = models.FileField(upload_to='test_models/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.class_obj.name}"
class Grade(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    
    test = models.ForeignKey(
        Test, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='grades'
    )
    
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(blank=True)
    
    scanned_image = models.ImageField(upload_to='scans/', null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        test_title = self.test.title if self.test else "General"
        return f"{self.student.username} - {test_title}: {self.grade}"
