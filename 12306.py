#-*- coding: utf-8 -*-
#
#这是自己写的测试代码..理论上应该可以的.没有验证码识别..后续加上
#很多post数据都是固定的..需要自己修改..比如订票人信息.
#
#
#
import pycurl
import re
import StringIO
import urllib
import json
import time
from bs4 import BeautifulSoup

status='uninit'
order_date='2013-01-18'

def load_img(c):
  while True:
		img_f=open('randcode.png','wb')
		c.setopt(pycurl.URL,'https://dynamic.12306.cn/otsweb/passCodeAction.do?rand=sjrand&0.5658475179953977')
		c.setopt(crl.WRITEFUNCTION, img_f.write)
		c.perform()
		img_f.close()
		print '请输入验证码文件(randcode.png)中的4个字符:'.decode('utf-8')
		code=raw_input()
		if len(code)==4:
			return code
		else:
			continue
	
def login(c):	
	post_data={
	'loginRand':'673',
	'loginUser.user_name':'test_guest1',
	'nameErrorFocus':'',	
	'passwordErrorFocus':'',	
	'randCode':'D7A2',
	'randErrorFocus':'focus',
	'refundFlag':'Y',
	'refundLogin':'N',
	'user.password':'test_guest1'}
	
	rand_img_url='passCodeAction.do?rand=sjrand&'
	c.setopt(pycurl.URL,login_initurl)
	c.perform()	
	codes=load_img(c)	
	post_data['randCode']=codes
	time.sleep(0.3)
	page_fp=StringIO.StringIO()
	c.setopt(pycurl.URL,login_asyncurl)
	c.setopt(crl.WRITEFUNCTION, page_fp.write)
	c.perform()	
	loginRands=page_fp.getvalue()
	j=json.loads(loginRands)
	post_data['loginRand']=j['loginRand']
	page_fp=StringIO.StringIO()
	c.setopt(pycurl.POSTFIELDS,  urllib.urlencode(post_data))
	c.setopt(pycurl.URL,login_post_url)
	c.setopt(crl.WRITEFUNCTION, page_fp.write)
	c.perform()
	#print page_fp.getvalue()
	status='login'

def print_tran_info(infos):
	id=0
	for tran in infos:
		s='%d: %s %s->%s 开车时间:%s 到达时间:%s 历时:%s'
		p_s=s%(id,tran['station_train_code'],tran['from_station_name'],tran['to_station_name'],tran['train_start_time'],tran['arrive_time'],tran['lishi'])
		print p_s.decode('utf-8')
		id += 1
		
def query(c,date,from_station,to_station):
	print 'query'
	ret=[]
	order_datas=[]
	order_date=date
	while not len(ret)>0:
		page_fp=StringIO.StringIO()
		s='https://dynamic.12306.cn/otsweb/order/querySingleAction.do?method=queryLeftTicket&orderRequest.train_date=%s&orderRequest.from_station_telecode=%s&orderRequest.to_station_telecode=%s&orderRequest.train_no=&trainPassType=QB&trainClass=QB#D#Z#T#K#QT#&includeStudent=00&seatTypeAndNum=&orderRequest.start_time_str=00:00--24:00'
		url=s%(date,from_station,to_station)
		c.setopt(pycurl.URL,url)
		c.setopt(crl.WRITEFUNCTION, page_fp.write)
		#c.setopt(pycurl.POSTFIELDS, urllib.urlencode({}))
		c.perform()
		strings=page_fp.getvalue().decode('utf-8')
		soup = BeautifulSoup(strings)
		aas=soup.select('a[onclick]')
		for a in aas:
			tmp=[]	
			strings=re.sub('.+\'(.*?)\'.+',r'\1',a['onclick'])
			tmp=strings.split('#')
			if len(tmp)>0:
				ret.append(tmp)
		if len(ret)>0:
			print 'ok...can order ticket..'
			for tran in ret:
				order_dict={}
				order_dict['include_student']='0'
				order_dict['round_start_time_str']=order_date
				order_dict['seattype_num']=''
				order_dict['single_round_type']='1'
				order_dict['start_time_str']='00:00--24:00'
				order_dict['train_class_arr']='QB#D#Z#T#K#QT#'
				order_dict['train_pass_type']='QB'
				order_dict['train_date']=order_date
				
				for i in range(len(tran)):					
					if i==0:
						order_dict['station_train_code']=tran[i].encode('utf-8')
					elif i== 1:
						order_dict['lishi']=tran[i].encode('utf-8')
					elif i== 2:
						order_dict['train_start_time']=tran[i].encode('utf-8')
					elif i== 3:
						order_dict['trainno4']=tran[i].encode('utf-8')
					elif i== 4:
						order_dict['from_station_telecode']=tran[i].encode('utf-8')
					elif i== 5:
						order_dict['to_station_telecode']=tran[i].encode('utf-8')
					elif i== 6:
						order_dict['arrive_time']=tran[i].encode('utf-8')
					elif i== 7:
						order_dict['from_station_name']=tran[i].encode('utf-8')
						order_dict['from_station_telecode_name']=tran[i].encode('utf-8')						
					elif i== 8:
						order_dict['to_station_name']=tran[i].encode('utf-8')
						order_dict['to_station_telecode_name']=tran[i].encode('utf-8')
					elif i== 9:
						order_dict['from_station_no']=tran[i].encode('utf-8')	
					elif i== 10:
						order_dict['to_station_no']=tran[i].encode('utf-8')	
					elif i== 11:
						order_dict['ypInfoDetail']=tran[i].encode('utf-8')	
					elif i== 12:
						order_dict['mmStr']=tran[i].encode('utf-8')	
					elif i== 13:
						order_dict['locationCode']=tran[i].encode('utf-8')	
				order_datas.append(order_dict)
			#print order_datas			
			return order_datas
		time.sleep(3)
	
	
def order(c,post_datas,id):
	print 'order id %d',id	
	token=''
	while len(token)==0:
		page_fp=open('confirmPassengerAction.txt','wb')
		order_url='https://dynamic.12306.cn/otsweb/order/querySingleAction.do?method=submutOrderRequest'
		c.setopt(pycurl.URL,order_url)
		c.setopt(pycurl.FOLLOWLOCATION, 1)
		c.setopt(pycurl.MAXREDIRS, 5)
		c.setopt(crl.WRITEFUNCTION, page_fp.write)
		c.setopt(pycurl.POSTFIELDS, urllib.urlencode(post_datas[id]))
		c.perform()
		content=''	
		page_fp.close()
		f=open('confirmPassengerAction.txt','r')
		ct=''
		for line in f.readlines():
			ct += line	
		hiddens=re.findall('<input.+?hidden.+?TOKEN.+?value="([^"]+?)">',ct)
		for hidden in hiddens:
			token = hidden
			print 'get token ok...',token
			break
		time.sleep(3)
	
	#ss=re.sub('\s','',page_fp.getvalue())
	#print ss
	#hiddens=re.findall('<input.+?hidden.+?>',ss)
	#for hidden in hiddens:
	#	print hidden
	#get_passger_url='https://dynamic.12306.cn/otsweb/order/confirmPassengerAction.do?method=getpassengerJson'
	
	rand_code_url='https://dynamic.12306.cn/otsweb/passCodeAction.do?rand=randp&0.08279546253388872'
	page_fp=open('passCode.png','wb')
	c.setopt(pycurl.URL,rand_code_url)
	c.setopt(crl.WRITEFUNCTION, page_fp.write)
	c.perform()
	page_fp.close()	
	passCode=raw_input('input passcode:')
	#queryLeftTicket
	#leftTicketStr=''
	#oldPassengers=''
	
def confirm(c):
	print 'confirm'
	'''
	https://dynamic.12306.cn/otsweb/order/confirmPassengerAction.do?method=checkOrderInfo&rand=NYXK
	checkbox0=0
	checkbox9=Y
	checkbox9=Y
	checkbox9=Y
	checkbox9=Y
	checkbox9=Y
	leftTicketStr=O004050061O004053026M004850050
	oldPassengers=陈a,1,110229198601019993
	oldPassengers=
	oldPassengers=
	oldPassengers=
	oldPassengers=
	orderRequest.bed_level_order_num=000000000000000000000000000000
	orderRequest.cancel_flag=1
	orderRequest.end_time=18:01
	orderRequest.from_station_name=杭州
	orderRequest.from_station_telecode=HZH
	orderRequest.id_mode=Y
	orderRequest.reserve_flag=A
	orderRequest.seat_type_code=O
	orderRequest.start_time=16:56
	orderRequest.station_train_code=D5663
	orderRequest.ticket_type_order_num=
	orderRequest.to_station_name=义乌
	orderRequest.to_station_telecode=YWH
	orderRequest.train_date=2013-02-03
	orderRequest.train_no=5l000D566303
	org.apache.struts.taglib.html.TOKEN=cdc435875b0a8414fa7a45bc4c06fcae
	passengerTickets=O,undefined,1,陈a,1,110229198601019993,13564804697,Y
	passenger_1_cardno=110229198601019993
	passenger_1_cardtype=1
	passenger_1_mobileno=13564804697
	passenger_1_name=陈a
	passenger_1_seat=O
	passenger_1_ticket=1
	randCode=NYXK
	tFlag=dc
	textfield=中文或拼音首字母
	
	
	https://dynamic.12306.cn/otsweb/order/confirmPassengerAction.do?method=confirmSingleForQueueOrder
	checkbox0=0
	checkbox9=Y
	checkbox9=Y
	checkbox9=Y
	checkbox9=Y
	checkbox9=Y
	leftTicketStr=O004050061O004053026M004850050
	oldPassengers=陈a,1,110229198601019993
	oldPassengers=
	oldPassengers=
	oldPassengers=
	oldPassengers=
	orderRequest.bed_level_order_num=000000000000000000000000000000
	orderRequest.cancel_flag=1
	orderRequest.end_time=18:01
	orderRequest.from_station_name=杭州
	orderRequest.from_station_telecode=HZH
	orderRequest.id_mode=Y
	orderRequest.reserve_flag=A
	orderRequest.seat_type_code=
	orderRequest.start_time=16:56
	orderRequest.station_train_code=D5663
	orderRequest.ticket_type_order_num=
	orderRequest.to_station_name=义乌
	orderRequest.to_station_telecode=YWH
	orderRequest.train_date=2013-02-03
	orderRequest.train_no=5l000D566303
	org.apache.struts.taglib.html.TOKEN=cdc435875b0a8414fa7a45bc4c06fcae
	passengerTickets=M,undefined,1,陈a,1,110229198601019993,13564804697,Y
	passenger_1_cardno=110229198601019993
	passenger_1_cardtype=1
	passenger_1_mobileno=13564804697
	passenger_1_name=陈a
	passenger_1_seat=M
	passenger_1_ticket=1
	randCode=NYXK
	textfield=中文或拼音首字母
		
	https://dynamic.12306.cn/otsweb/order/myOrderAction.do?method=getOrderWaitTime&tourFlag=dc
	'''
	
	
query_url='https://dynamic.12306.cn/otsweb/order/querySingleAction.do?method=queryLeftTicket&orderRequest.train_date=2013-01-28&orderRequest.from_station_telecode=HZH&orderRequest.to_station_telecode=HBB&orderRequest.train_no=&trainPassType=QB&trainClass=QB%23D%23Z%23T%23K%23QT%23&includeStudent=00&seatTypeAndNum=&orderRequest.start_time_str=00%3A00--24%3A00'
login_initurl='https://dynamic.12306.cn/otsweb/loginAction.do?method=init'
login_asyncurl='https://dynamic.12306.cn/otsweb/loginAction.do?method=loginAysnSuggest'
login_post_url='https://dynamic.12306.cn/otsweb/loginAction.do?method=login'

order_url=''
confirm_url = ''


pycurl.COOKIESESSION = 96
#url = "https://dynamic.12306.cn/otsweb/order/querySingleAction.do?method=queryLeftTicket&orderRequest.train_date=2013-01-28&orderRequest.from_station_telecode=HZH&orderRequest.to_station_telecode=HBB&orderRequest.train_no=&trainPassType=QB&trainClass=QB%23D%23Z%23T%23K%23QT%23&includeStudent=00&seatTypeAndNum=&orderRequest.start_time_str=00%3A00--24%3A00"
crl = pycurl.Curl()
crl.setopt(pycurl.SSL_VERIFYPEER, 0)   
crl.setopt(pycurl.SSL_VERIFYHOST, 0)
crl.setopt(pycurl.USERAGENT,'Mozilla/5.0 (Windows NT 6.1; rv:18.0) Gecko/20100101 Firefox/18.0')
crl.setopt(pycurl.VERBOSE,1)
crl.setopt(pycurl.FOLLOWLOCATION, 1)
crl.setopt(pycurl.MAXREDIRS, 5)
page_fp = StringIO.StringIO()
crl.setopt(crl.WRITEFUNCTION, page_fp.write)

crl.setopt(pycurl.COOKIEFILE, "12306") 

crl.setopt(pycurl.COOKIEJAR, "cookie_file_name") 

login(crl)
while True:
	print "请输入订票日期(格式 2013-01-09):".decode('utf-8')
	dt=raw_input()
	print "请输入出发站名:".decode('utf-8')
	fs=raw_input()
	print "请输入目的站名:".decode('utf-8')
	ts=raw_input()
	trans_infos=query(crl,dt,fs,ts)
	print_tran_info(trans_infos)
	order(crl,trans_infos,0)
	
