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

from dock import *
import gtk, gtk.glade
import pango
from geom import *
import copy
import os
from config import *

class label(object):
	
    """Textos dos blocos"""
	
    ## Construtor do label
    #  @param x posicao x em relacao ao bloco que o label vai estar
    #  @param y posicao y em relacao ao bloco que o label vai estar
    #  @param text texto que vai aparecer no label
    #  @param font nome da fonte que sera usada
    #  @param size tamanho da fonte
    #  @param color cor da fonte
    def __init__(self, x, y, text, font, size, color):
        self.x    = x
        self.y    = y
        self.text = text
        self.font = font
        self.size = size
        self.color = color
        self.Block = None

        self.fd = pango.FontDescription(font)
        self.fd.set_size(size*pango.SCALE)

    ## Atribui um bloco ao label
    # @param block bloco do label
    def set_block(self, block):
        self.Block = block

    ## Muda a posicao do label
    # @param x coordenada x do label
    # @param y coordenada y do label
    def set_pos(self, x , y):
        self.x = x
        self.y = y
        
        if self.Block:
            self.Block.redraw()

    ## Muda o texto do label
    #  @param text novo texto
    def set_text(self, text):
        self.text = text
        
        try:
            self.Block.redraw()
        except AttributeError: # Tudo bem
            pass

    ## Muda a fonte do label
    #  @param text nova fonte
    def set_font(self, font, size):
        self.font = font
        self.size = size
        
        self.fd = pango.FontDescription(font)
        self.fd.set_size(size*pango.SCALE)  
        
        try:
            self.Block.redraw()
        except AttributeError: # Tudo bem
            pass


class Block(object):

    """Um bloco"""

    #associa uma string com um tipo de bloco, essa string será usada para
    #salvar e carregar blocos de arquivos
    dict_blockref = {}

    #tipo de bloco -> pixbuf associado
    dict_img = {}

    #tipo de bloco -> pixbuf que será exibido no menu associado
    dict_menu_img = {}

    ## Associa uma string com um tipo de bloco
    # @param name string
    # @param _type tipo de bloco
    @staticmethod
    def new_block_type(name, _type):
        Block.dict_blockref[name] = _type
    
    ## Construtor do bloco
    def __init__(self):
        
        #encontra a string associada ao tipo do bloco
        self._type = None
        for (name, _type) in Block.dict_blockref.items():
            if type(self) == _type:
                self._type = name
        if self._type is None:
            print "Block type "+str( type(self) )+" não definido!"
        
        self.erasable = True	# se o bloco pode ser apagado pelo usuário
        self.lock     = True	# se o bloco não deve ser atualizado no canvas
        
        self.has_parent = False	# se o bloco não está no topo da árvore
        
        self.connections = []	# todas as conexões do bloco
        
        self.code = []			# texto e diretivas do código que o bloco gera
        
        self.properties = {}	# propriedades do bloco
                                # nome da propriedade -> valor
                                # todos os atributos que serão e carregados
                                # deverão ser uma chave neste dicionário
        self.drawimg = [None, None]
        #               ^       ^ pixbuf da imagem do bloco selecionado
        #               ^ pixbuf da imagem do bloco normal
        self.menuimg = None # pixbuf que tem a imagem de menu desse bloco
        
        self.click = False	# se o mouse está pressionado na área do bloco
        self.click_pos = Vector(-1, -1) # posicao do clique relativa ao bloco do mouse
        self.drag_pos  = Vector(-1, -1) # posicao do clique relativa ao ultimo clique verificado
        
        self.was_put = False	# se o bloco já foi inserido em um canvas

        # se um bloco tiver gtk.widgets dentro dele, eles deverão estar nesse conjunto
        self.widget_children = set()
        # conjunto de todos os labels do bloco
        self.label = set()
        
        # gtk.box que vai conter a barra de propriedades do bloco
        self.gui = None
        
        # canvas a que o bloco pertence
        self.canvas = None
        
        # propriedades comuns a todos os blocos
        self.create_property("x", -1)	# posição x do bloco
        self.create_property("y", -1)	# posição y do bloco
        self.create_property("selected", False)	# se o bloco está selecionado
        self.create_property("layer", 0)	# prioridade na renderização
    
    ## Retorna o bloco que está no topo daquele ramo da árvore de blocos
    def get_top(self):
        block = self
        
        while block.has_parent == True:
            r     = block
            block = block.get_docks()[0].get_destiny_block()
            if block is None: return r
        
        return block

    ## Esta função será chamada sempre que o bloco for apagado,
    #  herde-o se necessário - ver database.py
    def remove(self):
        pass

    def set_layer(self, l):
        self.set_property("layer", l)
        self.mark_dirty()
        
    def get_layer(self):
        return self.get_property("layer")

    ## prioridade de renderização de um bloco
    layer = property(get_layer, set_layer, doc="prioridade de renderização do bloco")

    ## Retorna uma string associada ao tipo do bloco
    def get_type(self):
        return self._type

    ## adiciona um trecho de código ao bloco
    # @param code
    # ( string ) o código adicionado será a própria string\n
    # ( Dock ) o código adicionado será o referenciado pela conexão\n
    # ( function ) o código adicionado será o valor de retorno da chamada da função
    def add_code(self, code):
        self.code.append(code)

    ## Cria uma cópia do bloco (não o insere em um canvas, mesmo se o original já estiver)
    def copy(self):
        newblock = Block.dict_blockref[ self.get_type() ]()
        
        newblock.properties = self.properties.copy()
        
        return newblock

    ## seleciona ou deseleciona um bloco
    #  @param t Bool que indica se seleciona ou não
    def set_selected(self, t):
        self.set_property("selected", t)
        self.mark_dirty()

    ## retorna se o bloco esta selecionado
    #  @return Bool que indica se esta selecionado ou não
    def get_selected(self):
        return self.get_property("selected")

    selected = property(get_selected, set_selected, doc="Se o bloco está selecionado")

    ## Retorna todas as conexões do bloco
    # @param include_parent se a conexao que aponta para o bloco-pai deve estar na lista
    def get_docks(self, include_parent = True):
        
        if include_parent:
            return self.connections[:]
        else:
            l = [x for x in self.connections if x.get_flow() != C_flow.TO_PARENT ]
            return l
            
    ## Retorna adiciona uma conexao ao bloco
    # @param  dock nova conexao
    def add_dock(self, dock):
        
        if dock.get_flow() == C_flow.TO_PARENT and self.has_parent == True:
            print "Ja existe uma conexao para um bloco-pai"
            return False
        else:
            if dock.get_flow() == C_flow.TO_PARENT:
                self.connections.insert( 0, dock )
                self.has_parent = True
            else:
                self.connections.append( dock )
            dock.set_origin_block(self)
            return True


    ## Esta função será chamada sempre que o bloco for colocado no canvas,
    #  herde-o se necessário - ver database.py
    def create(self):
        pass

    ## Cria uma nova propriedade
    #  @param n nome da propriedade
    #  @param v valor inicial da propriedade
    def create_property(self, n, v = None):
        # Propriedades:
        # É impossível serializar a estrutura toda do bloco, já que ele contém
        # várias auto-referências e referências cruzadas a outros blocos e a imagens,
        # a solução aqui foi fazer com que os atributos que fossem necessários para
        # carregar e salvar o bloco [como a posição, valor, etc] fossem uma chave e
        # um valor em um dicionário. No fim, esse dicionário que é salvo
        self.properties[n] = v
    
    ## Muda o valor da propriedade n para v
    #  @param n nome da propriedade
    #  @param v novo valor
    def set_property(self, n, v):
        self.properties[n] = v
        
    ## Recupera o valor de uma propriedade
    #  @param n nome da propriedade
    #  @return   valor dela
    def get_property(self, n):
        return self.properties[n]
        
    ## Retorna a árvore de blocos
    #  @return lista que inclui o bloco e a arvore abaixo dele
    def get_tree(self):
        tree=[self]
        for dock in self.get_docks(False):
            if dock.get_enabled() == False:
                tree.extend( dock.get_destiny_block().get_tree() )
        return tree

    ## Mata todos os gtk.widgets que o bloco contenha
    def kill_widgets(self):
        for w,x,y in self.widget_children:
            w.destroy()

    ## Mata a barra de propriedades associada ao bloco
    def kill_gui(self):
        if self.gui != None:
            self.gui.destroy()

    ## Mostra a barra de propriedades associada ao bloco
    def show_gui(self, prop_box):
        if not self.gui is None:
            if self.gui.get_parent() is None:
                prop_box.pack_start(self.gui)
                
            self.gui.show_all()
    
    ## Esconde a barra de propriedades associada ao bloco
    def hide_gui(self):
        if not self.gui == None:
            self.gui.hide()

    ## Adiciona um widget ao bloco
    #  @param widget novo widget
    #  @param offsetx posicao x do widget em relacao ao bloco
    #  @param offsety posicao y do widget em relacao ao bloco
    def add_widget(self, widget, offsetx, offsety):
        
        #Alguns widgets não tem uma gtk.gdk.window associada,
        #isso faz com que eles desenhem no canvas, o que não é bom,
        #por isso coloco todos widgets dentro de gtk.eventboxes
        
        evb = gtk.EventBox()
        evb.add( widget )
        self.widget_children.add( (evb, offsetx, offsety) )

    ## Cria a barra de propriedades associada ao bloco - ver database.py
    def create_gui(self, *args):
        return None

    def get_x(self):
        return self.get_property("x")

    def get_y(self):
        return self.get_property("y")

    def set_x(self, x):
        self.set_property('x', int(x) )

    def set_y(self, y):
        self.set_property('y', int(y) )
    
    x = property(get_x, set_x, doc="Posição X do bloco")
    y = property(get_y, set_y, doc="Posição Y do bloco")

    def get_position(self):
        return Vector(self.x, self.y)

    def set_position(self, pos):
        self.x  = pos.x
        self.y  = pos.y

    ## Posição XY do bloco em seu canvas
    position = property(get_position, set_position, doc="Posição XY do bloco" )

    def set_image(self, imgfile, menuimgfile):
        self.img_ok = self.load_image(imgfile, menuimgfile)

    def get_image(self):
        return self.drawimg

    def get_menu_image(self):
        return self.menuimg
    
    ## Será executado quando o botao do mouse for pressionado em cima do bloco
    def bpress(self, pos, doubleclick = False):

        if doubleclick:
            self.brelease(pos)        

        self.click = True
        
        self.click_pos = self.get_position().copy()
        self.drag_pos  = pos-self.get_position()
        
        if self.selected == False or doubleclick == True:
            self.canvas.b_connect_overlay()
            self.canvas.unselect( self.canvas.get_children() )
            self.canvas.select( self.get_tree() )
        
        self.canvas.set_group( self )
    
    ## Será executado quando o botao do mouse for solto em cima do bloco    
    def brelease(self, pos):
        self.click = False
        
        has_collision = self.canvas.unset_group()
        
        if has_collision == True:
            d = self.click_pos - self.get_position()
            for block in self.canvas.get_selected():
                block.translate(d)

    ## Move o bloco
    #  @param pos nova posição do bloco
    def move(self, pos):
        self.mark_dirty()
        self.set_position(pos)
        self.mark_dirty()

        for (w, offx, offy) in self.widget_children:
            self.canvas.move(w, self.get_x() + offx, self.get_y() + offy)

    ## Translada o bloco por um vetor
    #  @param r vetor que será adicionado a posição atual do bloco
    def translate(self, r):
        self.mark_dirty()
        self.set_position( self.get_position() + r )
        self.mark_dirty()

        for (w, offx, offy) in self.widget_children:
            self.canvas.move(w, self.get_x() + offx, self.get_y() + offy)

    ## Será executado no ato de arrastar o bloco pelo canvas
    def drag(self, pos):
        if self.click == True:
            r = pos-self.get_position()-self.drag_pos
            
            for block in self.canvas.get_selected():
                block.translate(r)

    ## faz o canvas marcar a posição atual do bloco como suja.
    #  o evento on_expose será gerado no canvas e redesenhará
    #  aquela área depois
    def mark_dirty(self):
        try:
            self.canvas.get_drawable().invalidate_rect(gtk.gdk.Rectangle( self.get_x(), self.get_y(), self.get_width(), self.get_height()), False)
        except AttributeError:
            pass
            
    def redraw(self):
        self.mark_dirty()
        self.draw( self.canvas.get_drawable(), self.canvas.get_gc() )
        self.mark_dirty()

    def draw_docks(self, drawable, gc):
        
        for dock in self.get_docks(True):
            if dock.get_enabled() == False:
                gc.set_foreground( gc.get_colormap().alloc_color('red') )
                drawable.draw_rectangle( gc, True, self.get_x()+dock.get_position().x, self.get_y()+dock.get_position().y, dock.get_rect().w, dock.get_rect().h )
            else:
                gc.set_foreground( gc.get_colormap().alloc_color('blue') )
                drawable.draw_rectangle( gc, False, dock.get_absposition().x, dock.get_absposition().y, dock.get_rect().w, dock.get_rect().h )
    
    ## desenha o bloco no canvas
    def draw(self, drawable, gc):
        
        global draw_info
        
        if self.lock:
            return
        
        if self.selected == True:
            drawable.draw_pixbuf(gc, self.get_image()[1], 0, 0, self.get_x(), self.get_y() )
        else:
            drawable.draw_pixbuf(gc, self.get_image()[0], 0, 0, self.get_x(), self.get_y() )
            
        self.draw_label(drawable, gc)
        
        # apenas para testes
        if draw_info and not (self.canvas is None):
            self.draw_docks(drawable, gc)

    ## função auxiliar de put
    def put_aux(self, canvas, x, y):
            canvas.add(self)
            self.canvas = canvas
            self.was_put = True
            
            for (w, offx, offy) in self.widget_children:
                self.canvas.put(w, 0, 0)
                w.show_all()
                
            self.move( Vector(x, y) )
            
            self.create()
            self.gui = self.create_gui()
            
            self.lock = False
            
    ## atribuindo um canvas a um bloco
    #  @param canvas canvas
    #  @param x posicao x inicial no canvas
    #  @param y posicao y inicial no canvas
    def put(self, canvas, x, y):
            
            self.put_aux(canvas, x, y)
            
            # fazendo novas conexões
            self.canvas.unselect( self.canvas.get_children() )
            self.canvas.select( (self,) )
            self.canvas.set_group( self )
            pos_inval = self.canvas.unset_group()
            self.canvas.unselect( self.canvas.get_children() )
            
            return pos_inval

    ## adiciona um novo label ao bloco
    #  @param label novo label
    def add_label(self, label):
        self.label.add(label)
        label.set_block(self)

    ## desenha os labels do bloco
    #  @param drawable gtk.gdk.drawable
    #  @param gc gtk.gdk.gc
    def draw_label(self, drawable, gc):
        
        for label in self.label:
            
            p = self.canvas.create_pango_layout(str(label.text))
            p.set_font_description(label.fd)
            
            if label.x == -1:
                swidth = p.get_size()[0]/pango.SCALE
                x = self.get_x() + self.get_width()/2 - swidth/2
            else:
                x = self.get_x() + label.x
            
            if label.y == -1:
                sheight = p.get_size()[1]/pango.SCALE
                y = self.get_y() + self.get_height()/2 - sheight/2
            else:
                y = self.get_y() + label.y
                
            gc.set_foreground( gc.get_colormap().alloc_color(label.color) )
            
            drawable.draw_layout(gc, x, y, p)
            
    ## atribui imagens ao bloco
    #  @param imagefile     nome do arquivo que contem a imagem no canvas do bloco
    #  @param menuimagefile nome do arquivo que contem a imagem no menu do bloco
    def load_image(self, imagefile, menuimagefile):

        if os.path.exists( imagefile ) == False:
            print "aviso! imagem '"+imagefile+"' nao encontrada"
            return False

        if os.path.exists( menuimagefile ) == False:
            print "aviso! imagem '"+menuimagefile+"' nao encontrada"
            return False
        
        try:
            img = Block.dict_img[imagefile]
        except KeyError:
            
            Block.dict_img[imagefile] = [None     ,     None]
            #                             ^ colorido     ^ PB
            
            Block.dict_img[imagefile][0] = gtk.gdk.pixbuf_new_from_file(imagefile)
            
            Block.dict_img[imagefile][1] = Block.dict_img[imagefile][0].copy()
            Block.dict_img[imagefile][0].saturate_and_pixelate(Block.dict_img[imagefile][1], 1, True)
            
        try:
            menuimg = Block.dict_menu_img[menuimagefile]
        except KeyError:
            
            Block.dict_menu_img[menuimagefile] = [None]
            
            Block.dict_menu_img[menuimagefile] = gtk.gdk.pixbuf_new_from_file(menuimagefile)
            
        self.menuimg = Block.dict_menu_img[menuimagefile]
        self.drawimg = Block.dict_img[imagefile]
        
        return True

    ## Retorna a imagem do bloco
    #  @return um gtk.gdk.pixbuf com a imagem do bloco exibida no canvas
    def make_image(self):
        
        self.lock = True
        
        pos = self.position
        select = self.selected
        
        self.position = Vector( 0, 0 )
        self.selected = False
        
        newpix = self.get_image()[0].copy()
        pixmap,_ = newpix.render_pixmap_and_mask()
        gc = pixmap.new_gc()
        #gc.set_foreground( gc.get_colormap().alloc_color('white') )
        gc.set_foreground( gc.get_colormap().alloc_color(gtk.gdk.Color(32896,32896,32896)) )
        pixmap.draw_rectangle(gc, True, 0, 0, self.get_width(), self.get_height())
        pixmap.draw_pixbuf(gc, newpix, 0, 0, 0, 0)
        self.draw_label(pixmap, gc)
        newpix.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, self.get_width(), self.get_height())
        
        newpix = newpix.add_alpha( True, chr(128), chr(128), chr(128) )
        
        self.position = pos
        self.selected = select
        
        self.lock = False
        
        return newpix

    ## Retorna a largura do bloco
    #  @return inteiro com a largura        
    def get_width(self):
        return self.get_image()[0].get_width()

    ## Retorna a altura do bloco
    #  @return inteiro com a altura
    def get_height(self):
        return self.get_image()[0].get_height()

    ## Verifica se a posição p está no bloco -- bounding box
    #  @param p vetor com a posição
    #  @return   bool dizendo se está dentro
    def is_at_xy_rect(self, p):
        ok = False

        p1 = self.get_position()
        p2 = p1 + Vector( self.get_width() - 1, self.get_height() - 1)
        
        if p.x >= p1.x and p.x <= p2.x and\
        p.y >= p1.y and p.y <= p2.y:
            ok = True

        return ok

    ## Verifica se a posição p está no bloco -- pixel-perfect
    #  @param p vetor com a posição
    #  @return   bool dizendo se está dentro
    def is_at_xy_pixel(self, p): 
        if self.is_at_xy_rect(p):
            
            p1 = self.get_position()
            
            pr = p - p1
            
            return ord(self.get_image()[0].get_pixels()[(int(pr.y)*self.get_width()+int(pr.x))*4+3]) != 0
            
        else:
            return False
