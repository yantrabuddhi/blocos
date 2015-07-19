# -*- coding: utf-8 -*- 

# Este arquivo é parte do programa Blocos
# Blocos é um software livre; você pode redistribui-lo e/ou 
# modifica-lo dentro dos termos da Licença Pública Geral GNU como 
# publicada pela Fundação do Software Livre (FSF); na versão 3 da 
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuido na esperança que possa ser  util, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from geom import *

class C_type( object ):
    ALL     = 0
    NORMAL  = 1
    LOGIC   = 2
    NUMBER  = 3

class C_form( object ):
    FEM = 0
    MASC = 1

# each block will be able to have one and just one connection to its parent,
# this connection will have its flow flag equal to TO_PARENT, the others
# will be TO_CHILD
class C_flow( object ):
    TO_PARENT = 0
    TO_CHILD  = 1

class Dock(object):

	def __init__(self, _rect, _type, format, flow = C_flow.TO_CHILD):
		self.destiny_conn = None
		self.origin_block       = None
		self.enabled            = None
		self._type              = None
		self.format             = None
		self.flow               = None
		
		self.set_type(_type)
		self.set_destiny_conn(None)
		self.set_enabled(True)
		self.set_format(format)
		self.set_flow(flow)
		
		self._rect = _rect.copy()
		
	def __eq__(self, dock2):
		return self.get_type() == dock2.get_type() and\
		self.get_format() == dock2.get_format() and\
		self.get_flow() == dock2.get_flow() and (self._rect == dock2._rect)

	#def __repr__(self):
	#	return "Conexão - enabled: "+str(self.get_enabled())+" tipo: "+str(self.get_type())+" formato: "+str(self.get_format())+" fluxo "+str(self.get_flow())+" origem "+str(type(self.get_origin_block()))+str(type(self.get_destiny_block()))

	def copy(self):
		newdock = Dock( self._rect, self._type, self.format, self.flow )
		if not self.get_destiny_conn() is None:
			newdock.connect( self.get_destiny_conn() )
		return newdock

	def get_destiny_block(self):
		if self.destiny_conn:
			return self.destiny_conn.origin_block
		else:
			return None

	def get_destiny_conn(self):
		return self.destiny_conn

	def set_destiny_conn(self, conn):
		self.destiny_conn = conn

	def get_origin_block(self):
		return self.origin_block

	def set_origin_block(self, block):
		self.origin_block = block
	
	def get_enabled(self):
		return self.enabled

	def set_enabled(self, value):
		self.enabled = value

	def set_flow(self, value):
		self.flow = value

	def get_flow(self):
		return self.flow

	def get_type(self):
		return self._type

	def set_type(self, value):
		self._type = value

	def get_format(self):
		return self.format

	def set_format(self, value):
		self.format = value

	def get_position(self):
		return Vector(self._rect.x, self._rect.y)

	def get_center(self):
		return self.get_absposition() + Vector(self.get_rect().get_size()[0], self.get_rect().get_size()[1])/(2)

	def get_absposition(self):
		return self.get_origin_block().get_position() + self.get_position()

	def get_rect(self):
		return self._rect

	def get_distance(self, dock2):
		return self.get_absposition() - dock2.get_absposition()

	def overlap(self, dock2):
	
		rect1 = self.get_rect().copy()
		rect2 = dock2.get_rect().copy()

		rect1.move( self.get_absposition()  )
		rect2.move( dock2.get_absposition() )
		return rect1.collide( rect2 )

	#rules to connect:
	# * the rectangles associated with each dock must collide
	# * the type of them must be equal
	# * the form of them must be different

	def is_possible_to_connect(self, dock2):

		if self == dock2 or self.get_origin_block() == dock2.get_origin_block():
			return False
		
		if self.get_type() == dock2.get_type() and self.get_format() != dock2.get_format() and\
		self.get_enabled() == True and dock2.get_enabled() == True and self.get_flow() != dock2.get_flow() and\
		self.overlap(dock2):
			return True
		else:
			return False
	
	def connect(self, dock2):
		
		if self.is_possible_to_connect(dock2):
			
			self.set_destiny_conn(dock2)
			self.set_enabled(False)
			
			dock2.set_destiny_conn(self)
			dock2.set_enabled(False)
			
			return True
		else:
			return False

	def disconnect(self):
		
		if self.get_enabled() == False:
			self.get_destiny_conn().set_destiny_conn(None)
			self.get_destiny_conn().set_enabled(True)
		
		self.set_destiny_conn(None)
		self.set_enabled(True)
		
