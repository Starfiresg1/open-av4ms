#!/usr/bin/env python
#-*-coding: utf-8 -*-

import math
from Status import Status

Stat = Status()

class Messwert:
	#Konstanten
	BIT_LADEN    = 1
	BIT_ENTLADEN = 2
	BIT_TRICKLE  = 4
	BIT_ERROR    = 8
	BIT_PAUSE    = 16
	BIT_CYCLE    = 32
	BIT_MICRO    = 64
	BIT_HOT      = 128

	def __init__(self,schacht,K1,K2,K3,K4,K5,K6,K7,K8):
		# ermitteln der Messwerte für einen Schacht
		idx = 3 + 2*schacht

		self.status     = int(K7[3+schacht])       # Zellenstatus
		self.flags      = int(K8[3+schacht])       # Flags

		if (self.flags & Messwert.BIT_LADEN) == Messwert.BIT_LADEN:
			self.state = 'L'      # Laden
		elif (self.flags & Messwert.BIT_ENTLADEN) == Messwert.BIT_ENTLADEN:
			self.state = 'E'      # Entladen
		elif (self.flags & Messwert.BIT_ERROR) == Messwert.BIT_ERROR:
			self.state = 'F'      # Fehlerhafte Zelle
		elif (self.flags & Messwert.BIT_TRICKLE) == Messwert.BIT_TRICKLE:
			self.state = 'V'      # Voll
		else:
			self.state = '-'      # Keine Zelle

		self.U          = float(K1[idx]) / 10000   # Spanung stromlos
		self.Ustrom     = float(K1[idx+1]) / 10000 # Spannung mit Ladestrom
		self.I_laden    = int(K2[idx]) / 10      # Ladestrom (mA)
		self.I_entladen = int(K2[idx+1]) / 10    # Entladestrom (mA)
		self.C_laden    = int(K3[idx])             # Ladekapazität (mAh)
		self.C_entladen = int(K3[idx+1])           # Entladekapazität (mAh)
		self.t_laden    = int(K4[idx])             # Ladezeit (s)
		self.t_entladen = int(K4[idx+1])           # Entladezeit (s)
		self.E_laden    = int(K5[idx])             # Ladeenergie (mWh)
		self.E_entladen = int(K5[idx+1])           # Entladeenergie (mWh)
		if K6 == None:
			self.Uprec = 0
		else:
			self.Uprec = float(K6[3+schacht]) / 10000  # Präzisionsspannung

		# ohne Zelle sollten die Spannungen 0 sein
		if self.state == '-':
			self.U = self.Ustrom = self.Uprec = 0.0

	def logmsg(self):
		msg = Stat.LogMessage(self.status,self.flags)
		if self.status == 35 or self.status == 140 or self.status == 155 or self.status == 175:  # Entladen beendet, Kapazität anhängen
			msg += "\n#Kapazität: {:d} mAh".format(self.C_entladen)
		return msg

	def statmsg(self):
		return Stat.StatusMessage(self.status,self.flags)

class Analyse:
	def __init__(self,schacht=0):
		self.schacht = schacht
		self.mwcount = 0
		self.samples_laden = self.samples_entladen = int(0)
		self.U_laden_mittel = float(0)
		self.U_laden_strom_mittel = float(0)
		self.U_entladen_mittel = float(0)
		self.U_schluss = float(0) # Ladeschlussspannung
		self.U_leer = float(0)    # Leerlaufspannung bei Entladeende
		self.U_pause = float(0)  # Ladeschlussspannung nach 2 min. Erholungspause
		self.I_entladen = 0
		self.I_laden = 0
		self.I_laden_rel = float(0)
		self.I_entladen_rel = float(0)
		self.C_nenn = self.E_nenn = 0
		self.C_laden = self.C_entladen = 0
		self.E_laden = self.E_entladen = 0
		self.LadeEnde_dU = False
		self.pause = False
		self.cycles = 0
		self.state = None
		self.tags = None
		self.taglist = ('cycles',
				'charge_end_delta_u',
				'avg_discharge_voltage',
				'discharge_voltage_level',
				'avg_charge_voltage',
				'avg_charge_voltage_i',
				'rel_charge_voltage',
				'rel_discharge_voltage',
				'charge_current',
				'rel_charge_current',
				'discharge_current',
				'rel_discharge_current',
				'nom_capacity',
				'capacity',
				'rel_capacity',
				'charge_capacity',
				'rel_charge_capacity',
				'efficiency',
				'energy',
				'rel_energy',
				'charge_energy',
				'rel_charge_energy',
				'energy_efficiency',
				'avg_charge_ri',
				'r_index',
				'flat_voltage',
				'flat_ri',
				'urteil')

		self.mw = None

	def reset_laden(self):
		self.samples_laden = float(0)
		self.U_laden_mittel = 0
		self.U_laden_strom_mittel = 0
		self.LadeEnde_dU = False
		self.U_schluss = self.mw.U
		self.U_leer = float(0)

	def reset_entladen(self):
		self.samples_entladen = int(0)
		self.U_entladen_mittel = 0
		self.U_schluss = float(0)
		self.U_leer = float(0)
		self.U_pause = float(0)

	def reset(self):
		self.cycles = 0
		self.reset_laden()
		self.reset_entladen()

	def messwert(self,mw):  # Messwert verarbeiten
		self.mw = mw       # Messwerte zum Abruf merken
		self.mwcount += 1

		# Zustandswechsel prüfen
		if self.state == '-' and mw.state != '-':  # Zelle eingelegt
			self.reset()
		elif self.state != '-' and mw.state == '-':  # Zelle entnommen
			self.reset()
		elif self.state != 'E' and mw.state == 'E':  # wechsel nach Entladen
			self.reset_entladen()
			self.cycles += 1
		elif self.state == 'E' and mw.state == 'L': # wechsel von Entladen nach Laden
			self.reset_laden()
			#print 'Reset Laden ({:d}) mw={:d}'.format(self.schacht,self.mwcount)

		self.state = mw.state

		if mw.status == 105:
			self.LadeEnde_dU = True

		self.C_laden = mw.C_laden
		self.E_laden = mw.E_laden
		self.C_entladen = mw.C_entladen
		self.E_entladen = mw.E_entladen

		# Entladeschlussspannung prüfen/merken
		if (mw.flags & Messwert.BIT_PAUSE) == Messwert.BIT_PAUSE:  # Pausenflag
			#print "Pause ({:d} C_laden={:d})".format(self.schacht,self.C_laden)
			self.pause = True
			if self.C_laden == 0:		# Pausenspannung nach Entladen merken
				self.U_pause = mw.U
				#print "Pausenspannung ({:d}): {:f}".format(self.schacht,self.U_pause)
				if self.U_leer == 0 and mw.U > self.U_schluss: # 1. Pausenwert der > U_schluss ist
					self.U_leer = mw.U
					#print "U_leer gemerkt ({:d})".format(self.schacht)
		else:
			self.pause = False

		# Messwert für Analyse verarbeiten
		if not self.pause:
			if mw.state == 'L':
				self.I_laden = mw.I_laden
				if self.C_nenn != 0:
					self.I_laden_rel = float(self.I_laden) / float(self.C_nenn)
				if self.C_entladen > 0:
					self.U_entladen_mittel = float(self.E_entladen) / float(self.C_entladen)
				self.U_laden_mittel = (self.U_laden_mittel * float(self.samples_laden) + mw.U) / \
					float((self.samples_laden + 1))
				self.U_laden_strom_mittel = (self.U_laden_strom_mittel * float(self.samples_laden) + mw.Ustrom) / \
					float((self.samples_laden + 1))
				self.samples_laden += 1
			elif mw.state == 'E':
				self.I_entladen = mw.I_entladen
				if self.C_nenn != 0:
					self.I_entladen_rel = float(self.I_entladen) / float(self.C_nenn)
				if self.C_laden > 0:
					self.U_laden_strom_mittel = float(self.E_laden) / float(self.C_laden)
				self.U_entladen_mittel = (self.U_entladen_mittel * float(self.samples_entladen) + mw.U) / \
					float((self.samples_entladen + 1))
				self.samples_entladen += 1
			elif mw.state == 'V':
				if self.C_entladen > 0:
					self.U_entladen_mittel = float(self.E_entladen) / float(self.C_entladen)
				if self.C_laden > 0:
					self.U_laden_strom_mittel = float(self.E_laden) / float(self.C_laden)

	def tag_description(self,tag):
		if self.tags == None:
			self.tags = dict( cycles="Anzahl Zyklen",
							avg_discharge_voltage="mittlere Entladespannung (V)",
							discharge_voltage_level="Entlade-Spannungslage (%)",
							charge_end_delta_u = "letztes Laden mit -dU beendet (0/1)",
							avg_charge_voltage = "mittlere Ladespannung stromlos (V)",
							avg_charge_voltage_i = "mittlere Ladespannung unter Strom (V)",
							rel_charge_voltage = "relative Ladespannung (%)",
							rel_discharge_voltage = "relative Entladespannung (%)",
							charge_current = "Ladestrom (mA)",
							discharge_current = "Entladestrom (mA)",
							rel_charge_current = "relativer Ladestrom",
							rel_discharge_current = "relativer Entladestrom",
							capacity = "Entladekapazität (mAh)",
							nom_capacity = "Nennkapazität (mAh)",
							rel_capacity = "relative Kapazität (%)",
							energy = "Entladeenergie (mWh)",
							rel_energy = "relative Energie (%)",
							charge_capacity = "Ladekapazität (mAh)",
							efficiency = "Effizienz (%)",
							charge_energy = "Ladeenergie (mWh)",
							rel_charge_capacity = "relative Ladekapazität (%)",
							rel_charge_energy = "relative Ladeenergie (%)",
							energy_efficiency = "Energieeffizienz (%)",
							avg_charge_ri = "mittlerer Ri Laden (mOhm)",
							r_index = "Innenwiderstandsindex Laden (%)",
							flat_voltage = "Spannung leer (V)",
							flat_ri = "Innenwiderstand leer (mOhm)",
							urteil = "Beurteilung")

		if tag in self.tags:
			return self.tags[tag]
		else:
			return "Unbekanntes Tag "+tag

	def set_c_nenn(self,c):
		self.C_nenn = c
		self.E_nenn = int(float(c) * 1.22 + 0.5)

	def get_c_nenn(self):
		return self.C_nenn

	def avg_discharge_voltage(self):
		return self.U_entladen_mittel

	def avg_charge_voltage(self):
		return self.U_laden_mittel

	def discharge_voltage_level(self):
		if self.U_entladen_mittel == 0: return 0.0
		return (self.U_entladen_mittel-1.0)/0.22*100.0

	def rel_charge_voltage(self):
		if self.U_laden_mittel == 0: return 0
		return self.U_laden_strom_mittel/self.U_laden_mittel*100.0

	def rel_discharge_voltage(self):
		if self.U_laden_mittel == 0: return 0
		return self.U_entladen_mittel/self.U_laden_mittel*100.0

	def efficiency(self):
		if self.C_laden == 0: return 0
		return float(self.C_entladen)/float(self.C_laden)*100.0

	def energy_efficiency(self):
		if self.E_laden == 0: return 0
		return float(self.E_entladen)/float(self.E_laden)*100.0

	def rel_capacity(self):
		if self.C_nenn == 0: return 0
		return float(self.C_entladen) / float(self.C_nenn) * 100.0

	def rel_charge_capacity(self):
		if self.C_nenn == 0: return 0
		return float(self.C_laden) / float(self.C_nenn) * 100.0

	def rel_energy(self):
		if self.E_nenn == 0: return 0
		return float(self.E_entladen) / float(self.E_nenn) * 100.0

	def rel_charge_energy(self):
		if self.E_nenn == 0: return 0
		return float(self.E_laden) / float(self.E_nenn) * 100.0

	def ri_laden(self):
		if self.I_laden == 0:
			return 0

		ri = ((self.U_laden_strom_mittel - self.U_laden_mittel) /
		               float(self.I_laden) * 1000.0)
		return int(round(ri * 1000.0))

	def r_index(self):
		if self.U_laden_mittel == 0:
			return float(0)

		return (1.0 - (self.U_laden_strom_mittel - self.U_laden_mittel) /
		               self.U_laden_mittel) * 1.08 * 100.0

	def flat_ri(self):
		if self.I_entladen == 0:
			return 0
		ri = (self.U_leer - self.U_schluss) * 1000 / float(self.I_entladen)
		return int(round(ri * 1000))

	def urteil(self):
		if self.C_nenn == 0:
			return '--'

		rindex = self.r_index()
		re = int(round(rindex * float(self.C_entladen) / float(self.C_nenn) / 2.0) * 2.0)
		#soll = math.sqrt(1.22) * float(self.C_nenn)
		#ist  = math.sqrt(self.U_entladen_mittel) * float(self.C_entladen)
		#re = int(round(ist / soll * 100.0 / 2.0) * 2.0)
		#re = int(round(self.rel_energy() / 2.0) * 2.0)
		if re == 0:
			return '--'
		#elif re >= 101:
		elif re >= 100:
			return 'sehr gut'
		elif re >= 98:
			return 'gut'
		elif re >= 95:
			return 'brauchbar'
		elif re >= 92:
			return 'schwach'
		else:
			return 'sehr schwach'

	def ergebnis(self):
		if self.state != 'V':
			return { 'error' : "Zustand ist nicht VOLL, Bewertung nicht möglich" }

		return dict( cycles = self.cycles,
					charge_end_delta_u = self.LadeEnde_dU,
					avg_discharge_voltage = self.U_entladen_mittel,
					discharge_voltage_level = self.discharge_voltage_level(),
					avg_charge_voltage = self.U_laden_mittel,
					avg_charge_voltage_i = self.U_laden_strom_mittel,
					rel_charge_voltage = self.rel_charge_voltage(),
					rel_discharge_voltage = self.rel_discharge_voltage(),
					charge_current = self.I_laden,
					discharge_current = self.I_entladen,
					rel_charge_current = self.I_laden_rel,
					rel_discharge_current = self.I_entladen_rel,
					nom_capacity = self.C_nenn,
					capacity = self.C_entladen,
					charge_capacity = self.C_laden,
					energy = self.E_entladen,
					charge_energy = self.E_laden,
					rel_capacity = self.rel_capacity(),
					rel_energy = self.rel_energy(),
					rel_charge_capacity = self.rel_charge_capacity(),
					rel_charge_energy = self.rel_charge_energy(),
					efficiency = self.efficiency(),
					energy_efficiency = self.energy_efficiency(),
					avg_charge_ri = self.ri_laden(),
					r_index = self.r_index(),
					flat_voltage = self.U_pause,
					flat_ri = self.flat_ri(),
					urteil = self.urteil())

	def ergebnis_xml(self):
		erg = self.ergebnis()
		xml = "<results>\n"
		for key, value in erg.iteritems():
			xml += "<{:s}>{:s}</{:s}>\n".format(key,str(value),key)
		xml += "</results>\n"
		return xml

	def ergebnis_text(self):
		if self.state != 'V':
			return "Zustand ist nicht VOLL, Bewertung nicht möglich"

		erg  = "Ergebnis:\n========\nAnzahl Zyklen: {:d}\n".format(self.cycles)
		if self.LadeEnde_dU:
			erg += "letztes Laden mit -dU beendet\n"
		erg += "mittlere Entladespannung: {:.2f} V\n".format(self.U_entladen_mittel)
		erg += "Entlade-Spannungslage: {:.0f}%\n".format(self.discharge_voltage_level())
		erg += "mittl. Ladespg. stromlos: {:.2f} V\n".format(self.U_laden_mittel)
		erg += "mittl. Ladespg. unter Strom: {:.2f} V\n".format(self.U_laden_strom_mittel)
		erg += "relative Ladespannung: {:.0f}%\n".format(self.rel_charge_voltage())
		erg += "relative Entladespg.: {:.0f}%\n".format(self.rel_discharge_voltage())
		erg += "Ladestrom: {:d} mA\n".format(self.I_laden)
		erg += "Entladestrom: {:d} mA\n".format(self.I_entladen)
		if self.I_laden_rel != 0.0:
			erg += "Ladestrom rel.: C/{:.1f}\n".format(1.0 / self.I_laden_rel)
		if self.I_entladen_rel != 0.0:
			erg += "Entladestrom rel.: C/{:.1f}\n".format(1.0 / self.I_entladen_rel)
		erg += "Entladekapazität: {:d} mAh\n".format(self.C_entladen)
		if self.C_nenn > 0:
			erg += "relative Kapazität: {:.0f}%\n".format(self.rel_capacity())
		erg += "Ladekapazität: {:d} mAh\n".format(self.C_laden)
		if self.C_nenn > 0:
			erg += "relative Ladekapazität: {:.0f}%\n".format(self.rel_charge_capacity())
		if self.C_laden > 0:
			erg += "Effizienz: {:.0f}%\n".format(self.efficiency())
		erg += "Entladeenergie: {:d} mWh\n".format(self.E_entladen)
		if self.E_nenn > 0:
			erg += "relative Energie: {:.0f}%\n".format(self.rel_energy())
		erg += "Ladeenergie: {:d} mWh\n".format(self.E_laden)
		if self.E_nenn > 0:
			erg += "relative Ladeenergie: {:.0f}%\n".format(self.rel_charge_energy())
		if self.E_laden > 0:
			erg += "Energieeffizienz: {:.0f}%\n".format(self.energy_efficiency())
		erg += "Ri Laden: {:d} mOhm\n".format(self.ri_laden())
		erg += "Innenwiderstandsindex Laden: {:.1f}%\n".format(self.r_index())
		erg += "Spannung leer: {:.2f} V\n".format(self.U_pause)
		erg += "Innenwiderstand leer: {:d} mOhm\n".format(self.flat_ri())
		if self.E_nenn > 0:
			erg += "Beurteilung: {:s}\n".format(self.urteil())
		return erg

	def aktuelle_werte(self):
		if self.mw == None:    #noch kein Messwert vorhanden
			return None

		werte = {}
		werte['cycle'] = self.cycles
		werte['state'] = self.mw.state
		werte['Laden'] = self.mw.state == 'L'
		werte['Entladen'] = self.mw.state == 'E'
		werte['Voll'] = self.mw.state == 'V'
		werte['Fehlerhaft'] = self.mw.state == 'F'
		werte['NoCell'] = self.mw.state == '-'
		werte['U'] = self.mw.U
		werte['Ustrom'] = self.mw.Ustrom
		werte['U_avg_chg'] = self.U_laden_mittel
		werte['U_avg_dischg'] = self.U_entladen_mittel
		werte['Ustrom_avg_chg'] = self.U_laden_strom_mittel
		werte['I_chg'] = self.mw.I_laden
		werte['I_dischg'] = self.mw.I_entladen
		werte['C_chg'] = self.mw.C_laden
		werte['C_dischg'] = self.mw.C_entladen
		werte['t_chg'] = self.mw.t_laden
		werte['t_dischg'] = self.mw.t_entladen
		werte['E_chg'] = self.E_laden
		werte['E_dischg'] = self.E_entladen

		if self.C_nenn > 0:
			werte['C_nenn'] = self.C_nenn
			werte['C_chg_rel'] = int(float(self.mw.C_laden) / float(self.C_nenn) * 100 + 0.5)
			werte['C_dischg_rel'] = int(float(self.mw.C_entladen) / float(self.C_nenn) * 100 + 0.5)
		if self.E_nenn > 0:
			werte['E_nenn'] = self.E_nenn
			werte['E_chg_rel'] = int(float(self.E_laden) / float(self.E_nenn) * 100 + 0.5)
			werte['E_dischg_rel'] = int(float(self.E_entladen) / float(self.E_nenn) * 100 + 0.5)

		if self.mw.C_entladen > 0:
			werte['Charge_Rate'] = int(float(self.mw.C_laden) / float(self.mw.C_entladen) * 100 + 0.5)
		if self.mw.C_laden > 0:
			werte['Discharge_Rate'] = int(float(self.mw.C_entladen) / float(self.mw.C_laden) * 100 + 0.5)
		if self.E_entladen > 0:
			werte['E_Charge_Rate'] = int(float(self.E_laden) / float(self.E_entladen) * 100 + 0.5)
		if self.E_laden > 0:
			werte['E_Discharge_Rate'] = int(float(self.E_entladen) / float(self.E_laden) * 100 + 0.5)

		werte['StatusMsg'] = self.mw.statmsg()
		werte['LogMsg'] = self.mw.logmsg()
		return werte
