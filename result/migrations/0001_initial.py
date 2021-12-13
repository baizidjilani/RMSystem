from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.CharField(max_length=100, primary_key='True', serialize=False)),
                ('section', models.CharField(max_length=100)),
                ('semester', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'classes',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.CharField(max_length=50, primary_key='True', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('shortname', models.CharField(default='X', max_length=50)),
                ('credits', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.CharField(max_length=100, primary_key='True', serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('registration_number', models.CharField(max_length=100, primary_key='True', serialize=False)),
                ('session', models.CharField(default='2017-18', max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('class_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='result.class')),
                ('department', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='result.department')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('department', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='result.department')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.student')),
            ],
            options={
                'verbose_name_plural': 'Marks',
                'unique_together': {('student', 'course')},
            },
        ),
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.department'),
        ),
        migrations.AddField(
            model_name='class',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.department'),
        ),
        migrations.CreateModel(
            name='AssignTeacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.class')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.course')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.teacher')),
            ],
            options={
                'unique_together': {('course', 'class_id', 'teacher')},
            },
        ),
        migrations.CreateModel(
            name='MarksClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Attendance', 'Attendance'), ('Term Test', 'Term Test'), ('Semester Final Exam', 'Semester Final Exam')], default='Attendance', max_length=50)),
                ('status', models.BooleanField(default='False')),
                ('assignteacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.assignteacher')),
            ],
            options={
                'unique_together': {('assignteacher', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Marks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Attendance', 'Attendance'), ('Term Test', 'Term Test'), ('Semester Final Exam', 'Semester Final Exam')], default='Attendance', max_length=50)),
                ('marks1', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('studentcourse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='result.studentcourse')),
            ],
            options={
                'unique_together': {('studentcourse', 'name')},
            },
        ),
    ]
