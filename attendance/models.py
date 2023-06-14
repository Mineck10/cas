from multiprocessing.spawn import old_main_modules
from statistics import mode
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from rest_framework.parsers import JSONParser

 

class Department(models.Model):
    description = models.TextField(blank=True, null=True)#name
    name = models.CharField(max_length=250)#name_shortform
    status = models.IntegerField(default = 1)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    contact = models.CharField(max_length=250)
    #dob = models.DateField(blank=True, null = True)#This can be deleted
    avatar = models.ImageField(blank=True, null = True, upload_to= 'images/')
    user_type = models.IntegerField(default = 2)
    #gender = models.CharField(max_length=100, choices=[('Male','Male'),('Female','Female')], blank=True, null= True)#This may be deleted
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank= False, null = True)

    def __str__(self):
        return self.user.username
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    print(instance)
    try:
        profile = UserProfile.objects.get(user = instance)
    except Exception as e:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

class Program(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default = 1)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    student_code = models.CharField(max_length=250,blank=True, null= True)
    program = models.ForeignKey(Program,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250)
    middle_name = models.CharField(max_length=250, blank=True, null= True)
    last_name = models.CharField(max_length=250)
    yos =  models.CharField(max_length=250, choices = [('1', 'First Year'),('2', 'Second Year'),('3', 'Third Year'),('4', 'Fourth Year')], blank=False, null=True )
    gender = models.CharField(max_length=100, choices=[('Male','Male'),('Female','Female')], blank=True, null= True)
    dob = models.DateField(blank=True, null= True)
    contact = models.CharField(max_length=250, blank=True, null= True)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_code + " - " + self.last_name + ", " + self.first_name  + " " +  self.middle_name
    

class AcademicYear(models.Model):
    academic_year = models.CharField(max_length=9, unique=True, help_text="Enter the academic year in the format 'YYYY-YYYY', e.g. '2022-2023'")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"({self.academic_year})"



class Semester(models.Model):
    semester = models.CharField(choices=[('1', 'First Semester'), ('2', 'Second Semester')], max_length=1)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('academic_year', 'semester')

    def __str__(self):
        return f"{self.semester}, {self.academic_year}" #f means formatted string
    
class Venue(models.Model):
    block = models.CharField(max_length=15)
    number = models.CharField(max_length=15)
    common_name = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.block}{self.number}"



class Schedule(models.Model):
    DAY = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    day = models.CharField(choices=DAY, max_length=9)
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_type = models.CharField(max_length=200, choices=[('1','Lecture'),('2','Practical'),('3','Tutorial')])
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.day} {self.course}"




#This (the below class) is the Course class (named as Class), it has to contain infos for courses,
#  we need to get Program's pk  (which is defined in Course class) and put it in here



class Course(models.Model):
    course_id = models.CharField(max_length=30)
    course_name = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    assigned_lecturer = models.ManyToManyField(UserProfile)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course_schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(default=1, choices=[(1, 'Active'),(2, 'Inactive')])
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.course_id + "-" + self.course_name

    #I need to define many2many relationship between Course and Lecturer, here

    def __str__(self):
        return "[" + self.course_id + "]" + '-' + self.course_name

class ClassStudent(models.Model):
    classIns = models.ForeignKey(Course,on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE) 

    def __str__(self):
        return self.student.student_code

    def get_present(self):
        student =  self.student
        _class =  self.classIns
        try:
            present = Attendance.objects.filter(classIns= _class, student=student, type = 1).count()
            return present
        except:
            return 0
    
    def get_tardy(self):
        student =  self.student
        _class =  self.classIns
        try:
            present = Attendance.objects.filter(classIns= _class, student=student, type = 2).count()
            return present
        except:
            return 0

    def get_absent(self):
        student =  self.student
        _class =  self.classIns
        try:
            present = Attendance.objects.filter(classIns= _class, student=student, type = 3).count()
            return present
        except:
            return 0

class Attendance(models.Model):
    classIns = models.ForeignKey(Course,on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    type = models.CharField(max_length=250, choices = [('1','Present'),('2','Tardy'),('1','Absent')] )
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.classIns.course_name + "  " +self.student.student_code
    



class PI_Data(models.Model):
    fingerprint = models.CharField(max_length=250, unique=True)
    registration_number = models.CharField(max_length=13,blank=True, null= True)#Unless there is data in the database, we may   submit without a value
    date_added = models.DateTimeField(default=timezone.now)
    

class FingerStore_Lecturer(models.Model):
    lecturer_number = models.ForeignKey(UserProfile,on_delete=models.CASCADE, null=True)
    template_number = models.CharField(max_length=50, unique=True)
    hash_number_lecturer = models.CharField(max_length=250, unique=True)




class FingerStore_Student(models.Model):
    student_number = models.ForeignKey(Student,on_delete=models.CASCADE, null=True)
    template_number = models.CharField(max_length=50, unique=True)
    hash_number_student = models.CharField(max_length=250, unique=True)