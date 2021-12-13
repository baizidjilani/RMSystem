from django.urls import path
from . import views
from django.contrib import admin



urlpatterns = [
    path('', views.index, name='index'),
    path('student/<slug:stud_id>/marks_list/', views.marks_list, name='marks_list'),

    path('student/<int:stud_id>/tabulation/', views.s_gen_tabulation, name='s_tabulation'),
    path('student/<int:stud_id>/tabulation/pdf/', views.s_GeneratePdf, name = 's_generate_pdf'),
    path('student/<int:stud_id>/tabulation/pdf/download', views.s_downloadPdf, name = 's_download_pdf'),

    path('teacher/<slug:teacher_id>/<int:choice>/Classes/', views.t_clas, name='t_clas'),
    path('teacher/<int:assign_id>/marks_list/', views.t_marks_list, name='t_marks_list'),
    path('teacher/<int:assign_id>/tabulation/', views.gen_tabulation, name='tabulation'),
    path('teacher/<int:assign_id>/Students/Marks/', views.student_marks, name='t_student_marks'),
    path('teacher/<int:marks_c_id>/marks_entry/', views.t_marks_entry, name='t_marks_entry'),
    path('teacher/<int:marks_c_id>/marks_entry/confirm/', views.marks_confirm, name='marks_confirm'),
    path('teacher/<int:marks_c_id>/Edit_marks/', views.edit_marks, name='edit_marks'),
    path('teacher/<int:assign_id>/tabulation/pdf/', views.GeneratePdf, name = 'generate_pdf'),
    path('teacher/<int:assign_id>/tabulation/pdf/download', views.downloadPdf, name = 'download_pdf'),
]
admin.site.site_url= None

