import socket
import select
from threading import Thread

class SockServer:
	def __init__(self):
		print "Server Init"
		#Server im Hintergrund starten
		self.active = True
		self.ServerThread = Thread(target=self.server,args=())
		self.ServerThread.start()

	def broadcast(self, message):
		#Keine message zum master socket senden
		for socket in self.client_list:
			if socket != self.sock:
				try :
					socket.sendall(message)
				except :
					# broken socket connection
					print "Client (%s, %s) is offline" % socket.getsockname()
					self.client_close.append(socket)
					self.client_list.remove(socket)
	
	def shutdown(self):
		self.active = False
		self.ServerThread.join()
		
	def server(self):
		print "Server starting..."
		self.client_list = []
		self.client_close = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('', 3333))
		self.sock.setblocking(0)
		self.sock.listen(5)
		self.client_list.append(self.sock)
		while self.active:
			read_sockets,write_sockets,error_sockets = select.select(self.client_list,[],[],10)
			for sock in read_sockets:
			#New connection
				if sock == self.sock:
					# Handle the case in which there is a new connection recieved through server_socket
					sockfd, addr = self.sock.accept()
					self.client_list.append(sockfd)
					print "Client (%s, %s) connected" % addr
				 
				#Some incoming message from a client
				else:
					# Data received from client, discard it
					try:
						sock.recv(1024)
					except:
						print "Client (%s, %s) is offline" % addr
						sock.close()
						self.client_list.remove(sock)
						continue
			for sock in self.client_close:
				sock.close()
				self.client_close.remove(sock)
				
		print "Server ending..."
		for sock in self.client_list:
			sock.shutdown(socket.SHUT_RDWR)
			sock.close()
