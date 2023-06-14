from django.contrib import admin
from .models import Department, Program, Course, Student,UserProfile, Attendance, PI_Data, Venue, AcademicYear, Semester, Schedule, ClassStudent

# Register your models here.

admin.site.register(Attendance)
admin.site.register(UserProfile)
admin.site.register(Department)
admin.site.register(Program)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(PI_Data)
admin.site.register(Venue)
admin.site.register(AcademicYear)
admin.site.register(Semester)
admin.site.register(Schedule)
admin.site.register(ClassStudent)



