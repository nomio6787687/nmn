from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse, HttpResponse
import json
from labb.settings import *
from django.views.decorators.csrf import csrf_exempt


def gettime(request):
    jsons = json.loads(request.body)
    action = jsons['action']

    today = datetime.now()
    data = [{'datetime':today}]
    resp = sendResponse(request, 200, data, action)
    return resp
# gettime

def dt_register(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    firstname = jsons['firstname']
    lastname = jsons['lastname']
    email = jsons['email']
    passw = jsons['passw']

    myCon = connectDB()
    cursor = myCon.cursor()
    
    query = F"""SELECT COUNT(*) AS usercount FROM t_user 
            WHERE email = '{email}' AND enabled = 1"""
    
    cursor.execute(query)
    columns = cursor.description
    respRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if respRow[0]['usercount'] == 1:
        data = [{'email':email}]
        resp = sendResponse(request, 1000, data, action)
    else:
        token = generateStr(12)
        query = F"""INSERT INTO public.t_user(
	email, lastname, firstname, passw, regdate, enabled, token, tokendate)
	VALUES ('{email}', '{lastname}', '{firstname}', '{passw}'
    , NOW(), 0, '{token}', NOW() + interval \'1 day\');"""
        cursor1 = myCon.cursor()
        cursor1.execute(query)
        myCon.commit()
        cursor1.close()
        data = [{'email':email, 'firstname':firstname, 'lastname': lastname}]
        resp = sendResponse(request, 1001, data, action)

    return resp
# dt_register

@csrf_exempt
def checkService(request):
    if request.method == "POST":
        try :
            jsons = json.loads(request.body)
        except json.JSONDecodeError:
            result = sendResponse(request, 3003, [], "no action")
            return JsonResponse(json.loads(result))
        action = jsons['action']

        if action == 'gettime':
            result = gettime(request)
            return JsonResponse(json.loads(result))
        elif action == 'register':
            result = dt_register(request)
            return JsonResponse(json.loads(result))
        else:
            result = sendResponse(request, 3001, [], action)
            return JsonResponse(json.loads(result))
    else:
        result = sendResponse(request, 3002, [], "no action")
        return JsonResponse(json.loads(result))
#checkService

