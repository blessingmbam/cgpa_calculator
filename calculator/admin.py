from django.contrib import admin
from .models import Semester, Course, Settings


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_code', 'units', 'grade', 'grade_point', 'semester')
    list_filter = ('semester', 'grade')
    search_fields = ('course_code',)


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'scale')
