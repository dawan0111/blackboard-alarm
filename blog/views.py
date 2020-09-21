import requests
import json
import base64
import datetime
import time

from multiprocessing import Process
from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.alert import Alert

def schedule(request):
    return render(request, 'blog/index.html', {})

def post_list(request):
    return render(request, 'blog/post_list.html', {})

def getAssignment(request):
    BbRouter = request.session['BbRouter']
    
    if not request.session['BbRouter']:
        B64_userId   = base64.b64decode(request.GET.get('userId'))
        B64_password = base64.b64decode(request.GET.get('password'))
        
        userId   = B64_userId.decode("UTF-8")
        password = B64_password.decode("UTF-8")
        
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("disable-gpu") 
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        
        prefs = {'profile.default_content_setting_values': {'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2}}
        '''
        9999999999
        1600602108
        '''
        options.add_experimental_option('prefs', prefs)
        
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        driverAlert = Alert(driver)
        
        driver.implicitly_wait(3)
        driver.get('https://learn.hanyang.ac.kr/ultra/institution-page')
        driver.find_element_by_id('entry-login-custom').click()
        
        driver.find_element_by_id('uid').send_keys(userId)
        driver.find_element_by_id('upw').send_keys(password)
        driver.find_element_by_id('login_btn').click()
        
        try:
            alert = driver.switch_to_alert()
            alert.accept()
        except:
            alerts = False
        
        cookies = driver.get_cookies()
        BbRouter= next(item for item in cookies if item["name"] == "BbRouter")
        driver.quit()
    
    try:
        request.session['BbRouter'] = BbRouter
        
        with requests.Session() as s:
            nowDateTime = datetime.datetime.now()
            nowDateFormat = nowDateTime.strftime('%Y-%m-%dT00:00:00Z')
            getSch = s.get('https://learn.hanyang.ac.kr/learn/api/v1/calendars/calendarItems?since='+nowDateFormat, headers={
                'Referer': 'https://learn.hanyang.ac.kr/ultra/calendar',
                'Cookie': 'BbRouter='+BbRouter['value'],
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
            })
            
            schList = getSch.json()['results']
            assignmentList = list(filter(lambda x: 'rawValue' in x['calendarNameLocalizable'], schList))
            
            request.session['BbRouter'] = {
                'name': 'BbRouter',
                'value': getSch.cookies.get_dict()['BbRouter'],
            }
            
            return HttpResponse(json.dumps({
                'code': 200,
                'data': assignmentList,
                'message': 'success',
            }, ensure_ascii=False), content_type="application/json")
    except:
        request.session['BbRouter'] = False
        
        return HttpResponse(json.dumps({
            'code': 401,
            'data': getSch.cookies.get_dict(),
            'message': 'auth error',
        }, ensure_ascii=False), content_type="application/json")


def getAssignmentDetail(request):
    calendarId = request.GET.get('calendarId')
    itemSourceId = request.GET.get('itemSourceId')
    
    BbRouter = request.session['BbRouter']
    
    courses = requests.get(
        'https://learn.hanyang.ac.kr/learn/api/v1/courses/'+calendarId+'/gradebook/columns/'+itemSourceId,
        headers={
            'Referer': 'https://learn.hanyang.ac.kr/ultra/calendar',
            'Cookie': 'BbRouter='+BbRouter['value'],
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        },
        params={
            'expand': 'collectExternalSubmissions,gradebookCategory'
        }
    )
    courseData = courses.json()
    
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
        
        data = attemptDetailData
        data["itemSourceId"] = itemSourceId
    
    return HttpResponse(json.dumps({
        'code': 200,
        'data': data,
        'message': 'success',
    }, ensure_ascii=False), content_type="application/json")
        