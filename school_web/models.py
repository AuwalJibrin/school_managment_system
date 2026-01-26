from django.db import models


class Book(models.Model):
    title =models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    category = models.CharField(max_length=100, blank=True, null=True)

    description= models.CharField(max_length=500)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='books/')

    def __str__ (self):
        return self.title
    

# Create your models here.
