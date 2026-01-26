from urllib import request
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from .models import Book



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
 
def Service(request):
    return render(request, "Service.html")

def contact(request):
    return render(request, "contact.html")



# Create your views here.

