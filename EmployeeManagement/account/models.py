from django.db import models
from django.contrib.auth.models import User


class Form(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)

class DynamicField(models.Model):
    FIELD_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('password', 'Password'),
    ]
    form=models.ForeignKey(Form,on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    field_type = models.CharField(choices=FIELD_CHOICES, max_length=10)
    
    def __str__(self):
        return self.label
    
class FormFieldSubmission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)  
    field_label = models.CharField(max_length=255)
    field_value = models.TextField()
    unique_id=models.PositiveIntegerField(default=0)

