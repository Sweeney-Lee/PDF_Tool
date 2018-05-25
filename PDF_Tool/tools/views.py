
from django.shortcuts import render


from .tools import *
import os


# Create your views here.

DIR =r"D:\Software\workplaces\Python_File\Django_File\PDF_Tool\templates\uploadFile"



def choose_functions(request):
    return render(request, 'index.html')

def cut(request):
    return Cut_PDF(request)

def encrypt(request):
    return Encrypt_Decrypt_PDF(request, 'Encrypt')

def decrypt(request):
    return Encrypt_Decrypt_PDF(request, 'Decrypt')

def merge(request):
    return Merge_PDF(request)

def add_watermark(request):
    return Add_watermark(request)
