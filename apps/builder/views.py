from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def builder_home(request):
    return render(request, 'builder/builder.html')
