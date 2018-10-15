// JavaScript Document
var version = "1.4";

var l1 = null;
var l2 = null;
var l3 = null;
var l4 = null;
var timer = null;
var counter = 0;
var firstload = true;

function setnenn(schacht) {
	var id = "cnenn" + schacht;
	var val = document.getElementById(id).value;
	var params = id + "=" + val;
	var req = new XMLHttpRequest();
	firstload = true;
	req.open("POST", "/control");
	req.onreadystatechange = fillStatus;
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.send(params);
}

function getState() {
	var req = new XMLHttpRequest();
	req.open("GET", "/control");
	req.onreadystatechange = fillStatus;
	req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	req.send(null);
}

function getLogbuch() {
	var req = new XMLHttpRequest();
	req.open("GET", "/logbuch");
	req.onreadystatechange = fillLogbuch;
	req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	req.send(null);
}

function checkVersion() {
		update_alert_field = document.getElementById("update_alert");
	if (av4version > version){
		update_alert_field.innerHTML = "eine neue Version ist verfügbar(" + version + " -> " + "<a href='http://av4ms.fahrner.name'>" + av4version + "</a>)";
		update_alert_field.style.display = "block";
	}else{
		update_alert_field.style.display = "none";		
	}
}

function fillMesswerte() {
	if (this.readyState == this.DONE) {
		if (this.status == 200 && this.responseXML != null) {
			var time = new Date();

			//Felder definieren
			l1_field = document.getElementById("l1");
			l2_field = document.getElementById("l2");
			l3_field = document.getElementById("l3");
			l4_field = document.getElementById("l4");

			s1txt_field = document.getElementById("s1txt");
			s2txt_field = document.getElementById("s2txt");
			s3txt_field = document.getElementById("s3txt");
			s4txt_field = document.getElementById("s4txt");

			cy1_field = document.getElementById("cy1");
			cy2_field = document.getElementById("cy2");
			cy3_field = document.getElementById("cy3");
			cy4_field = document.getElementById("cy4");

			u1e_field = document.getElementById("u1e");
			u1l_field = document.getElementById("u1l");
			u2e_field = document.getElementById("u2e");
			u2l_field = document.getElementById("u2l");
			u3e_field = document.getElementById("u3e");
			u3l_field = document.getElementById("u3l");
			u4e_field = document.getElementById("u4e");
			u4l_field = document.getElementById("u4l");

			u1eavg_field = document.getElementById("u1eavg");
			u1lavg_field = document.getElementById("u1lavg");
			u2eavg_field = document.getElementById("u2eavg");
			u2lavg_field = document.getElementById("u2lavg");
			u3eavg_field = document.getElementById("u3eavg");
			u3lavg_field = document.getElementById("u3lavg");
			u4eavg_field = document.getElementById("u4eavg");
			u4lavg_field = document.getElementById("u4lavg");

			i1e_field = document.getElementById("i1e");
			i1l_field = document.getElementById("i1l");
			i2e_field = document.getElementById("i2e");
			i2l_field = document.getElementById("i2l");
			i3e_field = document.getElementById("i3e");
			i3l_field = document.getElementById("i3l");
			i4e_field = document.getElementById("i4e");
			i4l_field = document.getElementById("i4l");

			c1e_field = document.getElementById("c1e");
			c1l_field = document.getElementById("c1l");
			c2e_field = document.getElementById("c2e");
			c2l_field = document.getElementById("c2l");
			c3e_field = document.getElementById("c3e");
			c3l_field = document.getElementById("c3l");
			c4e_field = document.getElementById("c4e");
			c4l_field = document.getElementById("c4l");

			c1erate_field = document.getElementById("c1erate");
			c1lrate_field = document.getElementById("c1lrate");
			c2erate_field = document.getElementById("c2erate");
			c2lrate_field = document.getElementById("c2lrate");
			c3erate_field = document.getElementById("c3erate");
			c3lrate_field = document.getElementById("c3lrate");
			c4erate_field = document.getElementById("c4erate");
			c4lrate_field = document.getElementById("c4lrate");

			t1e_field = document.getElementById("t1e");
			t1l_field = document.getElementById("t1l");
			t2e_field = document.getElementById("t2e");
			t2l_field = document.getElementById("t2l");
			t3e_field = document.getElementById("t3e");
			t3l_field = document.getElementById("t3l");
			t4e_field = document.getElementById("t4e");
			t4l_field = document.getElementById("t4l");

			e1e_field = document.getElementById("e1e");
			e1l_field = document.getElementById("e1l");
			e2e_field = document.getElementById("e2e");
			e2l_field = document.getElementById("e2l");
			e3e_field = document.getElementById("e3e");
			e3l_field = document.getElementById("e3l");
			e4e_field = document.getElementById("e4e");
			e4l_field = document.getElementById("e4l");

			e1erate_field = document.getElementById("e1erate");
			e1lrate_field = document.getElementById("e1lrate");
			e2erate_field = document.getElementById("e2erate");
			e2lrate_field = document.getElementById("e2lrate");
			e3erate_field = document.getElementById("e3erate");
			e3lrate_field = document.getElementById("e3lrate");
			e4erate_field = document.getElementById("e4erate");
			e4lrate_field = document.getElementById("e4lrate");

			clock_field = document.getElementById("clock");

			//Antwort vom Server
			xml = this.responseXML;

			l1_resp = xml.getElementsByTagName("l1")[0];
			l2_resp = xml.getElementsByTagName("l2")[0];
			l3_resp = xml.getElementsByTagName("l3")[0];
			l4_resp = xml.getElementsByTagName("l4")[0];

			s1_resp = xml.getElementsByTagName("s1")[0];
			s2_resp = xml.getElementsByTagName("s2")[0];
			s3_resp = xml.getElementsByTagName("s3")[0];
			s4_resp = xml.getElementsByTagName("s4")[0];

			s1txt_resp = xml.getElementsByTagName("s1txt")[0];
			s2txt_resp = xml.getElementsByTagName("s2txt")[0];
			s3txt_resp = xml.getElementsByTagName("s3txt")[0];
			s4txt_resp = xml.getElementsByTagName("s4txt")[0];

			cy1_resp = xml.getElementsByTagName("cy1")[0];
			cy2_resp = xml.getElementsByTagName("cy2")[0];
			cy3_resp = xml.getElementsByTagName("cy3")[0];
			cy4_resp = xml.getElementsByTagName("cy4")[0];

			u1e_resp = xml.getElementsByTagName("u1e")[0];
			u1l_resp = xml.getElementsByTagName("u1l")[0];
			u2e_resp = xml.getElementsByTagName("u2e")[0];
			u2l_resp = xml.getElementsByTagName("u2l")[0];
			u3e_resp = xml.getElementsByTagName("u3e")[0];
			u3l_resp = xml.getElementsByTagName("u3l")[0];
			u4e_resp = xml.getElementsByTagName("u4e")[0];
			u4l_resp = xml.getElementsByTagName("u4l")[0];

			u1eavg_resp = xml.getElementsByTagName("u1eavg")[0];
			u1lavg_resp = xml.getElementsByTagName("u1lavg")[0];
			u2eavg_resp = xml.getElementsByTagName("u2eavg")[0];
			u2lavg_resp = xml.getElementsByTagName("u2lavg")[0];
			u3eavg_resp = xml.getElementsByTagName("u3eavg")[0];
			u3lavg_resp = xml.getElementsByTagName("u3lavg")[0];
			u4eavg_resp = xml.getElementsByTagName("u4eavg")[0];
			u4lavg_resp = xml.getElementsByTagName("u4lavg")[0];

			i1e_resp = xml.getElementsByTagName("i1e")[0];
			i1l_resp = xml.getElementsByTagName("i1l")[0];
			i2e_resp = xml.getElementsByTagName("i2e")[0];
			i2l_resp = xml.getElementsByTagName("i2l")[0];
			i3e_resp = xml.getElementsByTagName("i3e")[0];
			i3l_resp = xml.getElementsByTagName("i3l")[0];
			i4e_resp = xml.getElementsByTagName("i4e")[0];
			i4l_resp = xml.getElementsByTagName("i4l")[0];

			c1e_resp = xml.getElementsByTagName("c1e")[0];
			c1l_resp = xml.getElementsByTagName("c1l")[0];
			c2e_resp = xml.getElementsByTagName("c2e")[0];
			c2l_resp = xml.getElementsByTagName("c2l")[0];
			c3e_resp = xml.getElementsByTagName("c3e")[0];
			c3l_resp = xml.getElementsByTagName("c3l")[0];
			c4e_resp = xml.getElementsByTagName("c4e")[0];
			c4l_resp = xml.getElementsByTagName("c4l")[0];

			c1erate_resp = xml.getElementsByTagName("c1erate")[0];
			c1lrate_resp = xml.getElementsByTagName("c1lrate")[0];
			c2erate_resp = xml.getElementsByTagName("c2erate")[0];
			c2lrate_resp = xml.getElementsByTagName("c2lrate")[0];
			c3erate_resp = xml.getElementsByTagName("c3erate")[0];
			c3lrate_resp = xml.getElementsByTagName("c3lrate")[0];
			c4erate_resp = xml.getElementsByTagName("c4erate")[0];
			c4lrate_resp = xml.getElementsByTagName("c4lrate")[0];

			t1e_resp = xml.getElementsByTagName("t1e")[0];
			t1l_resp = xml.getElementsByTagName("t1l")[0];
			t2e_resp = xml.getElementsByTagName("t2e")[0];
			t2l_resp = xml.getElementsByTagName("t2l")[0];
			t3e_resp = xml.getElementsByTagName("t3e")[0];
			t3l_resp = xml.getElementsByTagName("t3l")[0];
			t4e_resp = xml.getElementsByTagName("t4e")[0];
			t4l_resp = xml.getElementsByTagName("t4l")[0];

			e1e_resp = xml.getElementsByTagName("e1e")[0];
			e1l_resp = xml.getElementsByTagName("e1l")[0];
			e2e_resp = xml.getElementsByTagName("e2e")[0];
			e2l_resp = xml.getElementsByTagName("e2l")[0];
			e3e_resp = xml.getElementsByTagName("e3e")[0];
			e3l_resp = xml.getElementsByTagName("e3l")[0];
			e4e_resp = xml.getElementsByTagName("e4e")[0];
			e4l_resp = xml.getElementsByTagName("e4l")[0];

			e1erate_resp = xml.getElementsByTagName("e1erate")[0];
			e1lrate_resp = xml.getElementsByTagName("e1lrate")[0];
			e2erate_resp = xml.getElementsByTagName("e2erate")[0];
			e2lrate_resp = xml.getElementsByTagName("e2lrate")[0];
			e3erate_resp = xml.getElementsByTagName("e3erate")[0];
			e3lrate_resp = xml.getElementsByTagName("e3lrate")[0];
			e4erate_resp = xml.getElementsByTagName("e4erate")[0];
			e4lrate_resp = xml.getElementsByTagName("e4lrate")[0];

			// bei leerem Schacht Logbuch löschen
			if (s1_resp.firstChild.nodeValue == '-')
				l1_field.value = ''
			if (s2_resp.firstChild.nodeValue == '-')
				l2_field.value = ''
			if (s3_resp.firstChild.nodeValue == '-')
				l3_field.value = ''
			if (s4_resp.firstChild.nodeValue == '-')
				l4_field.value = ''
				
			// Spaltenüberschrift unterstrichen je nach Zustand
			hd1e_div = document.getElementById("hd1ediv");
			hd1l_div = document.getElementById("hd1ldiv");
			hd2e_div = document.getElementById("hd2ediv");
			hd2l_div = document.getElementById("hd2ldiv");
			hd3e_div = document.getElementById("hd3ediv");
			hd3l_div = document.getElementById("hd3ldiv");
			hd4e_div = document.getElementById("hd4ediv");
			hd4l_div = document.getElementById("hd4ldiv");
			if (s1_resp.firstChild.nodeValue == 'E')
				hd1e_div.style.textDecoration="underline";
			else
				hd1e_div.style.textDecoration="none";
			if (s1_resp.firstChild.nodeValue == 'L')
				hd1l_div.style.textDecoration="underline";
			else
				hd1l_div.style.textDecoration="none";

			if (s2_resp.firstChild.nodeValue == 'E')
				hd2e_div.style.textDecoration="underline";
			else
				hd2e_div.style.textDecoration="none";
			if (s2_resp.firstChild.nodeValue == 'L')
				hd2l_div.style.textDecoration="underline";
			else
				hd2l_div.style.textDecoration="none";

			if (s3_resp.firstChild.nodeValue == 'E')
				hd3e_div.style.textDecoration="underline";
			else
				hd3e_div.style.textDecoration="none";
			if (s3_resp.firstChild.nodeValue == 'L')
				hd3l_div.style.textDecoration="underline";
			else
				hd3l_div.style.textDecoration="none";

			if (s4_resp.firstChild.nodeValue == 'E')
				hd4e_div.style.textDecoration="underline";
			else
				hd4e_div.style.textDecoration="none";
			if (s4_resp.firstChild.nodeValue == 'L')
				hd4l_div.style.textDecoration="underline";
			else
				hd4l_div.style.textDecoration="none";

			//Werte eintragen (Logbuch kann auch leer sein)
			var uhrzeit = time.toLocaleTimeString().substr(0,5)
			if (l1_resp.firstChild != null) {
				if (l1 == null) l1 = l1_resp.firstChild.nodeValue;
				if (l1 != l1_resp.firstChild.nodeValue) {
					l1_field.value = l1_field.value + "[" + uhrzeit + "] " + l1_resp.firstChild.nodeValue + "\n";
					l1 = l1_resp.firstChild.nodeValue;
				}
			}
			if (l2_resp.firstChild != null) {
				if (l2 == null) l2 = l2_resp.firstChild.nodeValue;
				if (l2 != l2_resp.firstChild.nodeValue) {
					l2_field.value = l2_field.value + "[" + uhrzeit + "] " + l2_resp.firstChild.nodeValue + "\n";
					l2 = l2_resp.firstChild.nodeValue;
				}
			}
			if (l3_resp.firstChild != null) {
				if (l3 == null) l3 = l3_resp.firstChild.nodeValue;
				if (l3 != l3_resp.firstChild.nodeValue) {
					l3_field.value = l3_field.value + "[" + uhrzeit + "] " + l3_resp.firstChild.nodeValue + "\n";
					l3 = l3_resp.firstChild.nodeValue;
				}
			}
			if (l4_resp.firstChild != null) {
				if (l4 == null) l4 = l4_resp.firstChild.nodeValue;
				if (l4 != l4_resp.firstChild.nodeValue) {
					l4_field.value = l4_field.value + "[" + uhrzeit + "] " + l4_resp.firstChild.nodeValue + "\n";
					l4 = l4_resp.firstChild.nodeValue;
				}
			}

			s1txt_field.value = s1txt_resp.firstChild.nodeValue;
			s2txt_field.value = s2txt_resp.firstChild.nodeValue;
			s3txt_field.value = s3txt_resp.firstChild.nodeValue;
			s4txt_field.value = s4txt_resp.firstChild.nodeValue;

			//Ein bzw Ausblenden der Zyklus Anzeige
			cy1_div = document.getElementById("cy1div");
			cy2_div = document.getElementById("cy2div");
			cy3_div = document.getElementById("cy3div");
			cy4_div = document.getElementById("cy4div");
			if (cy1_resp.firstChild.nodeValue == 0)
				cy1_div.style.display="none";
			else {
				cy1_field.innerHTML = cy1_resp.firstChild.nodeValue;
				cy1_div.style.display="inline";				
			}
			if (cy2_resp.firstChild.nodeValue == 0)
				cy2_div.style.display="none";
			else {
				cy2_field.innerHTML = cy2_resp.firstChild.nodeValue;
				cy2_div.style.display="inline";				
			}
			if (cy3_resp.firstChild.nodeValue == 0)
				cy3_div.style.display="none";
			else {
				cy3_field.innerHTML = cy3_resp.firstChild.nodeValue;
				cy3_div.style.display="inline";				
			}
			if (cy4_resp.firstChild.nodeValue == 0)
				cy4_div.style.display="none";
			else {
				cy4_field.innerHTML = cy4_resp.firstChild.nodeValue;
				cy4_div.style.display="inline";				
			}

			u1e_field.value = u1e_resp.firstChild.nodeValue;
			u1l_field.value = u1l_resp.firstChild.nodeValue;
			u2e_field.value = u2e_resp.firstChild.nodeValue;
			u2l_field.value = u2l_resp.firstChild.nodeValue;
			u3e_field.value = u3e_resp.firstChild.nodeValue;
			u3l_field.value = u3l_resp.firstChild.nodeValue;
			u4e_field.value = u4e_resp.firstChild.nodeValue;
			u4l_field.value = u4l_resp.firstChild.nodeValue;

			u1eavg_field.value = u1eavg_resp.firstChild.nodeValue;
			u1lavg_field.value = u1lavg_resp.firstChild.nodeValue;
			u2eavg_field.value = u2eavg_resp.firstChild.nodeValue;
			u2lavg_field.value = u2lavg_resp.firstChild.nodeValue;
			u3eavg_field.value = u3eavg_resp.firstChild.nodeValue;
			u3lavg_field.value = u3lavg_resp.firstChild.nodeValue;
			u4eavg_field.value = u4eavg_resp.firstChild.nodeValue;
			u4lavg_field.value = u4lavg_resp.firstChild.nodeValue;

			i1e_field.value = i1e_resp.firstChild.nodeValue;
			i1l_field.value = i1l_resp.firstChild.nodeValue;
			i2e_field.value = i2e_resp.firstChild.nodeValue;
			i2l_field.value = i2l_resp.firstChild.nodeValue;
			i3e_field.value = i3e_resp.firstChild.nodeValue;
			i3l_field.value = i3l_resp.firstChild.nodeValue;
			i4e_field.value = i4e_resp.firstChild.nodeValue;
			i4l_field.value = i4l_resp.firstChild.nodeValue;

			c1e_field.value = c1e_resp.firstChild.nodeValue;
			c1l_field.value = c1l_resp.firstChild.nodeValue;
			c2e_field.value = c2e_resp.firstChild.nodeValue;
			c2l_field.value = c2l_resp.firstChild.nodeValue;
			c3e_field.value = c3e_resp.firstChild.nodeValue;
			c3l_field.value = c3l_resp.firstChild.nodeValue;
			c4e_field.value = c4e_resp.firstChild.nodeValue;
			c4l_field.value = c4l_resp.firstChild.nodeValue;

			c1erate_field.value = c1erate_resp.firstChild.nodeValue;
			c1lrate_field.value = c1lrate_resp.firstChild.nodeValue;
			c2erate_field.value = c2erate_resp.firstChild.nodeValue;
			c2lrate_field.value = c2lrate_resp.firstChild.nodeValue;
			c3erate_field.value = c3erate_resp.firstChild.nodeValue;
			c3lrate_field.value = c3lrate_resp.firstChild.nodeValue;
			c4erate_field.value = c4erate_resp.firstChild.nodeValue;
			c4lrate_field.value = c4lrate_resp.firstChild.nodeValue;

			t1e_field.value = t1e_resp.firstChild.nodeValue;
			t1l_field.value = t1l_resp.firstChild.nodeValue;
			t2e_field.value = t2e_resp.firstChild.nodeValue;
			t2l_field.value = t2l_resp.firstChild.nodeValue;
			t3e_field.value = t3e_resp.firstChild.nodeValue;
			t3l_field.value = t3l_resp.firstChild.nodeValue;
			t4e_field.value = t4e_resp.firstChild.nodeValue;
			t4l_field.value = t4l_resp.firstChild.nodeValue;

			e1e_field.value = e1e_resp.firstChild.nodeValue;
			e1l_field.value = e1l_resp.firstChild.nodeValue;
			e2e_field.value = e2e_resp.firstChild.nodeValue;
			e2l_field.value = e2l_resp.firstChild.nodeValue;
			e3e_field.value = e3e_resp.firstChild.nodeValue;
			e3l_field.value = e3l_resp.firstChild.nodeValue;
			e4e_field.value = e4e_resp.firstChild.nodeValue;
			e4l_field.value = e4l_resp.firstChild.nodeValue;

			e1erate_field.value = e1erate_resp.firstChild.nodeValue;
			e1lrate_field.value = e1lrate_resp.firstChild.nodeValue;
			e2erate_field.value = e2erate_resp.firstChild.nodeValue;
			e2lrate_field.value = e2lrate_resp.firstChild.nodeValue;
			e3erate_field.value = e3erate_resp.firstChild.nodeValue;
			e3lrate_field.value = e3lrate_resp.firstChild.nodeValue;
			e4erate_field.value = e4erate_resp.firstChild.nodeValue;
			e4lrate_field.value = e4lrate_resp.firstChild.nodeValue;

			clock_field.value = time.toLocaleTimeString();

			counter++;
			if (counter > 60) {
				getState();
				counter = 0;
			}
		}
	}
}

function fillStatus() {
	if (this.readyState == this.DONE) {
		if (this.status == 200 && this.responseXML != null) {
			var xml = this.responseXML;

			ran = document.getElementById("ran");
			raus = document.getElementById("raus");
			autostopan = document.getElementById("autostopan");
			autostopaus = document.getElementById("autostopaus");
			logname_field = document.getElementById("logname");
			c1nenn_field = document.getElementById("cnenn1");
			c2nenn_field = document.getElementById("cnenn2");
			c3nenn_field = document.getElementById("cnenn3");
			c4nenn_field = document.getElementById("cnenn4");

			logstate_resp = xml.getElementsByTagName("logging")[0];
			autostopstate_resp = xml.getElementsByTagName("autostop")[0];
			logname_resp = xml.getElementsByTagName("logfile")[0];
			c1nenn_resp = xml.getElementsByTagName("c1nenn")[0];
			c2nenn_resp = xml.getElementsByTagName("c2nenn")[0];
			c3nenn_resp = xml.getElementsByTagName("c3nenn")[0];
			c4nenn_resp = xml.getElementsByTagName("c4nenn")[0];

			if(logstate_resp.firstChild.nodeValue == "True")
				ran.checked = "checked";
			else
				raus.checked = "checked";
			if(autostopstate_resp.firstChild.nodeValue == "True")
				autostopan.checked = "checked";
			else
				autostopaus.checked = "checked";
			if (firstload) {
				c1nenn_field.value = c1nenn_resp.firstChild.nodeValue;
				c2nenn_field.value = c2nenn_resp.firstChild.nodeValue;
				c3nenn_field.value = c3nenn_resp.firstChild.nodeValue;
				c4nenn_field.value = c4nenn_resp.firstChild.nodeValue;
				logname_field.value = logname_resp.firstChild.nodeValue;
				firstload = false;
			}
		}
	}
}

function fillLogbuch() {
	if (this.readyState == this.DONE) {
		if (this.status == 200 && this.responseXML != null) {
			var xml = this.responseXML;
			l1_field = document.getElementById("l1");
			l2_field = document.getElementById("l2");
			l3_field = document.getElementById("l3");
			l4_field = document.getElementById("l4");

			l1_resp = xml.getElementsByTagName("logbuch1")[0];
			l2_resp = xml.getElementsByTagName("logbuch2")[0];
			l3_resp = xml.getElementsByTagName("logbuch3")[0];
			l4_resp = xml.getElementsByTagName("logbuch4")[0];

			if (l1_resp.firstChild == null)
				l1_field.value = ' '
			else
				l1_field.value = l1_resp.firstChild.nodeValue;

			if (l2_resp.firstChild == null)
				l2_field.value = ' '
			else
				l2_field.value = l2_resp.firstChild.nodeValue;

			if (l3_resp.firstChild == null)
				l3_field.value = ' '
			else
				l3_field.value = l3_resp.firstChild.nodeValue;

			if (l4_resp.firstChild == null)
				l4_field.value = ' '
			else
				l4_field.value = l4_resp.firstChild.nodeValue;
		}
	}
}

function getMesswerte() {
	var req = new XMLHttpRequest();
	req.open("GET", "/messwerte");
	req.onreadystatechange = fillMesswerte;
	req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	req.send(null);
}

function enablelog(){
	logname_field = document.getElementById("logname");
	logname = logname_field.value;
	var params = "logging=start&logfile=" + logname;
	var req = new XMLHttpRequest();
	req.open("POST", "/control");
	req.onreadystatechange = fillStatus;
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.send(params);
	alert("Logging aktiviert");
}

function disablelog() {
	var params = "logging=stop";
	var req = new XMLHttpRequest();
	req.open("POST", "/control");
	req.onreadystatechange = fillStatus;
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.send(params);
	alert("Logging deaktiviert");
}

function enableautostop() {
	var params = "autostop=True";
	var req = new XMLHttpRequest();
	req.open("POST", "/control");
	req.onreadystatechange = fillStatus;
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.send(params);
	alert("Autostop aktiviert");
}

function disableautostop() {
	var params = "autostop=False";
	var req = new XMLHttpRequest();
	req.open("POST", "/control");
	req.onreadystatechange = fillStatus;
	req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	req.send(params);
	alert("Autostop deaktiviert");
}

function do_shutdown() {
	if (this.readyState == this.DONE) {
		if (this.status == 200 && this.responseXML != null) {
			var xml = this.responseXML;
			logstate_resp = xml.getElementsByTagName("logging")[0];
			fillStatus();
			if (logstate_resp.firstChild.nodeValue == "True"){
				alert("Bitte zuerst Logging ausschalten");
				return;
			}
			else {
				if (confirm("Wollen sie den AV4-Server wirklich herunterfahren?")){
					var params = "shutdown=True";
					var req = new XMLHttpRequest();
					req.open("POST", "/control");
					req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
					req.send(params);
					window.clearInterval(timer);
				}
				else
					return;
			}
		}
	}
}

function shutdown() {
	var req = new XMLHttpRequest();
	req.open("GET", "/control");
	req.onreadystatechange = do_shutdown;
	req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	req.send(null);
}

function run() {
	window.document.title = "AV4ms Zellen-Inspektor v." + version
	checkVersion();
	getState();
	getLogbuch();
	timer = window.setInterval("getMesswerte()",1000);
}
