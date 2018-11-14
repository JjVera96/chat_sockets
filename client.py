# -*- coding: utf-8 -*-
import socket
import select
import sys
import json

class Cliente():
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.ip, self.port))
		print('Conectado al servidor chat de la ip {} en el puerto {}'.format(self.ip, self.port))
		self.username = ''

	def menu_inicio(self):
		while True:
			print('Bienvenido al Chat !!')
			print('0. Salir')
			print('1. Registrarse')
			print('2. Ingresar')
			self.op = int(input('Opcion: '))
			if not self.op: 
				print('Chat terminado')
				self.s.close()
				sys.exit()
			if self.op == 1:
				self.username = input('Ingrese un Usuario: ')
				self.password = input('Ingrese una Contraseña: ')
				self.name = input('Ingrese Nombres: ')
				self.last_name = input('Ingrese Apellidos: ')
				self.edad = input('Ingrese Edad: ')
				self.gender = input('Ingrese Genero: ')
				self.s.send('reg-{}/{}/{}/{}/{}/{}'.format(self.username, self.password, self.name, self.last_name, self.edad, self.gender).encode('utf8'))
				self.data = self.s.recv(1024).decode('utf8')
				if self.data == 'Registrado':
					print('\nRegistro con exito\n')
					return True
				else:
					print('\n'+self.data+'\n')
			if self.op == 2:
				self.username = input('Ingrese Usuario: ')
				self.password = input('Ingrese Contraseña: ')
				self.s.send('ing-{}/{}'.format(self.username, self.password).encode('utf8'))
				self.data = self.s.recv(1024).decode('utf8')
				if self.data == 'Exito':
					print('\nIngreso con exito\n')
					return True
				else:
					print('\n'+self.data+'\n')

	def menu_secundario(self):
		while True:
			print('...Salas de Chat...')
			print('0. Salir')
			print('1. Mostrar salas disponibles')
			print('2. Mostrar usuarios disponibles')
			print('3. Entrar a una sala')
			print('4. Crea tu sala')
			print('5. Eliminar sala')
			self.op = int(input('Opcion: '))
			
			#Salir
			if not self.op: 
				print('Chat terminado')
				self.mensaje = 'exit-{}/{}'.format(self.username, None)
				self.s.close()
				sys.exit()

			#Mostrar las salas disponibles
			if self.op == 1:
				self.s.send('IR-'.encode('utf8'))
				self.data = self.s.recv(1024).decode('utf8')
				self.data = json.loads(self.data)
				print('\nSalas Activas')
				print(self.data['rooms'])
				print('\n')

			#Mostrar usuarios disponibles
			if self.op == 2:
				self.s.send('show users-'.encode('utf8'))
				self.data = self.s.recv(1024).decode('utf8')
				self.data = json.loads(self.data)
				print('\nUsuarios Activos')
				print(self.data['users'])
				print('\n')

			#Entrar a una sala
			if self.op == 3:
				self.s.send('IR-'.encode('utf8'))
				self.data = self.s.recv(1024).decode('utf8')
				self.data = json.loads(self.data)
				if len(self.data['rooms']):
					self.nombre = input('Ingrese nombre a la sala: ')
					if self.nombre in self.data['rooms']:
						self.s.send('ngR-{}'.format(self.nombre).encode('utf8'))
						return self.nombre
					else:
						print('\nEsta sala no existe\n')
				else:
					print('\nNo hay salas, crea tu propia sala\n')

			#Crear mi sala
			if self.op == 4:
				nombre = input('Ingrese nombre a la sala: ')
				self.s.send('nR-{}'.format(nombre).encode('utf8'))
				self.room = nombre
				return self.room

			if self.op == 5:
				nombre = input('Ingrese nombre a la sala: ')
				self.s.send('dR-{}'.format(nombre).encode('utf8'))
				self.data = self.s.recv(1024).decode('utf8')
				print('\n{}\n'.format(self.data))

	def pantalla(self):
		sys.stdout.write('->')
		sys.stdout.flush()

	def chat(self, room):
		self.pantalla()
		self.room = room
		while True:
			self.socket_list = [sys.stdin, self.s]
			self.read_sockets, self.write_sockets, self.error_sockets = select.select(self.socket_list , [], [])
			for self.sock in self.read_sockets:
				if self.sock == self.s:
					self.data =  self.sock.recv(1024).decode('utf8')
					if self.data[0] == '#':
						self.comando, self.cuerpo = self.data.split('-')
						if self.comando == '#room':
							self.room = self.cuerpo
							print('\nIngresaste a la sala {}'.format(self.room))
						if self.comando == '#remove':
							print('\nLa sala {} fue eliminada.'.format(self.room))
							return
					else:
						sys.stdout.write(self.data + '\n')
					self.pantalla()
				else:
					self.msg = sys.stdin.readline()
					if self.msg[0] == '#':
						self.msg = self.msg.rstrip('\n')
						if ' ' in self.msg:
							self.comando, self.cuerpo = self.msg.split(' ', 1)
							#Enviar privado 
							if self.comando == '#private':
								self.persona, self.envio = self.cuerpo.split(' ', 1)
								self.mensaje = 'private-{}/(mensaje privado) {}:{}'.format(self.persona, self.username, self.envio)
								self.s.send(self.mensaje.encode('utf8'))
							#Crear sala, salgo de la actual sala y entro a la nueva
							elif self.comando == '#cR':
								self.mensaje = 'cR-{}/{}'.format(self.cuerpo, self.room)
								self.s.send(self.mensaje.encode('utf8'))
							#Cambiar sala, salgo de la actual sala y entro a otra
							elif self.comando == '#gR':
								self.mensaje = 'gR-{}/{}'.format(self.cuerpo, self.room)
								self.s.send(self.mensaje.encode('utf8'))
							#Mostrar usuarios
							elif self.comando == '#show':
								self.mensaje = 'show users-'
								self.s.send(self.mensaje.encode('utf8'))
							#Eliminar una sala
							elif self.comando == '#dR':
								self.mensaje = 'dR-{}'.format(self.room)
								self.s.send(self.mensaje.encode('utf8'))
							else:
								print('No existe tal comando (Space)')
						else:
							self.comando = self.msg.rstrip('\n')
							#Mostrar salas
							if self.comando == '#IR':
								self.mensaje = 'IR-'
								self.s.send(self.mensaje.encode('utf8'))
							#Salir 
							elif self.comando == '#exit':
								self.mensaje = 'exit-{}/{}'.format(self.username, self.room)
								self.s.send(self.mensaje.encode('utf8'))
								self.s.close()
								sys.exit()
							#Dejar sala
							elif self.comando == '#eR':
								self.mensaje = 'eR-{}'.format(self.room)
								self.s.send(self.mensaje.encode('utf8'))
								return
							else:
								print('No existe tal comando (With Space)')
					else:
						#chat-room/username:msg
						self.mensaje = 'chat-{}/{}:'.format(self.room,self.username) + self.msg.rstrip('\n')
						self.s.send(self.mensaje.encode('utf8'))
					self.pantalla() 
		print('\nDejaste la sala.\n')

	def run(self):
		self.menu_inicio()
		while True:
			self.room = self.menu_secundario()
			print('\nIngresaste a la sala {}'.format(self.room))
			self.chat(self.room)

def main():
	cliente = Cliente('10.253.129.41', 5000)
	cliente.run()

if __name__ == "__main__":
	main()