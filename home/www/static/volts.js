// JavaScript Document

var req = new XMLHttpRequest();
var timer = null;

function fillVolts() {
	if (this.readyState == this.DONE) {
		if (this.status == 200 && this.responseXML != null) {
			var time = new Date();

			//Felder definieren
			u1e_field = document.getElementById("u1e");
			//u1l_field = document.getElementById("u1l");
			u2e_field = document.getElementById("u2e");
			//u2l_field = document.getElementById("u2l");
			u3e_field = document.getElementById("u3e");
			//u3l_field = document.getElementById("u3l");
			u4e_field = document.getElementById("u4e");
			//u4l_field = document.getElementById("u4l");

			clock_field = document.getElementById("clock");

			//Antwort vom Server
			xml = this.responseXML;

			u1e_resp = xml.getElementsByTagName("u1e")[0];
			u1l_resp = xml.getElementsByTagName("u1l")[0];
			u2e_resp = xml.getElementsByTagName("u2e")[0];
			u2l_resp = xml.getElementsByTagName("u2l")[0];
			u3e_resp = xml.getElementsByTagName("u3e")[0];
			u3l_resp = xml.getElementsByTagName("u3l")[0];
			u4e_resp = xml.getElementsByTagName("u4e")[0];
			u4l_resp = xml.getElementsByTagName("u4l")[0];

			//Werte eintragen (Logbuch kann auch leer sein)
			u1e_field.value = u1e_resp.firstChild.nodeValue;
			//u1l_field.value = u1l_resp.firstChild.nodeValue;
			u2e_field.value = u2e_resp.firstChild.nodeValue;
			//u2l_field.value = u2l_resp.firstChild.nodeValue;
			u3e_field.value = u3e_resp.firstChild.nodeValue;
			//u3l_field.value = u3l_resp.firstChild.nodeValue;
			u4e_field.value = u4e_resp.firstChild.nodeValue;
			//u4l_field.value = u4l_resp.firstChild.nodeValue;

			clock_field.value = time.toLocaleTimeString();

			if (timer == null) {
				timer = window.setInterval("getVolts()",1000);
			}
		}
	}
}

function getVolts() {
	req.open("GET", "/volts");
	req.onreadystatechange = fillVolts;
	req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	req.send(null);
}

function run() {
	getVolts();
}
