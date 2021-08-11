from django.db import IntegrityError
from django.shortcuts import redirect

class AlreadyExistsError(IntegrityError):
    pass


class AlreadyContactsError(IntegrityError):
    pass

class ValidationError(IntegrityError):
    pass
