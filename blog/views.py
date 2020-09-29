import requests
import json
import base64
import datetime
import time

import os

from multiprocessing import Process
from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.alert import Alert

def offline(request):
    return render(request, 'blog/offline.html', {})

def schedule(request):
    return render(request, 'blog/index.html', {})

def post_list(request):
    request.session['BbRouter'] = "";
    return render(request, 'blog/post_list.html', {})


def fetchAssignment(BbRouter, request):
    
    with requests.Session() as s:
        
        nowDateTime = datetime.datetime.now()
        nowDateFormat = nowDateTime.strftime('%Y-%m-%dT00:00:00Z')
        getSch = s.get(
            'https://learn.hanyang.ac.kr/learn/api/v1/calendars/calendarItems?since='+nowDateFormat,
            headers={
                'Referer': 'https://learn.hanyang.ac.kr/ultra/calendar',
                'Cookie': 'BbRouter='+BbRouter['value'],
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
            }
        )
        
        getSchResult = getSch.json()
        
        if "results" not in getSchResult:
            return False
        else:
            schList = getSchResult['results']
            assignmentList = list(filter(lambda x: 'rawValue' in x['calendarNameLocalizable'] and x['itemSourceType'] != "blackboard.data.calendar.CalendarEntry", schList))
            
            request.session['BbRouter'] = {
                'name': 'BbRouter',
                'value': getSch.cookies.get_dict()['BbRouter'],
            }
            
            return assignmentList

def getAssignment(request):
    if not request.session['BbRouter']:
        request.session['BbRouter'] = {
            'name': '',
            'value': '',
        }
    
    assignments = fetchAssignment(request.session['BbRouter'], request)
    
    if not assignments:
        B64_userId   = base64.b64decode(request.GET.get('userId'))
        B64_password = base64.b64decode(request.GET.get('password'))
        
        userId   = B64_userId.decode("UTF-8")
        password = B64_password.decode("UTF-8")
        decodeUserId = request.GET.get('decodeUserId')
        
        CLIENT_INFO = {
            'client_id': 'f02a2d25639bed7abc3d7c0e1e773b4',
            'response_type': 'code',
            'redirect_uri': 'https://learn.hanyang.ac.kr',
            'scope': '35,10'
        }
    
        USER_INFO = {
            '_userId': userId,
            '_password': password,
            'identck': 'mobile_002',
            'sinbun': '',
        }
        
        AUTH_INFO = {
            'userId': decodeUserId,
            'crsmainPk1': '', 
            'sharedSecret': 'gksdid!!eogkrry@@',
            'autoSignOnUrl': 'https://learn.hanyang.ac.kr/webapps/oslt-auth-provider-autosignon-BB5a998b8c44671/service/login/_202_1'   
        }
        
        try:
            with requests.Session() as s:
                s.get('https://learn.hanyang.ac.kr')
                s.get('https://api.hanyang.ac.kr/oauth/authorize', params=CLIENT_INFO)
                s.post('https://api.hanyang.ac.kr/oauth/login_submit.json', data=USER_INFO)
                s.get('https://api.hanyang.ac.kr/oauth/authorize', params=CLIENT_INFO, allow_redirects=True)
                
                userAuthReq = s.post('https://learn.hanyang.ac.kr/webapps/fn-2ndauth-BB5a998b8c44671/json/secondAuth/checkUser', data=AUTH_INFO)
                userTokenReq = s.get(userAuthReq.json()['url'])
                userToken = userTokenReq.cookies.get_dict()['BbRouter']
                
                assignments = fetchAssignment({
                    'name': 'BbRouter',
                    'value': userToken
                }, request)
        except ValueError:
            return HttpResponse(json.dumps({
                'code': 401,
                'error': ValueError,
            }), content_type="application/json")
            
    
    return HttpResponse(json.dumps({
        'code': 200,
        'data': assignments,
        'message': 'success',
    }, ensure_ascii=False), content_type="application/json")


def getAssignmentDetail(request):
    calendarId = request.GET.get('calendarId')
    itemSourceId = request.GET.get('itemSourceId')
    
    BbRouter = request.session['BbRouter']
    
    attemptReq = requests.get('https://learn.hanyang.ac.kr/learn/api/v1/courses/'+calendarId+'/gradebook/columns/'+itemSourceId+'/grades',
        headers={
            'Referer': 'https://learn.hanyang.ac.kr/ultra/calendar',
            'Cookie': 'BbRouter='+BbRouter['value'],
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        },
        params={
            'expand': 'attemptsLeft'
        }
    )
    attemptData = attemptReq.json()
    data = {}
    
    if 'status' in attemptData or not attemptData['results'][0]['firstAttemptId']:
        data = {
            "status": 'IN_PROGRESS',
            "itemSourceId": itemSourceId
        }
    else:
        attemptData2 = attemptData['results'][0]
        
        attemptDetailReq = requests.get('https://learn.hanyang.ac.kr/learn/api/v1/courses/'+calendarId+'/gradebook/attempts/'+attemptData2['firstAttemptId'],
            headers={
                'Referer': 'https://learn.hanyang.ac.kr/ultra/calendar',
                'Cookie': 'BbRouter='+BbRouter['value'],
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
            },
            params= {
                'expand': 'toolAttemptDetail,alignedGoals,members,attempts,attempts.toolAttemptDetail,lastFeedbackAuthor,attempts.lastFeedbackAuthor'
            }
        )
        
        attemptDetailData = attemptDetailReq.json()
        
        data["status"] = attemptDetailData["status"]
        data["itemSourceId"] = itemSourceId
    
    return HttpResponse(json.dumps({
        'code': 200,
        'data': data,
        'message': 'success',
    }, ensure_ascii=False), content_type="application/json")
        