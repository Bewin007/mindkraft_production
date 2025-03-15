from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, register_no, mobile_no, password, date_of_birth, recipt_no=None, intercollege=False, is_enrolled=False, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not password:
            raise ValueError("Password needs to be set")
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            register_no=register_no,
            mobile_no=mobile_no,
            date_of_birth=date_of_birth,
            recipt_no=recipt_no,
            intercollege=intercollege,
            is_enrolled=is_enrolled,
            **extra_fields
        )
        user.set_password(password)
        user.mkid = self.generate_mkid()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, register_no, mobile_no, password, date_of_birth, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, first_name, last_name, register_no, mobile_no, password, date_of_birth, **extra_fields)

    def generate_mkid(self):
        last_user = User.objects.order_by("-id").first()
        if last_user and last_user.mkid.startswith("MK25P"):
            last_number = int(last_user.mkid[5:])  # Extract numeric part correctly
        else:
            last_number = 0
        return f"MK25P{last_number + 1:05d}"

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    register_no = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    mkid = models.CharField(max_length=10, unique=True, editable=False)
    date_of_birth = models.DateField()
    recipt_no = models.CharField(max_length=16, default='')  # New field to save hexadecimal value
    intercollege = models.BooleanField(default=False)
    is_enrolled = models.BooleanField(default=False)
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "register_no", "mobile_no", "date_of_birth"]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college_name = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    dept = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    tshirt = models.BooleanField(default=False)
    registered_at = models.DateTimeField(default=timezone.now)  # New field added
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.college_name}"