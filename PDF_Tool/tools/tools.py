# _*_ coding:utf-8 _*_

import PyPDF2
import os
import re
from django.shortcuts import render
from django.http import StreamingHttpResponse

DIR =r"D:\Software\workplaces\Python_File\Django_File\PDF_Tool\templates\uploadFile"

# judgeCharacter
def judgeCharacter(filename):
    for i in filename:
        if i >= '\u4e00' and i <= '\u9fa5' or i in ['\\', '/', ':', '?', '#', '"', '<', '>', '|']:
            return False
    return True

# judgePDFName
def judgePDFName(filename):
    if not judgeCharacter(filename):
        return False
    JudgePDF = re.compile(r'(\.pdf)$', re.I)
    if JudgePDF.search(filename):
        return True
    else:
        return False

# judgeEncrypted
def judgeEncrypted(file):
    with open(file, 'rb') as pdfFile:
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        if pdfReader.isEncrypted:
            return True
        else:
            return False

# judgePagesOK
def judgePagesOK(file, pages):
    if judgeEncrypted(file):
        error = 'The PDF is encrypted ! Please firstly remove encryption of it !'
        os.remove(file)
        return error
    with open(file, 'rb') as pdfFile:
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        maxNumPage = pdfReader.numPages
    pagesOK =[]
    symbol = ""
    for i in pages:
        if i.isalnum():
            continue
        elif i is ":":
            symbol += i
        elif i is ",":
            symbol += i
        else:
            error = 'allowed symbol is "," or ":" !'
            return error
    if symbol is "":
        if int(pages) > 0 and int(pages) <= maxNumPage:
            pagesOK = [int(pages) - 1]
        else:
            error = 'pages is should from 1 to maxNumpage: ' + str(maxNumPage)
            return error
    elif symbol == ":" and len(pages) >= 3:
        start, end = pages.split(':')
        start, end = int(start) - 1, int(end) - 1
        if start < 0 or end >= maxNumPage or start >= end:
            error = "start: end \nstart < 0 and end >= maxNumPage and start <= end"
            return error
        else:
            pagesOK = [i for i in range(start, end + 1)]
    elif symbol == ',' * len(symbol):
        for i in pages.split(','):
            if i == '':
                error = "between ',' is should have a number !"
                return error
            if int(i) < 0 or int(i) > maxNumPage:
                error = 'pages is should from 1 to maxNumpage: ' + str(maxNumPage)
                return error
            pagesOK.append(int(i) - 1)
    else:
        error = "':' should in one and shouldn't use with ',' !"
        return error
    return pagesOK


# saveFile
def saveFile(file, savefile):
    destination = open(savefile, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()

# file_download
def file_download(filename):
    file = os.path.join(DIR, filename)

    def file_iterator(file, chunk_size=512):
        with open(file, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    response = StreamingHttpResponse(file_iterator(file))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
    return response


# cult
def cult(file, page, result):

    with open(file, 'rb') as pdfFile:
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        pdfWriter = PyPDF2.PdfFileWriter()
        for pageNum in page:
            pdfWriter.addPage(pdfReader.getPage(pageNum))

        with open(result, 'wb') as resultPdf:
            pdfWriter.write(resultPdf)

# Encrypt
def Encrypt(file, password, result):
    with open(file, 'rb') as pdfFile:
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        pdfWriter = PyPDF2.PdfFileWriter()
        for pageNum in range(pdfReader.numPages):
            pdfWriter.addPage(pdfReader.getPage(pageNum))
        pdfWriter.encrypt(password)
        with open(result, 'wb') as resultPdf:
            pdfWriter.write(resultPdf)

# Decrypt
def Decrypt(file, password, result):
    with open(file, 'rb') as pdfFile:
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        pdfReader.decrypt(password)
        pdfWriter = PyPDF2.PdfFileWriter()
        for pageNum in range(pdfReader.numPages):
            pdfWriter.addPage(pdfReader.getPage(pageNum))
        with open(result, 'wb') as resultPdf:
            pdfWriter.write(resultPdf)

# Merge
def Merge(files, resultpath):
    merger = PyPDF2.PdfFileMerger()
    for file in files:
        merger.append(PyPDF2.PdfFileReader(file))
    merger.write(resultpath)






# Cut_PDF
def Cut_PDF(request):
    if request.method == "POST":
        file = request.FILES.get("file", None)
        pages = request.POST.get("pages", None)
        result = request.POST.get("result", None)

        if file and pages and result:

            if judgePDFName(file.name) and judgePDFName(result):

                savefile = os.path.join(DIR, file.name)
                saveFile(file, savefile)

                pages = judgePagesOK(savefile, pages)
                if type(pages) == list:
                    resultpath = os.path.join(DIR, result)
                    cult(savefile, pages, resultpath)
                    return file_download(result)

                else:
                    error = pages
            else:
                error = "The filename should end with '.pdf' !"
        else:
            error = 'Please input completely !'

        return render(request, 'Cut.html', {'error': error})
    else:
        return render(request, 'Cut.html')

# Encrypt_Decrypt_PDF
def Encrypt_Decrypt_PDF(request, Encrypt_Decrypt):
    html = Encrypt_Decrypt + '.html'
    if request.method == "POST":
        file = request.FILES.get("file", None)
        password = request.POST.get("password", None)
        result = request.POST.get("result", None)

        if file and password and result:
            if judgePDFName(file.name) and judgePDFName(result):
                if judgeCharacter(password):
                    savefile = os.path.join(DIR, file.name)
                    saveFile(file, savefile)

                    resultpath = os.path.join(DIR, result)
                    if Encrypt_Decrypt == 'Encrypt':
                        if judgeEncrypted(savefile):

                            error = 'The PDF is encrypted ! Please firstly remove encryption of it !'
                            os.remove(savefile)
                        else:
                            Encrypt(savefile, password, resultpath)
                            return file_download(result)
                    else:
                        with open(savefile, 'rb') as pdfFile:
                            pdfReader = PyPDF2.PdfFileReader(pdfFile)
                            if pdfReader.isEncrypted:
                                if pdfReader.decrypt(password):
                                    Decrypt(savefile, password, resultpath)
                                    return file_download(result)
                                else:
                                    error = 'The password is wrong !'
                            else:
                                error = 'The PDF you input is not encrypted!'
                else:
                    error = '''The password should not have Chinese and special symbol in
                     ['\\', '/', ':', '?', '#', '"', '<', '>', '|']'''

            else:
                error = "The filename should end with '.pdf' !"
        else:
            error = 'Please input completely !'

        return render(request, html, {'error': error})
    else:
        return render(request, html)


# Merge_PDF
def Merge_PDF(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        result = request.POST.get("result", None)
        error = ''
        if files and result:
            savefiles = []
            for file in files:
                if judgePDFName(file.name) and judgePDFName(result):

                    savefile = os.path.join(DIR, file.name)
                    savefiles.append(savefile)
                    saveFile(file, savefile)

                    if judgeEncrypted(savefile):
                        error = 'One of PDFs is encrypted ! Please firstly remove encryption of it !'
                else:
                    error = "The filename should end with '.pdf' !"
            if error == '':
                resultpath = os.path.join(DIR, result)
                Merge(savefiles, resultpath)
                return file_download(result)

        else:
            error = 'Please input completely !'

        return render(request, 'Merge.html', {'error': error})
    else:
        return render(request, 'Merge.html')


# watermark
def watermark(savefile, savewatermark, pages, resultpath):

    with open(savewatermark, 'rb') as pdfWatermark:
        watermarkReader = PyPDF2.PdfFileReader(pdfWatermark)

        with open(savefile, 'rb') as markFile:
            pdfReader = PyPDF2.PdfFileReader(markFile)
            maxNumPage = pdfReader.numPages
            pdfWriter = PyPDF2.PdfFileWriter()
            startpage = pages[0]
            endpage = pages[-1]

            print(pages)
            print(startpage, endpage)

            watermarkrange = range(startpage, endpage + 1)
            otherrange1 = range(0, startpage)
            otherrange2 = range(endpage + 1, maxNumPage)
            print(watermarkrange, otherrange1, otherrange2)
            for page in otherrange1:
                pageObj = pdfReader.getPage(page)
                pdfWriter.addPage(pageObj)

            for i in watermarkrange:
                temp = pdfReader.getPage(i)
                temp.mergePage(watermarkReader.getPage(0))
                pdfWriter.addPage(temp)

            for page in otherrange2:
                pageObj = pdfReader.getPage(page)
                pdfWriter.addPage(pageObj)
            with open(resultpath, 'wb') as resultPdfFile:
                pdfWriter.write(resultPdfFile)


# Add_watermark
def Add_watermark(request):
    if request.method == "POST":
        file = request.FILES.get("file", None)
        watermarkfile = request.FILES.get("watermark", None)
        pages = request.POST.get("pages", None)
        result = request.POST.get("result", None)

        if file and watermarkfile and pages and result:

            if judgePDFName(file.name) and judgePDFName(watermarkfile.name) and judgePDFName(result):

                savefile = os.path.join(DIR, file.name)
                saveFile(file, savefile)

                savewatermark = os.path.join(DIR, watermarkfile.name)
                saveFile(watermarkfile, savewatermark)

                pages = judgePagesOK(savefile, pages)
                if type(pages) == list:
                    with open(savewatermark, 'rb') as pdfFile:
                        pdfReader = PyPDF2.PdfFileReader(pdfFile)
                        if pdfReader.isEncrypted:
                            error = 'The watermarkPDF is encrypted. Please decrypt firstly!'
                        else:
                            maxNumPage = pdfReader.numPages
                            if maxNumPage == 1:

                                resultpath = os.path.join(DIR, result)
                                watermark(savefile, savewatermark, pages, resultpath)
                                return file_download(result)
                            else:
                                error = 'The page of watermark should be one. Please cut it firstly!'
                else:
                    error = pages
            else:
                error = "The filename should end with '.pdf' !"
        else:
            error = 'Please input completely !'

        return render(request, 'Add_Watermark.html', {'error': error})
    else:
        return render(request, 'Add_Watermark.html')





