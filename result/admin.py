from django.contrib import admin
from datetime import timedelta, datetime
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import path
from .models import Department, Class, Student, Course, Teacher, AssignTeacher, Marks, StudentCourse, User

# Register your models here.


class ClassInline(admin.TabularInline):
    model = Class
    extra = 0

class DepartmentAdmin(admin.ModelAdmin):
    inlines = [ClassInline]
    list_display = ('name', 'id')
    search_fields = ('name', 'id')
    ordering = ['name']


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0


class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'semester', 'section')
    search_fields = ('id', 'department__name', 'semester', 'section')
    ordering = ['department__name', 'semester', 'section']
    inlines = [StudentInline]


class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'credits', 'department')
    search_fields = ('id', 'name', 'department__name')
    ordering = ['department', 'id']


class AssignTeacherAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'course', 'teacher')
    search_fields = ('class_id__department__name', 'class_id__id', 'course__name', 'teacher__name', 'course__shortname')
    ordering = ['class_id__department__name', 'class_id__id', 'course__id']
    raw_id_fields = ['class_id', 'course', 'teacher']


class MarksInline(admin.TabularInline):
    model = Marks
    extra = 0


class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'student', 'course',)
    search_fields = ('student__name', 'course__name', 'student__class_id__id', 'student__class_id__department__name')
    ordering = ('student__class_id__department__name', 'student__class_id__id', 'student__registration_number')
    inlines = [MarksInline]


class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'name', 'session', 'department')
    search_fields = ('registration_number', 'name', 'session', 'class_id__id', 'class_id__department__name')
    ordering = ['class_id__department__name', 'class_id__id', 'registration_number']


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name', 'department__name')
    ordering = ['department__name', 'name']


admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(AssignTeacher, AssignTeacherAdmin)
admin.site.register(StudentCourse, StudentCourseAdmin)

