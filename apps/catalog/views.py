from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.knowledge.models import Norm, CourtCase, LegalOpinion


@login_required
def home(request):
    context = {
        'norm_count': Norm.objects.count(),
        'case_count': CourtCase.objects.count(),
        'opinion_count': LegalOpinion.objects.count(),
    }
    return render(request, 'home.html', context)
