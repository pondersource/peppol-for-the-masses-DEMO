from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def SOAP(
    request, to_username,  template_name="SOAP_client/.../....html"
):
    """ Create a ConnectionRequest """

    if request.method == "POST":
        ....
        else:
            return redirect("....")

    return render(request, template_name)
