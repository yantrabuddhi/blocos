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

## Implementa alguns tipos geométricos

class Vector( object ):
    
    """Define um vetor"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Vector(self.x, self.y)

    def __eq__(self, p):
        if self.x == p.x and self.y == p.y:
            return True
        else:
            return False

    def __add__(self, Vector2):
        return Vector(self.x + Vector2.x, self.y + Vector2.y)

    def __sub__(self, Vector2):
        return Vector(self.x - Vector2.x, self.y - Vector2.y)

    def __mul__(self, n):
        return Vector(n*self.x, n*self.y)

    def __div__(self, n):
        return Vector(self.x/n, self.y/n)

    def __repr__(self):
        return "("+str(self.x)+","+str(self.y)+")"
    
class Rect( object ):
    
    """
    Essa classe representa um retângulo
    """
    
    def __init__(self, x, y, w, h):
        
        """
        Cria um retângulo com na posição (x,y) e com largura w
        e altura h
        """
        
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    ## Verfica se um ponto está dentro do retângulo
    #  @param pos vetor com a posição do ponto        
    def pos_inside(self, pos):
        return ( pos.x >= self.x and pos.y >= self.y and pos.x <= self.x+self.w and pos.y <= self.y+self.h )
        

    def move(self, vpos):
        
        """
        Move o retângulo para
        uma posição indicada por vpos
        """
        
        self.x = vpos.x
        self.y = vpos.y

    def __and__(self, rect2):
        
        """
        Sobrecarga do operador &: Retorna a intersecção
        entre o retângulo e rect2
        """
        
        p1 = Vector( max(self.x, rect2.x), max(self.y, rect2.y) )
        p2 = Vector( min(self.x+self.w, rect2.x+rect2.w), min(self.y+self.h, rect2.y+rect2.h) )

        d = p2 - p1
        
        return Rect(p1.x, p1.y, d.x, d.y)

    def is_valid(self):
        
        """
        Verifica se o retângulo é válido
        """
        
        if self.w >= 0 and self.h >= 0:
            return True
        else:
            return False
    
    def copy(self):
        
        """
        Retorna um outro retângulo
        equivalente
        """
        
        return Rect(self.x, self.y, self.w, self.h)

    def collide(self, rect2):
        
        """
        Verifica se há a colisão com outro retângulo
        """
        
        return (self & rect2).is_valid()

    def __eq__(self, rect2):
        
        return (self.x == rect2.x) and (self.y == rect2.y) and (self.w == rect2.w) and (self.h == rect2.h)

    @staticmethod
    def create_rect_from_vector(v1, v2):
        """
        Cria um retângulo a partir dos
        pontos v1 e v2
        """
        x1 = min(v1.x, v2.x )
        x2 = max(v1.x, v2.x )
        y1 = min(v1.y, v2.y )
        y2 = max(v1.y, v2.y )
        
        return Rect(x1,y1,x2-x1,y2-y1)

    def __repr__(self):
        return "("+str(self.x)+","+str(self.y)+"|"+str(self.w)+","+str(self.h)+")"
