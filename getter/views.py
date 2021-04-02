import csv
import requests
# from django.http import HttpResponse
from django.shortcuts import render


def main(request):
    context = {}
    return render(request, 'getter/main.html', context)
