#!/usr/bin/env python
#-*-coding: utf-8 -*-

import string,cgi,sys,os,fcntl
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import daemon
from Pages import Pages
import base64
import Password

Seiten = Pages()
if Password.password != None:
	AuthHeader = 'Basic ' + base64.b64encode(Password.password)
else:
	AuthHeader = ''

class MyHandler(BaseHTTPRequestHandler):

	def do_AUTHHEAD(self):
		self.send_response(401)
		self.send_header('WWW-Authenticate', 'Basic realm=\"AV4ms\"')
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_HEAD(self,ctype='text/html'):
		self.send_response(200)
		self.send_header('Version','HTTP/1.1')
		self.send_header('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
		self.send_header('Pragma', 'no-cache')
		self.send_header('Content-type', ctype)
		self.send_header('Expires', 'Fri, 01 Jan 1990 00:00:00 GMT')
		self.end_headers()
		
	def do_GET(self):
		global AuthHeader
		if Password.password == None or self.headers.getheader('Authorization') == AuthHeader:
			try:
				if self.path == '/':
					self.path = '/static/index.html'
				if self.path == '/messwerte':
					self.GET_messwerte()
				elif self.path == '/control':
					self.GET_control()
				elif self.path == '/logbuch':
					self.GET_logbuch()
				elif self.path == '/analyse':
					self.GET_analyse()
				elif self.path == '/volts':
					self.GET_volts()
				elif self.path[0:8] == '/static/':
					f = open(curdir + sep + self.path)
					if self.path.endswith('.js'):
						self.do_HEAD('application/javascript')
					elif self.path.endswith('.css'):
						self.do_HEAD('text/css')
					elif self.path.endswith('.ico'):
						self.do_HEAD('image/vnd.microsoft.icon')
					else:
						self.do_HEAD('text/html')
					self.wfile.write(f.read())
					f.close()
				return

			except IOError:
				self.send_error(404,'File Not Found: %s' % self.path)

		elif self.headers.getheader('Authorization') == None:
			self.do_AUTHHEAD()
			self.wfile.write('no auth header received')
		else:
			self.do_AUTHHEAD()
			self.wfile.write(self.headers.getheader('Authorization'))
			self.wfile.write('not authenticated')

	def do_POST(self):
		if Password.password == None or self.headers.getheader('Authorization') == AuthHeader:
			try:
				form = cgi.FieldStorage(
					fp=self.rfile,
					headers=self.headers,
					environ={'REQUEST_METHOD':'POST',
						'CONTENT_TYPE':self.headers['Content-Type'],
					})

				if self.path == '/control':
					Seiten.post_control(form)
					self.GET_control()
				else:
					self.send_error(404,'File Not Found: %s' % self.path)

			except :
				pass

		elif self.headers.getheader('Authorization') == None:
			self.do_AUTHHEAD()
			self.wfile.write('no auth header received')
		else:
			self.do_AUTHHEAD()
			self.wfile.write(self.headers.getheader('Authorization'))
			self.wfile.write('not authenticated')

	def GET_control(self):
		self.do_HEAD('text/xml')
		self.wfile.write(Seiten.control())

	def GET_messwerte(self):
		self.do_HEAD('text/xml')
		self.wfile.write(Seiten.messwerte())

	def GET_volts(self):
		self.do_HEAD('text/xml')
		self.wfile.write(Seiten.volts())

	def GET_logbuch(self):
		self.do_HEAD('text/xml')
		self.wfile.write(Seiten.logbuch())

	def GET_analyse(self):
		self.do_HEAD('text/html')
		self.wfile.write(Seiten.analyse())

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
	try:
		uid = os.getuid()
		if uid == 0:
			port = 80
		else:
			port = 8080
		server = HTTPServer(('', port), MyHandler)
		print 'started httpserver...'
		if uid == 0: # root?
			os.setgid(33)    # dann www-data
			os.setuid(33)
		server.serve_forever()
	except KeyboardInterrupt:
		print '^C received, shutting down server'
		server.socket.close()

context = daemon.DaemonContext(
	working_directory = '/home/www',
	umask=0o002,
	pidfile = PidFile("/tmp/webserver.pid"),
	files_preserve = [sys.stdout,sys.stderr]
	)
with context:
	run()
