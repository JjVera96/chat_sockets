# -*- coding: utf-8 -*-
import socket
import select
from pymongo import MongoClient
import sys
import json

class Servidor():
	def __init__(self, ip, port):
		self.client = MongoClient('10.253.130.254', 27017)
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

	def registrar(self, username, password, name, last_name, edad, gender):
		new_user = {
			'username' : username,
			'password' : password,
			'name' : name,
			'last_name' : last_name,
			'edad' : edad,
			'gender' : gender
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
							self.username, self.password, self.name, self.last_name, self.edad, self.gender = self.cuerpo.split('/')
							self.response = self.registrar(self.username, self.password, self.name, self.last_name, self.edad, self.gender)
							if self.response == 'Registrado':
								self.contacts[self.username] = self.sock
							self.sock.send(self.response.encode('utf8'))

						#Ingresar usuario
						if self.cabeza == 'ing':
							self.username, self.password = self.cuerpo.split('/')
							self.response = self.ingresar(self.username, self.password)
							if self.response == 'Exito':
								self.contacts[self.username] = self.sock
							self.sock.send(self.response.encode('utf8'))

						#Mostrar salas
						if self.cabeza == 'IR':
							self.response = json.dumps({'rooms' : list(self.rooms.keys())}).encode('utf8')
							self.sock.send(self.response)

						#Mostrar usuarios
						if self.cabeza == 'show users' :
							self.response = json.dumps({'users' : list(self.contacts.keys())}).encode('utf8')
							self.sock.send(self.response)

						#Crear sala desde lobby
						if self.cabeza == 'nR':
							self.rooms[self.cuerpo] = []
							self.rooms[self.cuerpo].append(self.sock)

						#Entrar a una sala desde lobby
						if self.cabeza == 'ngR':
							self.rooms[self.cuerpo].append(self.sock)

						#Chat
						if self.cabeza == 'chat':
							self.room, self.mensaje = self.cuerpo.split('/')
							for self.person in self.rooms[self.room]:
								if self.person != self.s and self.person != self.sock:
									self.person.send(self.mensaje.encode('utf8'))

						#Eliminar sala
						if self.cabeza == 'dR':
							print(self.rooms[self.cuerpo])
							if self.rooms[self.cuerpo][0] == self.sock:
								for self.person in self.rooms[self.cuerpo]:
									self.person.send('#remove-'.encode('utf8'))
								del self.rooms[self.cuerpo]
								self.sock.send('Ok'.encode('utf8'))
							else:
								self.sock.send('Denegado'.encode('utf8'))
							
						#Crear una sala estando en otra
						if self.cabeza == 'cR':
							print('cR')
							self.nroom, self.room = self.cuerpo.split('/')
							if not self.nroom in self.rooms:
								self.lista_usuarios = self.rooms[self.room]
								self.indice = self.lista_usuarios.index(self.sock)
								print(self.lista_usuarios)
								del self.lista_usuarios[self.indice]
								print(self.lista_usuarios)
								self.rooms[self.nroom] = []
								self.rooms[self.nroom].append(self.sock)
								print(self.rooms[self.nroom])
								self.sock.send('#room-{}'.format(self.nroom).encode('utf8'))
							else:
								self.sock.send('Esta sala ya existe'.encode('utf8'))

						#Cambiar sala
						if self.cabeza == 'gR':
							print('gR')
							self.nroom, self.room = self.cuerpo.split('/')
							if self.nroom in self.rooms:
								self.lista_usuarios = self.rooms[self.room]
								self.indice = self.lista_usuarios.index(self.sock)
								print(self.lista_usuarios)
								del self.lista_usuarios[self.indice]
								print(self.lista_usuarios)
								self.rooms[self.nroom].append(self.sock)
								print(self.rooms[self.nroom])
								self.sock.send('#room-{}'.format(self.nroom).encode('utf8'))
							else:
								self.sock.send('Esta sala no existe'.encode('utf8'))

						#Privado a alguien
						if self.cabeza == 'private':
							self.person, self.mensaje = self.cuerpo.split('/')
							if self.person in self.contacts:
								self.sock_person = self.contacts[self.person]
								self.sock_person.send(self.mensaje.encode('utf8'))
							else:
								self.sock.send('No existe tal usuario'.encode('utf8'))

						#Salir sala
						if self.cabeza == 'eR':
							self.room = self.cuerpo
							self.lista_usuarios = self.rooms[self.room]
							self.indice = self.lista_usuarios.index(self.sock)
							del self.lista_usuarios[self.indice]

						#Salir chat
						if self.cabeza == 'exit':
							self.username, self.room = self.cuerpo.split('/')
							if not self.room is None:
								self.lista_usuarios = self.rooms[self.room]
								self.indice = self.lista_usuarios.index(self.sock)
								del self.lista_usuarios[self.indice]
							del self.contacts[self.username]


def main():
	server = Servidor('10.253.129.41', 5000)
	server.run()

if __name__ == '__main__':
	main()