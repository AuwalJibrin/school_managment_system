from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Book
from .forms import BookForm



def e_library(request):
    books = Book.objects.all()
    return render(request, 'e_library.html', {'books': books})



def download_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return FileResponse(book.pdf_file.open(), as_attachment=True)



def index(request):
    return render(request,"index.html")


def about(request):
    return render(request, "about.html")
 
def service(request):
    return render(request, "service.html")

@login_required
@role_required('admin')
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
            return redirect('admin-dashboard')
    else:
        form = BookForm()
    return render(request, 'school_web/book_form.html', {'form': form, 'title': 'Add Book'})

@login_required
@role_required('admin')
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect('admin-dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'school_web/book_form.html', {'form': form, 'title': 'Edit Book'})

@login_required
@role_required('admin')
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect('admin-dashboard')
    return render(request, 'school_web/book_confirm_delete.html', {'book': book})


def contact(request):
    if request.method == 'POST':
        messages.success(request, "Your message has been sent successfully!")
        return render(request, "contact.html")
    return render(request, "contact.html")



@login_required
@role_required('admin')
def book_list(request):
    books = Book.objects.all().select_related('assigned_to')
    return render(request, 'school_web/book_list.html', {'books': books})

# Create your views here.

