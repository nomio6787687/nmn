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
    result = sendResponse(200, data, action)   
    return result

def getasuult(request):
    
    jsons = json.loads(request.body)
    action = jsons['action']
    try:
        onn = jsons['onn']
        hicheelkod = jsons['hicheelkod']
        huvilbar = jsons['huvilbar']
        asuulttoo = jsons["asuulttoo"]
    except Exception as e:
        action = action
        data = [{"error": str(e) + " key error"}]
        result = sendResponse(404, data, action)
        return result

    try: 
        myCon = connectDB()
        cursor = myCon.cursor()
        
        query = F"""SELECT t_asuult.aid, t_asuult.asuult, t_asuult.hicheelkod, t_asuult.onn, t_asuult.catkod, 
                            t_asuult.onoo, t_asuult.huvilbar, t_asuult.huvilbarid, t_asuult.minutes
                            FROM mttest.t_asuult
                            WHERE onn = {onn} AND hicheelkod = {hicheelkod} AND huvilbar = '{huvilbar}'
                            ORDER BY random()
                            LIMIT {asuulttoo}"""
        cursor.execute(query)
        columns = cursor.description
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()

        # print(respRow)
        for row in respRow:
            cursor = myCon.cursor()
        
            query = F"""SELECT hid,aid,hariult, correctans, hariultid 
                        FROM mttest.t_hariult 
                        WHERE aid = {row['aid']} 
                        ORDER BY hariultid"""
            cursor.execute(query)
            columns = cursor.description
            respRowHariult = [{columns[index][0]:column for index, 
                column in enumerate(value)} for value in cursor.fetchall()]
            
            row["hariult"] = respRowHariult

            cursor.close()

        disconnectDB(myCon)
        
        data = respRow
        result = sendResponse(200, data, action)
        return result
    except Exception as e:
        action = action
        data = [{"error": str(e) + " database error"}]
        result = sendResponse(404, data, action)
        return result
#getasuult


@csrf_exempt
def checkService(request):
    if request.method == "POST":
        try :
            jsons = json.loads(request.body)
        except json.JSONDecodeError:
            action = "wrong json"
            data = []
            result = sendResponse(request, 404, data, "action")
            return JsonResponse(json.loads(result))
        if 'action' in jsons:
            action = jsons['action']
            if action == 'gettime':
                
                result = gettime(request)
                return JsonResponse(json.loads(result))
            elif action == 'getasuult':
                
                result = getasuult(request)
                return JsonResponse(json.loads(result))
        else:
            data = {'action':"not found"}
            return JsonResponse(data)
    else:
        action = "method buruu"
        data = []
        result = sendResponse(404, data, action)
        return JsonResponse(json.loads(result))


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
    resultRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if resultRow[0]['usercount'] == 1:
        data = [{'email':email}]
        result = sendResponse(request, 1000, data, action)
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
        result = sendResponse(request, 1001, data, action)

    return result
# dt_register



