import os
import sys
import json
import shutil
import sqlite3
import requests
from .models import *
from time import time
from pprint import pprint
from subprocess import call
from urlparse import urlparse
from django.conf import settings
from subprocess import Popen,PIPE
from django.shortcuts import render
from django.http import HttpResponse
from requests.exceptions import HTTPError
from django.template import loader, Context, Template, RequestContext

def home(request):
    html = u''
    project_list = []
    
    # Recorrer proyectos almacenados para obtener ficheros y bears totales en cada uno
    for project in Project.objects.all():
        total_files = 0
        for files in File.objects.filter(ProjectName = project):
            total_files += 1
        total_bears = 0
        for bears in Bear.objects.filter(ProjectName = project):
            total_bears += 1
        percen = float(total_files)/float(project.TotalFiles)
        project_list.append((total_bears, total_files, project.Name, percen))
    # Ordenar la lista
    project_list.sort(key=lambda project_list: project_list[3], reverse=False)

    # Para cada proyecto, preparacion del codigo html que se mostrara
    for i in project_list:
        project = Project.objects.get(Name = i[2])
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">' + project.Name + '</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4> URL en GitHub: <a href="' + project.URL + '">' + project.URL + '</a></h4>'
        html += '<h4>Ficheros Python totales: ' + project.TotalFiles + '</h4>'
        html += '<h4>Ficheros afectados: ' + str(i[1]) + '</h4>'
        html += '<h4>% ficheros afectados: ' + str(float(i[3])*100)[0:5] + ' %</h4>'
        html += '<h4>Bears almacenados: ' + str(i[0]) + '</h4>'
        html += '<h4><a href="http://localhost:8000/analyzer/project/' + project.Name + '">M&aacute;s informaci&oacute;n >>></a></h4>'
        html += '</div>'

    # Carga de datos en template
    template = loader.get_template('home.html')
    return HttpResponse(template.render(Context({'html':html})))

def statisticsBear(request):
    html_bear = u''
    bear_list = []
    bear_data = []
    
    # Recorrer bears almacenados e incluir en la lista
    for bear in Bear.objects.all():
        if not bear.Bear in bear_list:
                bear_list.append(bear.Bear)

    # Contar numero de bears por tipo
    for i in bear_list:
        count = 0
        for bear in Bear.objects.filter(Bear = i):
            count +=1
        bear_data.append((count, i))
    bear_data.sort(key=lambda bear_data: bear_data[0], reverse=True)

    # Preparar html para mostrar la cantidad de cada tipo de bear encontrado
    html_bear += '<div class="col-md-12"><table class="table table-striped">'
    html_bear += '<thead><tr><th>#</th><th>Cantidad</th><th>Bear</th></tr></thead><tbody>'
    count = 1
    for i in bear_data:
        html_bear += '<tr><td>' + str(count) + '</td><td>' + str(i[0]) + '</td><td><a href="http://localhost:8000/analyzer/show/?item=' + str(i[1]) + '&option=3">' + str(i[1]) + '</a></td></tr>'
        count += 1
    html_bear += '</tbody></table></div>'
    stats_type = 'Cantidad de bears por tipo'
    navbar = '<li><a href="http://localhost:8000/analyzer/statistics/project">Proyectos</a></li><li><a href="http://localhost:8000/analyzer/statistics/file">Ficheros</a></li> <li class="active"><a href="http://localhost:8000/analyzer/statistics/bear">Bears</a></li>'

    # Carga de datos en template
    template = loader.get_template('statistics.html')
    return HttpResponse(template.render(Context({'html':html_bear, 'stats_type':stats_type, 'navbar':navbar})))

def statisticsFile(request):
    html_file = u''
    file_list = []

    # Recorrer ficheros almacenados para obtener informacion de cantidad de bears encontrados por fichero
    for files in File.objects.all():
        total_bears = 0
        project = files.ProjectName
        project_name = project.Name
        for bears in Bear.objects.filter(FileName = files):
            total_bears += 1
        file_list.append((total_bears, files.Name, project_name))
    file_list.sort(key=lambda file_list: file_list[0], reverse=True)

    # Preparar html para mostrar la informacion
    html_file += '<div class="col-md-12"><table class="table table-striped">'
    html_file += '<thead><tr><th>#</th><th>Bears</th><th>Fichero</th><th>Proyecto</th></tr></thead><tbody>'
    count = 1
    for i in file_list:
        html_file += '<tr><td>' + str(count) + '</td><td>' + str(i[0]) + '</td><td><a href="http://localhost:8000/analyzer/show/?item=' + str(i[1]) + '&option=2">' + str(i[1]) + '</a></td><td><a href="http://localhost:8000/analyzer/show/?item=' + str(i[2]) + '&option=1">' + str(i[2]) + '</a></td></tr>'
        count += 1
    html_file += '</tbody></table></div>'
    stats_type = 'Cantidad de bears por fichero'
    navbar = '<li><a href="http://localhost:8000/analyzer/statistics/project">Proyectos</a></li><li class="active"><a href="http://localhost:8000/analyzer/statistics/file">Ficheros</a></li> <li><a href="http://localhost:8000/analyzer/statistics/bear">Bears</a></li>'

    # Carga de datos en template
    template = loader.get_template('statistics.html')
    return HttpResponse(template.render(Context({'html':html_file, 'stats_type':stats_type, 'navbar':navbar})))

def statisticsProject(request):
    html_project = u''
    project_list = []

    # Recorrer proyectos almacenados para obtener cantidad de ficheros y bears encontrados
    for project in Project.objects.all():
        total_files = 0
        for files in File.objects.filter(ProjectName = project):
            total_files += 1
        total_bears = 0
        for bears in Bear.objects.filter(ProjectName = project):
            total_bears += 1
        percen = float(total_files)/float(project.TotalFiles)
        project_list.append((total_bears, total_files, project.TotalFiles, project.Name, percen))
    project_list.sort(key=lambda project_list: project_list[4], reverse=True)

    # Preparar html para mostrar la informacion
    html_project += '<div class="col-md-12"><table class="table table-striped">'
    html_project += '<thead><tr><th>#</th><th>Bears</th><th>% ficheros afectados</th><th>Ficheros afectados</th><th>Ficheros Python</th><th>Proyecto</th></tr></thead><tbody>'
    count = 1
    for i in project_list:
        html_project += '<tr><td>' + str(count) + '</td><td>' + str(i[0]) + '</td><td>' + str(float(i[4])*100)[0:5] + '</td><td>' + str(i[1]) + '</td><td>' + str(i[2]) + '</td><td><a href="http://localhost:8000/analyzer/show/?item=' + str(i[3]) + '&option=1">' + str(i[3]) + '</a></td></tr>'
        count += 1
    html_project += '</tbody></table></div>'
    stats_type = 'Cantidad de bears por proyecto'
    navbar = '<li class="active"><a href="http://localhost:8000/analyzer/statistics/project">Proyectos</a></li><li><a href="http://localhost:8000/analyzer/statistics/file">Ficheros</a></li> <li><a href="http://localhost:8000/analyzer/statistics/bear">Bears</a></li>'

    # Carga de datos en template
    template = loader.get_template('statistics.html')
    return HttpResponse(template.render(Context({'html':html_project, 'stats_type':stats_type, 'navbar':navbar})))

def projectInfo(request, resource):
    html = u''

    # Trata de abrir el proyecto indicado
    try:
        project = Project.objects.get(Name=resource)
    # En caso de que no exista, lanzar mensaje de error
    except Project.DoesNotExist:
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de b&uacute;squeda</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>El proyecto ' + resource + ' no se encuentra almacenado en la base de datos.</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    # Preparar html con la informacion de proyecto
    name = project.Name
    html += '<div class="page-header"><h3><b><a href="http://localhost:8000/analyzer/project/' + name + '">' + name + '</a></b></h3></div>'
    html += '<h4> URL en GitHub: <a href="' + project.URL + '">' + project.URL + '</a></h4>'
    html += '<h4># ficheros Python: ' + project.TotalFiles + '</h4>'
    total_files = 0
    for files in File.objects.filter(ProjectName = project):
        total_files += 1
    html += '<h4># ficheros afectados: ' + str(total_files) + '</h4>'
    percen = float(total_files)/float(project.TotalFiles)
    html += '<h4>% ficheros afectados: ' + str(float(percen)*100)[0:5] + ' %</h4>'
    total_bears = 0
    for bears in Bear.objects.filter(ProjectName = project):
        total_bears += 1
    html += '<hr>'
    html += '<div class="page-header"><h4>Ficheros analizados</h4></div>'
    html += '<div id="newFiles" style="display:none;">'
    file_list = []
    # Para cada fichero, incluir lista con tipo de bears encontrados
    for files in File.objects.filter(ProjectName = project):
        total_bears = 0
        bear_list = []
        for bears in Bear.objects.filter(FileName = files):
            total_bears += 1
            if not bears.Bear in bear_list:
                bear_list.append(bears.Bear)
        file_list.append((total_bears, bear_list, files.Name))
    file_list.sort(key=lambda file_list: file_list[0], reverse=True)
    html += '<div class="col-md-12"><table class="table table-striped">'
    html += '<thead><tr><th>Fichero</th><th># Bears</th><th>Tipo de Bears encontrados</th></tr></thead><tbody>'
    for i in file_list:
        bear2text = ""
        for j in i[1]:
            bear2text += '<a href="http://localhost:8000/analyzer/show/?item=' + j + '&option=3">' + j + '</a>' + ', '
        html += '<tr><td><a href="http://localhost:8000/analyzer/file/' + name + '/' + str(i[2]) + '">' + str(i[2]) + '</a></td><td>' + str(i[0]) + '</td><td>' + bear2text+ '</td></tr>'
    html += '</tbody></table></div>'
    html += '</div>'
    html += '<a href="javascript:dispHandle(newFiles)"><b>Mostrar/ocultar ficheros analizados en ' + name + '</b></a>'

    # Carga de datos en template
    template = loader.get_template('projectInfo.html')
    return HttpResponse(template.render(Context({'html':html, 'project':name})))

def fileInfo(request, resource):
    html = u''
    projectName = resource.split("/")[0] + "/" + resource.split("/")[1]

    # Trata de abrir el proyecto al que pertenece el fichero
    try:    
        project = Project.objects.get(Name = projectName)
    # En caso de que no exista, lanzar mensaje de error
    except Project.DoesNotExist:
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de b&uacute;squeda</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>El proyecto ' + projectName + ' no se encuentra almacenado en la base de datos.</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    fileName = resource.split("/")[2]
    # Trata de abrir fichero
    try:    
        files = File.objects.get(Name = fileName, ProjectName = project)
    # En caso de que no exista, lanzar mensaje de error
    except File.DoesNotExist:
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de b&uacute;squeda</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>El fichero ' + fileName + ' no se encuentra almacenado en la base de datos dentro del proyecto ' + projectName + '.</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    # Preparacion de codigo html para mostrar datos
    html += '<div class="page-header"><h3><b><a href="http://localhost:8000/analyzer/file/' + projectName + "/" + fileName + '">' + fileName + '</a></b></h3></div>'
    html += '<h4>Proyecto: <a href="http://localhost:8000/analyzer/project/' + projectName + '">' + projectName + '</a></h4>'
    html += '<h4>URL en GitHub: <a href="' + files.URL + '">' + files.URL + '</a></h4>'
    html += '<h4>Path local: ' + files.FilePath + '</h4>'
    html += '<hr>'
    html += '<div class="page-header"><h4>Bears encontrados</h4></div>'
    html += '<div id="newFiles" style="display:none;">'
    bear_list = []
    # Incluir bears encontrados
    for bear in Bear.objects.filter(ProjectName = project, FileName = files):
        bear_list.append((bear.Bear, bear.StartLine, bear.EndLine, bear.Message, bear.BearId))
    bear_list.sort(key=lambda bear_list: bear_list[0], reverse=True)
    html += '<div class="col-md-12"><table class="table table-striped">'
    html += '<thead><tr><th>Bear</th><th>Start Line</th><th>End Line</th><th>Message</th><th>Id</th></tr></thead><tbody>'
    for i in bear_list:
        html += '<tr><td><a href="http://localhost:8000/analyzer/bear/' + str(i[4]) + '">' + str(i[0]) + '</a></td><td>' + str(i[1]) + '</td><td>' + str(i[2]) + '</td><td>' + str(i[3]) + '</td><td><a href="http://localhost:8000/analyzer/bear/' + str(i[4]) + '">' + str(i[4]) + '</a></td></tr>'
    html += '</tbody></table></div>'
    html += '</div>'
    html += '<a href="javascript:dispHandle(newFiles)"><b>Mostrar/ocultar bears encontrados en ' + fileName + '</b></a>'

    # Carga de datos en template
    template = loader.get_template('fileInfo.html')
    return HttpResponse(template.render(Context({'html':html, 'project':projectName, 'filename':fileName})))

def bearInfo(request, resource):
    html = u''

    # Trata de abrir el bear
    try:
        bear = Bear.objects.get(BearId = resource)
    # En caso de que no exista, lanzar mensaje de error
    except Bear.DoesNotExist:
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de b&uacute;squeda</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>El Id ' + resource + ' no corresponde a ning&uacute;n bear almacenado en la base de datos.</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    project = bear.ProjectName
    projectname = project.Name
    name = project.Name
    files = bear.FileName
    filename = files.Name

    # Preparacion de codigo html para mostrar informacion almacenada
    html += '<hr>'
    html += '<div class="page-header"><h4>' + bear.Bear + '</h4></div>'
    html += '<div class="col-md-12"><table class="table table-striped">'
    html += '<tbody>'
    html += '<tr><td><b>Proyecto</b></td><td><a href="http://localhost:8000/analyzer/project/' + projectname + '">' + projectname + '</a></td></tr>'
    html += '<tr><td><b>Fichero</b></td><td><a href="http://localhost:8000/analyzer/file/' + projectname + '/' + filename + '">' + filename + '</a></td></tr>'
    html += '<tr><td><b>L&iacute;nea inicial</b></td><td><a href="' + bear.StartLineURL + '">' + str(bear.StartLine) + '</a></td></tr>'
    html += '<tr><td><b>L&iacute;nea final</b></td><td><a href="' + bear.EndLineURL + '">' + str(bear.EndLine) + '</a></td></tr>'
#    html += '<tr><td><b>Aspect</b></td><td>' + bear.Aspect + '</td></tr>'
    html += '<tr><td><b>Confidence</b></td><td>' + str(bear.Confidence) + '</td></tr>'
    html += '<tr><td><b>Debug Message</b></td><td>' + bear.DebugMsg + '</td></tr>'
    html += '<tr><td><b>Diffs</b></td><td>' + bear.Diffs + '</td></tr>'
    html += '<tr><td><b>Id</b></td><td>' + bear.BearId + '</td></tr>'
    html += '<tr><td><b>Message</b></td><td>' + bear.Message + '</td></tr>'
#    html += '<tr><td><b>Message Arguments</b></td><td>' + bear.MessageArguments + '</td></tr>'
#    html += '<tr><td><b>Message Base</b></td><td>' + bear.MessageBase + '</td></tr>'
    html += '<tr><td><b>Severity</b></td><td>' + str(bear.Severity) + '</td></tr>'
    html += '</tbody></table></div>'

    # Carga de datos en template
    template = loader.get_template('bearInfo.html')
    return HttpResponse(template.render(Context({'html':html, 'bear':bear.Bear, 'project':projectname, 'filename':filename})))

def analyse(request):

    # Muestra pagina de analisis
    template = loader.get_template('analyse.html')
    return HttpResponse(template.render())

def analyseURL(request):

    # Muestra pagina de analisis por URL
    template = loader.get_template('analyseURL.html')
    return HttpResponse(template.render())

def analyseFile(request):

    # Muestra pagina de analisis por fichero local
    template = loader.get_template('analyseFile.html')
    return HttpResponse(template.render())   

def processFile(request):
    # Toma el path del fichero introducido    
    resource = request.GET
    
    # Quedarse con la parte que contiene el path dado
    path = resource['path']

    # Abrir el fichero
    try:
        urls_file = open(path, 'r')
    # En caso de error, lanzar mensaje
    except IOError:
        html = u''
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de lectura de fichero</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>La ruta proporcionada no es correcta o no corresponde a un fichero v&aacute;lido. Pruebe a buscar el proyecto en <a href="https://github.com/">GitHub</a>.</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    # Variable para guardar los proyectos analizados
    analyzed_projects = []

    # Recorrer el fichero linea a linea, descargando y analizando cada proyecto
    for line in urls_file:

        # Asegurarse de que el string no tenga espacios a los lados
        stripped_line = line.strip()

        # Comprobar que se trata de una url correcta de GitHub
        url_line = urlparse(stripped_line)
        if url_line.netloc != "github.com":
            # Si no es una url valida, saltar esta linea
            print "UrlError: La linea '" + stripped_line + "' no pertenece a una url de un proyecto de GitHub"
            continue
        try:
            r = requests.get(stripped_line)
            r.raise_for_status()
        except HTTPError:
            print "UrlError: La linea '" + stripped_line + "' no pertenece a una url v&aacute;lida."
            continue

        # Obtener el nombre del proyecto
        project_name = url_line.path.split(".")[0]
        project_name = project_name[1:len(project_name)]

        # Cambiar el directorio de trabajo, para que las descargas vayan al directorio definido en settings
        os.chdir(settings.CONSTANTS['workspace'])
       
        # Descargar proyecto con git
        call(["git","clone",stripped_line])

        #Obtener la ruta al fichero descargado (dentro del directorio local)
        project_path = "/tmp/" + project_name.split("/")[1]
        python_files = project_path + "/**.py"

        # Ficheros Python del proyecto
        lstDir = os.walk(project_path)
        total_py_files = 0        

        for root, dirs, files in lstDir:
            for myfile in files:
                (name, ext) = os.path.splitext(myfile)
                if(ext == ".py"):
                    total_py_files += 1
              
        # Comprobar la existencia del proyecto. Si existe, se sobreescribe
        if Project.objects.filter(Name = project_name, URL = stripped_line).exists():
            Project.objects.filter(Name = project_name, URL = stripped_line).delete()
            myProject = Project(Name = project_name, URL = stripped_line, TotalFiles = str(total_py_files))
            myProject.save()
        else:
            myProject = Project(Name = project_name, URL = stripped_line, TotalFiles = str(total_py_files))
            myProject.save()

        analyzed_projects.append(project_name)

        print "Analizando " + project_name + "..."

        # Ejecutar COALA sobre el proyecto y guardar la salida en un fichero JSON para su posterior analisis
        p1 = Popen(["coala", "--json", "--files", python_files], stdout=PIPE)
        p2 = Popen(["tee", settings.CONSTANTS['jsonFile']], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        output = p2.communicate()[0]

        # Una vez analizado y creado el fichero JSON, elimino el proyecto de disco local
        shutil.rmtree(project_path)


        # Abrir el fichero JSON
        try:
            with open(settings.CONSTANTS['jsonFile']) as data_file:
                data = json.load(data_file)
        except ValueError:
            if Project.objects.filter(Name = project_name, URL = stripped_line).exists():
                Project.objects.filter(Name = project_name, URL = stripped_line).delete()
            continue
        print "Procesando JSON..."        

        # Extraer los campos del fichero JSON
        for i in range(0, len(data["results"]["default"])):
            default = i
            additional_info = data["results"]["default"][i]["additional_info"]
            affected_code = data["results"]["default"][i]["affected_code"]

            # Si no hay affected_code (para Bears que analizan el proyecto desde otra perspectiva), se rellena con "None"
            try:
                affected_code_file = data["results"]["default"][i]["affected_code"][0]["file"]
                var_file = affected_code_file.split("/")
                analyzed_file = var_file[len(var_file)-1].strip()
                url_file = "https://github.com/" + project_name + "/blob/master/" + analyzed_file
                affected_code_start_line = data["results"]["default"][i]["affected_code"][0]["start"]["line"]
                url_start_line = url_file + "#L" + str(affected_code_start_line)
                if str(affected_code_start_line).strip() == "None":
                    affected_code_start_line = 0
                    url_start_line = "None"              
                affected_code_end_line = data["results"]["default"][i]["affected_code"][0]["end"]["line"]
                url_end_line = url_file + "#L" + str(affected_code_end_line)
                if str(affected_code_end_line).strip() == "None":
                    affected_code_end_line = 0
                    url_end_line = "None"
            except IndexError:
                affected_code_file = "None"
                analyzed_file = "None"
                url_file = "None"
                affected_code_start_line = 0
                url_start_line = "None"
                affected_code_end_line = 0
                url_end_line = "None"

            aspect = data["results"]["default"][i]["aspect"]
            confidence = data["results"]["default"][i]["confidence"]
            debug_msg = data["results"]["default"][i]["debug_msg"]
            diffs = data["results"]["default"][i]["diffs"]
            data_id = data["results"]["default"][i]["id"]
            message = data["results"]["default"][i]["message"]
            message_arguments = data["results"]["default"][i]["message_arguments"]
            message_base = data["results"]["default"][i]["message_base"]
            origin = data["results"]["default"][i]["origin"]
            severity = data["results"]["default"][i]["severity"]

            # Comprobar la existencia del fichero en BBDD. Si no existe, guardar el nuevo fichero
            myProject = Project.objects.get(Name = project_name)
            try:
                myFile = File.objects.get(Name = analyzed_file, ProjectName = myProject)
            except File.DoesNotExist:
                newFile = File(Name = analyzed_file, URL = url_file, ProjectName = myProject, FilePath = affected_code_file)
                newFile.save()

            # Guardar los datos de la salida del Bear
            myFile = File.objects.get(Name = analyzed_file, ProjectName = myProject)
            newBear = Bear(Bear = origin, ProjectName = myProject, FileName = myFile, StartLine = affected_code_start_line, StartLineURL = url_start_line, EndLine = affected_code_end_line, EndLineURL = url_end_line, Aspect = aspect, Confidence = confidence, DebugMsg = debug_msg, Diffs = str(diffs), BearId = str(data_id), Message = message, MessageArguments = str(message_arguments), MessageBase = message_base, Severity = severity)
            newBear.save()

    # Cerrar el fichero
    urls_file.close()

    html = u''
    fileId = 1

    # Preparar html para mostrar los datos de los proyectos analizados (ver projectInfo)
    for k in analyzed_projects:
        project = Project.objects.get(Name=k)
        html += '<div class="page-header"><h3><b><a href="http://localhost:8000/analyzer/project/' + k + '">' + k + '</a></b></h3></div>'
        html += '<h4> URL en GitHub: <a href="' + project.URL + '">' + project.URL + '</a></h4>'
        html += '<h4># ficheros Python: ' + project.TotalFiles + '</h4>'
        total_files = 0
        for files in File.objects.filter(ProjectName = project):
            total_files += 1
        html += '<h4># ficheros afectados: ' + str(total_files) + '</h4>'
        percen = float(total_files)/float(project.TotalFiles)
        html += '<h4>% ficheros afectados: ' + str(float(percen)*100)[0:5] + ' %</h4>'
        total_bears = 0
        for bears in Bear.objects.filter(ProjectName = project):
            total_bears += 1
        html += '<hr>'
        html += '<div class="page-header"><h4>Ficheros analizados</h4></div>'
        html += '<div id="new' + str(fileId) + '" style="display:none;">'
        file_list = []
        for files in File.objects.filter(ProjectName = project):
            total_bears = 0
            bear_list = []
            for bears in Bear.objects.filter(FileName = files):
                total_bears += 1
                if not bears.Bear in bear_list:
                    bear_list.append(bears.Bear)
            file_list.append((total_bears, bear_list, files.Name))
        file_list.sort(key=lambda file_list: file_list[0], reverse=True)
        html += '<div class="col-md-12"><table class="table table-striped">'
        html += '<thead><tr><th>Fichero</th><th># Bears</th><th>Tipo de Bears encontrados</th></tr></thead><tbody>'
        for i in file_list:
            bear2text = ""
            for j in i[1]:
                bear2text += '<a href="http://localhost:8000/analyzer/show/?item=' + j + '&option=3">' + j + '</a>' + ', '
            html += '<tr><td><a href="http://localhost:8000/analyzer/file/' + k + '/' + str(i[2]) + '">' + str(i[2]) + '</a></td><td>' + str(i[0]) + '</td><td>' + bear2text+ '</td></tr>'
        html += '</tbody></table></div>'
        html += '</div>'
        html += '<a href="javascript:dispHandle(new' + str(fileId) + ')"><b>Mostrar/ocultar ficheros analizados en ' + project_name + '</b></a>'
        fileId += 1

    # Carga de datos en template
    template = loader.get_template('process.html')
    return HttpResponse(template.render(Context({'html':html})))

def processURL(request):
    # Tomar el path del fichero introducido    
    resource = request.GET
    line = resource['url']

    # Asegurarse de que el string no tenga espacios a los lados
    stripped_line = line.strip()

    # Comprobar que se trata de una url de GitHub
    url_line = urlparse(stripped_line)
    if url_line.netloc != "github.com":
        # Si no es una url valida, lanzar mensaje de error
        print "UrlError: La linea '" + stripped_line + "' no pertenece a una url de un proyecto de GitHub"
        html = u''
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error en URL</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>La URL proporcionada no es correcta. Pruebe a buscar el proyecto en <a href="https://github.com/">GitHub</a>. Recuerde que la estructura b&aacute;sica de las URLs debe ser: https://github.com/AUTOR/PROYECTO.git</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    try:
        r = requests.get(stripped_line)
        r.raise_for_status()
    except HTTPError:
        html = u''
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de b&uacute;squeda</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>La URL proporcionada no es correcta. Pruebe a buscar el proyecto en <a href="https://github.com/">GitHub</a>. Recuerde que la estructura b&aacute;sica de las URLs debe ser: https://github.com/AUTOR/PROYECTO.git</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    # Obtener el nombre del proyecto
    project_name = url_line.path.split(".")[0]
    project_name = project_name[1:len(project_name)]

    # Cambar el directorio de trabajo, para que se tome la ruta especificada en settings
    os.chdir(settings.CONSTANTS['workspace'])
   
    # Descargar en proyecto con git
    call(["git","clone",stripped_line])

    #Obtener la ruta al fichero descargado (dentro del directorio local)
    project_path = "/tmp/" + project_name.split("/")[1]
    python_files = project_path + "/**.py"

    # Ficheros Python del proyecto
    lstDir = os.walk(project_path)
    total_py_files = 0        

    for root, dirs, files in lstDir:
        for myfile in files:
            (name, ext) = os.path.splitext(myfile)
            if(ext == ".py"):
                total_py_files += 1
    
    # Comprobar la existencia del proyecto. Si existe, se sobreescribe
    if Project.objects.filter(Name = project_name, URL = stripped_line).exists():
        Project.objects.filter(Name = project_name, URL = stripped_line).delete()
        myProject = Project(Name = project_name, URL = stripped_line, TotalFiles = str(total_py_files))
        myProject.save()
    else:
        myProject = Project(Name = project_name, URL = stripped_line, TotalFiles = str(total_py_files))
        myProject.save()

    print "Analizando " + project_name + "..."

    # Ejecutar COALA sobre el proyecto y guardar la salida en un fichero JSON para su posterior analisis
    p1 = Popen(["coala", "--json", "--files", python_files], stdout=PIPE)
    p2 = Popen(["tee", settings.CONSTANTS['jsonFile']], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]

    # Una vez analizado y creado el fichero JSON, elimino el proyecto de disco local
    shutil.rmtree(project_path)

    # Abrir el fichero JSON
    try:
        with open(settings.CONSTANTS['jsonFile']) as data_file:
            data = json.load(data_file)
    except ValueError:
        if Project.objects.filter(Name = project_name, URL = stripped_line).exists():
            Project.objects.filter(Name = project_name, URL = stripped_line).delete()
        html = u''
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de b&uacute;squeda</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>Se ha producido un error de lectura de los datos analizados.</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    print "Procesando JSON..." 

    # Extraer los campos del fichero JSON
    for i in range(0, len(data["results"]["default"])):
        default = i
        additional_info = data["results"]["default"][i]["additional_info"]
        affected_code = data["results"]["default"][i]["affected_code"]

        # Si no hay affected_code (para Bears que analizan el proyecto desde otra perspectiva), se rellena con "None"
        try:
            affected_code_file = data["results"]["default"][i]["affected_code"][0]["file"]
            var_file = affected_code_file.split("/")
            analyzed_file = var_file[len(var_file)-1].strip()
            url_file = "https://github.com/" + project_name + "/blob/master/" + analyzed_file
            affected_code_start_line = data["results"]["default"][i]["affected_code"][0]["start"]["line"]
            url_start_line = url_file + "#L" + str(affected_code_start_line)
            if str(affected_code_start_line).strip() == "None":
                affected_code_start_line = 0
                url_start_line = "None"            
            affected_code_end_line = data["results"]["default"][i]["affected_code"][0]["end"]["line"]
            url_end_line = url_file + "#L" + str(affected_code_end_line)
            if str(affected_code_end_line).strip() == "None":
                affected_code_end_line = 0
                url_end_line = "None"
        except IndexError:
            affected_code_file = "None"
            analyzed_file = "None"
            url_file = "None"
            affected_code_start_line = 0
            url_start_line = "None"
            affected_code_end_line = 0
            url_end_line = "None"

        aspect = data["results"]["default"][i]["aspect"]
        confidence = data["results"]["default"][i]["confidence"]
        debug_msg = data["results"]["default"][i]["debug_msg"]
        diffs = data["results"]["default"][i]["diffs"]
        data_id = data["results"]["default"][i]["id"]
        message = data["results"]["default"][i]["message"]
        message_arguments = data["results"]["default"][i]["message_arguments"]
        message_base = data["results"]["default"][i]["message_base"]
        origin = data["results"]["default"][i]["origin"]
        severity = data["results"]["default"][i]["severity"]

        # Comprobar la existencia del fichero en la BBDD. Si no existe, guardar el nuevo fichero
        myProject = Project.objects.get(Name = project_name)
        try:
            myFile = File.objects.get(Name = analyzed_file, ProjectName = myProject)
        except File.DoesNotExist:
            newFile = File(Name = analyzed_file, URL = url_file, ProjectName = myProject, FilePath = affected_code_file)
            newFile.save()

        # Guardar los datos de la salida del Bear
        myFile = File.objects.get(Name = analyzed_file, ProjectName = myProject)
        newBear = Bear(Bear = origin, ProjectName = myProject, FileName = myFile, StartLine = affected_code_start_line, StartLineURL = url_start_line, EndLine = affected_code_end_line, EndLineURL = url_end_line, Aspect = aspect, Confidence = confidence, DebugMsg = debug_msg, Diffs = str(diffs), BearId = str(data_id), Message = message, MessageArguments = str(message_arguments), MessageBase = message_base, Severity = severity)
        newBear.save()

    # Preparar el codigo html para mostrar los datos del proyecto analizado (ver projectInfo)
    html = u''
    project = Project.objects.get(Name=project_name)
    html += '<div class="page-header"><h3><b><a href="http://localhost:8000/analyzer/project/' + project_name + '">' + project_name + '</a></b></h3></div>'
    html += '<h4> URL en GitHub: <a href="' + project.URL + '">' + project.URL + '</a></h4>'
    html += '<h4># ficheros Python: ' + project.TotalFiles + '</h4>'
    total_files = 0
    for files in File.objects.filter(ProjectName = project):
        total_files += 1
    html += '<h4># ficheros analizados: ' + str(total_files) + '</h4>'
    percen = float(total_files)/float(project.TotalFiles)
    html += '<h4>% ficheros afectados: ' + str(float(percen)*100)[0:5] + ' %</h4>'
    total_bears = 0
    for bears in Bear.objects.filter(ProjectName = project):
        total_bears += 1
    html += '<hr>'
    html += '<div class="page-header"><h4>Ficheros analizados</h4></div>'
    html += '<div id="newFiles" style="display:none;">'
    file_list = []
    for files in File.objects.filter(ProjectName = project):
        total_bears = 0
        bear_list = []
        for bears in Bear.objects.filter(FileName = files):
            total_bears += 1
            if not bears.Bear in bear_list:
                bear_list.append(bears.Bear)
        file_list.append((total_bears, bear_list, files.Name))
    file_list.sort(key=lambda file_list: file_list[0], reverse=True)
    html += '<div class="col-md-12"><table class="table table-striped">'
    html += '<thead><tr><th>Fichero</th><th># Bears</th><th>Tipo de Bears encontrados</th></tr></thead><tbody>'
    for i in file_list:
        bear2text = ""
        for j in i[1]:
            bear2text += '<a href="http://localhost:8000/analyzer/show/?item=' + j + '&option=3">' + j + '</a>' + ', '
        html += '<tr><td><a href="http://localhost:8000/analyzer/file/' + project_name + '/' + str(i[2]) + '">' + str(i[2]) + '</a></td><td>' + str(i[0]) + '</td><td>' + bear2text+ '</td></tr>'
    html += '</tbody></table></div>'
    html += '</div>'
    html += '<a href="javascript:dispHandle(newFiles)"><b>Mostrar/ocultar ficheros analizados en ' + project_name + '</b></a>'

    # Carga de datos en template
    template = loader.get_template('process.html')
    return HttpResponse(template.render(Context({'html':html})))

def search(request):

    # Muestra pagina de busqueda
    template = loader.get_template('search.html')
    return HttpResponse(template.render())

def showResults(request):
    # Tomar el path del fichero introducido    
    res = request.GET
    
    item = str(res['item'])
    option = str(res['option'])

    html = u''

    # En caso de buscar por proyecto
    if option == "1":
        if Project.objects.filter(Name = item).exists():
            myProject = Project.objects.get(Name = item)
            html += '<div class="panel-heading">'
            html += '<h3 align=center class="panel-title">' + myProject.Name + '</h3></div>'
            html += '<div class="panel-body">'
            html += '<h4> URL en GitHub: <a href="' + myProject.URL + '">' + myProject.URL + '</a></h4>'
            html += '<h4>Ficheros Python: ' + myProject.TotalFiles + '</h4>'
            total_files = 0
            for files in File.objects.filter(ProjectName = myProject):
                total_files += 1
            html += '<h4>Ficheros analizados: ' + str(total_files) + '</h4>'
            percen = float(total_files)/float(myProject.TotalFiles)
            html += '<h4>% ficheros afectados: ' + str(float(percen)*100)[0:5] + ' %</h4>'
            total_bears = 0
            for bears in Bear.objects.filter(ProjectName = myProject):
                total_bears += 1
            html += '<h4>Bears almacenados: ' + str(total_bears) + '</h4>'
            html += '<h4><a href="http://localhost:8000/analyzer/project/' + myProject.Name + '">M&aacute;s informaci&oacute;n >>></a></h4>'
            html += '</div>'
        else:
            html += '<h3> El proyecto ' + item + ' no existe en la BBDD</h3>'
            template = loader.get_template('show.html')
            return HttpResponse(template.render(Context({'html':html, 'item':item})))

    # En caso de buscar por fichero
    elif option == "2":
        if File.objects.filter(Name = item).exists():
            for files in File.objects.filter(Name = item):
                project = files.ProjectName
                projectname = project.Name
                html += '<div class="panel-heading">'
                html += '<h3 align=center class="panel-title">' + item + '</h3></div>'
                html += '<div class="panel-body">'
                html += '<h4>Nombre del proyecto: <a href="http://localhost:8000/analyzer/project/' + projectname + '">' + projectname + '</a></h4>'
                html += '<h4>URL en GitHub: <a href="' + files.URL + '">' + files.URL + '</a></h4>'
                html += '<h4>Path local: ' + files.FilePath + '</h4>'
                total_bears = 0
                for bears in Bear.objects.filter(ProjectName = project, FileName = files):
                    total_bears += 1
                html += '<h4>Bears almacenados: ' + str(total_bears) + '</h4>'
                html += '<h4><a href="http://localhost:8000/analyzer/file/' + project.Name + '/' + item + '">M&aacute;s informaci&oacute;n >>></a></h4>'
                html += '</div>'
        else:
            html += '<h3> El fichero ' + item + ' no existe en la BBDD</h3>'
            template = loader.get_template('show.html')
            return HttpResponse(template.render(Context({'html':html, 'item':item})))

    # En caso de buscar por bear
    elif option == "3":
        if Bear.objects.filter(Bear = item).exists():
            for bear in Bear.objects.filter(Bear = item):
                project = bear.ProjectName
                projectname = project.Name
                name = project.Name
                files = bear.FileName
                filename = files.Name
                html += '<div class="panel-heading">'
                html += '<h3 align=center class="panel-title">' + item + '</h3></div>'
                html += '<div class="panel-body">'
                html += '<h4>Nombre del proyecto: <a href="http://localhost:8000/analyzer/project/' + projectname + '">' + projectname + '</a></h4>'
                html += '<h4>Nombre del fichero: <a href="http://localhost:8000/analyzer/file/' + projectname + '/' + filename + '">' + filename + '</a></h4>'                
                html += '<h4>L&iacute;nea inicial fichero: <a href="' + bear.StartLineURL + '">' + str(bear.StartLine) + '</a></h4>'
                html += '<h4>Message: ' + bear.Message + '</h4>'
                html += '<h4>Severity: ' + str(bear.Severity) + '</h4>'
                html += '<h4><a href="http://localhost:8000/analyzer/bear/' + bear.BearId + '">M&aacute;s informaci&oacute;n >>></a></h4>'
                html += '</div>'
        else:
            html += '<h3> El bear ' + item + ' no existe en la BBDD</h3>'
            template = loader.get_template('show.html')
            return HttpResponse(template.render(Context({'html':html, 'item':item})))

    # En caso de no especificar ninguna (error)
    else:
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de b&uacute;squeda</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>No se ha especificado una opci&oacute;n de b&uacute;squeda v&aacute;lida.</h4>'
        html += '</div>'

        template = loader.get_template('error.html')
        return HttpResponse(template.render(Context({'html':html})))

    # Cargar datos en template
    template = loader.get_template('show.html')
    return HttpResponse(template.render(Context({'html':html, 'item':item})))

def removeProject(request, resource):
    html = u''

    # Comprobar la existencia del proyecto. Si existe, se sobreescribe
    if Project.objects.filter(Name = resource).exists():
        Project.objects.filter(Name = resource).delete()       
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Eliminaci&oacute;n completada</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>Se ha eliminado el proyecto ' + resource + ' de la base de datos.</h4>'
        html += '</div>'
    else:
        html += '<div class="panel-heading">'
        html += '<h3 align=center class="panel-title">Error de eliminaci&oacuten</h3></div>'
        html += '<div class="panel-body">'
        html += '<h4>El proyecto ' + resource + ' no existe en la base de datos.</h4>'
        html += '</div>'

    template = loader.get_template('remove.html')
    return HttpResponse(template.render(Context({'html':html})))
