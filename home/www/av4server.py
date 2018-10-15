#!/usr/bin/env python
#-*-coding: utf-8 -*-

import sys, os
import serial
from threading import Thread
import daemon
import fcntl
import binascii
import time
import sys, os, os.path
import ConfigParser
import argparse
import gzip
import logging, logging.handlers
import Pyro.core
from Pyro.errors import PyroError
import netifaces
import traceback
import locale

from av4analyse import Messwert, Analyse
from av4logbuch import Logbuch
from SockServer import SockServer

sys.path.insert(0, '/home/www/odslib')
import odslib

paragraf = binascii.unhexlify('a7') # Scheiss Windows-Zeichensatz
global logger
logger = None

def WaitForNetwork():
	while True:
		for iface in netifaces.interfaces():
			adresses = netifaces.ifaddresses(iface)
			if netifaces.AF_INET in adresses:
				iadr = adresses[netifaces.AF_INET][0]
				if iadr['addr'] != '127.0.0.1':
					return
		time.sleep(30)

def Reader(server,logger):
	logger.info("Reader started")
	while True:
		try:
			ser = serial.Serial(port=server.DeviceName,baudrate=115200,timeout=10)
			#logger.info("Serial port {:s} opened".format(server.DeviceName))
			line = ser.readline()  # 1. verstümmelte Zeile überlesen
			line = ser.readline()
			while line != '':
				if not server.SerialConnected:
					logger.info("Datenempfang gestartet")
					server.SerialConnected = True
				server.ProcessData(line)
				line = ser.readline()
			if server.SerialConnected:
				logger.warning("Datemempfang unterbrochen")
				server.SerialConnected = False
			ser.close()
		except:
			server.SerialConnected = False
			logger.error(traceback.format_exc())
		time.sleep(60)
			
class AV4Server(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		self.Reading = True
		self.SerialConnected = False
		self.Logging = False
		self.Autostop = False
		self.stoptimer = None
		self.Idle = True
		self.Kanal = [None,None,None,None,None,None,None,None,None]
		self.K7tmp = None
		self.Ana1 = Analyse(schacht=1)
		self.Ana2 = Analyse(schacht=2)
		self.Ana3 = Analyse(schacht=3)
		self.Ana4 = Analyse(schacht=4)
		self.Ana = [None,self.Ana1,self.Ana2,self.Ana3,self.Ana4]
		self.Logbuch = [None,Logbuch(),Logbuch(),Logbuch(),Logbuch()]
		self.ReadConfig()
		self.Start_Reader()
		self.SockServer = SockServer()
		
	def ReadConfig(self):
		config = ConfigParser.RawConfigParser()
		config.read('/etc/av4server.conf')
		self.DeviceName = config.get('av4server','device')
		self.LogDirectory = config.get('av4server','logdir')
		self.LogFilename = config.get('av4server','logfile')
		try:
			self.Timestamps = config.getboolean('av4server','timestamps')
		except ConfigParser.NoOptionError:
			self.Timestamps = False
		try:
			self.Compress = config.getboolean('av4server','compress')
		except ConfigParser.NoOptionError:
			self.Compress = False
		try:
			self.astoptime = config.getint('av4server','autostop')
		except ConfigParser.NoOptionError:
			self.astoptime = 600
		try:
			self.RawRecord = config.getboolean('av4server','rawrecord')
		except ConfigParser.NoOptionError:
			self.RawRecord = False
		try:
			self.RawCast = config.getboolean('av4server','rawcast')
		except ConfigParser.NoOptionError:
			self.RawCast = False
		try:
			self.Ukorr = config.getfloat('av4server','ukorr')
			logger.info("Spannungskorrekturfaktor {:f}".format(self.Ukorr))
		except ConfigParser.NoOptionError:
			self.Ukorr = None
		
	def TimestampLine(self,line):
		# Timestamp in Openformat-Zeile einfügen
		ts = '{:.3f}'.format(time.time())
		return line[0:5] + ts + line[5:]

	def voltage_corr(self,channel,line):
		# Zeile von Kanal 1/5 zerlegen, Spannungen/Energie korrigieren
		# und wieder zusammenbauen
		f = line.rstrip().split(';')
		line = "${:d};1;".format(channel)
		for i in range(3,11):
			u = int(round(float(f[i]) * self.Ukorr))
			line += ";{:05d}".format(u)
		line += ";0\n"
		return line
		
	def ProcessData(self,line):
		global paragraf, logger
		
		# Roh an alle Socks Listener schicken
		if self.RawCast == True:
			self.SockServer.broadcast(line)
		
		if line[0] == paragraf:
			line = '$' + line[1:]

		# Korrektur wg. nicht kalibrierter Referenzspannung
		# kann entfallen wenn die Firmware das macht
		if self.Ukorr != None:
			if line[0:2] == '$1':   # Spannungen korrigieren
				line = self.voltage_corr(1,line)
			elif line[0:2] == '$5':  # Energie korrigieren
				line = self.voltage_corr(5,line)
		
		# Bearbeitet an alle Socks Listener schicken
		if self.RawCast == False and line[0] == '$':
			self.SockServer.broadcast(line)
			
		if self.Logging == True:
			if line[0] == '$' or self.RawRecord:      # Keine Morsecodes und anderen Müll
				if self.Timestamps:
					self.Logfile.write(self.TimestampLine(line))
				else:
					self.Logfile.write(line)
					
		line = line.rstrip()
		if line[0] == '$':
			f = line.split(';')
			if f[0] == '$1':
				if len(f) < 12: return # ungültige Daten
				self.Kanal[1] = f
			elif f[0] == '$2':
				if len(f) < 12: return # ungültige Daten
				self.Kanal[2] = f
			elif f[0] == '$3':
				if len(f) < 12: return # ungültige Daten
				self.Kanal[3] = f
			elif f[0] == '$4':
				if len(f) < 12: return # ungültige Daten
				self.Kanal[4] = f
			elif f[0] == '$5':
				if len(f) < 12: return # ungültige Daten
				self.Kanal[5] = f
			elif f[0] == '$6':
				if len(f) < 8:  return # ungültige Daten
				self.Kanal[6] = f
				#print K6
			elif f[0] == '$7':
				if len(f) < 8:  return # ungültige Daten
				self.K7tmp = f         # Kanal 7 & 8 nur gemeinsam bereit stellen
				#print K7
			elif f[0] == '$8':
				if len(f) < 8:  return # ungültige Daten
				if self.K7tmp == None: return # Kanal 7 fehlt
				self.Kanal[7] = self.K7tmp
				self.Kanal[8] = f
				idle_before = self.Idle
				self.Idle = self.Alle_Zellen_fertig(f)
				finished = self.Idle and not idle_before
				if self.Kanal[1] <> None:  # Kanaele vollständig?
					# Messwerte aus Kanälen extrahieren
					try:
						mw1 = Messwert(0,self.Kanal[1],self.Kanal[2],self.Kanal[3],self.Kanal[4],self.Kanal[5],self.Kanal[6],self.Kanal[7],self.Kanal[8])
						self.Ana1.messwert(mw1)
						if mw1.state == '-':         # Keine Zelle
							self.Logbuch[1].clear()  # Logbuch löschen
						else:
							self.Logbuch[1].update(mw1.logmsg())
					except ValueError:
						logger.warning("Datenfehler")
					
					try:
						mw2 = Messwert(1,self.Kanal[1],self.Kanal[2],self.Kanal[3],self.Kanal[4],self.Kanal[5],self.Kanal[6],self.Kanal[7],self.Kanal[8])
						self.Ana2.messwert(mw2)
						if mw2.state == '-':         # Keine Zelle
							self.Logbuch[2].clear()  # Logbuch löschen
						else:
							self.Logbuch[2].update(mw2.logmsg())
					except ValueError:
						logger.warning("Datenfehler")

					try:
						mw3 = Messwert(2,self.Kanal[1],self.Kanal[2],self.Kanal[3],self.Kanal[4],self.Kanal[5],self.Kanal[6],self.Kanal[7],self.Kanal[8])
						self.Ana3.messwert(mw3)
						if mw3.state == '-':         # Keine Zelle
							self.Logbuch[3].clear()  # Logbuch löschen
						else:
							self.Logbuch[3].update(mw3.logmsg())
					except ValueError:
						logger.warning("Datenfehler")

					try:
						mw4 = Messwert(3,self.Kanal[1],self.Kanal[2],self.Kanal[3],self.Kanal[4],self.Kanal[5],self.Kanal[6],self.Kanal[7],self.Kanal[8])
						self.Ana4.messwert(mw4)
						if mw4.state == '-':         # Keine Zelle
							self.Logbuch[4].clear()  # Logbuch löschen
						else:
							self.Logbuch[4].update(mw4.logmsg())
					except ValueError:
						logger.warning("Datenfehler")

				# Bei Ladeende Analysetabelle erzeugen
				if finished and not self.Alle_Schaechte_leer(f):
					self.AnalyseODS()
					
				# Soll Aufzeichnung beendet werden?
				if self.stoptimer <> None:
					self.stoptimer -= 1
					if self.stoptimer <= 0:
						self.stop_logging()
						self.stoptimer = None
						logger.info("Aufzeichnung automatisch gestoppt")
				elif self.Autostop:
					if self.Idle:
						self.stoptimer = self.astoptime
						self.Autostop = False
						logger.info("Laden beendet, Aufzeichnungsstop in {:d} Sekunden".format(self.astoptime))
				#print K8

	def AnalyseODS(self,overwrite=False):
		global logger
		
		#Dateiname
		fn = self.LogFilename
		if fn[-4:] == '.csv':    # .csv abschneiden
			fn = fn[:-4]
		fn = '/home/www/av4logs/' + fn + '.ods'

		# vorhandene Analysen nicht überschreiben
		if os.path.exists(fn) and not overwrite:
			logger.info('Analyse ' + fn + ' existiert bereits')
			return
		
		doc=odslib.ODS()
		doc.content.getSheet(0).setSheetName("Analyse")

		# Spalten-Beschriftung
		doc.content.getColumn(0).setWidth("6.3cm")
		doc.content.getCell(1, 0).stringValue("Zelle 1").setAlignHorizontal("right")
		doc.content.getCell(2, 0).stringValue('Zelle 2').setAlignHorizontal("right")
		doc.content.getCell(3, 0).stringValue('Zelle 3').setAlignHorizontal("right")
		doc.content.getCell(4, 0).stringValue('Zelle 4').setAlignHorizontal("right")


		#Analysen besorgen
		analysed = False
		ana=self.Read_Analysen()
		for zelle in range(0,4):
			a = ana[zelle]
			if not 'error' in a:
				self.AnalyseODSfields(doc,zelle,a,not analysed)
				analysed = True

		if analysed:
			doc.save(fn)		

	def AnalyseODSfields(self,doc,zelle,a,label):
		from av4analyse import Analyse
		Analyse = Analyse()
		col = zelle + 1
		row = 0
		for tag in Analyse.taglist:
			row += 1
			if tag in a:
				val = a[tag]
					
				# Prozentwerte durch 100 teilen
				if tag in ['discharge_voltage_level','rel_charge_voltage','rel_discharge_voltage',
						   'rel_capacity','rel_energy','rel_charge_capacity','rel_charge_energy',
						   'efficiency','energy_efficiency']:
					#val /=  100
					val = round(float(val),0)
				elif tag in ['rel_charge_current','rel_discharge_current']:
					v = float(val)
					if v != 0.0:
						val = "C/{:.1f}".format(1.0 / v)
					else:
						val = "--"
				elif tag != 'urteil':
					val = round(float(val),2)
				
				if tag in ['urteil','capacity','r_index','avg_discharge_voltage']:
					bold = True
				else:
					bold = False
					
				txt = Analyse.tag_description(tag)
				if label:
					doc.content.getCell(0,row).stringValue(txt).setBold(bold)
				if tag in ['urteil','rel_charge_current','rel_discharge_current']:
					doc.content.getCell(col,row).stringValue(val).setBold(bold).setAlignHorizontal('right')
				else:
					doc.content.getCell(col,row).floatValue(val).setBold(bold)
							
	def Alle_Zellen_fertig(self,flags):
		try:
			if int(flags[3]) & 3 <> 0:        # Schacht 1 laden oder entladen
				return False
			if int(flags[4]) & 3 <> 0:        # Schacht 2 laden oder entladen
				return False
			if int(flags[5]) & 3 <> 0:        # Schacht 3 laden oder entladen
				return False
			if int(flags[6]) & 3 <> 0:        # Schacht 4 laden oder entladen
				return False
			return True
		except ValueError:
			return False
				
	def Alle_Schaechte_leer(self,flags):
		try:
			if int(flags[3]) <> 0:		# Schacht 1 nicht leer
				return False
			if int(flags[4]) <> 0:		# Schacht 2 nicht leer
				return False
			if int(flags[5]) <> 0:		# Schacht 3 nicht leer
				return False
			if int(flags[6]) <> 0:		# Schacht 4 nicht leer
				return False
			return True
		except ValueError:
			return False
				
	def Start_Reader(self):
		# Reader muss im Background laufen damit er nicht blockiert
		global logger
		self.ReaderThread = Thread(target=Reader,args=(self,logger,))
		self.ReaderThread.start()

	def log_file(self,filename):
		self.LogFilename = filename
		if not '.' in self.LogFilename:
			self.LogFilename += '.csv'
					
	def start_logging(self,fname=None):
		global logger
		if (self.Logging == True):
			return "Aufzeichnung läuft bereits"
		
		if fname <> None:
			self.LogFilename = fname
			
		filename = self.LogDirectory + '/' + self.LogFilename
		
		self.Logging = True
		if self.Compress:
			self.Logfile = gzip.open(filename+'.gz','a')
		else:
			self.Logfile = open(filename,'a')
		logger.info('Starting Log on ' + filename)
		return "Aufzeichnung gestartet"
	
	def set_autostop(self,status):
		global logger
		if status <> self.Autostop:
			if status == True and self.Idle:
				logger.info("Lader untätig, Autostop nicht möglich")
				return
			self.Autostop = status
			if status == True:
				logger.info("Autostop aktiviert")
			else:
				logger.info("Autostop deaktiviert")
		if status == False:
			self.stoptimer = None

	def get_autostop(self):
		return self.Autostop or self.stoptimer <> None
	
	def stop_logging(self):
		global logger
		self.set_autostop(False)
		if self.Logging:
			self.Logging = False
			self.Logfile.close()
			logger.info("Aufzeichnung gestoppt")
		return "Aufzeichnung gestoppt"
	
	def Status_Reading(self):
		return self.Reading
	
	def Status_Serial(self):
		return self.SerialConnected
		
	def Status_Logging(self):
		return self.Logging
	
	def Status_Logfile(self):
		return self.LogFilename
	
	def Read_Kanal(self,kanal):
		return self.Kanal[kanal]
	
	def Read_Kanaele(self):
		return self.Kanal
	
	def aktuelle_werte(self,schacht):
		w = self.Ana[schacht].aktuelle_werte()
		if not self.SerialConnected:
			w['StatusMsg'] = 'Keine Verbindung zum Ladegerät'
		return w
	
	def Read_Logbuch(self,schacht):
		return self.Logbuch[schacht].logbuch
	
	def Read_Analyse(self,schacht):
		if schacht == 1:
			return self.Ana1.ergebnis()
		elif schacht == 2:
			return self.Ana2.ergebnis()
		elif schacht == 3:
			return self.Ana3.ergebnis()
		elif schacht == 4:
			return self.Ana4.ergebnis()

	def Set_C_nenn(self,schacht,c):
		if schacht == 1:
			self.Ana1.set_c_nenn(c)
		elif schacht == 2:
			self.Ana2.set_c_nenn(c)
		elif schacht == 3:
			self.Ana3.set_c_nenn(c)
		elif schacht == 4:
			self.Ana4.set_c_nenn(c)
		
	def Get_C_nenn(self,schacht):
		if schacht == 1:
			return self.Ana1.get_c_nenn()
		elif schacht == 2:
			return self.Ana2.get_c_nenn()
		elif schacht == 3:
			return self.Ana3.get_c_nenn()
		elif schacht == 4:
			return self.Ana4.get_c_nenn()
		
	def Read_Analysen(self):
		return [self.Ana1.ergebnis(),self.Ana2.ergebnis(),self.Ana3.ergebnis(),self.Ana4.ergebnis()]

	def Read_Analyse_text(self,schacht):
		if schacht == 1:
			return self.Ana1.ergebnis_text()
		elif schacht == 2:
			return self.Ana2.ergebnis_text()
		elif schacht == 3:
			return self.Ana3.ergebnis_text()
		elif schacht == 4:
			return self.Ana4.ergebnis_text()
		
	def shutdown(self):
		self.stop_logging()
		os.system("sudo shutdown -h now")
		
class PidFile(object):
	"""Context manager that locks a pid file.  Implemented as class
	not generator because daemon.py is calling .__exit__() with no parameters
	instead of the None, None, None specified by PEP-343."""
	# pylint: disable=R0903

	def __init__(self, path):
		self.path = path
		self.pidfile = None

	def __enter__(self):
		self.pidfile = open(self.path, "a+")
		try:
			fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
		except IOError:
			raise SystemExit("Already running according to " + self.path)
		self.pidfile.seek(0)
		self.pidfile.truncate()
		self.pidfile.write(str(os.getpid()))
		self.pidfile.flush()
		self.pidfile.seek(0)
		return self.pidfile

	def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
		try:
			self.pidfile.close()
		except IOError as err:
			# ok if file was just closed elsewhere
			if err.errno != 9:
				raise
		os.remove(self.path)

def run():
	global logger
	try:
		locale.setlocale(locale.LC_ALL, '')
		logger = logging.getLogger('av4server')
		hdlr = logging.handlers.TimedRotatingFileHandler('/var/log/av4server/av4server.log',\
						when='midnight',backupCount=7)
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr) 
		logger.setLevel(logging.INFO)

		#Warten bis Netzwerk bereit ist
		logger.info("Waiting for Network")
		WaitForNetwork()
		
		# Pyro Server starten
		logger.info("Init Pyro Server")
		Pyro.core.initServer()
		logger.info("Initiate Pyro Daemon")
		pyrodaemon = Pyro.core.Daemon()
		logger.info("Connect to Pyro Daemon")
		uri=pyrodaemon.connect(AV4Server(),'AV4Server')

		# enter the service loop.
		print 'AV4Server is ready.'
		print 'The URI is: ',uri

		logger.info('The URI is: ' + uri.__str__())
		pyrodaemon.requestLoop()
	except SystemExit:
		sys.exit()
	except:
		f = open('/tmp/av4server.trace','w')
		traceback.print_exc(file=f)
		f.close()
		sys.exit()
	
parser = argparse.ArgumentParser(description='AV4 Server')
parser.add_argument('--nodaemon', dest='nodaemon', action='store_true',
				help='Server im Vordergrund starten')

args = parser.parse_args()

if args.nodaemon == True:
	run()
else:
	context = daemon.DaemonContext(
		working_directory = '/tmp',
		umask=0o002,
		pidfile = PidFile("/tmp/av4server.pid"),
		files_preserve = [sys.stdout,sys.stderr]
		)
	with context:
		run()
