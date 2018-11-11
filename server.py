# -*- coding: utf-8 -*-
import socket
import select
from pymongo import MongoClient
import sys
import json

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
				return 'Registrado'
			else:
				return 'Usuario ya existe'
		except:
			return 'Error'
		
	def ingresar(self, username, password):
		self.user = self.users.find_one({'username' : username})
		if self.user is None:
			return 'Usuario no existe'
		elif self.user['password'] == password:
			return 'Exito'
		else:
			return 'Contraseña incorrecta'

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
					self.data = self.sock.recv(1024).decode('utf8')
					if self.data:
						self.cabeza, self.cuerpo = self.data.split('-')
						
						#Registrar un nuevo usuario
						if self.cabeza == 'reg':
							self.username, self.password = self.cuerpo.split('/')
							self.response = self.registrar(self.username, self.password)
							if self.response == 'Registrado':
								self.contacts[self.sock] = self.username
							self.sock.send(self.response.encode('utf8'))

						#Ingresar usuario
						if self.cabeza == 'ing':
							self.username, self.password = self.cuerpo.split('/')
							self.response = self.ingresar(self.username, self.password)
							if self.response == 'Exito':
								self.contacts[self.username] = self.sock
							self.sock.send(self.response.encode('utf8'))

						#Mostrar salas
						if self.cabeza == '#IR':
							self.response = json.dumps({'rooms' : list(self.rooms.keys())}).encode('utf8')
							self.sock.send(self.response)

						#Mostrar usuarios
						if self.cabeza == '#show users' :
							self.response = json.dumps({'users' : list(self.contacts.items())}).encode('utf8')
							self.sock.send(self.response)

						#Crear sala 
						if self.cabeza == '#cR':
							self.rooms[self.cuerpo] = []
							self.rooms[self.cuerpo].append(self.sock)
							self.sock.send('Ok'.encode('utf8'))

						#Entrar a una sala
						if self.cabeza == '#gR':
							self.rooms[self.cuerpo].append(self.sock)
							self.sock.send('Ok'.encode('utf8'))

						#Eliminar sala dR
						if self.cabeza == '#dR':
							if self.rooms[self.cuerpo][0] == self.sock:
								del self.rooms[self.cuerpo]
								self.sock.send('Ok'.encode('utf8'))
							else:
								self.sock.send('Denegado'.encode('utf8'))

						#Chat
						if self.cabeza == 'chat':
							self.room, self.mensaje = self.cuerpo.split('/')
							for self.person in self.rooms[self.room]:
								if self.person != self.s:
									print("AQUI")
									print(self.mensaje)
									self.person.send(self.mensaje.encode('utf8'))

def main():
	server = Servidor('192.168.1.61', 8080)
	server.run()

if __name__ == '__main__':
	main()

