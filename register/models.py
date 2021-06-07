from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self,email,password= None,is_active= True,is_staff= False,is_admin= False):
        if not email:
            raise ValueError("User must have an email address")
        if not password:
            raise ValueError("User must have a password")
        user_obj  = self.model(
            email = self.normalize_email(email)
        )
        user_obj.set_password(password)
        user_obj.staff      = is_staff
        user_obj.admin      = is_admin
        user_obj.is_active     = is_active
        user_obj.save(using = self._db)

        return user_obj

    def create_staffUser(self,email,password=None):

        user = self.create_user(email,
                                password = password,
                                is_staff = True
        )
        return user

    def create_superuser(self,email,password=None):

        user = self.create_user(email,
                                password = password,
                                is_staff = True,
                                is_admin = True
        )
        return user

class User(AbstractBaseUser):

    email      = models.EmailField(max_length=255,unique=True)
    user_name  = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=False,null=True)
    last_name  = models.CharField(max_length=150, blank=False,null=True)
    website    = models.CharField(max_length=150, unique=True)

    active     = models.BooleanField(default=False) # can login
    staff      = models.BooleanField(default=True)
    admin      = models.BooleanField(default=False)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = [user_name,first_name,last_name,website]

    objects = UserManager()

    def __str__(self):
        return self.user_name

    def get_user_name(self):
        return self.user_name

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_website(self):
        return self.website

    def has_perm(self , perm , obj = None ):
        return True

    def has_module_perms(self , app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.admin

class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    # extend extra data
