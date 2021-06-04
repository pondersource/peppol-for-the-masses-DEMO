from django.db import models

# Create your models here.

class Invoice(models.Model):

    website = models.URLField(max_length = 200)
    first_name = models.CharField(max_length=140)
    last_name = models.CharField(max_length=50)
