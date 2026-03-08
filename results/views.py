from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Result, Subject, Term
from .forms import ResultForm
from attendance.models import Student

def is_staff(user):
    return user.is_authenticated and user.role in ['admin', 'staff']

@login_required
def result_list(request):
    if request.user.role == 'student':
        results = Result.objects.filter(student__user=request.user).select_related('subject', 'term')
        context = {
            'results': results,
            'is_student': True
        }
    else:
        results = Result.objects.all().select_related('student__user', 'subject', 'term')
        
        student_f = request.GET.get('student')
        term_f = request.GET.get('term')
        subject_f = request.GET.get('subject')
        
        if student_f:
            results = results.filter(student_id=student_f)
        if term_f:
            results = results.filter(term_id=term_f)
        if subject_f:
            results = results.filter(subject_id=subject_f)
            
        context = {
            'results': results,
            'students': Student.objects.all().select_related('user'),
            'terms': Term.objects.all(),
            'subjects': Subject.objects.all(),
            'is_staff': True
        }
    return render(request, 'results/result_list.html', context)

@login_required
@user_passes_test(is_staff)
def result_add(request):
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Result added successfully!")
            return redirect('results:result-list')
    else:
        form = ResultForm()
    
    context = {
        'form': form,
        'title': 'Add Result',
        'students': Student.objects.all().select_related('user'),
        'subjects': Subject.objects.all(),
        'terms': Term.objects.all(),
    }
    return render(request, 'results/result_form.html', context)

@login_required
@user_passes_test(is_staff)
def result_edit(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, "Result updated successfully!")
            return redirect('results:result-list')
    else:
        form = ResultForm(instance=result)
        
    context = {
        'form': form,
        'title': 'Edit Result',
        'result': result,
        'students': Student.objects.all().select_related('user'),
        'subjects': Subject.objects.all(),
        'terms': Term.objects.all(),
    }
    return render(request, 'results/result_form.html', context)

@login_required
@user_passes_test(is_staff)
def result_delete(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, "Result deleted successfully!")
        return redirect('results:result-list')
    return render(request, 'results/result_confirm_delete.html', {'result': result})
