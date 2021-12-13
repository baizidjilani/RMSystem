from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from datetime import timedelta


class Department(models.Model):
    id = models.CharField(primary_key='True', max_length=100)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    id = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=50)
    shortname = models.CharField(max_length=50, default='X')
    credits = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class Class(models.Model):
    id = models.CharField(primary_key='True', max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    section = models.CharField(max_length=100)
    semester = models.IntegerField()

    class Meta:
        verbose_name_plural = 'classes'

    def __str__(self):
        d = Department.objects.get(name=self.department)
        return '%s : %d %s' % (d.name, self.semester, self.section)


class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, 'student'):
            return True
        return False

    @property
    def is_teacher(self):
        if hasattr(self, 'teacher'):
            return True
        return False

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, default=1)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    registration_number = models.CharField(primary_key='True', max_length=100)
    session = models.CharField(max_length=100, default='2017-18')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AssignTeacher(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('course', 'class_id', 'teacher'),)

    def __str__(self):
        cl = Class.objects.get(id=self.class_id_id)
        cr = Course.objects.get(id=self.course_id)
        te = Teacher.objects.get(id=self.teacher_id)
        return '%s : %s : %s' % (te.name, cr.shortname, cl)


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('student', 'course'),)
        verbose_name_plural = 'Marks'

    def __str__(self):
        sname = Student.objects.get(name=self.student)
        cname = Course.objects.get(name=self.course)
        return '%s : %s' % (sname.name, cname.shortname)

    def get_cie(self):
        marks_list = self.marks_set.all()
        m = []
        for mk in marks_list:
            m.append(mk.marks1)
        cie = math.ceil(sum(m[:5]) / 2)
        return cie

test_name = (
    ('Attendance', 'Attendance'),
    ('Term Test', 'Term Test'),
    ('Semester Final Exam', 'Semester Final Exam'),
)

class Marks(models.Model):
    studentcourse = models.ForeignKey(StudentCourse, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=test_name, default='Attendance')
    marks1 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        unique_together = (('studentcourse', 'name'),)

    @property
    def total_marks(self):
        if self.name == 'Semester Final Exam':
            return 70
        elif self.name == 'Attendance':
            return 10
        else:
            return 20


class MarksClass(models.Model):
    assignteacher = models.ForeignKey(AssignTeacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=test_name, default='Attendance')
    status = models.BooleanField(default='False')

    class Meta:
        unique_together = (('assignteacher', 'name'),)

    @property
    def total_marks(self):
        if self.name == 'Semester Final Exam':
            return 70
        elif self.name == 'Attendance':
            return 10
        else:
            return 20


def create_marks(sender, instance, **kwargs):
    if kwargs['created']:
        if hasattr(instance, 'name'):
            ass_list = instance.class_id.assignteacher_set.all()
            for ass in ass_list:
                try:
                    StudentCourse.objects.get(student=instance, course=ass.course)
                except StudentCourse.DoesNotExist:
                    sc = StudentCourse(student=instance, course=ass.course)
                    sc.save()
                    sc.marks_set.create(name='Attendance')
                    sc.marks_set.create(name='Term Test')
                    sc.marks_set.create(name='Semester Final Exam')
        elif hasattr(instance, 'course'):
            stud_list = instance.class_id.student_set.all()
            cr = instance.course
            for s in stud_list:
                try:
                    StudentCourse.objects.get(student=s, course=cr)
                except StudentCourse.DoesNotExist:
                    sc = StudentCourse(student=s, course=cr)
                    sc.save()
                    sc.marks_set.create(name='Attendance')
                    sc.marks_set.create(name='Term Test')
                    sc.marks_set.create(name='Semester Final Exam')


def create_marks_class(sender, instance, **kwargs):
    if kwargs['created']:
        for name in test_name:
            try:
                MarksClass.objects.get(assignteacher=instance, name=name[0])
            except MarksClass.DoesNotExist:
                m = MarksClass(assignteacher=instance, name=name[0])
                m.save()

def delete_marks(sender, instance, **kwargs):
    stud_list = instance.class_id.student_set.all()
    StudentCourse.objects.filter(course=instance.course, student__in=stud_list).delete()



post_save.connect(create_marks, sender=Student)
post_save.connect(create_marks, sender=AssignTeacher)
post_save.connect(create_marks_class, sender=AssignTeacher)
post_delete.connect(delete_marks, sender=AssignTeacher)
