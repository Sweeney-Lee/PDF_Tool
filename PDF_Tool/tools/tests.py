from django.test import TestCase
import re
import PyPDF2
import os
# Create your tests here.
JudgePDF = re.compile(r'(\.pdf)$', re.I)
filename = '1df(2).pdf'
if JudgePDF.search(filename):
    print('1')
else:
    print('2')