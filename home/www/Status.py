#!/usr/bin/env python
#-*-coding: utf-8 -*-

# Klasse für die Status/Logmeldungen des AV4
class Status:
	# Flags:
	# bit 0 = Laden
	# bit 1 = Entladen
	# bit 2 = Trickle charge
	# bit 3 = Error
	# bit 4 = Pause
	# bit 5 = Cycle aktiv
	# bit 6 = Micro-Zelle
	# bit 7 = Hot

	HOT = 0b10000000
	AAA = 0b01000000
	CYC = 0b00100000
	PAU = 0b00010000
	ERR = 0b00001000
	TRI = 0b00000100
	DIS = 0b00000010
	CHG = 0b00000001
	
	def bit(self,f,b):
		return (f & b) == b
		
	def Laden(self,f):
		return self.bit(int(f),self.CHG)

	def Entladen(self,f):
		return self.bit(int(f),self.DIS)

	def Voll(self,f):
		return self.bit(int(f),self.TRI)

	def ZellTyp(self,f):
		if self.bit(f,self.AAA):
			return 'Micro Zelle'
		else:
			return 'Mignon Zelle'
			
	def StatusMessage(self,status,flags,debug=False):
		
		s = int(status)
		f = int(flags)

		if debug:
			msg = '#' + status + ':' + hex(f)
		else:
			msg = ' '
		
		if   s == 0:				msg = "Keine Zelle erkannt"
		elif s == 5:
									msg = self.ZellTyp(f) + " formieren"              
		elif s == 10 or s == 15:
			msg = self.ZellTyp(f) + " entlädt"
			if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s == 25:
			msg = self.ZellTyp(f) + " prüft Entladeende"
			if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s == 35:
			msg = self.ZellTyp(f) + " entladen beendet"
			if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s == 40:
			msg = self.ZellTyp(f) + " lädt"
			if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s > 40 and s < 100:
			msg = self.ZellTyp(f) + " lädt\nVollerkennung aktiv"
			if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s >= 100 and s < 180:
			msg = self.ZellTyp(f) + " laden beendet"
			if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s == 180 or s == 185:
			msg = self.ZellTyp(f) + " Voll\nLadeerhaltung aktiv"

		elif s == 200:
			if self.bit(f,self.DIS):
				msg = self.ZellTyp(f) + " pausiert beim Entladen"
				if self.bit(f,self.CYC): msg += '\nRecycle aktiv'
			elif self.bit(f,self.CHG):
				msg = self.ZellTyp(f) + " pausiert beim Laden"
				if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s == 225:
			msg = "Übertemperatur: Laden einer " + self.ZellTyp(f) + " pausiert"
			if self.bit(f,self.CYC): msg += '\nRecycle aktiv'

		elif s == 230 or s == 235:
			msg = "Zelle wegen fehlgeschlagenem HOT-Recycle gesperrt"

		elif s == 240:
			if   self.bit(f,self.PAU):	msg = "Spanung an " + self.ZellTyp(f) + " während Pause am wegbrechen"
			elif self.bit(f,self.ERR):	msg = "Zelle wegen zu niedriger Spannung bei der Bearbeitung gesperrt"
			else:						msg = "Spanung an " + self.ZellTyp(f) + " am wegbrechen oder vom Formatieren noch zu wenig"
			if self.bit(f,self.CYC):	msg += '\nRecycle aktiv'

		elif s == 245:
			if self.bit(f,self.ERR):	msg = "Zelle wegen zu hoher Spannung bei der Bearbeitung gesperrt"
			else:						msg = "Spanung an " + self.ZellTyp(f) + " im Moment sehr hoch"
			if self.bit(f,self.CYC):	msg += '\nRecycle aktiv'

		elif s == 250:
			msg = "Zelle wegen zu hoher Spannung beim Einschalten / Einlegen gesperrt"

		return msg

	def LogMessage(self,status,flags):
		s = int(status)
		f = int(flags)

		msg = ''
		
		if   s == 0:				msg = "Keine Zelle erkannt oder Zelle wurde entnommen"

		elif s == 5:
									msg = "Formieren vom Anwender auf allen freien Schächten gestartet, in denen keine Zelle erkannt wurde"

		elif s == 10:
									msg = "Entladen einer " + self.ZellTyp(f) + " beginnt"

		elif s == 35:
			msg = "Entladen einer " + self.ZellTyp(f) + " wurde beendet"
			if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 40:
			if self.bit(f,self.CHG):     msg = "Laden einer " + self.ZellTyp(f) + " beginnt/wird fortgesetzt"

		elif s == 50:
			if self.bit(f,self.CHG):     msg = "Laden einer " + self.ZellTyp(f) + " beginnt/wird fortgesetzt"

		elif s == 65:
			if self.bit(f,self.CHG):
				msg = "Beim Laden einer " + self.ZellTyp(f) + " wurde deutlicher Spannungsanstieg erkannt"
				if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 75:
			if self.bit(f,self.CHG):
				msg = "Beim Laden einer " + self.ZellTyp(f) + " wurde kleiner Spannungsanstieg erkannt"
				if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 85:
			if self.bit(f,self.CHG):
				msg = "Beim Laden einer " + self.ZellTyp(f) + " wurde ebener Spannungsverlauf erkannt"
				if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 95:
			if self.bit(f,self.CHG):
				msg = "Beim Laden einer " + self.ZellTyp(f) + " wurde Rückgang der Spannung erkannt"
				if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 100:
			msg = "Laden einer " + self.ZellTyp(f) + " wurde wegen ebenem Spannungsverlauf beendet"
			if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 105:
			msg = "Laden einer " + self.ZellTyp(f) + " wurde wegen einem Rückgang der Spannung beendet"
			if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 110 or s == 115:
			msg = "Laden einer " + self.ZellTyp(f) + " wurde wegen Übertemperatur beendet"
			if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 120 or s == 125:
			msg = "Ladestrom einer " + self.ZellTyp(f) + " wegen Übertemperatur reduziert"
			if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 130 or s == 135:
			msg = "Laden einer " + self.ZellTyp(f) + " wegen Übertemperatur abgebrochen -- Recycle beginnt"

		elif s == 140:
			if self.bit(f,self.CYC):   msg = "Entladen einer " + self.ZellTyp(f) + " beendet -- Recycle fortgesetzt, da noch nicht oft genug entladen wurde"

		elif s == 145:
			if self.bit(f,self.CYC):   msg = "Laden einer " + self.ZellTyp(f) + " wegen Übertemperatur abgebrochen -- Recycle wird fortgesetzt, da noch nicht oft genug entladen wurde"

		elif s == 150:
			if self.bit(f,self.CYC):   msg = "Laden einer " + self.ZellTyp(f) + " wegen Übertemperatur abgebrochen -- Recycle wird fortgesetzt, da noch nicht oft genug entladen wurde"

		elif s == 155:
			if self.bit(f,self.CYC):   msg = "Entladen einer " + self.ZellTyp(f) + " beendet -- Recycle fortgesetzt, da mehr Ah entladen wurden als zuvor"

		elif s == 160 or s == 165:
			if self.bit(f,self.CYC):   msg = "Laden einer " + self.ZellTyp(f) + " wegen Übertemperatur abgebrochen -- Recycle wird fortgesetzt, da mehr Ah entladen wurden als zuvor"

		elif s == 170:
			if self.bit(f,self.CYC|self.DIS):   msg = "Recycle einer " + self.ZellTyp(f) + " wurde aktiviert"

		elif s == 175:
			if self.bit(f,self.CYC|self.CHG):   msg = "Entladen einer " + self.ZellTyp(f) + " beendet -- Recycle wird mit der Abschluss-Ladung beendet, da keine weitere Kapazitätszunahme erreicht wurde"

		elif s == 200:
			if   self.bit(f,self.PAU|self.DIS):
				msg = "Pause beim Entladen einer " + self.ZellTyp(f)
				if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'
			elif self.bit(f,self.PAU|self.CHG):
				msg = "Pause beim Laden einer " + self.ZellTyp(f)
				if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 225:
			if self.bit(f,self.CHG):
				msg = "Übertemperatur: Laden einer " + self.ZellTyp(f) + " pausiert"
				if self.bit(f,self.CYC):	msg += ' -- Recycle aktiv'

		elif s == 230 or s == 235:
			if self.bit(f,self.ERR):	msg = "Zelle wurde zu oft HEISS -- Auch das automatische Übertemperatur-Recycle wurde abgebrochen - Zelle Defekt?"

		elif s == 240:
			if self.bit(f,self.ERR):	msg = "Spanung bei Laden / Entladen / Erhalten / Pause weggebrochen oder Formatieren nicht erfolgreich - Zelle Defekt?"

		elif s == 245:
			if self.bit(f,self.ERR):	msg = "Spanung bei Formieren / Laden / Entladen / Erhalten zu hoch - defekter Akku? - Primärzelle?"

		elif s == 250:
			if self.bit(f,self.ERR):	msg = "Spanung beim Einlegen / Einschalten zu hoch - frisch geladener Akku? - Primärzelle? - Stromausfall beim Laden?"

		return msg
