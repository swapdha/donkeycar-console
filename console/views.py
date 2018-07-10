from django.shortcuts import render

# Django
from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.http import JsonResponse
import simplejson as json
import requests
from .models import remarks
from .models import credentials
from .models import github
from .models import controller
import subprocess
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.conf import settings
from os import listdir
from os.path import isfile, join, isdir
from .models import Jobs
from django.db import IntegrityError
import time
import json
from django.http import JsonResponse
from django.shortcuts import redirect

import requests
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect
from datetime import datetime
import os
import os.path
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from datetime import datetime
from django.urls import reverse

import pytz
import boto3
import base64
from operator import itemgetter
import glob
from .models import remarks
from .models import credentials
from .models import github
import subprocess

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
import zipfile

from django.http import HttpResponse
import io
from django import template

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from console.models import *



def credentials_check(f):
    def wrap(request, *args, **kwargs):
        count = credentials.objects.filter().count()
        count1 = github.objects.filter().count()

        if (count != 0 and count1 != 0):
            result = credentials.objects.raw('SELECT * FROM console_credentials LIMIT 1;')
            global AWS_ACCESS_KEY_ID
            global AWS_SECRET_ACCESS_KEY
            AWS_ACCESS_KEY_ID = result[0].aws_access_key_id
            AWS_SECRET_ACCESS_KEY = result[0].aws_secret_access_key
        else:
            return HttpResponseRedirect("/settings/")
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def index(request):

    return HttpResponseRedirect('/home/')




@credentials_check
def drive(request):

       try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
       except:
            updated_local_directory_name = ''
       print(request.POST)
       global proc
       print("hey")
       if 'start' in request.POST:
           print("start")
           try:
               exist_controller = controller.objects.latest('id')
               controller_mode = exist_controller.training
           except:
               controller_mode = ''

           if controller_mode != '':

              proc = subprocess.Popen(["python", "/home/pi/"+updated_local_directory_name+"/manage.py", "drive",controller_mode])
           else:
              proc = subprocess.Popen(["python", "/home/pi/"+updated_local_directory_name+"/manage.py", "drive"])

       # proc = subprocess.Popen(["python", "/home/pi/d2/manage.py", "drive"])

       elif 'stop' in request.POST:
           try:
             proc.kill()
           except:
               print("no proc")


       template = loader.get_template('console/home.html')
       return HttpResponse(template.render({}, request))

def kill_proc(request):
    try:
       autopilot_proc.kill()
    except:
        print("no autopilot ptoc")
    return HttpResponseRedirect('/jobs/')


@credentials_check
def save_local_directory(request):
        message = ""
        updated_repo = ""
        try:
            credential = credentials.objects.latest('id')
            aws_key_id = credential.aws_access_key_id
        except:
            aws_key_id = ''
        if request.method == "POST":
            local_directory_name = request.POST.get('local_directory')

            if local_directory_name != None:

                try:
                    exist_local_directory= local_directory.objects.latest('id')
                    local_directory.objects.filter(id=exist_local_directory.id).update(name=local_directory_name)

                    message = "Local Directory  has been updated"

                except:
                    new_local_directory = local_directory(name=local_directory_name)
                    new_local_directory.save()
                    message = "Local Directory has been saved"
        try:
            updated_name = github.objects.latest('id')
            updated_repo_name = updated_name.name
            updated_extension = updated_name.extension
        except:
            updated_repo_name = ''
            updated_extension = ''
        try:
            updated_controller = controller.objects.latest('id')
            updated_training_controller = updated_controller.training
        except:
            updated_training_controller = ''
        try:
            updated_local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = updated_local_directory.name
        except:
            updated_local_directory_name = ''

        template = loader.get_template('console/local_directory.html')
        return HttpResponse(template.render({'status': message,'local_directory': updated_local_directory_name, 'training_controller': updated_training_controller,
                                             'updated_extension': updated_extension, 'updated_repo': updated_repo_name,
                                             'AWS_KEY': aws_key_id}, request))


@credentials_check
def display_data_folders(request):
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''

        list_data = os.popen('ls ~/'+updated_local_directory_name+'/data/').read()

        directories = list_data.split()
        dataFolders = []
        print(directories)
        for dir in directories:

            direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/' + dir).read()
            direcPath = direcPath.split()

            if os.path.isdir(direcPath[0]):

                if os.path.exists(direcPath[0] + '/donkeycar-console.json') == True:
                    with open(direcPath[0] + '/donkeycar-console.json', 'r') as outfile:
                        data = json.load(outfile)
                        print(data)
                    tmp = data["no"]
                    noImages = os.popen('ls -l ~/' + updated_local_directory_name + '/data/' + dir + ' | grep .jpg | wc -l').read()
                    data["no"] = noImages

                    with open(direcPath[0] + '/donkeycar-console.json', 'w') as jsonFile:
                        json.dump(data, jsonFile)
                else:
                    with open(direcPath[0] + '/donkeycar-console.json', 'w') as outfile:
                        noImages = os.popen('ls -l ~/'+updated_local_directory_name+'/data/' + dir + ' | grep .jpg | wc -l').read()
                        noImages.strip()
                        print(noImages)
                        noImages = int(noImages)

                        year = os.popen('date +"%Y"').read()
                        time = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $8}'").read()
                        month = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $6}'").read()
                        day = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $7}'").read()
                        date = year + " " + month + " " + day + " " + time
                        d = datetime.strptime(date, '%Y\n %b\n %d\n %H:%M\n')
                        d = d.strftime('%Y-%m-%d %H:%M')
                        json.dump({"name": dir, "no": noImages, "date": d, "remarks": []}, outfile)

                with open(direcPath[0] + '/donkeycar-console.json', 'r') as result:
                    data = json.load(result)
                    dataFolders.append(data)

        dataFolders.sort(key=itemgetter('date'), reverse=True)
        print(dataFolders)
        context = {
            'result': dataFolders,
        }

        return render(request, 'console/data_folders.html', context)

def getfiles(request):
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''
        result = request.GET.get('dir', '')
        print(result)
        zip_io = io.BytesIO()
        direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/').read()
        direcPath = direcPath.split()
        with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
            for f in os.listdir(direcPath[0] + result):
                backup_zip.write(direcPath[0] + result + '/' + f)

        response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % result + ".zip"
        response['Content-Length'] = zip_io.tell()
        return response

def delete_data(request):
    name= request.GET.get('name', '')
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''
    os.system('sudo rm -r ~/'+updated_local_directory_name+'/data/'+name)
    return HttpResponseRedirect('/data/')

def delete_data_folder_comment(request):

    comment= request.GET.get('comment', '')
    name= request.GET.get('name', '')
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''

    if (id and name):
        direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/' + name).read()
        direcPath = direcPath.split()
        with open(direcPath[0] + '/donkeycar-console.json', 'r') as outfile:
            data = json.load(outfile)
        with open(direcPath[0] + '/donkeycar-console.json', 'w') as writefile:
            (data['remarks']).remove(comment)
            json.dump(data, writefile)

    return HttpResponseRedirect('/data/')

def add_data_folder_comment(request):


    data_name = request.POST['name']
    print(data_name)
    data_comment = request.POST['var']
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''
    direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/' + data_name).read()
    direcPath = direcPath.split()
    with open(direcPath[0] + '/donkeycar-console.json', 'r') as outfile:
            data = json.load(outfile)
            print(data['remarks'])
            print(len(data['remarks']))
    with open(direcPath[0] + '/donkeycar-console.json', 'w') as writefile:
            (data['remarks']).append(data_comment)
            json.dump(data, writefile)
    return HttpResponse('success')
def sizify(value):

    # value = ing(value)
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)
@credentials_check
def list_jobs(request):
       jobs = Jobs.objects.order_by('-date')[:30]
       for job in jobs:
           import re
           list = re.findall("'(.*?)'", job.tubs)
           job.tubs = list


           if job.size != 'N/A':
              job.size=sizify(int(job.size))
       context = {
         'models': jobs,

       }
       template = loader.get_template('console/jobs.html')
       return HttpResponse(template.render(context, request))



def save_controller_settings(request):
    message = ""
    updated_repo = ""
    try:
        credential = credentials.objects.latest('id')
        aws_key_id = credential.aws_access_key_id
    except:
        aws_key_id = ''
    if request.method == "POST":
        training_controller = request.POST.get('training_controller')

        if training_controller != None :
            try:
                exist_controller = controller.objects.latest('id')
                controller.objects.filter(id=exist_controller.id).update(training=training_controller)

                message = "Controller settings have been updated"
            except Exception as e:

                new_controller = controller(
                    training=training_controller)
                new_controller.save()
                message = "Controller settings have been updated"




    try:
        updated_name = github.objects.latest('id')
        updated_repo_name = updated_name.name
        updated_extension = updated_name.extension
    except:
        updated_repo_name = ''
        updated_extension = ''
    try:
        updated_controller = controller.objects.latest('id')
        updated_training_controller = updated_controller.training
    except:
        updated_training_controller = ''

    try:
        updated_local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = updated_local_directory.name
    except:
        updated_local_directory_name = ''

    template = loader.get_template('console/controller.html')
    return HttpResponse(template.render({'local_directory': updated_local_directory_name,'controller_message': message,'training_controller':updated_training_controller,'updated_extension':updated_extension,'updated_repo':updated_repo_name,'AWS_KEY':aws_key_id}, request))


@credentials_check
def list_jobs_success(request):

       jobs = Jobs.objects.order_by('-date')[:30]
       for job in jobs:
           import re
           list = re.findall("'(.*?)'", job.tubs)
           job.tubs = list
           if job.size != 'N/A':
              job.size=sizify(int(job.size))
       context = {
         'models': jobs,
        'success': "New Job Added !"

       }
       template = loader.get_template('console/jobs.html')
       return HttpResponse(template.render(context, request))




def save_credentials(request):
    message = ""
    if request.method == "POST":

        UPDATED_AWS_ACCESS_KEY_ID = request.POST.get('key1')
        UPDATED_AWS_SECRET_ACCESS_KEY = request.POST.get('key2')

        if ((UPDATED_AWS_ACCESS_KEY_ID != None) & (UPDATED_AWS_SECRET_ACCESS_KEY != None)):
            client = boto3.client('s3', aws_access_key_id=UPDATED_AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=UPDATED_AWS_SECRET_ACCESS_KEY)
            sts = boto3.client('sts', aws_access_key_id=UPDATED_AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=UPDATED_AWS_SECRET_ACCESS_KEY)
            try:
                response = sts.get_caller_identity()

                try:
                    client.create_bucket(Bucket=UPDATED_AWS_ACCESS_KEY_ID.lower())
                    conn = S3Connection(aws_access_key_id=UPDATED_AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=UPDATED_AWS_SECRET_ACCESS_KEY)

                    bucket = conn.get_bucket(UPDATED_AWS_ACCESS_KEY_ID.lower())
                    k = bucket.new_key('models/')
                    k.set_contents_from_string('')
                    k = bucket.new_key('data/')
                    k.set_contents_from_string('')
                    count = credentials.objects.filter().count()
                    if count == 0:
                        credential = credentials(
                            aws_access_key_id=UPDATED_AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=UPDATED_AWS_SECRET_ACCESS_KEY)
                        credential.save()
                        message = "Credentials have been updated !"



                    else:
                        credential = credentials.objects.latest('id')
                        credentials.objects.filter(id=credential.id).update(aws_access_key_id=UPDATED_AWS_ACCESS_KEY_ID,
                                                                            aws_secret_access_key=UPDATED_AWS_SECRET_ACCESS_KEY)
                        message = "Credentials have been updated !"
                except Exception as e1:
                    print(e1)
                    message = "Can't Create S3 bucket: Check IAM Permissions and re-enter your credentials"

            except Exception as e:
                print(e)
                message = "Incorrect Credentials"


    try:
        credential = credentials.objects.latest('id')
        aws_key_id = credential.aws_access_key_id
    except:
        aws_key_id = ''
        updated_repo =""
    try:
        updated_name = github.objects.latest('id')
        updated_repo_name = updated_name.name
        updated_extension = updated_name.extension
    except:
        updated_repo_name = ''
        updated_extension = ''
    try:
        updated_controller = controller.objects.latest('id')
        updated_training_controller = updated_controller.training
    except:
        updated_training_controller = ''

    try:
        updated_local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = updated_local_directory.name
    except:
        updated_local_directory_name = ''



    template = loader.get_template('console/credentials.html')
    return HttpResponse(template.render({'message': message,'local_directory': updated_local_directory_name,'training_controller':updated_training_controller,'AWS_KEY': aws_key_id,'updated_repo':updated_repo_name,'updated_extension':updated_extension}, request))






def save_github_repo(request):
    message = ""
    updated_repo = ""
    try:
        credential = credentials.objects.latest('id')
        aws_key_id = credential.aws_access_key_id
    except:
        aws_key_id = ''
    if request.method == "POST":
        repo = request.POST.get('repo')
        extension = request.POST.get('extension')

        print(repo)

        result = os.system('git ls-remote  ' + repo)
        if result == 0:
            if repo != None:
                try:
                   exist_repo = github.objects.latest('id')
                   github.objects.filter(id=exist_repo.id).update(name=repo)
                   github.objects.filter(id=exist_repo.id).update(extension=extension)
                   message = "Github Repository has been updated"
                except:
                   new_github = github(name=repo,extension=extension)
                   new_github.save()
                   message = "Github Repository has been updated"


        else:
            message = "Please enter a git repository"
    try:
        updated_name = github.objects.latest('id')
        updated_repo_name = updated_name.name
        updated_extension = updated_name.extension
    except:
        updated_repo_name = ''
        updated_extension = ''
    try:
        updated_controller = controller.objects.latest('id')
        updated_training_controller = updated_controller.training
    except:
        updated_training_controller = ''

    try:
        updated_local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = updated_local_directory.name
    except:
        updated_local_directory_name = ''


    template = loader.get_template('console/github.html')
    return HttpResponse(template.render({'status': message,'local_directory': updated_local_directory_name,'training_controller':updated_training_controller,'updated_extension':updated_extension,'updated_repo':updated_repo_name,'AWS_KEY':aws_key_id}, request))


def delete_remark(request):
    id= request.GET.get('id', '')
    remarks.objects.filter(id=id).delete()
    return HttpResponseRedirect('/jobs/')
def delete_job(request):
    id= request.GET.get('id', '')
    Jobs.objects.filter(id=id).delete()
    return HttpResponseRedirect('/jobs/')


def add_remark(request):

    job_id =  request.POST['id']
    print(job_id)
    comment = request.POST['var']
    print(comment)
    remark = remarks(remark=comment)
    remark.save()
    job = Jobs.objects.get(id=job_id)
    job.Comments.add(remark)
    return HttpResponse('success')

def verify_logs(state,id,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):

            conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(AWS_ACCESS_KEY_ID.lower())
            s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            for key in bucket.list():

                if key.name == 'job_'+ str(id) +'.log':
                    #url = "https://s3.console.aws.amazon.com/s3/object/"+AWS_ACCESS_KEY_ID.lower()+"/"+ key.name
                    url_to_download= "https://s3.amazonaws.com/"+AWS_ACCESS_KEY_ID.lower()+"/"+ key.name
                    Jobs.objects.filter(id=id).update(log_url=url_to_download)
                    object_acl = s3.ObjectAcl(AWS_ACCESS_KEY_ID.lower(), key.name)
                    response = object_acl.put(ACL='public-read')


                if key.name == 'job_'+ str(id) +'_commands.log':
                    url1_to_download= "https://s3.amazonaws.com/"+AWS_ACCESS_KEY_ID.lower()+"/"+ key.name
                    Jobs.objects.filter(id=id).update(commands_log_url=url1_to_download)
                    object_acl = s3.ObjectAcl(AWS_ACCESS_KEY_ID.lower(), key.name)
                    response1 = object_acl.put(ACL='public-read')


def cancel_request(request):
       client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
       id = request.GET.get('id', '')
       job = Jobs.objects.get(id=id)
       client.terminate_instances(
           InstanceIds=[
               job.instance_id
           ]
       )
       Jobs.objects.filter(id=id).update(state='Canceled')
       Jobs.objects.filter(id=id).update(duration='0')
       return HttpResponseRedirect('/jobs/')

@credentials_check
def update_status_by_id(request):
        client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
        now = datetime.now(pytz.utc)
        id = request.GET.get('id', '')
        job = Jobs.objects.get(id=id)
        verify_logs(job.state,job.id,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
        if job.request_id != "0":
                if now > job.date + timedelta(minutes=job.request_time):
                    try:
                        response = client.describe_spot_instance_requests(
                            SpotInstanceRequestIds=[
                                job.request_id
                            ]

                        )
                        value = response['SpotInstanceRequests'][0]['Status']['Code']
                        Jobs.objects.filter(id=job.id).update(request_state=value)
                        instance_id = response['SpotInstanceRequests'][0]['InstanceId']
                        Jobs.objects.filter(id=job.id).update(instance_id=instance_id)
                    except Exception as e:
                        print(e)


        now = datetime.now(pytz.utc)
        print("now",now)
        if job.state == 'Pending':
            if job.request_state == 'schedule-expired':
                Jobs.objects.filter(id=job.id).update(state='Failed')
                Jobs.objects.filter(id=job.id).update(duration='0')


            else:
                conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                bucket = conn.get_bucket(AWS_ACCESS_KEY_ID.lower())
                for key in bucket.list('models'):
                    name = key.name.split('/')
                    print(key)
                    date = key.last_modified
                    print(date)
                    print("job.date" + str(job.date))
                    try:
                        updated_repo = github.objects.latest('id')
                        extension= updated_repo.extension
                    except:
                        extension = ''

                    if extension != '' :
                       model_name = 'job_' + str(job.id)+ extension
                    else:
                       model_name = 'job_' + str(job.id)

                    if name[1] == model_name:
                        Jobs.objects.filter(id=job.id).update(state='Finished')
                        Jobs.objects.filter(id=job.id).update(size=key.size)
                        duration = parse_datetime(date) - job.date
                        hours, minutes, seconds = convert_timedelta(duration)
                        time = str(minutes) + " m and " + str(seconds) + " s"
                        print(time)
                        Jobs.objects.filter(id=job.id).update(duration=time)
                    elif now > job.date + timedelta(minutes=job.instance_max):
                        Jobs.objects.filter(id=job.id).update(state='Failed')
                        Jobs.objects.filter(id=job.id).update(duration='0')

        job = Jobs.objects.get(id=id)

        if job.request_state == 'instance-terminated-by-user' and job.state == 'Pending':
            Jobs.objects.filter(id=job.id).update(state='Failed')
            Jobs.objects.filter(id=job.id).update(duration='0')






        return HttpResponseRedirect('/jobs/')



def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds
@credentials_check
def copy_local(request):
       id = request.GET.get('id', '')
       try:
           Local_directory = local_directory.objects.latest('id')
           updated_local_directory_name = Local_directory.name
       except:
           updated_local_directory_name = ''
       path = os.popen('echo ~/'+updated_local_directory_name+'/models/').read()
       path = path.split()
       try:
           updated_repo = github.objects.latest('id')
           extension = updated_repo.extension
       except:
           extension = ''
       if extension != '':
           model_name = 'job_' + str(id) + extension
       else:
           model_name = 'job_' + str(id)
       s3_data = {'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID, 'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY}

       url = "https://dconsole.proactivesystem.com.hk/downloadFromS3"
       headers = {'Content-type': 'application/json'}
       response = requests.post(url, data=json.dumps(s3_data), headers=headers)

       print(response.json())
       response_url = (response.json())['url']
       o = urlparse(response_url)
       key_path = o.path.split('/', 1)[1]
       s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
       if( os.path.exists(path[0]+model_name) == True ):
         print("it exists")
       else:
           s3.Object(AWS_ACCESS_KEY_ID.lower(),key_path.split('/', 1)[1] + '/' + model_name).download_file(path[0] + model_name)

       return HttpResponseRedirect('/jobs/')


@credentials_check
def autopilot(request):
        id = request.GET.get('id', '')
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''

        path = os.popen('echo ~/'+updated_local_directory_name+'/models/').read()
        path = path.split()
        try:
            updated_repo = github.objects.latest('id')
            extension = updated_repo.extension
        except:
            extension = ''
        if extension != '':
            model_name = 'job_' + str(id) + extension
        else:
            model_name = 'job_' + str(id)
        job_name = 'job_' + str(id)
        s3_data = {'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID, 'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY}

        url = "https://dconsole.proactivesystem.com.hk/downloadFromS3"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(s3_data), headers=headers)

        print(response.json())
        response_url = (response.json())['url']
        o = urlparse(response_url)
        key_path = o.path.split('/', 1)[1]
        s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        if (os.path.exists(path[0] + model_name) == True):
            print("it exists")
        else:
            s3.Object(AWS_ACCESS_KEY_ID.lower(), key_path.split('/', 1)[1] + '/' + model_name).download_file(
                path[0] + job_name)

        try:
           exist_controller = controller.objects.latest('id')
           controller_mode = exist_controller.autopilot
        except:
           controller_mode=''

        global autopilot_proc

        autopilot_proc = subprocess.Popen(["python", "/home/pi/"+updated_local_directory_name+"/manage.py", "drive", "--model", "/home/pi/"+updated_local_directory_name+"/models/" + job_name])
        return HttpResponseRedirect('/jobs/')

        #os.system('python ~/d2/manage.py drive --model ~/d2/models/' + model_name)
def get_car_status_autopilot(request):
    try:
        poll = autopilot_proc.poll()
        if poll == None:
            responseCode = 200
            responseMessage = 'Your process is up and running!'
            response = 'Autopilot'

        else:
            responseMessage = 'Your process is down!'
            response = ''
    except:
        responseMessage = 'Your process is down!'
        print(responseMessage)
        response = ''

    return HttpResponse(response)


def get_car_status_training(request):
    try:
        poll = proc.poll()
        if poll == None:

            responseCode = 200
            responseMessage = 'Your process is up and running!'
            response = 'Training'
            return HttpResponse(response)
        else:
            responseCode = 604
            responseMessage = 'Your process is down!'
            response = ''

            print(responseMessage)
    except:

        responseMessage = 'Your process is down!'
        response = ''

    return HttpResponse(response)
@credentials_check
def home(request):
       template = loader.get_template('console/home.html')
       return HttpResponse(template.render({}, request))

@credentials_check
def create_job(request):
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''
        choices = ['t2.micro', 't2.medium', 'g2.2xlarge', 'g2.8xlarge', 'p2.xlarge', 'p3.2xlarge', 'p3.8xlarge']
        errorMessage = ""
        conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        bucket = conn.get_bucket(AWS_ACCESS_KEY_ID.lower())
        message = ""
        job_number = Jobs.objects.filter().count()
        if request.method == "POST":
            checked_data = request.POST.getlist('chk[]')
            instance_type = request.POST.get('choice')
            availability_zone = request.POST.get('AZ')
            max_time = request.POST.get('max_time')
            request_time = request.POST.get('request_time')

            print(availability_zone)
            print(instance_type)
            print(max_time)
            print(request_time)

            if max_time == '':
                max_time = 15
            if request_time == '':
                request_time = 2
            try:
               availability_zone = availability_zone.split()
               price = availability_zone[1]
            except:
                print("no avai")

            print(checked_data)
            if len(checked_data) == 0 or int(max_time) >= 60:
                if len(checked_data) == 0 and int(max_time) >= 60:
                    message = " No selected items and EC2 Termination Time maximum must be 60 minutes "
                elif len(checked_data) == 0:
                    message = " No selected items"
                elif int(max_time) >= 60:
                    message = "EC2 Termination Time maximum must be 60 minutes "


            else:
                job = Jobs(
                    tubs=checked_data,
                    state="Pending",
                    job_number=job_number + 1,
                    instance=instance_type,
                    price=price,
                    availability_zone=availability_zone[0],
                    instance_max=max_time)
                job.save()
                selected_data = ""
                dataPath = os.popen('echo ~/'+updated_local_directory_name+'/data/').read()
                dataPath = dataPath.split()

                for dir in checked_data:
                    selected_data += " " + dir
                    print(selected_data)
                if len(selected_data) != 0:

                    try:
                        updated_repo = github.objects.latest('id')
                        extension= updated_repo.extension
                    except:
                        extension = ''
                    if extension != '' :
                       model_name = 'job_' + str(job.id)+ extension
                    else:
                       model_name = 'job_' + str(job.id)

                    job_name = 'job_' + str(job.id)

                    os.chdir(dataPath[0])
                    current_path = os.popen('pwd').read()
                    print(current_path)
                    os.system('tar -zcf   job_' + str(job.id) + '.tar.gz ' + selected_data)
                    tarfile_size = os.popen("ls -sh job_" + str(job.id) + ".tar.gz  | awk '{print $1}'").read()
                    print(tarfile_size)
                    Jobs.objects.filter(id=job.id).update(tarfile_size=tarfile_size)

                    current_path = os.popen('pwd').read()
                    current_path = current_path.split()
                    s3_data = {'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID, 'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY}

                    url = "https://dconsole.proactivesystem.com.hk/uploadToS3"
                    headers = {'Content-type': 'application/json'}
                    response = requests.post(url, data=json.dumps(s3_data), headers=headers)

                    print(response.json())
                    response_url = (response.json())['url']
                    o = urlparse(response_url)
                    path = o.path.split('/', 1)[1]
                    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                    tarfile_name = 'job_' + str(job.id) + '.tar.gz'
                    s3.meta.client.upload_file(os.path.join(current_path[0], tarfile_name), AWS_ACCESS_KEY_ID.lower(),
                                               path.split('/', 1)[1] + '/' + tarfile_name)

                    if instance_type != '':
                        termination_time = (Jobs.objects.get(id=job.id)).instance_max
                        github_repo = github.objects.latest('id')

                        data = {'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID, 'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY,
                                'github_repo': github_repo.name, 'termination_time': termination_time,
                                'model_name': model_name, 'availability_zone': availability_zone[0], 'job_name':job_name,
                                'instance_type': instance_type, 'request_time': request_time}
                        url = "https://dconsole.proactivesystem.com.hk/launchEC2"
                        headers = {'Content-type': 'application/json'}
                        response = requests.post(url, data=json.dumps(data), headers=headers)
                        print(response.json())
                        Jobs.objects.filter(id=job.id).update(request_id=(response.json())['request_id'])
                        # response =launch_ec2_instance(job.id,job_name,instance_type,availability_zone[0],termination_time,request_time)
                        Jobs.objects.filter(id=job.id).update(date=datetime.now())
                        if "InvalidParameterValue" in response:
                            errorMessage = "This type of instance is invalid"
                            job.delete()
                        elif "UnauthorizedOperation" in response:
                            errorMessage = "Check your IAM Permissions"
                            job.delete()
                    else:
                        errorMessage = " Enter an instance type "
                        job.delete()
                    os.system('rm -r  job_' + str(job.id) + '.tar.gz ')
                    return HttpResponseRedirect('/jobs/success/')

        list_data = os.popen('ls ~/'+updated_local_directory_name+'/data/').read()
        directories = list_data.split()
        dataFolders = []
        print(directories)
        for dir in directories:

            direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/' + dir).read()
            direcPath = direcPath.split()

            if os.path.isdir(direcPath[0]):

                if os.path.exists(direcPath[0] + '/donkeycar-console.json') == True:
                    with open(direcPath[0] + '/donkeycar-console.json', 'r') as outfile:
                        data = json.load(outfile)
                        print(data)
                    tmp = data["no"]
                    noImages = os.popen('ls -l ~/' + updated_local_directory_name + '/data/' + dir + ' | grep .jpg | wc -l').read()
                    data["no"] = noImages

                    with open(direcPath[0] + '/donkeycar-console.json', 'w') as jsonFile:
                        json.dump(data, jsonFile)

                else:
                    with open(direcPath[0] + '/donkeycar-console.json', 'w') as outfile:
                        noImages = os.popen('ls -l ~/'+updated_local_directory_name+'/data/' + dir + ' | grep .jpg | wc -l').read()
                        noImages.strip()
                        noImages = int(noImages)
                        year = os.popen('date +"%Y"').read()
                        time = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $8}'").read()
                        month = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $6}'").read()
                        day = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $7}'").read()
                        date = year + " " + month + " " + day + " " + time
                        d = datetime.strptime(date, '%Y\n %b\n %d\n %H:%M\n')
                        d = d.strftime('%Y-%m-%d %H:%M')
                        json.dump({"name": dir, "no": noImages, "date": d, "remarks": []}, outfile)

                with open(direcPath[0] + '/donkeycar-console.json', 'r') as result:
                    data = json.load(result)
                    dataFolders.append(data)

        dataFolders.sort(key=itemgetter('date'), reverse=True)
        jobs = Jobs.objects.order_by('-date')[:30]
        for job in jobs:
           if job.size != 'N/A':
              job.size = sizify(int(job.size))


        context = {
            'models': jobs,
            'result': dataFolders,
            'message': message,
            'errorMessage': errorMessage,
            'choices': choices,

        }
        return render(request, 'console/create_job.html',context)



def delete_empty_folders(request):
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''

    list_data = os.popen('ls ~/' + updated_local_directory_name + '/data/').read()

    directories = list_data.split()
    print(directories)
    for dir in directories:

        direcPath = os.popen('echo ~/' + updated_local_directory_name + '/data/' + dir).read()
        direcPath = direcPath.split()

        if os.path.isdir(direcPath[0]):

                    noImages = os.popen(
                        'ls -l ~/' + updated_local_directory_name + '/data/' + dir + ' | grep .jpg | wc -l').read()
                    noImages.strip()
                    print(noImages)
                    noImages = int(noImages)

                    if noImages == 0 :
                        os.system('sudo rm -r '+direcPath[0])

    return HttpResponseRedirect('/data/')

def check_availability_zone(instance_type):
    client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,region_name='us-east-1')
    response = client.describe_spot_price_history(
    InstanceTypes=[
        instance_type
    ],
    ProductDescriptions=[
        'Linux/UNIX',
    ],
        MaxResults=6,

    )


    List= response['SpotPriceHistory']
    List.sort(key=itemgetter('SpotPrice'))

    models = { az['AvailabilityZone'] for az in List}
    listAZ = list(models)

    newlist=[]
    for l in listAZ:
        listA = [x for x in List if x['AvailabilityZone']== l]
        newlist.append(l + " " + listA[0]['SpotPrice']  + "/H")


    return newlist

def display_availability(request,name):
        response = check_availability_zone(name)
        return HttpResponse(response)


