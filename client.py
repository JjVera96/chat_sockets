# -*- coding: utf-8 -*-
import socket
import select
import sys

class Cliente():
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.ip, self.port))
		print('Conectado al servidor chat de la ip {} en el puerto {}'.format(self.ip, self.port))

	def prompt(self):
		sys.stdout.write('#[TU]: ')
		sys.stdout.flush()

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
				self.s.send('reg-{}/{}'.format(self.username, self.password).encode('ascii'))
				self.data = self.s.recv(1024).decode('ascii')
				if self.data == 'Registrado':
					print('\nRegistro con exito\n')
					return True
				else:

					print('\n'+self.data+'\n')
			if self.op == 2:
				self.username = input('Ingrese Usuario: ')
				self.password = input('Ingrese Contraseña: ')
				self.s.send('ing-{}/{}'.format(self.username, self.password).encode('ascii'))
				self.data = self.s.recv(1024).decode('ascii')
				if self.data == 'Exito':
					print('\nIngreso con exito\n')
					return True
				else:
					print('\n'+self.data+'\n')

	def menu_secundario(self):
		while True:
			print('...Salas de Chat...')
			print('1. Mostrar salas disponibles')
			print('2. Entrar a una sala')
			print('3. Crea tu sala')
			print('4. Salir')

	def run(self):
		self.menu_inicio()
		self.menu_secundario()
		self.s.close()

def main():
	cliente = Cliente('192.168.1.61', 5005)
	cliente.run()


if __name__ == "__main__":
	main()