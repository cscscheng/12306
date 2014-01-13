# -*- coding: UTF-8 -*-

import json
import httplib2
import urllib
import re
from time import gmtime,strftime


myheaders={'Connection': 'keep-alive','Referer': 'https://kyfw.12306.cn/otn/index/init','User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0','Host': 'kyfw.12306.cn',}
cookies={}

h=httplib2.Http(".cache",disable_ssl_certificate_validation=True)

LOGIN_START_URL='https://kyfw.12306.cn/otn/login/init'
LOGIN_CODE_URL='https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand'
LOGIN_POST_URL1='https://kyfw.12306.cn/otn/login/loginAysnSuggest'
LOGIN_POST_URL2='https://kyfw.12306.cn/otn/login/userLogin'
CHECK_LOGINCODE_URL='https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'
SEARCH_TICKET_URL1='https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2014-01-29&leftTicketDTO.from_station=SHH&leftTicketDTO.to_station=ZZF&purpose_codes=ADULT'
SEARCH_TICKET_URL='https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT'

def GetDataByUrl(Url,header):
	if len(Url)>10:
		resp,content=h.request(Url,"GET",headers=header);
		if resp.status == 200:
			if  resp.has_key('set-cookie')>0:				
				cookies=re.sub('Path=/.*,','',resp['set-cookie'])
				cookies=re.sub('path=/','',cookies)
				myheaders['Cookie'] = cookies
			return content
		else:
			print 'GetDataByUrl Error'
			print resp
			
def PostDataToUrl(Url,Data,header):
	if len(Url)>10:
		resp,content=h.request(Url,"POST",headers=header,body=urllib.urlencode(Data))
		if resp.status == 200:
			return content
		else:
			print 'PostDataToUrl error'
			print resp
		
		
def GetLoginCodePic():
	while True:
		loginheader=myheaders
		print loginheader
		data=GetDataByUrl(LOGIN_CODE_URL,loginheader)
		if len(data)>10:		
			f=open('LoginCode.jpg','wb')
			f.write(data)
			f.close()
			code=raw_input("input the LoginCode:")
			check_data={'rand':'sjrand','randCode':code}
			checkheader=myheaders
			checkheader['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
			
			check_ret = PostDataToUrl(CHECK_LOGINCODE_URL,check_data,checkheader)
			check_json=json.loads(check_ret)
			if check_json['data'] == 'Y':
				print 'Login Code Check OK'
				return code
			else:
				print 'Error Code'
				
		
def DoLogin(username,password):
	while True:
		GetDataByUrl(LOGIN_START_URL,myheaders)
		code=GetLoginCodePic()
		if len(code) == 4:
			post_data={'loginUserDTO.user_name':username,'randCode':code,'userDTO.password':password}
			LoginPostHeader=myheaders
			LoginPostHeader['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
			login_step1=PostDataToUrl(LOGIN_POST_URL1,post_data,LoginPostHeader)
			login_json=json.loads(login_step1)
			if  login_json.has_key('data')and len(login_json['data']) >0:
				print "LoginOK!!"
				return 1
			else:
				print login_json
				#print login_json['messages'][0]

def SearchTicket(start,end,date):
	SearchLink=SEARCH_TICKET_URL%(date,start,end)
	print SearchLink
	SearchHearder=myheaders
	SearchHearder['Referer']='https://kyfw.12306.cn/otn/leftTicket/init'
	data=GetDataByUrl(SearchLink,SearchHearder)
	return data




def SubmitOrderStep1(train_info):
	STEP1_LINK='https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'	
	submit_data={'back_train_date':'2014-01-10','purpose_codes':'ADULT','query_from_station_name':train_info['from_station_name'].encode('utf-8'),'query_to_station_name':train_info['to_station_name'].encode('utf-8'),
		'secretStr':train_info['secretStr'].encode('utf-8'),'tour_flag':'dc','undefined':''}
	submit_header=myheaders
	submit_header['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	submit_header['Referer']='https://kyfw.12306.cn/otn/leftTicket/init'
	data = PostDataToUrl(STEP1_LINK,submit_data,submit_header)
	return data

def GetSubmitCodePic(tokenstr):
	
	while True:
		Code_URL='https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp'
		sub_header=myheaders
		sub_header['Referer']='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		data=GetDataByUrl(Code_URL,sub_header)
		if len(data)>10:		
			f=open('SubmitCode.jpg','wb')
			f.write(data)
			f.close()
			code=raw_input("input the SubmitCode:")
			check_data={'REPEAT_SUBMIT_TOKEN':tokenstr,'_json_att':'','rand':'randp','randCode':code}
			checkheader=myheaders
			checkheader['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
			checkheader['Referer']='https://kyfw.12306.cn/otn/confirmPassenger/initDc'			
			CHECK_URL='https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'
			check_ret = PostDataToUrl(CHECK_URL,check_data,checkheader)
			check_json=json.loads(check_ret)
			if check_json['data'] == 'Y':
				print 'GetSubmitCodePic Check OK'
				return code
			else:
				print 'Error Code'
				
def GenPassengerStr(infos):
	strs=''
	if infos.has_key('seattype') and len(infos['seattype'])>0:
		strs = infos['seattype'][0]+',0,1,'+infos['name']+',1,'+infos['IDStrings']+',15158166885,N'
	print strs
	return strs


def GetPassengerInfos(infos):
	url='https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
	postdata={'REPEAT_SUBMIT_TOKEN':infos['tokenstr'],'_json_att':''}
	head=myheaders
	head['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	head['Referer']='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
	data = PostDataToUrl(url,postdata,head)
	return data
	
		


def CheckOrderInfo(codestr,infos):
	GetPassengerInfos(infos)
	check_url='https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
	check_header=myheaders
	check_header['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	check_header['Referer']='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
	if infos['bed_level_order_num'] =='null':
		infos['bed_level_order_num']='000000000000000000000000000000'
	
	passengerstr=GenPassengerStr(infos)
	check_data = {'REPEAT_SUBMIT_TOKEN':infos['tokenstr'],'_json_att':'','bed_level_order_num':infos['bed_level_order_num'],'cancel_flag':'2','oldPassengerStr':'_+','passengerTicketStr':passengerstr,'randCode':codestr,'tour_flag':'dc'}
	print check_data
	check_ret = PostDataToUrl(check_url,check_data,check_header)
	check_json=json.loads(check_ret)
	if check_json.has_key('data') and check_json['data'].has_key('submitStatus') and len(check_json['messages'])==0:
		print 'CheckOrderInfo OK can submit order'
		print check_json
		return 1
	else:
		print check_json['messages'][0]
		return 0
	
	

def GetQueueInfo(infos):
	queuelink='https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
	queueheader=myheaders
	queueheader['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	queueheader['Referer']='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
	
	queuedata={'REPEAT_SUBMIT_TOKEN':infos['tokenstr'],'_json_att':'','fromStationTelecode':infos['fromtelecode'],'toStationTelecode':infos['totelecode'],
		'leftTicket':infos['leftstr'],'purpose_codes':'00','seatType':'1','stationTrainCode':infos['trancode'],'train_no':infos['tranno'],'train_date':'Wed Jan 29 2014 00:00:00 GMT+0800'}
	print queuedata
	
	data=PostDataToUrl(queuelink,queuedata,queueheader)
	
	return data

def confirmOrder(infos):
	URL='https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
	head=myheaders
	head['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	head['Referer']='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
	postdata={'train_location':infos['train_location'],'randCode':infos['randcode'],'REPEAT_SUBMIT_TOKEN':infos['tokenstr'],'_json_att':'','key_check_isChange':infos['key_check_isChange'],'oldPassengerStr':'_+','leftTicketStr':infos['leftstr'],'purpose_codes':'00','passengerTicketStr':infos['PassengerStr']}
	data=PostDataToUrl(URL,postdata,head)
	jsons=json.load(data)
	print jsons
	if jsons.has_key('messages') and len(jsons['messages']) == 0 and jsons.has_key('status') and jsons['status'] == True:
		print 'submit order OK..GetOrder id.'
		GetOrderID(infos)
	
	
	
def GetOrderID(infos):
	while True:
		timenow=time()*1000
		timestr='%f'%timenow
		randstr=timestr.split('.')[0]
		url='https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random='+randstr+'&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN='+infos['tokenstr']	
		data=GetDataByUrl(url)
		j=json.loads(data)
		print j
		if j.has_key('orderid') and len(j['orderid'])>0:
			print 'OrderTicket OK..'+j['orderid']
			return 0
		else:
			print 'Wait for ORderid'
			
	return 1

def GetValualeByName(name,data,mode='notnull'):
	regstr="'"+name+"':'{0,1}([^'^,]+)'{0,1}"
	f=re.findall(regstr,data)
	j=''
	for i in f:
		if mode=='notnull' and i != 'null':
			return i
		if mode == 'max' and i != 'null':
			if len(i)>len(j):
				j=i
		
	if len(j)>0:
		return j
	return i

def GenDateString(timestr):
	return strftime("%a %d %b %Y %H:%M:%S GMT+0800", gmtime(float(timestr)/1000+28800))


def GetSeatTypeCode(strs):
	ret=[]
	lines=re.findall('\[([^\]]+)\]',strs)
	if len(lines):
		for line in lines:
			ids=re.findall("'id':'(.)'",line)
			if len(ids)>0:
				for id in ids:
					if id not in ret:
						ret.append(id)
	return ret
	

def SubmitStep2():	
	step2_url='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
	step2_data={'_json_att':''}
	step2_header=myheaders
	step2_header['Referer']='https://kyfw.12306.cn/otn/leftTicket/init'
	data=PostDataToUrl(step2_url,step2_data,step2_header)
	repeatsubmit=re.findall("var globalRepeatSubmitToken = '([a-z0-9]+)';",data)
	ticketinfos=re.findall("var ticketInfoForPassengerForm=(.+);",data)
	orderRequestDTOinfos=re.findall("orderRequestDTO=(.+);",data)
	seattypes=re.findall("ticket_seat_codeMap=(.+);",data)
	infos={}
	infos['tokenstr'] = ''
	infos['fromtelecode']=GetValualeByName('from_station_telecode',data)
	infos['leftstr']=GetValualeByName('leftTicketStr',data)
	infos['trancode']=GetValualeByName('station_train_code',data)
	infos['totelecode']=GetValualeByName('to_station_telecode',data)
	infos['tranno']=GetValualeByName('train_no',data)
	infos['trandate']=GenDateString(GetValualeByName('time',data,'max'))
	infos['cancel_flag']=GetValualeByName('cancel_flag',data)
	infos['bed_level_order_num']=GetValualeByName('bed_level_order_num',data)
	infos['tour_flag']=GetValualeByName('tour_flag',data)
	infos['key_check_isChange'] = GetValualeByName('key_check_isChange',data)
	infos['train_location'] = GetValualeByName('train_location',data)
	infos['seattype']=[]
	infos["name"]='xijinp'
	infos['IDStrings']='110101198801014714'
	
	if len(seattypes)>0:
		infos['seattype'] = GetSeatTypeCode(seattypes[0])
		passengerstr=GenPassengerStr(infos)
		infos['PassengerStr']=passengerstr
	if len(repeatsubmit)>0:
		infos['tokenstr'] = repeatsubmit[0]		
		submitcode=GetSubmitCodePic(repeatsubmit[0])
		infos['randcode']=submitcode
		ret=CheckOrderInfo(submitcode,infos)
		if ret==1:
			print 'check order info ok'		
			infodata=GetQueueInfo(infos)	
			queinfos=json.loads(infodata)
			if 	queinfos.has_key('data') and queinfos['data'].has_key('op_1') and queinfos.has_key('messages') and len(queinfos['messages'])==0:
				print 'Do Post Order !!'
				print queinfos
				infos['leftstr']=queinfos['data']['ticket']
				confirmOrder(infos)
			else:
				print queinfos
				
		else:
			print 'check error'	

#zy_num 一等 
#ze_num 二等
#yw_num 硬卧
#yz_num 硬座
#rw_num 软卧
#rz_num 软座
#swz_num  商务座
#tz_num   特等座
#gr_num  高级软卧
#wz_num 无座
#qt_num 其他

loginstatus = 0			
loginstatus = DoLogin('xijinpingzhuxi','shenjian88')
while loginstatus:	
	SearchResult=SearchTicket('SHH','HZH','2014-01-29')
	SearchJsons=json.loads(SearchResult)
	if SearchJsons.has_key('data'):
		Tranininfos=SearchJsons['data']
		for traninfo in Tranininfos:			
			if traninfo['queryLeftNewDTO']['station_train_code'] == 'D5589':#here
				submitinfo={}
				submitinfo=traninfo['queryLeftNewDTO']
				submitinfo['secretStr']=traninfo['secretStr']
				data_sub1=SubmitOrderStep1(submitinfo)
				sub1_json=json.loads(data_sub1)
				if sub1_json.has_key('status') and sub1_json['status']==True:
					print 'submit step1 ok..'
					print sub1_json
					SubmitStep2()
				else:
					print sub1_json['messages']
					print 'submit step 1 error do research'
			
	
	
