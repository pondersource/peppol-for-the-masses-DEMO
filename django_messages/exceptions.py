from django.db import IntegrityError
from django.shortcuts import redirect

class NotPeppolError(IntegrityError):
    pass
