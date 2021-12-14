from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import Count
from .models import Department, Class, Student, Course, Teacher, AssignTeacher, StudentCourse, Marks, MarksClass
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa  

# Create your views here.


@login_required
def index(request):
    if request.user.is_teacher:
        return render(request, 'result/teacher_homepage.html')
    if request.user.is_student:
        return render(request, 'result/student_homepage.html')
    return render(request, 'result/logout.html')


@login_required
def t_clas(request, teacher_id, choice):
    teacher1 = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'result/teacher_classes.html', {'teacher1': teacher1, 'choice': choice})


@login_required()
def marks_list(request, stud_id):
    stud = Student.objects.get(registration_number=stud_id, )
    ass_list = AssignTeacher.objects.filter(class_id_id=stud.class_id)
    sc_list = []
    for ass in ass_list:
        try:
            sc = StudentCourse.objects.get(student=stud, course=ass.course)
        except StudentCourse.DoesNotExist:
            sc = StudentCourse(student=stud, course=ass.course)
            sc.save()
            sc.marks_set.create(type='A', name='Attendance')
            sc.marks_set.create(type='T', name='Term Test')
            sc.marks_set.create(type='S', name='Semester Final Exam')
        sc_list.append(sc)

    return render(request, 'result/student_marks_list.html', {'sc_list': sc_list, 'stud':stud})



@login_required()
def t_marks_list(request, assign_id):
    id_assign = get_object_or_404(AssignTeacher, id=assign_id)
    m_list = MarksClass.objects.filter(assignteacher=id_assign)
    return render(request, 'result/teacher_marks_list.html', {'m_list': m_list, 'id_assign': id_assign})


@login_required()
def t_marks_entry(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assignteacher
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'mc': mc,
    }
    return render(request, 'result/teacher_marks_entry.html', context)


@login_required()
def marks_confirm(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assignteacher
    cr = ass.course
    cl = ass.class_id
    for s in cl.student_set.all():
        mark = request.POST[s.registration_number]
        sc = StudentCourse.objects.get(course=cr, student=s)
        m = sc.marks_set.get(name=mc.name)
        m.marks1 = mark
        m.save()
    mc.status = True
    mc.save()
    return HttpResponseRedirect(reverse('t_marks_list', args=(ass.id,)))


@login_required()
def edit_marks(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    cr = mc.assignteacher.course
    stud_list = mc.assignteacher.class_id.student_set.all()
    m_list = []
    for stud in stud_list:
        sc = StudentCourse.objects.get(course=cr, student=stud)
        m = sc.marks_set.get(name=mc.name)
        m_list.append(m)
    context = {
        'mc': mc,
        'm_list': m_list,
    }
    return render(request, 'result/edit_marks.html', context)


@login_required()
def student_marks(request, assign_id):
    ass = AssignTeacher.objects.get(id=assign_id)
    queryset = Marks.objects.raw('SELECT result_marks.id,\
    result_marks.studentcourse_id, sum(marks1) as total_marks, result_studentcourse.student_id, \
    result_studentcourse.course_id \
    from result_marks INNER JOIN \
    result_studentcourse on studentcourse_id = result_studentcourse.id \
    group by studentcourse_id')
    sc_list = StudentCourse.objects.filter(
        student__in=ass.class_id.student_set.all(), course=ass.course)
    return render(request, 'result/t_student_marks.html', {'sc_list': sc_list, 'queryset': queryset})


@login_required()
def gen_tabulation(request, assign_id):
    idAssign = get_object_or_404(AssignTeacher, id=assign_id)
    c_code = AssignTeacher.objects.all()
    # ass = AssignTeacher.objects.get(id=assign_id)
    # c_mark = Marks.objects.values('studentcourse__id').annotate(total_marks = Sum('marks1'))
    sc_list = StudentCourse.objects.raw('select result_studentcourse.id,\
        result_studentcourse.student_id as regi, result_student.name as stu_name,result_studentcourse.course_id, result_course.credits,\
        sum(marks1) as total_marks\
        from result_studentcourse\
        INNER JOIN  result_marks on result_studentcourse.id = result_marks.studentcourse_id\
        INNER JOIN result_student ON result_studentcourse.student_id = result_student.registration_number\
        INNER JOIN result_course on result_studentcourse.course_id = result_course.id\
        group by studentcourse_id')

    t_credits = Course.objects.all().aggregate(Sum('credits'))
    total = t_credits['credits__sum']
    unique_stu = Student.objects.raw('select distinct(registration_number), name from result_student')

    tab = {}
    for u in unique_stu:
        gpa = 0.0
        total_gpa = 0.0
        for mark in sc_list:
            if u.registration_number == mark.regi:
                if mark.total_marks >= 80:
                    gpa = (mark.credits*4.0)
                elif mark.total_marks >= 75:
                    gpa = (mark.credits*3.75)
                elif mark.total_marks >= 70:
                    gpa = (mark.credits*3.50)
                elif mark.total_marks >= 65:
                    gpa = (mark.credits*3.25)
                elif mark.total_marks >= 60:
                    gpa = (mark.credits*3.0)
                elif mark.total_marks >= 55:
                    gpa = (mark.credits*2.75)
                elif mark.total_marks >= 50:
                    gpa = (mark.credits*2.50)
                elif mark.total_marks >= 45:
                    gpa = (mark.credits*2.25)
                elif mark.total_marks >= 40:
                    gpa = (mark.credits*2.0)
                else:
                    gpa = 0.0
            total_gpa += gpa
            gpa = 0.0
        gpa = round(total_gpa/total, 2)
        tab.update({u.registration_number: gpa})

    
    # total_student = StudentCourse.objects.raw('SELECT count(DISTINCT result_studentcourse.student_id) as total_stu FROM result_studentcourse')
    total_student = StudentCourse.objects.values('student_id').distinct().count()
    return render(request, 'result/tabulation.html', {'c_code': c_code, 'sc_list': sc_list, 'total_student': total_student, 'tab': tab, 'idAssign': idAssign, 't_credits':t_credits, 'unique_stu':unique_stu})


@login_required()
def s_gen_tabulation(request, stud_id):
    stud = Student.objects.get(registration_number=stud_id, )
    c_code = AssignTeacher.objects.all()
    # ass = AssignTeacher.objects.get(id=assign_id)
    # c_mark = Marks.objects.values('studentcourse__id').annotate(total_marks = Sum('marks1'))
    sc_list = StudentCourse.objects.raw('select result_studentcourse.id,\
        result_studentcourse.student_id as regi, result_student.name as stu_name,result_studentcourse.course_id, result_course.credits,\
        sum(marks1) as total_marks\
        from result_studentcourse\
        INNER JOIN  result_marks on result_studentcourse.id = result_marks.studentcourse_id\
        INNER JOIN result_student ON result_studentcourse.student_id = result_student.registration_number\
        INNER JOIN result_course on result_studentcourse.course_id = result_course.id\
        group by studentcourse_id')

    t_credits = Course.objects.all().aggregate(Sum('credits'))
    total = t_credits['credits__sum']
    unique_stu = Student.objects.raw('select distinct(registration_number), name from result_student')

    tab = {}
    for u in unique_stu:
        gpa = 0.0
        total_gpa = 0.0
        for mark in sc_list:
            if u.registration_number == mark.regi:
                if mark.total_marks >= 80:
                    gpa = (mark.credits*4.0)
                elif mark.total_marks >= 75:
                    gpa = (mark.credits*3.75)
                elif mark.total_marks >= 70:
                    gpa = (mark.credits*3.50)
                elif mark.total_marks >= 65:
                    gpa = (mark.credits*3.25)
                elif mark.total_marks >= 60:
                    gpa = (mark.credits*3.0)
                elif mark.total_marks >= 55:
                    gpa = (mark.credits*2.75)
                elif mark.total_marks >= 50:
                    gpa = (mark.credits*2.50)
                elif mark.total_marks >= 45:
                    gpa = (mark.credits*2.25)
                elif mark.total_marks >= 40:
                    gpa = (mark.credits*2.0)
                else:
                    gpa = 0.0
            total_gpa += gpa
            gpa = 0.0
        gpa = round(total_gpa/total, 2)
        tab.update({u.registration_number: gpa})

    
    # total_student = StudentCourse.objects.raw('SELECT count(DISTINCT result_studentcourse.student_id) as total_stu FROM result_studentcourse')
    total_student = StudentCourse.objects.values('student_id').distinct().count()
    return render(request, 'result/student_tabulation.html', {'c_code': c_code, 'sc_list': sc_list, 'total_student': total_student, 'tab': tab, 't_credits':t_credits, 'unique_stu':unique_stu, 'stud':stud})


# html to pdf

def GeneratePdf(request, assign_id):
    id_assign = get_object_or_404(AssignTeacher, id=assign_id)
    course_code = AssignTeacher.objects.all()
    marks_list = StudentCourse.objects.raw('select result_studentcourse.id,\
        result_studentcourse.student_id as regi, result_student.name as stu_name,result_studentcourse.course_id, result_course.credits,\
        sum(marks1) as total_marks\
        from result_studentcourse\
        INNER JOIN  result_marks on result_studentcourse.id = result_marks.studentcourse_id\
        INNER JOIN result_student ON result_studentcourse.student_id = result_student.registration_number\
        INNER JOIN result_course on result_studentcourse.course_id = result_course.id\
        group by studentcourse_id')

    t_credits = Course.objects.all().aggregate(Sum('credits'))
    total = t_credits['credits__sum']
    unique_stu = Student.objects.raw('select distinct(registration_number), name from result_student')

    tabu = {}
    for sc in marks_list:
        gpa = 0.0
        total_gpa = 0.0
        for mark in marks_list:
            if sc.regi == mark.regi:
                if mark.total_marks >= 80:
                    gpa = (mark.credits*4.0)
                elif mark.total_marks >= 75:
                    gpa = (mark.credits*3.75)
                elif mark.total_marks >= 70:
                    gpa = (mark.credits*3.50)
                elif mark.total_marks >= 65:
                    gpa = (mark.credits*3.25)
                elif mark.total_marks >= 60:
                    gpa = (mark.credits*3.0)
                elif mark.total_marks >= 55:
                    gpa = (mark.credits*2.75)
                elif mark.total_marks >= 50:
                    gpa = (mark.credits*2.50)
                elif mark.total_marks >= 45:
                    gpa = (mark.credits*2.25)
                elif mark.total_marks >= 40:
                    gpa = (mark.credits*2.0)
                else:
                    gpa = 0.0
            total_gpa += gpa
            gpa = 0.0
        gpa = round(total_gpa/total, 2)
        tabu.update({sc.regi: gpa})
    # total_student = StudentCourse.objects.raw('SELECT count(DISTINCT result_studentcourse.student_id) as total_stu FROM result_studentcourse')
    total_student = StudentCourse.objects.values('student_id').distinct().count()
    return render(request, 'result/show_pdf.html', {'course_code': course_code, 'marks_list': marks_list,'total_student': total_student, 'tabu': tabu, 'id_assign':id_assign, 't_credits':t_credits, 'unique_stu':unique_stu})


def s_GeneratePdf(request, stud_id):
    stud = Student.objects.get(registration_number=stud_id, )
    course_code = AssignTeacher.objects.all()
    marks_list = StudentCourse.objects.raw('select result_studentcourse.id,\
        result_studentcourse.student_id as regi, result_student.name as stu_name,result_studentcourse.course_id, result_course.credits,\
        sum(marks1) as total_marks\
        from result_studentcourse\
        INNER JOIN  result_marks on result_studentcourse.id = result_marks.studentcourse_id\
        INNER JOIN result_student ON result_studentcourse.student_id = result_student.registration_number\
        INNER JOIN result_course on result_studentcourse.course_id = result_course.id\
        group by studentcourse_id')

    t_credits = Course.objects.all().aggregate(Sum('credits'))
    total = t_credits['credits__sum']
    unique_stu = Student.objects.raw('select distinct(registration_number), name from result_student')

    tabu = {}
    for sc in marks_list:
        gpa = 0.0
        total_gpa = 0.0
        for mark in marks_list:
            if sc.regi == mark.regi:
                if mark.total_marks >= 80:
                    gpa = (mark.credits*4.0)
                elif mark.total_marks >= 75:
                    gpa = (mark.credits*3.75)
                elif mark.total_marks >= 70:
                    gpa = (mark.credits*3.50)
                elif mark.total_marks >= 65:
                    gpa = (mark.credits*3.25)
                elif mark.total_marks >= 60:
                    gpa = (mark.credits*3.0)
                elif mark.total_marks >= 55:
                    gpa = (mark.credits*2.75)
                elif mark.total_marks >= 50:
                    gpa = (mark.credits*2.50)
                elif mark.total_marks >= 45:
                    gpa = (mark.credits*2.25)
                elif mark.total_marks >= 40:
                    gpa = (mark.credits*2.0)
                else:
                    gpa = 0.0
            total_gpa += gpa
            gpa = 0.0
        gpa = round(total_gpa/total, 2)
        tabu.update({sc.regi: gpa})
    # total_student = StudentCourse.objects.raw('SELECT count(DISTINCT result_studentcourse.student_id) as total_stu FROM result_studentcourse')
    total_student = StudentCourse.objects.values('student_id').distinct().count()
    return render(request, 'result/student_show_pdf.html', {'course_code': course_code, 'marks_list': marks_list,'total_student': total_student, 'tabu': tabu, 't_credits':t_credits, 'unique_stu':unique_stu, 'stud':stud})


def downloadPdf(request, assign_id):
    course_code = AssignTeacher.objects.all()
    marks_list = StudentCourse.objects.raw('select result_studentcourse.id,\
        result_studentcourse.student_id as regi, result_student.name as stu_name,result_studentcourse.course_id, result_course.credits,\
        sum(marks1) as total_marks\
        from result_studentcourse\
        INNER JOIN  result_marks on result_studentcourse.id = result_marks.studentcourse_id\
        INNER JOIN result_student ON result_studentcourse.student_id = result_student.registration_number\
        INNER JOIN result_course on result_studentcourse.course_id = result_course.id\
        group by studentcourse_id')

    t_credits = Course.objects.all().aggregate(Sum('credits'))
    total = t_credits['credits__sum']
    unique_stu = Student.objects.raw('select distinct(registration_number), name from result_student')

    tabu = {}
    for sc in marks_list:
        gpa = 0.0
        total_gpa = 0.0
        for mark in marks_list:
            if sc.regi == mark.regi:
                if mark.total_marks >= 80:
                    gpa = (mark.credits*4.0)
                elif mark.total_marks >= 75:
                    gpa = (mark.credits*3.75)
                elif mark.total_marks >= 70:
                    gpa = (mark.credits*3.50)
                elif mark.total_marks >= 65:
                    gpa = (mark.credits*3.25)
                elif mark.total_marks >= 60:
                    gpa = (mark.credits*3.0)
                elif mark.total_marks >= 55:
                    gpa = (mark.credits*2.75)
                elif mark.total_marks >= 50:
                    gpa = (mark.credits*2.50)
                elif mark.total_marks >= 45:
                    gpa = (mark.credits*2.25)
                elif mark.total_marks >= 40:
                    gpa = (mark.credits*2.0)
                else:
                    gpa = 0.0
            total_gpa += gpa
            gpa = 0.0
        gpa = round(total_gpa/total, 2)
        tabu.update({sc.regi: gpa})
    # total_student = StudentCourse.objects.raw('SELECT count(DISTINCT result_studentcourse.student_id) as total_stu FROM result_studentcourse')
    total_student = StudentCourse.objects.values('student_id').distinct().count()
    template_path = 'result/download_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Tabulation Sheet.pdf"'
    template = get_template(template_path)
    html = template.render({'course_code': course_code, 'marks_list': marks_list, 'total_student': total_student, 'tabu': tabu, 't_credits':t_credits, 'unique_stu':unique_stu})

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
       return HttpResponse('Errors <pre>' + html + '</pre>')
    return response

def s_downloadPdf(request, stud_id):
    course_code = AssignTeacher.objects.all()
    marks_list = StudentCourse.objects.raw('select result_studentcourse.id,\
        result_studentcourse.student_id as regi, result_student.name as stu_name,result_studentcourse.course_id, result_course.credits,\
        sum(marks1) as total_marks\
        from result_studentcourse\
        INNER JOIN  result_marks on result_studentcourse.id = result_marks.studentcourse_id\
        INNER JOIN result_student ON result_studentcourse.student_id = result_student.registration_number\
        INNER JOIN result_course on result_studentcourse.course_id = result_course.id\
        group by studentcourse_id')

    t_credits = Course.objects.all().aggregate(Sum('credits'))
    total = t_credits['credits__sum']
    unique_stu = Student.objects.raw('select distinct(registration_number), name from result_student')

    tabu = {}
    for sc in marks_list:
        gpa = 0.0
        total_gpa = 0.0
        for mark in marks_list:
            if sc.regi == mark.regi:
                if mark.total_marks >= 80:
                    gpa = (mark.credits*4.0)
                elif mark.total_marks >= 75:
                    gpa = (mark.credits*3.75)
                elif mark.total_marks >= 70:
                    gpa = (mark.credits*3.50)
                elif mark.total_marks >= 65:
                    gpa = (mark.credits*3.25)
                elif mark.total_marks >= 60:
                    gpa = (mark.credits*3.0)
                elif mark.total_marks >= 55:
                    gpa = (mark.credits*2.75)
                elif mark.total_marks >= 50:
                    gpa = (mark.credits*2.50)
                elif mark.total_marks >= 45:
                    gpa = (mark.credits*2.25)
                elif mark.total_marks >= 40:
                    gpa = (mark.credits*2.0)
                else:
                    gpa = 0.0
            total_gpa += gpa
            gpa = 0.0
        gpa = round(total_gpa/total, 2)
        tabu.update({sc.regi: gpa})
    # total_student = StudentCourse.objects.raw('SELECT count(DISTINCT result_studentcourse.student_id) as total_stu FROM result_studentcourse')
    total_student = StudentCourse.objects.values('student_id').distinct().count()
    template_path = 'result/download_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Tabulation Sheet.pdf"'
    template = get_template(template_path)
    html = template.render({'course_code': course_code, 'marks_list': marks_list, 'total_student': total_student, 'tabu': tabu, 't_credits':t_credits, 'unique_stu':unique_stu})

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
       return HttpResponse('Errors <pre>' + html + '</pre>')
    return response