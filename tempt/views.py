from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages #import messages

# thanks to https://www.ordinarycoders.com/blog/article/django-user-register-login-logout for the code and tutorial
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("recipes:index")
        messages.error(request, "Unsuccessful registration. Invalid information. Please try again.")
    form = NewUserForm
    return render (request=request, template_name="registration/new_user.html", context={"register_form":form})

def sources(request):
    return render(request, 'sources.html', {})