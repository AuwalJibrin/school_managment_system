from django.db import models
from attendance.models import Student



class Session(models.Model):
    name = models.CharField(max_length=20)  # e.g. 2024/2025
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Term(models.Model):
    name = models.CharField(max_length=20)  # First Term, Second Term
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.session}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    ca_score = models.PositiveIntegerField()
    exam_score = models.PositiveIntegerField()

    total = models.PositiveIntegerField(blank=True, null=True)
    grade = models.CharField(max_length=2, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'term')

    def save(self, *args, **kwargs):
        self.total = self.ca_score + self.exam_score

        if self.total >= 70:
            self.grade = 'A'
        elif self.total >= 60:
            self.grade = 'B'
        elif self.total >= 50:
            self.grade = 'C'
        elif self.total >= 45:
            self.grade = 'D'
        else:
            self.grade = 'F'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject}"
# Create your models here.
