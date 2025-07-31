from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuário')
    name = models.CharField(max_length=100, verbose_name='Nome')
    doc_bi = models.CharField(max_length=20, unique=True, verbose_name='BI')
    birth_date = models.DateField(verbose_name='Data de Nascimento')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Telefone')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    def __str__(self):
        return self.name
    
    @property
    def username(self):
        return self.user.username if self.user else None
