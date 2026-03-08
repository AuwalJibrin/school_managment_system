from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Student, Attendance
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from .forms import StudentForm
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from xhtml2pdf import pisa
import csv
import datetime

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_staff(user):
    return user.is_authenticated and user.role == 'staff'

def is_student(user):
    return user.is_authenticated and user.role == 'student'

def send_attendance_notification(subject, message, recipient_email):
    """Helper to send email notifications"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=True,
        )
    except Exception:
        pass # Don't crash if email fails

@login_required
@user_passes_test(is_staff)
def mark_attendance(request):
    students = Student.objects.all()
    today = timezone.now().date()
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status:
                try:
                    Attendance.objects.create(
                        student=student,
                        status=status,
                        marked_by=request.user,
                        verification_status='Verified',
                        verified_by=request.user,
                        check_in_time=timezone.localtime().time() # Staff marking is 'now'
                    )
                except IntegrityError:
                    pass
        messages.success(request, "Attendance marked successfully for today.")
        return redirect('attendance:mark-attendance')
        
    marked_today = Attendance.objects.filter(date=today).values_list('student_id', flat=True)
    
    context = {
        'students': students,
        'today': today,
        'marked_today': marked_today,
    }
    return render(request, 'attendance/mark_attendance.html', context)

@login_required
@user_passes_test(is_student)
def student_mark_attendance(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student-dashboard')

    today = timezone.localdate()
    now_time = timezone.localtime().time()
    
    # Late cutoff: 8:30 AM
    cutoff_time = datetime.time(8, 30)
    
    if Attendance.objects.filter(student=student, date=today).exists():
        messages.info(request, "You have already marked your attendance for today.")
    else:
        try:
            status = 'Present'
            if now_time > cutoff_time:
                status = 'Late'
            
            Attendance.objects.create(
                student=student,
                status=status,
                marked_by=request.user,
                verification_status='Pending',
                check_in_time=now_time
            )
            msg = "Attendance marked! Waiting for staff verification."
            if status == 'Late':
                msg = f"Marked as LATE ({now_time.strftime('%H:%M')}). Waiting for staff verification."
                # Notify on Late
                if student.user.email:
                    send_attendance_notification(
                        "Late Arrival Notification",
                        f"Dear {student.user.username},\n\nYou have been marked LATE today at {now_time.strftime('%H:%M')}.\n\nRegards,\nSchool Admin",
                        student.user.email
                    )
                
            messages.success(request, msg)
        except IntegrityError:
            messages.error(request, "Error marking attendance.")

    return redirect('attendance:student-attendance')

@login_required
@user_passes_test(is_student)
def student_request_leave(request):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        try:
            student = request.user.student_profile
            today = timezone.localdate()
            
            if Attendance.objects.filter(student=student, date=today).exists():
                messages.warning(request, "Attendance record already exists for today.")
            else:
                Attendance.objects.create(
                    student=student,
                    status='Leave',
                    leave_reason=reason,
                    marked_by=request.user,
                    verification_status='Pending',
                    check_in_time=timezone.localtime().time()
                )
                messages.success(request, "Leave request submitted successfully.")
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
        except Exception as e:
            messages.error(request, f"Error submitting request: {e}")
            
    return redirect('attendance:student-attendance')

@login_required
@user_passes_test(is_staff)
def staff_verify_attendance(request): 
    pending_records = Attendance.objects.filter(verification_status='Pending').order_by('-date')

    if request.method == 'POST':
        attendance_id = request.POST.get('attendance_id')
        action = request.POST.get('action') # 'verify', 'reject'
        rejection_reason = request.POST.get('rejection_reason', '')
        
        try:
            record = Attendance.objects.get(id=attendance_id)
            if action == 'verify':
                record.verification_status = 'Verified'
                record.verified_by = request.user
                record.save()
                messages.success(request, f"Verified: {record.student.user.username}")
            elif action == 'reject':
                record.verification_status = 'Rejected'
                record.rejection_reason = rejection_reason
                record.verified_by = request.user
                record.save()
                
                # Notify on Rejection
                if record.student.user.email:
                    send_attendance_notification(
                        "Attendance Rejected",
                        f"Dear {record.student.user.username},\n\nYour attendance claim for {record.date} was REJECTED.\nReason: {rejection_reason}\n\nRegards,\nSchool Admin",
                        record.student.user.email
                    )
                
                messages.warning(request, f"Rejected: {record.student.user.username}")
        except Attendance.DoesNotExist:
            messages.error(request, "Record not found.")
            
        return redirect('attendance:verify-attendance')

    return render(request, 'attendance/staff_verify_attendance.html', {'pending_records': pending_records})

@login_required
@user_passes_test(is_admin)
def view_attendance_admin(request):
    attendances = Attendance.objects.all().order_by('-date')
    
    # Filtering
    date_query = request.GET.get('date')
    class_query = request.GET.get('class')
    student_query = request.GET.get('student')
    
    if date_query:
        attendances = attendances.filter(date=date_query)
    if class_query:
        attendances = attendances.filter(student__class_name__icontains=class_query)
    if student_query:
        attendances = attendances.filter(student__user__username__icontains=student_query)
        
    context = {
        'attendances': attendances,
    }
    return render(request, 'attendance/admin_attendance.html', context)

@login_required
@user_passes_test(is_admin)
def export_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Student', 'Class', 'Time', 'Status', 'Verification', 'Marked By', 'Notes'])

    attendances = Attendance.objects.all().select_related('student', 'student__user', 'marked_by')
    for att in attendances:
        notes = []
        if att.rejection_reason:
            notes.append(f"Rejected: {att.rejection_reason}")
        if att.leave_reason:
            notes.append(f"Leave: {att.leave_reason}")
            
        writer.writerow([
            att.date,
            att.student.user.get_full_name() or att.student.user.username,
            att.student.class_name,
            att.check_in_time.strftime('%H:%M') if att.check_in_time else '-',
            att.status,
            att.verification_status,
            att.marked_by.username if att.marked_by else '-',
            " | ".join(notes)
        ])

    return response

@login_required
@user_passes_test(is_admin)
def export_attendance_pdf(request):
    attendances = Attendance.objects.all().order_by('-date')[:100] # Limit for demo
    template_path = 'attendance/attendance_pdf.html' # Need to create this
    context = {'attendances': attendances}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
@user_passes_test(is_admin)
def defaulters_list(request):
    # Logic: Students with < 75% verified attendance (Present or Late)
    students = Student.objects.all()
    defaulters = []
    
    for student in students:
        total = student.attendance_set.count() # Or better logic for total WORK days
        # Simplifying: Total records marked (including absent) = total days
        if total > 0:
            present = student.attendance_set.filter(status__in=['Present', 'Late'], verification_status='Verified').count()
            percentage = (present / total) * 100
            if percentage < 75:
                defaulters.append({
                    'student': student,
                    'percentage': round(percentage, 1),
                    'total': total,
                    'present': present
                })
    
    return render(request, 'attendance/defaulters_list.html', {'defaulters': defaulters})

@login_required
@user_passes_test(is_student)
def view_attendance_student(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect('student-dashboard')
        
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    
    # Calculate stats only on Verified Present/Late
    # Verified Leave allows tracking excusal but doesn't count against? 
    # For simplicity: Total Present includes Present + Late (Verified)
    
    # Filter for stats
    verified_recs = attendances.filter(verification_status='Verified')
    
    total_present = verified_recs.filter(status__in=['Present', 'Late']).count()
    total_absent = verified_recs.filter(status='Absent').count() 
    # Leave doesn't count as absent if verified? Let's say it's neutral.
    
    total_records = total_present + total_absent
    percentage = 0
    if total_records > 0:
        percentage = round((total_present / total_records) * 100, 2)

    context = {
        'attendances': attendances,
        'total_present': total_present,
        'total_absent': total_absent,
        'percentage': percentage,
        'today': timezone.now().date(),
        'marked_today': attendances.filter(date=timezone.now().date()).exists()
    }
    return render(request, 'attendance/student_attendance.html', context)

@login_required
@user_passes_test(is_staff)
def staff_student_list(request):
    students = Student.objects.all().select_related('user').order_by('class_name', 'user__username')
    
    # Filters
    semester = request.GET.get('semester')
    class_name = request.GET.get('class')
    search = request.GET.get('search')
    
    if semester:
        students = students.filter(semester=semester)
    if class_name:
        students = students.filter(class_name__icontains=class_name)
    if search:
        students = students.filter(user__username__icontains=search)
        
    # Enrich with attendance data
    student_data = []
    for s in students:
        total = s.attendance_set.count()
        present = s.attendance_set.filter(status__in=['Present', 'Late'], verification_status='Verified').count()
        percentage = 0
        if total > 0:
            percentage = round((present / total) * 100, 1)
            
        student_data.append({
            'student': s,
            'percentage': percentage,
            'total_attendance': total
        })

    # Get unique classes/semesters for filter dropdowns
    classes = Student.objects.values_list('class_name', flat=True).distinct()
    semesters = Student.objects.values_list('semester', flat=True).distinct()

    context = {
        'students': student_data,
        'classes': classes,
        'semesters': semesters,
    }
    return render(request, 'attendance/staff_student_list.html', context)

@login_required
@user_passes_test(is_staff)
def student_list(request):
    search = request.GET.get('search', '')
    class_filter = request.GET.get('class', '')
    
    students = Student.objects.all().select_related('user')
    
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) | 
            Q(user__last_name__icontains=search) | 
            Q(admission_number__icontains=search)
        )
    
    if class_filter:
        students = students.filter(class_name=class_filter)
        
    classes = Student.objects.values_list('class_name', flat=True).distinct()
    
    return render(request, 'students/student_list.html', {
        'students': students,
        'classes': classes,
    })

@login_required
@user_passes_test(is_staff)
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully!")
            return redirect('attendance:student-list')
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student'})

@login_required
@user_passes_test(is_staff)
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect('attendance:student-list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Edit Student', 'student': student})

@login_required
@user_passes_test(is_staff)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        user = student.user
        student.delete()
        user.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect('attendance:student-list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})

@login_required
@user_passes_test(is_staff)
def student_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_view.html', {'student': student})
