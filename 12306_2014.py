# -*- coding: UTF-8 -*-

"""
这是测试程序.我还无法分析席位..所以可能会买到无座的票..请自行修改.
好了..写的很烂.哈哈..大家见笑了
"""
import json
import httplib2
import urllib
import re
import time
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
			return ""
			
def PostDataToUrl(Url,Data,header):
	if len(Url)>10:
		resp,content=h.request(Url,"POST",headers=header,body=urllib.urlencode(Data))
		if resp.status == 200:
			return content
		else:
			return ""
		
	
def GetStationNames():
	url='https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
	head=myheaders
	data=GetDataByUrl(url,head)
	ret={}
	if len(data)>0:
		stations=re.findall('@([^@]+)',data)
		if len(stations)>0:
			for s in stations:
				tmpret=[]
				tmpret=s.split('|')
				if len(tmpret)>2:
					ret[tmpret[1]]=tmpret[2]
	return ret
	
	
def GetLoginCodePic():
	while True:
		loginheader=myheaders
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
	SearchHearder=myheaders
	SearchHearder['Referer']='https://kyfw.12306.cn/otn/leftTicket/init'
	data=GetDataByUrl(SearchLink,SearchHearder)
	return data




def SubmitOrderStep1(train_info):
	STEP1_LINK='https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'	
	submit_data={'back_train_date':train_info['back_date'],'purpose_codes':'ADULT','query_from_station_name':train_info['from_station_name'].encode('utf-8'),'query_to_station_name':train_info['to_station_name'].encode('utf-8'),
		'secretStr':train_info['secretStr'].encode('utf-8'),'train_date':train_info['train_date'],'tour_flag':'dc','undefined':''}
	submit_header=myheaders
	submit_header['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	submit_header['Referer']='https://kyfw.12306.cn/otn/leftTicket/init'
	#print submit_data
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
				print 'SubmitCodePic Check OK'
				return code
			else:
				print 'Error Code'
				
def GenPassengerStr(infos):
	strs=''
	if infos.has_key('seattype') and len(infos['seattype'])>0:
		strs = infos['seattype'][0]+',0,1,'+infos['name']+',1,'+infos['IDStrings']+',15158166885,N'
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
	check_ret = PostDataToUrl(check_url,check_data,check_header)
	check_json=json.loads(check_ret)
	if check_json.has_key('data') and check_json['data'].has_key('submitStatus') and len(check_json['messages'])==0:
		print 'CheckOrderInfo OK can submit order'
		#print check_json
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
	#print queuedata
	
	data=PostDataToUrl(queuelink,queuedata,queueheader)
	
	return data

def confirmOrder(infos):
	URL='https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
	head=myheaders
	head['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
	head['Referer']='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
	postdata={'train_location':infos['train_location'],'randCode':infos['randcode'],'REPEAT_SUBMIT_TOKEN':infos['tokenstr'],'_json_att':'','key_check_isChange':infos['key_check_isChange'],'oldPassengerStr':'_+','leftTicketStr':infos['leftstr'],'purpose_codes':'00','passengerTicketStr':infos['PassengerStr']}
	data=PostDataToUrl(URL,postdata,head)
	#print data
	jsons=json.loads(data)
	if jsons.has_key('errMsg') and len(jsons['errMsg'] )>0 :
		print jsons['errMsg']
	else:		 
		ret = GetOrderID(infos)
		if ret == 1:
			print 'Error'
			return 1
		print '太好了..终与能回家了..感谢党,感谢国家..感谢12306 让我回家..'.decode('utf-8')
		print '小伙伴们..快去支付吧..你已经有票了..'.decode('utf-8')
		GetOrderID(infos)
	
	
	
def GetOrderID(infos):
	i=0
	while True:
		timenow=time.time()*1000
		timestr='%f'%timenow
		randstr=timestr.split('.')[0]
		url='https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random='+randstr+'&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN='+infos['tokenstr']	
		head=myheaders		
		data=GetDataByUrl(url,head)
		j=json.loads(data)
		#print j
		if j.has_key('orderId') and len(j['orderId'])>0:
			print 'OrderTicket OK..'
			return 0
		else:
			print 'Wait for ORderid :'
			print j['data']['msg']
			time.sleep(1)
			i=i+1
			if  i>2:
				return 1
			
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

def GenDateString2():
	return strftime("%Y-%m-%d", time.localtime())



def GetSeatTypeCode(strs):
	seat_names={'S':'一等包座', 'M':'一等座','O':'二等座','P':'特等座','Q':'观光座','1':'硬座','2':'软座','3':'硬卧','4':'软卧','6':'高级软卧','9':'商务座'}
	ret=[]
	lines=re.findall('\[([^\]]+)\]',strs)
	if len(lines):
		for line in lines:
			ids=re.findall("'id':'(.)'",line)
			if len(ids)>0:
				for id in ids:
					if id not in ret:
						ret.append(id)
	for s in ret:
		if seat_names.has_key(s):
			print seat_names[s].decode('utf-8')
	return ret

def GetTicketLeftDetail(strs):
	ret=[]
	lines=re.findall("'leftDetails':\[([^\]]+)\]",strs)
	if len(lines):
		for line in lines:
			ids=line.split(',')
			if len(ids)>0:
				for id in ids:
					id=id.replace(",",'')
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
	seattypes=re.findall("init_seatTypes=(.+);",data)
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
	
	infos["name"]='name'
	infos['IDStrings']='身份证号码这里是'
		
	if len(seattypes)>0:
		infos['seattype'] = GetSeatTypeCode(seattypes[0])
		passengerstr=GenPassengerStr(infos)
		infos['PassengerStr']=passengerstr
	else:
		print 'No seat ticket...'
		return
	if len(repeatsubmit)>0:
		infos['tokenstr'] = repeatsubmit[0]		
		submitcode=GetSubmitCodePic(repeatsubmit[0])
		infos['randcode']=submitcode
		ret=CheckOrderInfo(submitcode,infos)
		if ret==1:
			print '天灵灵,地灵灵,保佑出张票..'.decode('utf-8')		
			infodata=GetQueueInfo(infos)	
			queinfos=json.loads(infodata)
			if 	queinfos.has_key('data') and queinfos['data'].has_key('op_1') and queinfos.has_key('messages') and len(queinfos['messages'])==0:
				print 'Yes 这次手快了点..看看运气怎么样 !!'.decode('utf-8')
				#print queinfos
				#这里的ticket是余票查询.但是有几个字段我分析不出来.最后3位好像是硬座票数.可能需要和座对应码对应起来
				#其实多找几趟车..就可以确定出来的.是我懒...哈哈..
				infos['leftstr']=queinfos['data']['ticket']
				##这里可以开线程几个线程同时post的..这样排队几率高点..
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





fromcode='SSH'
tocode='HYQ'
startdate='2014-01-24'

stationsdict=GetStationNames()

station2='深圳北'
if len(station2)>0:
	for key,val in stationsdict.iteritems():
		if re.findall(station2,key):
			print key.decode('utf-8')+'===>'+val
			fromcode=val
			station2=key

station='衡阳'
for key,val in stationsdict.iteritems():
	if re.findall(station,key):
		print key.decode('utf-8')+'===>'+val
		#tocode=val
		#station=key


	
print station2.decode('UTF-8')+':'+fromcode+"==>"+station.decode('utf-8')+':'+tocode+' 出发时间: '.decode('utf-8')+startdate


loginstatus = 0			
loginstatus = DoLogin('rails_guest1','shenjian123456')
while loginstatus:	
	SearchResult=SearchTicket(fromcode,tocode,startdate)
	if len(SearchResult)<10:
		print '搜索太快了..休息一下!!'.decode('utf-8')
		time.sleep(5)
		continue
	SearchJsons=json.loads(SearchResult)
	if SearchJsons.has_key('data'):
		Tranininfos=SearchJsons['data']
		for traninfo in Tranininfos:			
			if traninfo['queryLeftNewDTO']['canWebBuy'] == 'Y': #这里可以加车次的过滤
				print '太好了..找到一辆火车 :'.decode('utf-8')+traninfo['queryLeftNewDTO']['station_train_code']
				if 0==traninfo['queryLeftNewDTO']['station_train_code'].find('G'):
					print '找到高铁了....'.decode('utf-8')
				else:
					continue
				#print traninfo['queryLeftNewDTO']
				submitinfo={}
				submitinfo=traninfo['queryLeftNewDTO']
				if len(traninfo['secretStr'])<20:
					print 'ERROR Not secretStr find'
					continue		
				submitinfo['secretStr']=urllib.unquote(traninfo['secretStr'])
				submitinfo['train_date']=startdate
				submitinfo['back_date'] = GenDateString2()
				#print submitinfo['back_date']
				data_sub1=SubmitOrderStep1(submitinfo)
				sub1_json=json.loads(data_sub1)
				if sub1_json.has_key('status') and sub1_json['status']==True:
					print '离买到票又进了一步了..验证身份信息成功啦!....'.decode('utf-8')
					#print sub1_json
					SubmitStep2()
				else:
					print sub1_json['messages'][0]
					print '手慢无啊...我下次会更努力的抢票的..别灰心..继续来...Come On..'.decode('utf-8')
		time.sleep(0.06)
	else:
		time.sleep(5)
			
	
	
