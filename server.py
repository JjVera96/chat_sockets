# -*- coding: utf-8 -*-
import socket
import select
from pymongo import MongoClient
import sys

class Servidor():
	def __init__(self, ip, port):
		self.client = MongoClient('192.168.1.64', 27017)
		self.db = self.client.distribuidos
		self.users = self.db.users
		self.host = ip
		self.port = port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.host, self.port))
		self.s.listen(0)
		self.contacts = {}
		self.rooms = {}
		self.conn_list = []
		print('Servidor escuchando por la ip {} en el puerto {}'.format(ip, port))

	def registrar(self, username, password):
		new_user = {
			'username' : username,
			'password' : password
		}
		try:
			self.user = self.users.find_one({'username' : username})
			if self.user is None:
				self.user_id = self.users.insert_one(new_user).inserted_id
				return 'Registrado'.encode('ascii')
			else:
				return 'Usuario ya existe'.encode('ascii')
		except:
			return 'Error'.encode('ascii')
		
	def ingresar(self, username, password):
		self.user = self.users.find_one({'username' : username})
		if self.user is None:
			return 'Usuario no existe'.encode('ascii')
		elif self.user['password'] == password:
			print(self.user)
			return 'Exito'.encode('ascii')
		else:
			return 'Contrasenia incorrecta'.encode('ascii')

	def run(self):
		self.conn_list.append(self.s)
		while True:
			self.ready_to_read,self.ready_to_write,self.in_error = select.select(self.conn_list,[],[],0)
			for self.sock in self.ready_to_read:
				if self.sock == self.s:
					self.conn, self.addr = self.s.accept()
					self.conn_list.append(self.conn)
					print('Cliente {} conectado'.format(self.addr))
				else:
					self.data = self.sock.recv(1024).decode('ascii')
					if self.data:
						self.cabeza, self.cuerpo = self.data.split('-')
						
						#Registrar un nuevo usuario
						if self.cabeza == 'reg':
							self.username, self.password = self.cuerpo.split('/')
							self.response = self.registrar(self.username, self.password)
							self.sock.send(self.response)

						#Ingresar usuario
						if self.cabeza == 'ing':
							self.username, self.password = self.cuerpo.split('/')
							self.response = self.ingresar(self.username, self.password)
							self.sock.send(self.response)

def main():
	server = Servidor('192.168.1.61', 5005)
	server.run()

if __name__ == '__main__':
	main()

