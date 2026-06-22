from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Norm, CourtCase, LegalOpinion


@login_required
def norm_detail(request, pk):
    norm = get_object_or_404(Norm, pk=pk)
    return render(request, 'knowledge/norm_detail.html', {'norm': norm})


@login_required
def case_detail(request, pk):
    case = get_object_or_404(CourtCase, pk=pk)
    return render(request, 'knowledge/case_detail.html', {'case': case})


@login_required
def opinion_detail(request, pk):
    opinion = get_object_or_404(LegalOpinion, pk=pk)
    return render(request, 'knowledge/opinion_detail.html', {'opinion': opinion})
