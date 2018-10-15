#!/usr/bin/env python
#-*-coding: utf-8 -*-

import Pyro.core
import os,re
from Status import Status

Stat = Status()

class Pages:
	
	def __init__(self):
		Pyro.core.initClient()
		self.av4 = None
		
	def connect(self):
		if self.av4 == None:
			self.av4 = Pyro.core.getProxyForURI('PYROLOC://localhost/AV4Server')

	def post_control(self,input):
		self.connect()
		for key in input:
			val = input.getvalue(key)
			if key == 'logfile':
				if val <> '':
					self.av4.log_file(val)
			elif key == 'logging':
				if val == 'start':
					self.av4.start_logging()
				elif val == 'stop':
					self.av4.stop_logging()
			elif key == 'autostop':
				if val == 'True':
					self.av4.set_autostop(True)
				else:
					self.av4.set_autostop(False)
			elif key[0:5] == 'cnenn':
				schacht = int(key[5])
				m = re.search('(\d+)',val)
				if m <> None:
					kapa = int(m.group(1))
					self.av4.Set_C_nenn(schacht,kapa)
					#print 'Nennkapazität Schacht {:d} = {:d}'.format(schacht,kapa)
			elif key == 'shutdown':
				if val == 'True':
					self.av4.stop_logging()
					os.system("sudo shutdown -h now")
		
	def control(self):
		self.connect()
		logging = str(self.av4.Status_Logging())
		logfile = self.av4.Status_Logfile()
		autostop = str(self.av4.get_autostop())
		serialok = str(self.av4.Status_Serial())
		c1nenn = c2nenn = c3nenn = c4nenn = ' '
		c = self.av4.Get_C_nenn(1)
		if c > 0:
			c1nenn = "{:d} mAh".format(c)
		c = self.av4.Get_C_nenn(2)
		if c > 0:
			c2nenn = "{:d} mAh".format(c)
		c = self.av4.Get_C_nenn(3)
		if c > 0:
			c3nenn = "{:d} mAh".format(c)
		c = self.av4.Get_C_nenn(4)
		if c > 0:
			c4nenn = "{:d} mAh".format(c)
		page = '''<?xml version="1.0" encoding="utf-8"?>
<control>
	<logging>{:s}</logging>
	<logfile>{:s}</logfile>
	<autostop>{:s}</autostop>
	<serialok>{:s}</serialok>
	<c1nenn>{:s}</c1nenn>
	<c2nenn>{:s}</c2nenn>
	<c3nenn>{:s}</c3nenn>
	<c4nenn>{:s}</c4nenn>
</control>'''.format(logging,logfile,autostop,serialok,c1nenn,c2nenn,c3nenn,c4nenn)
		return page

	def messwerte(self):
		global Stat
		self.connect()

		#[K0,K1,K2,K3,K4,K5,K6,K7,K8] = self.av4.Read_Kanaele()
		#AVG=self.av4.Read_Average_Voltage()

		werte = [None,self.av4.aktuelle_werte(1),self.av4.aktuelle_werte(2),
			self.av4.aktuelle_werte(3),self.av4.aktuelle_werte(4)]

		#Initialisieren aller Tags
		u1e = u1l = u2e = u2l = u3e = u3l = u4e = u4l = ' '
		i1e = i1l = i2e = i2l = i3e = i3l = i4e = i4l = ' '
		c1e = c1l = c2e = c2l = c3e = c3l = c4e = c4l = ' '
		c1nenn = c2nenn = c3nenn = c4nenn = ' '
		c1erate = c1lrate = c2erate = c2lrate = c3erate = c3lrate = c4erate = c4lrate = ' '
		t1e = t1l = t2e = t2l = t3e = t3l = t4e = t4l = ' '
		e1e = e1l = e2e = e2l = e3e = e3l = e4e = e4l = ' '
		e1nenn = e2nenn = e3nenn = e4nenn = ' '
		e1erate = e1lrate = e2erate = e2lrate = e3erate = e3lrate = e4erate = e4lrate = ' '
		s1 = s2 = s3 = s4 = '-'
		s1txt = s2txt = s3txt = s4txt = 'Unbekannt'
		l1 = l2 = l3 = l4 = ''
		u1eavg = u2eavg = u3eavg = u4eavg = ' '
		u1lavg = u2lavg = u3lavg = u4lavg = ' '
		cy1 = cy2 = cy3 = cy4 = ' '

		if werte[1] <> None:
			cy1 = "{:d}".format(werte[1]['cycle'])
			cy2 = "{:d}".format(werte[2]['cycle'])
			cy3 = "{:d}".format(werte[3]['cycle'])
			cy4 = "{:d}".format(werte[4]['cycle'])
			
			s1 = werte[1]['state']
			s2 = werte[2]['state']
			s3 = werte[3]['state']
			s4 = werte[4]['state']

			s1txt=werte[1]['StatusMsg']
			s2txt=werte[2]['StatusMsg']
			s3txt=werte[3]['StatusMsg']
			s4txt=werte[4]['StatusMsg']

			l1=werte[1]['LogMsg']
			l2=werte[2]['LogMsg']
			l3=werte[3]['LogMsg']
			l4=werte[4]['LogMsg']

			u1e="{:4.2f} V".format(werte[1]['U'])
			u1l="{:4.2f} V".format(werte[1]['Ustrom'])
			u2e="{:4.2f} V".format(werte[2]['U'])
			u2l="{:4.2f} V".format(werte[2]['Ustrom'])
			u3e="{:4.2f} V".format(werte[3]['U'])
			u3l="{:4.2f} V".format(werte[3]['Ustrom'])
			u4e="{:4.2f} V".format(werte[4]['U'])
			u4l="{:4.2f} V".format(werte[4]['Ustrom'])

			i1l="{:.0f} mA".format(werte[1]['I_chg'])
			i1e="{:.0f} mA".format(werte[1]['I_dischg'])
			i2l="{:.0f} mA".format(werte[2]['I_chg'])
			i2e="{:.0f} mA".format(werte[2]['I_dischg'])
			i3l="{:.0f} mA".format(werte[3]['I_chg'])
			i3e="{:.0f} mA".format(werte[3]['I_dischg'])
			i4l="{:.0f} mA".format(werte[4]['I_chg'])
			i4e="{:.0f} mA".format(werte[4]['I_dischg'])

			if 'C_nenn' in werte[1]:
				c1nenn="{:d} mAh".format(werte[1]['C_nenn'])
				
			c1l="{:.0f} mAh".format(werte[1]['C_chg'])
			c1e="{:.0f} mAh".format(werte[1]['C_dischg'])
			if 'C_chg_rel' in werte[1]:
				c1lrate = "{:d} %".format(werte[1]['C_chg_rel'])
			else:
				c1lrate = ' '
			if 'C_dischg_rel' in werte[1]:
				c1erate = "{:d} %".format(werte[1]['C_dischg_rel'])
			else:
				c1erate = ' '

			if 'C_nenn' in werte[2]:
				c2nenn="{:d} mAh".format(werte[2]['C_nenn'])
			c2l="{:.0f} mAh".format(werte[2]['C_chg'])
			c2e="{:.0f} mAh".format(werte[2]['C_dischg'])
			if 'C_chg_rel' in werte[2]:
				c2lrate = "{:d} %".format(werte[2]['C_chg_rel'])
			else:
				c2lrate = ' '
			if 'C_dischg_rel' in werte[2]:
				c2erate = "{:d} %".format(werte[2]['C_dischg_rel'])
			else:
				c2erate = ' '

			if 'C_nenn' in werte[3]:
				c3nenn="{:d} mAh".format(werte[3]['C_nenn'])
			c3l="{:.0f} mAh".format(werte[3]['C_chg'])
			c3e="{:.0f} mAh".format(werte[3]['C_dischg'])
			if 'C_chg_rel' in werte[3]:
				c3lrate = "{:d} %".format(werte[3]['C_chg_rel'])
			else:
				c3lrate = ' '
			if 'C_dischg_rel' in werte[3]:
				c3erate = "{:d} %".format(werte[3]['C_dischg_rel'])
			else:
				c3erate = ' '

			if 'C_nenn' in werte[4]:
				c4nenn="{:d} mAh".format(werte[4]['C_nenn'])
			c4l="{:.0f} mAh".format(werte[4]['C_chg'])
			c4e="{:.0f} mAh".format(werte[4]['C_dischg'])
			if 'C_chg_rel' in werte[4]:
				c4lrate = "{:d} %".format(werte[4]['C_chg_rel'])
			else:
				c4lrate = ' '
			if 'C_dischg_rel' in werte[4]:
				c4erate = "{:d} %".format(werte[4]['C_dischg_rel'])
			else:
				c4erate = ' '

			sec = werte[1]['t_chg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t1l = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)
			sec = werte[1]['t_dischg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t1e = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)
			sec = werte[2]['t_chg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t2l = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)
			sec = werte[2]['t_dischg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t2e = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)
			sec = werte[3]['t_chg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t3l = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)
			sec = werte[3]['t_dischg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t3e = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)
			sec = werte[4]['t_chg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t4l = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)
			sec = werte[4]['t_dischg']
			min = sec / 60 % 60
			hrs = sec /3600
			sec = sec % 60
			t4e = "{:d}:{:02d}:{:02d}".format(hrs,min,sec)

			if 'E_nenn' in werte[1]:
				e1nenn="{:d} mAh".format(werte[1]['E_nenn'])
			e1l="{:.0f} mWh".format(werte[1]['E_chg'])
			e1e="{:.0f} mWh".format(werte[1]['E_dischg'])
			if 'E_chg_rel' in werte[1]:
				e1lrate = "{:d} %".format(werte[1]['E_chg_rel'])
			else:
				e1lrate = ' '
			if 'E_dischg_rel' in werte[1]:
				e1erate = "{:d} %".format(werte[1]['E_dischg_rel'])
			else:
				e1erate = ' '

			if 'E_nenn' in werte[2]:
				e2nenn="{:d} mAh".format(werte[2]['E_nenn'])
			e2l="{:.0f} mWh".format(werte[2]['E_chg'])
			e2e="{:.0f} mWh".format(werte[2]['E_dischg'])
			if 'E_chg_rel' in werte[2]:
				e2lrate = "{:d} %".format(werte[2]['E_chg_rel'])
			else:
				e2lrate = ' '
			if 'E_dischg_rel' in werte[2]:
				e2erate = "{:d} %".format(werte[2]['E_dischg_rel'])
			else:
				e2erate = ' '

			if 'E_nenn' in werte[3]:
				e3nenn="{:d} mAh".format(werte[3]['E_nenn'])
			e3l="{:.0f} mWh".format(werte[3]['E_chg'])
			e3e="{:.0f} mWh".format(werte[3]['E_dischg'])
			if 'E_chg_rel' in werte[3]:
				e3lrate = "{:d} %".format(werte[3]['E_chg_rel'])
			else:
				e3lrate = ' '
			if 'E_dischg_rel' in werte[3]:
				e3erate = "{:d} %".format(werte[3]['E_dischg_rel'])
			else:
				e3erate = ' '

			if 'E_nenn' in werte[4]:
				e4nenn="{:d} mAh".format(werte[4]['E_nenn'])
			e4l="{:.0f} mWh".format(werte[4]['E_chg'])
			e4e="{:.0f} mWh".format(werte[4]['E_dischg'])
			if 'E_chg_rel' in werte[4]:
				e4lrate = "{:d} %".format(werte[4]['E_chg_rel'])
			else:
				e4lrate = ' '
			if 'E_dischg_rel' in werte[4]:
				e4erate = "{:d} %".format(werte[4]['E_dischg_rel'])
			else:
				e4erate = ' '

			u1eavg="{:4.2f} V".format(werte[1]['U_avg_dischg'])
			u2eavg="{:4.2f} V".format(werte[2]['U_avg_dischg'])
			u3eavg="{:4.2f} V".format(werte[3]['U_avg_dischg'])
			u4eavg="{:4.2f} V".format(werte[4]['U_avg_dischg'])
			u1lavg="{:4.2f} V".format(werte[1]['U_avg_chg'])
			u2lavg="{:4.2f} V".format(werte[2]['U_avg_chg'])
			u3lavg="{:4.2f} V".format(werte[3]['U_avg_chg'])
			u4lavg="{:4.2f} V".format(werte[4]['U_avg_chg'])

		mw = '<?xml version="1.0" encoding="utf-8"?>\n<messwerte>\n<spannung>\n'
		mw += '\t<u1e>'+u1e+'</u1e>\n'
		mw += '\t<u1l>'+u1l+'</u1l>\n'
		mw += '\t<u2e>'+u2e+'</u2e>\n'
		mw += '\t<u2l>'+u2l+'</u2l>\n'
		mw += '\t<u3e>'+u3e+'</u3e>\n'
		mw += '\t<u3l>'+u3l+'</u3l>\n'
		mw += '\t<u4e>'+u4e+'</u4e>\n'
		mw += '\t<u4l>'+u4l+'</u4l>\n'
		mw += '\t<u1eavg>'+u1eavg+'</u1eavg>\n'
		mw += '\t<u2eavg>'+u2eavg+'</u2eavg>\n'
		mw += '\t<u3eavg>'+u3eavg+'</u3eavg>\n'
		mw += '\t<u4eavg>'+u4eavg+'</u4eavg>\n'
		mw += '\t<u1lavg>'+u1lavg+'</u1lavg>\n'
		mw += '\t<u2lavg>'+u2lavg+'</u2lavg>\n'
		mw += '\t<u3lavg>'+u3lavg+'</u3lavg>\n'
		mw += '\t<u4lavg>'+u4lavg+'</u4lavg>\n</spannung>\n'
		
		mw += '<strom>\n\t<i1e>'+i1e+'</i1e>\n'
		mw += '\t<i1l>'+i1l+'</i1l>\n'
		mw += '\t<i2e>'+i2e+'</i2e>\n'
		mw += '\t<i2l>'+i2l+'</i2l>\n'
		mw += '\t<i3e>'+i3e+'</i3e>\n'
		mw += '\t<i3l>'+i3l+'</i3l>\n'
		mw += '\t<i4e>'+i4e+'</i4e>\n'
		mw += '\t<i4l>'+i4l+'</i4l>\n</strom>\n'
		
		mw += '<kapazitaet>\n'
		mw += '\t<c1nenn>'+c1nenn+'</c1nenn>'
		mw += '\t<c1e>'+c1e+'</c1e>\n'
		mw += '\t<c1erate>'+c1erate+'</c1erate>\n'
		mw += '\t<c1l>'+c1l+'</c1l>\n'
		mw += '\t<c1lrate>'+c1lrate+'</c1lrate>\n'
		mw += '\t<c2nenn>'+c2nenn+'</c2nenn>'
		mw += '\t<c2e>'+c2e+'</c2e>\n'
		mw += '\t<c2erate>'+c2erate+'</c2erate>\n'
		mw += '\t<c2l>'+c2l+'</c2l>\n'
		mw += '\t<c2lrate>'+c2lrate+'</c2lrate>\n'
		mw += '\t<c3nenn>'+c3nenn+'</c3nenn>'
		mw += '\t<c3e>'+c3e+'</c3e>\n'
		mw += '\t<c3erate>'+c3erate+'</c3erate>\n'
		mw += '\t<c3l>'+c3l+'</c3l>\n'
		mw += '\t<c3lrate>'+c3lrate+'</c3lrate>\n'
		mw += '\t<c4nenn>'+c4nenn+'</c4nenn>'
		mw += '\t<c4e>'+c4e+'</c4e>\n'
		mw += '\t<c4erate>'+c4erate+'</c4erate>\n'
		mw += '\t<c4l>'+c4l+'</c4l>\n'
		mw += '\t<c4lrate>'+c4lrate+'</c4lrate>\n</kapazitaet>\n'

		mw += '<zeit>\n\t<t1e>'+t1e+'</t1e>\n'
		mw += '\t<t1l>'+t1l+'</t1l>\n'
		mw += '\t<t2e>'+t2e+'</t2e>\n'
		mw += '\t<t2l>'+t2l+'</t2l>\n'
		mw += '\t<t3e>'+t3e+'</t3e>\n'
		mw += '\t<t3l>'+t3l+'</t3l>\n'
		mw += '\t<t4e>'+t4e+'</t4e>\n'
		mw += '\t<t4l>'+t4l+'</t4l>\n</zeit>\n'
		
		mw += '<energie>\n'
		mw += '\t<e1nenn>'+e1nenn+'</e1nenn>'
		mw += '\t<e1e>'+e1e+'</e1e>\n'
		mw += '\t<e1erate>'+e1erate+'</e1erate>\n'
		mw += '\t<e1l>'+e1l+'</e1l>\n'
		mw += '\t<e1lrate>'+e1lrate+'</e1lrate>\n'
		mw += '\t<e2nenn>'+e2nenn+'</e2nenn>'
		mw += '\t<e2e>'+e2e+'</e2e>\n'
		mw += '\t<e2erate>'+e2erate+'</e2erate>\n'
		mw += '\t<e2l>'+e2l+'</e2l>\n'
		mw += '\t<e2lrate>'+e2lrate+'</e2lrate>\n'
		mw += '\t<e3nenn>'+e3nenn+'</e3nenn>'
		mw += '\t<e3e>'+e3e+'</e3e>\n'
		mw += '\t<e3erate>'+e3erate+'</e3erate>\n'
		mw += '\t<e3l>'+e3l+'</e3l>\n'
		mw += '\t<e3lrate>'+e3lrate+'</e3lrate>\n'
		mw += '\t<e4nenn>'+e4nenn+'</e4nenn>'
		mw += '\t<e4e>'+e4e+'</e4e>\n'
		mw += '\t<e4erate>'+e4erate+'</e4erate>\n'
		mw += '\t<e4l>'+e4l+'</e4l>\n'
		mw += '\t<e4lrate>'+e4lrate+'</e4lrate>\n</energie>\n'

		mw += '<status>\n\t<s1>'+s1+'</s1>\n'
		mw += '\t<s1txt>'+s1txt+'</s1txt>\n'
		mw += '\t<cy1>'+cy1+'</cy1>\n'
		mw += '\t<s2>'+s2+'</s2>\n'
		mw += '\t<s2txt>'+s2txt+'</s2txt>\n'
		mw += '\t<cy2>'+cy2+'</cy2>\n'
		mw += '\t<s3>'+s3+'</s3>\n'
		mw += '\t<s3txt>'+s3txt+'</s3txt>\n'
		mw += '\t<cy3>'+cy3+'</cy3>\n'
		mw += '\t<s4>'+s4+'</s4>\n'
		mw += '\t<s4txt>'+s4txt+'</s4txt>\n'
		mw += '\t<cy4>'+cy4+'</cy4>\n</status>\n'

		mw += '<log>\n\t<l1>'+l1+'</l1>\n'
		mw += '\t<l2>'+l2+'</l2>\n'
		mw += '\t<l3>'+l3+'</l3>\n'
		mw += '\t<l4>'+l4+'</l4>\n</log>\n</messwerte>\n'
		
		return mw
	
	def volts(self):
		global Stat
		self.connect()

		werte = [None,self.av4.aktuelle_werte(1),self.av4.aktuelle_werte(2),
			self.av4.aktuelle_werte(3),self.av4.aktuelle_werte(4)]

		#Initialisieren aller Tags
		u1e = u1l = u2e = u2l = u3e = u3l = u4e = u4l = ' '

		if werte[1] <> None:
			u1e="{:.4f}".format(werte[1]['U'])
			u1l="{:.4f}".format(werte[1]['Ustrom'])
			u2e="{:.4f}".format(werte[2]['U'])
			u2l="{:.4f}".format(werte[2]['Ustrom'])
			u3e="{:.4f}".format(werte[3]['U'])
			u3l="{:.4f}".format(werte[3]['Ustrom'])
			u4e="{:.4f}".format(werte[4]['U'])
			u4l="{:.4f}".format(werte[4]['Ustrom'])


		mw = '<?xml version="1.0" encoding="utf-8"?>\n<messwerte>\n<spannung>\n'
		mw += '\t<u1e>'+u1e+'</u1e>\n'
		mw += '\t<u1l>'+u1l+'</u1l>\n'
		mw += '\t<u2e>'+u2e+'</u2e>\n'
		mw += '\t<u2l>'+u2l+'</u2l>\n'
		mw += '\t<u3e>'+u3e+'</u3e>\n'
		mw += '\t<u3l>'+u3l+'</u3l>\n'
		mw += '\t<u4e>'+u4e+'</u4e>\n'
		mw += '\t<u4l>'+u4l+'</u4l>\n'
		mw += '</spannung>\n</messwerte>\n'
		
		return mw
	
	def logbuch(self):
		self.connect()
		lb1 = self.av4.Read_Logbuch(1)
		lb2 = self.av4.Read_Logbuch(2)
		lb3 = self.av4.Read_Logbuch(3)
		lb4 = self.av4.Read_Logbuch(4)
		
		page = '''<?xml version="1.0" encoding="utf-8"?>
<logbuch>
	<logbuch1>{:s}</logbuch1>
	<logbuch2>{:s}</logbuch2>
	<logbuch3>{:s}</logbuch3>
	<logbuch4>{:s}</logbuch4>
</logbuch>'''.format(lb1,lb2,lb3,lb4)
		return page
		
	def analyse(self):
		self.connect()
		[Ana1,Ana2,Ana3,Ana4] = self.av4.Read_Analysen()

		def get_wert(ana,key):
			if key in ana:
				return ana[key]
			else:
				return None
			
		error = [get_wert(Ana1,"error"),
			get_wert(Ana2,"error"),
			get_wert(Ana3,"error"),
			get_wert(Ana4,"error")]
		cycles = [get_wert(Ana1,"cycles"),
			get_wert(Ana2,"cycles"),
			get_wert(Ana3,"cycles"),
			get_wert(Ana4,"cycles")]
		nom_capacity = [get_wert(Ana1,"nom_capacity"),
			get_wert(Ana2,"nom_capacity"),
			get_wert(Ana3,"nom_capacity"),
			get_wert(Ana4,"nom_capacity")]
		charge_end_delta_u = [get_wert(Ana1,"charge_end_delta_u"),
			get_wert(Ana2,"charge_end_delta_u"),
			get_wert(Ana3,"charge_end_delta_u"),
			get_wert(Ana4,"charge_end_delta_u")]
		avg_discharge_voltage = [get_wert(Ana1,"avg_discharge_voltage"),
			get_wert(Ana2,"avg_discharge_voltage"),
			get_wert(Ana3,"avg_discharge_voltage"),
			get_wert(Ana4,"avg_discharge_voltage")]
		discharge_voltage_level = [get_wert(Ana1,"discharge_voltage_level"),
			get_wert(Ana2,"discharge_voltage_level"),
			get_wert(Ana3,"discharge_voltage_level"),
			get_wert(Ana4,"discharge_voltage_level")]
		avg_charge_voltage = [get_wert(Ana1,"avg_charge_voltage"),
			get_wert(Ana2,"avg_charge_voltage"),
			get_wert(Ana3,"avg_charge_voltage"),
			get_wert(Ana4,"avg_charge_voltage")]
		avg_charge_voltage_i = [get_wert(Ana1,"avg_charge_voltage_i"),
			get_wert(Ana2,"avg_charge_voltage_i"),
			get_wert(Ana3,"avg_charge_voltage_i"),
			get_wert(Ana4,"avg_charge_voltage_i")]
		rel_charge_voltage = [get_wert(Ana1,"rel_charge_voltage"),
			get_wert(Ana2,"rel_charge_voltage"),
			get_wert(Ana3,"rel_charge_voltage"),
			get_wert(Ana4,"rel_charge_voltage")]
		rel_discharge_voltage = [get_wert(Ana1,"rel_discharge_voltage"),
			get_wert(Ana2,"rel_discharge_voltage"),
			get_wert(Ana3,"rel_discharge_voltage"),
			get_wert(Ana4,"rel_discharge_voltage")]
		rel_charge_current = [get_wert(Ana1,"rel_charge_current"),
			get_wert(Ana2,"rel_charge_current"),
			get_wert(Ana3,"rel_charge_current"),
			get_wert(Ana4,"rel_charge_current")]
		rel_discharge_current = [get_wert(Ana1,"rel_discharge_current"),
			get_wert(Ana2,"rel_discharge_current"),
			get_wert(Ana3,"rel_discharge_current"),
			get_wert(Ana4,"rel_discharge_current")]
		capacity = [get_wert(Ana1,"capacity"),
			get_wert(Ana2,"capacity"),
			get_wert(Ana3,"capacity"),
			get_wert(Ana4,"capacity")]
		charge_capacity = [get_wert(Ana1,"charge_capacity"),
			get_wert(Ana2,"charge_capacity"),
			get_wert(Ana3,"charge_capacity"),
			get_wert(Ana4,"charge_capacity")]
		efficiency = [get_wert(Ana1,"efficiency"),
			get_wert(Ana2,"efficiency"),
			get_wert(Ana3,"efficiency"),
			get_wert(Ana4,"efficiency")]
		energy = [get_wert(Ana1,"energy"),
			get_wert(Ana2,"energy"),
			get_wert(Ana3,"energy"),
			get_wert(Ana4,"energy")]
		charge_energy = [get_wert(Ana1,"charge_energy"),
			get_wert(Ana2,"charge_energy"),
			get_wert(Ana3,"charge_energy"),
			get_wert(Ana4,"charge_energy")]
		energy_efficiency = [get_wert(Ana1,"energy_efficiency"),
			get_wert(Ana2,"energy_efficiency"),
			get_wert(Ana3,"energy_efficiency"),
			get_wert(Ana4,"energy_efficiency")]
		rel_capacity = [get_wert(Ana1,"rel_capacity"),
			get_wert(Ana2,"rel_capacity"),
			get_wert(Ana3,"rel_capacity"),
			get_wert(Ana4,"rel_capacity")]
		rel_charge_capacity = [get_wert(Ana1,"rel_charge_capacity"),
			get_wert(Ana2,"rel_charge_capacity"),
			get_wert(Ana3,"rel_charge_capacity"),
			get_wert(Ana4,"rel_charge_capacity")]
		rel_energy = [get_wert(Ana1,"rel_energy"),
			get_wert(Ana2,"rel_energy"),
			get_wert(Ana3,"rel_energy"),
			get_wert(Ana4,"rel_energy")]
		rel_charge_energy = [get_wert(Ana1,"rel_charge_energy"),
			get_wert(Ana2,"rel_charge_energy"),
			get_wert(Ana3,"rel_charge_energy"),
			get_wert(Ana4,"rel_charge_energy")]
		avg_charge_ri = [get_wert(Ana1,"avg_charge_ri"),
			get_wert(Ana2,"avg_charge_ri"),
			get_wert(Ana3,"avg_charge_ri"),
			get_wert(Ana4,"avg_charge_ri")]
		r_index = [get_wert(Ana1,"r_index"),
			get_wert(Ana2,"r_index"),
			get_wert(Ana3,"r_index"),
			get_wert(Ana4,"r_index")]
		flat_voltage = [get_wert(Ana1,"flat_voltage"),
			get_wert(Ana2,"flat_voltage"),
			get_wert(Ana3,"flat_voltage"),
			get_wert(Ana4,"flat_voltage")]
		flat_ri = [get_wert(Ana1,"flat_ri"),
			get_wert(Ana2,"flat_ri"),
			get_wert(Ana3,"flat_ri"),
			get_wert(Ana4,"flat_ri")]
		urteil = [get_wert(Ana1,"urteil"),
			get_wert(Ana2,"urteil"),
			get_wert(Ana3,"urteil"),
			get_wert(Ana4,"urteil")]

		ana = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>AV4ms Analyse</title>
<link href="static/style.css" rel="stylesheet" type="text/css" />
<link rel="shortcut icon" href="/static/favicon2.png" type="image/x-icon" />
</head>
<body>
<table id="table_inner">
\t<tr>
'''
		for i in range(4):
			ana += '\t\t<td valign="top">\n\t\t\t<fieldset>\n\t\t\t<legend>Zelle {:d}</legend>\n\t\t\t<table id="table_schacht">\n'.format(i+1)
			
			if error[i] <> None:
				ana += '\t\t\t\t<tr><td colspan="2">{:s}</td></tr>\n'.format(error[i])
			if cycles[i] <> None:
				ana += '\t\t\t\t<tr><td>Anzahl Zyklen</td><td>{:d}</td></tr>\n'.format(cycles[i])
			if charge_end_delta_u[i] <> None:
				if charge_end_delta_u[i]: janein = "Ja"
				else: janein = "Nein"
				ana += '\t\t\t\t<tr><td>Ladeende &minus;&Delta;U</td><td>{:s}</td></tr>\n'.format(janein)				
			if avg_discharge_voltage[i] <> None:
				ana += '\t\t\t\t<tr><td>&Oslash;&nbsp;Spannung (E)</td><td>{:.2f}&nbsp;V</td></tr>\n'.format(avg_discharge_voltage[i])
			if discharge_voltage_level[i] <> None:
				ana += '\t\t\t\t<tr><td>Spannungslage (E)</td><td>{:.0f}%</td></tr>\n'.format(discharge_voltage_level[i])
			if avg_charge_voltage[i] <> None:
				ana += '\t\t\t\t<tr><td>&Oslash;&nbsp;Spannung stromlos (L)</td><td>{:.2f}&nbsp;V</td></tr>\n'.format(avg_charge_voltage[i])
			if avg_charge_voltage_i[i] <> None:
				ana += '\t\t\t\t<tr><td>&Oslash;&nbsp;Spannung unter Strom (L)</td><td>{:.2f}&nbsp;V</td></tr>\n'.format(avg_charge_voltage_i[i])
			if rel_charge_voltage[i] <> None:
				ana += '\t\t\t\t<tr><td>rel. Spannung (L)</td><td>{:.0f}%</td></tr>\n'.format(rel_charge_voltage[i])
			if rel_discharge_voltage[i] <> None:
				ana += '\t\t\t\t<tr><td>rel. Spannung (E)</td><td>{:.0f}%</td></tr>\n'.format(rel_discharge_voltage[i])
			if rel_charge_current[i] <> None:
				if rel_charge_current[i] <> 0.0:
					ana += '\t\t\t\t<tr><td>rel. Strom (L)</td><td>C/{:.1f}</td></tr>\n'.format(1.0 / rel_charge_current[i])
			if rel_discharge_current[i] <> None:
				if rel_discharge_current[i] <> 0.0:
					ana += '\t\t\t\t<tr><td>rel. Strom (E)</td><td>C/{:.1f}</td></tr>\n'.format(1.0 / rel_discharge_current[i])
			if nom_capacity[i] <> None:
				ana += '\t\t\t\t<tr><td>Nennkapazität</td><td>{:d}&nbsp;mAh</td></tr>\n'.format(nom_capacity[i])
			if capacity[i] <> None:
				ana += '\t\t\t\t<tr><td>Kapazität (E)</td><td>{:d}&nbsp;mAh</td></tr>\n'.format(capacity[i])
			if rel_capacity[i] <> None:
				ana += '\t\t\t\t<tr><td>rel. Kapazität (E)</td><td>{:.0f}%</td></tr>\n'.format(rel_capacity[i])
			if charge_capacity[i] <> None:
				ana += '\t\t\t\t<tr><td>Kapazität (L)</td><td>{:d}&nbsp;mAh</td></tr>\n'.format(charge_capacity[i])
			if rel_charge_capacity[i] <> None:
				ana += '\t\t\t\t<tr><td>rel. Kapazität (L)</td><td>{:.0f}%</td></tr>\n'.format(rel_charge_capacity[i])
			if efficiency[i] <> None:
				ana += '\t\t\t\t<tr><td>Effizienz</td><td>{:.0f}%</td></tr>\n'.format(efficiency[i])
			if energy[i] <> None:
				ana += '\t\t\t\t<tr><td>Energie (E)</td><td>{:d}&nbsp;mWh</td></tr>\n'.format(energy[i])
			if rel_energy[i] <> None:
				ana += '\t\t\t\t<tr><td>rel. Energie (E)</td><td>{:.0f}%</td></tr>\n'.format(rel_energy[i])
			if charge_energy[i] <> None:
				ana += '\t\t\t\t<tr><td>Energie (L)</td><td>{:d}&nbsp;mWh</td></tr>\n'.format(charge_energy[i])
			if rel_charge_energy[i] <> None:
				ana += '\t\t\t\t<tr><td>rel. Energie (L)</td><td>{:.0f}%</td></tr>\n'.format(rel_charge_energy[i])
			if energy_efficiency[i] <> None:
				ana += '\t\t\t\t<tr><td>Energieeffizienz</td><td>{:.0f}%</td></tr>\n'.format(energy_efficiency[i])
			if avg_charge_ri[i] <> None:
				ana += '\t\t\t\t<tr><td>Mittlerer Ri (L)</td><td>{:d}&nbsp;m&Omega;</td></tr>\n'.format(avg_charge_ri[i])
			if r_index[i] <> None:
				ana += '\t\t\t\t<tr><td>Ri-Index (L)</td><td>{:.1f}%</td></tr>\n'.format(r_index[i])
			if flat_voltage[i] <> None:
				ana += '\t\t\t\t<tr><td>Spannung leer</td><td>{:.2f}&nbsp;V</td></tr>\n'.format(flat_voltage[i])
			if flat_ri[i] <> None:
				ana += '\t\t\t\t<tr><td>Ri leer</td><td>{:d}&nbsp;m&Omega;</td></tr>\n'.format(flat_ri[i])
			if urteil[i] <> None:
				ana += '\t\t\t\t<tr><td>Beurteilung</td><td>{:s}</td></tr>\n'.format(urteil[i])
			ana += '\t\t\t</table>\n\t\t\t</fieldset>\n\t\t</td>\n'

		ana += '\t</tr>\n</table>\n</body>\n</html>'

		return ana
