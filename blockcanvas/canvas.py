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

import gtk, gtk.glade
import block
import container
import os
import string
import tempfile

from geom import *
from commands import *
from config import *


## verifica se 2 pixbufs estao colidindo
#  @param x1 posição x de pix1
#  @param y1 posição y de pix1
#  @param pix1 gtk.gdk.Pixbuf
#  @param x2 posição x de pix2
#  @param y2 posição y de pix2
#  @param pix2 gtk.gdk.Pixbuf
#  @return   bool dizendo se estão colidindo
def collide_pixbuf(x1, y1, pix1, x2, y2, pix2):
    p1 = Vector(x1, y1)
    p2 = Vector(x2, y2)
    
    p3 = p1 + Vector( pix1.get_width(), pix1.get_height() )
    p4 = p2 + Vector( pix2.get_width(), pix2.get_height() ) 
    
    img1 = pix1.get_pixels()
    img2 = pix2.get_pixels()
    
    c1 = Vector( max(p1.x, p2.x), max(p1.y, p2.y) )
    c2 = Vector( min(p3.x, p4.x), min(p3.y, p4.y) )
    
    (w, h) = (c2.x - c1.x, c2.y - c1.y)
    
    r1 = c1 - p1
    r2 = c1 - p2
    
    collide = False
    
    y = 0
    x = 0
    
    while( y < h and collide == False ):
        x = 0
        while( x < w and collide == False ):
            if ord(img1[((y+int( r1.y ))*pix1.get_width()+(x+int( r1.x )))*4+3]) != 0\
            and ord(img2[((y+int( r2.y ))*pix2.get_width()+(x+int( r2.x )))*4+3]) != 0:
                collide = True
            x = x+1
        y = y+1
            
    return collide

class Canvas( container.Block_container, gtk.Layout ):

    """Classe que implementa um container de blocos em um gtk.Layout"""

    def __init__(self, prop_box):
        container.Block_container.__init__(self)
        
        gtk.Layout.__init__(self, None, None)
        
        self.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)
        self.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        self.set_flags(gtk.CAN_FOCUS)
        
        self.connect("motion_notify_event",  self.on_motion_notify)
        self.connect("leave_notify_event",   self.on_leave_notify)
        self.connect("enter_notify_event",   self.on_enter_notify)        
        self.connect("button_press_event",   self.on_button_press)
        self.connect("button_release_event", self.on_button_release)
        self.connect("expose-event",         self.on_expose)
        self.connect("key-press-event",      self.on_key_press)
        
        #Scrollbars
        self.get_hadjustment().connect("value-changed", self.scrollscreen)
        self.get_vadjustment().connect("value-changed", self.scrollscreen)
        
        self.change_stack  = []
        self.undo_flag = False
        
        self.clicked       = None   # Flag que serve para indicar se o mouse
                                    #  está dentro do canvas
        
        self.create_block  = None   # Tipo do bloco que deve ser criado,
                                    #  se for None, não está no modo de criação
                                    #  de novo bloco
                                    
                                    
        self.last_saved     = ""    # Ultimo arquivo salvado, para comparar se o programa foi
                                    #  alterado antes de fechar
        
        self.first_expose  = False  # já fui mostrado?
        
        self.prop_box = prop_box    # Nesse gtk.Box aparecerão as propriedades
                                    # do bloco selecionado
        
        self.drawable     = None    # gtk.gdk.Drawable
        self.gc           = None    # gtk.gdk.GC
        self.cm           = None    # gtk.gdk.Colormap
        self.bg           = None    # background color
        
        self.startblock   = None    # aponta para o start block
        
        self.mousex = -1            # Posição X do mouse no canvas... -1 -> fora do canvas
        self.mousey = -1            # Posição Y do mouse no canvas... -1 -> fora do canvas
        
        self.selectrect_on = False  # Se o retângulo de seleção está ativado
        self.selectrect_p1 = None   # ponto mais a esquerda do retangulo de seleção
        self.selectrect_p2 = None   # ponto mais a direita do retangulo de seleção
        self.selectrect    = None   # retangulo de seleção [geometric.Rect]
        
        #pixbuf da seta que acompanha o bloco selecionado
        self.arrow = gtk.gdk.pixbuf_new_from_file('images/arrow.png')
    
    ## Mostra a barra de propriedades de
    #  um bloco que foi clicado
    #  @param block bloco clicado
    def set_clicked(self, block):
        if self.clicked is not None:
            self.arrow_mark_dirty()
            self.clicked.hide_gui()
        self.clicked = block
        if self.clicked is not None:
            self.arrow_mark_dirty()
            self.clicked.show_gui(self.prop_box)
    
    ## Salva o estado atual do canvas em uma pilha
    #  para fazer o undo
    def change_done(self):
        
        if self.undo_flag == True:
            return
        
        k = tempfile.TemporaryFile('w+', 0)
        
        if len(self.change_stack) > 10:
            k = self.change_stack.pop(0)
        
        self.change_stack.append( k )
        self.save( k )
        
        k.flush()
        k.seek(0)

    ## Retorna o último estado salvo na pilha de undo
    def get_last_state(self):
        return self.change_stack[-1]
    
    ## Coloca no canvas o último estado salvo na pilha
    def undo(self):
        
        try:
            k = self.change_stack.pop()
        except IndexError:
            return
        
        self.undo_flag = True
        self.load( k )
        k.close()
        self.undo_flag = False        
        
        self.load_update()
    
    ## limpa o canvas
    def clear(self):
        self.change_done()
        container.Block_container.clear(self)
        self.first_expose = False
        self.set_clicked(None)
        
    def remove_selected(self):
        self.change_done()
        
        if self.clicked in self.get_selected():
            self.set_clicked(None)
        
        container.Block_container.remove_selected(self)
        self.set_adjustment()
    
    def load(self, file):
        container.Block_container.load(self, file)
        self.set_adjustment()

    def paste(self):
        self.change_done()
        container.Block_container.paste(self)
        self.set_adjustment()

    def get_drawable(self):
        return self.drawable

    def get_gc(self):
        return self.gc

    ## Ajusta as scrollbars para os blocos no canvas
    def set_adjustment(self):
        
        maxx = 0
        maxy = 0
        
        # max value of the scrolls should be the block more distant + 50 in x and y
        for block in self.get_children():
            
            if block.get_x()+block.get_width() > maxx:
                maxx = block.get_x()+block.get_width()
                
            if block.get_y()+block.get_height() > maxy:
                maxy = block.get_y()+block.get_height()
                
        self.get_hadjustment().set_all(self.get_hadjustment().value, 0, maxx+50, 1)
        self.get_vadjustment().set_all(self.get_vadjustment().value, 0, maxy+50, 1)

        # resize canvas
        self.set_size(maxx+10, maxy+10)

    def scrollscreen(self, adjustment):
        self.on_expose(None, None)

    ## Verifica se tudo está bem para mandar o código para a placa
    def code_ok(self):
        
        self.unselect( self.get_children() )
        
        l = []
        ans = True
        
        ans, b = container.Block_container.dock_ok(self, self.startblock)
        l.append(b)

        if ans == True:
            for npblock in newprocedure_block.get_list():
                ans, b = container.Block_container.dock_ok(self, npblock)
                l.append(b)
                if ans == False:
                    break
            
        if ans == False:
            self.unselect( self.get_children() )
            for missing_connections_blocks in l:
                self.select( missing_connections_blocks )
            return 1            
        
        for block in self.get_children():
            if type(block) == set_variable_block and \
            not block.dock_parent.get_enabled():
                if block.get_variable() == "":
                    self.unselect( self.get_children() )
                    self.select( [block,] )
                    return 2
                
        return 0

    ## Retorna o código gerado pelos blocos
    #  @return string com o código
    def get_code(self):
        
        txt=""
        
        #lista com todos os nomes de variáveis
        #for var in variable_block.get_names():
        #    txt+= "global "+var+"\n"
        
        txt += self.code(self.startblock)+'\n'
        for npblock in newprocedure_block.get_list():
            txt += self.code(npblock) + '\n'

        # indentar código
        s=[]
        indent_level=0
        for i in txt:
            if i=='[':
                indent_level+=1
            if i==']':
                indent_level-=1
                s=s[:-1]
            s.append(i)
            
            if i=='\n':
                s+=['\t']*indent_level
        
        return string.join(s,'')
        
    ## marca a seta como posição suja
    def arrow_mark_dirty(self):
        if self.clicked:
            self.get_drawable().invalidate_rect(gtk.gdk.Rectangle( self.clicked.get_x()-self.arrow.get_width(), self.clicked.get_y(), self.arrow.get_width(), self.clicked.get_height()), False)

    ## marca o retângulo de seleção como sujo
    def selectrect_mark_dirty(self):
        self.get_drawable().invalidate_rect(gtk.gdk.Rectangle( self.selectrect.x-2, self.selectrect.y-2, self.selectrect.w+4, self.selectrect.h+4 ), False )

    ## marca a imagem flutuante de novo bloco como suja
    def create_block_mark_dirty(self):
        self.get_drawable().invalidate_rect(gtk.gdk.Rectangle( self.mousex, self.mousey, self.create_block.get_width(), self.create_block.get_height() ), False )

    def on_button_press(self, widget, event):
        
        self.grab_focus()
        
        if self.create_block is None:
            
            block = self.find( Vector(event.x, event.y) )
            if block == None:
                self.unselect( self.get_children() )
                
                self.set_clicked(None)
                
                self.selectrect_on = True
                self.selectrect_p1 = Vector(self.mousex, self.mousey)
                self.selectrect = Rect(0, 0, 1 , 1)
                
                return True
            else:
                
                self.set_clicked(block)
                
                block.bpress( Vector(event.x, event.y), event.type == gtk.gdk._2BUTTON_PRESS )
                
                self.get_toplevel().window.set_cursor( gtk.gdk.Cursor(gtk.gdk.FLEUR) )

        else:
            self.change_done()
            # criar novo bloco
            newblock = self.create_block.copy()
            newblock.put(self, event.x, event.y)
            
            self.set_clicked(newblock)
            
            self.create_block = None
            
            self.get_toplevel().window.set_cursor(None)
            
        return True

    def on_key_press(self, widget, event):
        
        keyname = gtk.gdk.keyval_name(event.keyval)
        
        if keyname in ("BackSpace", "Delete"):
            self.remove_selected()
        elif keyname == "Escape":
            print 'esc'
            #cancel create-mode
            if not self.create_block is None:
                self.create_block_mark_dirty()
                self.create_block = None
                self.get_toplevel().window.set_cursor(None)
                
            if self.selectrect_on:
                self.selectrect_mark_dirty()
                self.selectrect_on = False
        elif keyname == "r":
            self.refresh()
        elif keyname == "":
            self.undo()

    def on_button_release(self, widget, event):
        
        if self.clicked:
            self.arrow_mark_dirty()
            self.clicked.brelease( Vector(event.x, event.y) )
            self.arrow_mark_dirty()

        if self.selectrect_on == True:
            
            if self.selectrect.w > 0 and self.selectrect.h > 0:
                self.selectrect_mark_dirty()
                
                collide_pix = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, self.selectrect.w, self.selectrect.h )
                collide_pix.fill( 0x00000000 )
                collide_pix = collide_pix.add_alpha(False, chr(255), chr(255), chr(255) )
                
                group = set()
                for block in self.get_children():
                    if self.selectrect.pos_inside( block.get_position() ) or collide_pixbuf(block.get_x(), block.get_y(), block.get_image()[0], self.selectrect.x, self.selectrect.y, collide_pix):
                        group.add( block )
                
                self.unselect( self.get_children() )
                self.select( group )
                self.set_group( self.clicked )
                
            self.selectrect_on = False
            
        self.get_toplevel().window.set_cursor(None)
        self.set_adjustment()
        
    def on_motion_notify(self, widget, event):
        
        if (not self.create_block is None) and self.mouse_in:
            #refresh the moving image of the create-block
            self.create_block_mark_dirty()
        if self.selectrect_on == True:
            #refresh the selection rectangle

            self.selectrect_mark_dirty()
            p1 = self.selectrect_p1
            p2 = Vector(int(event.x), int(event.y))
            self.selectrect = Rect.create_rect_from_vector(p1, p2)
        
        self.mousex = int(event.x)
        self.mousey = int(event.y)
        
        if self.clicked:
            self.arrow_mark_dirty()
            self.clicked.drag( Vector(event.x, event.y) )
            self.arrow_mark_dirty()

    def on_enter_notify(self, widget, event):
        self.mouse_in = True

    def on_leave_notify(self, widget, event):
        self.mouse_in = False
        
        if self.create_block != None:
            self.create_block_mark_dirty()
            self.mousex = -1
            self.mousey = -1

    ## encontra o bloco inicio
    #  @return bloco início            
    def find_startblock(self):
        for block in self.get_children():
            if type(block) == start_block:
                return block

        return None

    ## Força a atualizaçao do canvas
    def refresh(self):

        if self.drawable != None:
            
            self.drawable.clear()
            
            self.startblock = self.find_startblock()
                    
            if self.startblock == None:
                print "error - start block not found!"
                
            self.on_expose(None, None)

    ## Reinicia o canvas
    def restart(self):
        self.clear()
        self.first_expose = False
        self.startblock = start_block()
        self.startblock.put(self, 10, 10)
        self.refresh()

    def on_expose(self, widget, event):
        
        if self.first_expose == False and event and widget:
            self.drawable     = event.window
            self.gc           = self.drawable.new_gc()
            self.cm           = self.gc.get_colormap()
            self.bg           = self.cm.alloc_color("#ffffff")
            
            if self.find_startblock() == None:
                self.startblock = start_block()
                self.startblock.put(self, 10, 10)
                self.set_clicked( self.startblock )
                self.change_done()
                
            self.first_expose = True
            
            self.set_adjustment()
            
        for block in self.get_children()[:]:
            if block.was_put == False:
                block.put(self, block.get_x(), block.get_y() )
            #blocos no fim da lista são desenhados na frente
            block.draw(self.drawable, self.gc)

        if self.clicked:
            #seta ao lado do bloco
            self.drawable.draw_pixbuf( self.gc, self.arrow, 0, 0, self.clicked.get_x()-self.arrow.get_width(), self.clicked.get_y()+self.clicked.get_height()/2-self.arrow.get_height()/2 )

        if not self.create_block is None:
            if self.mousex != -1 and self.mousey != -1:
                #uma imagem flutuando com uma previsão do novo bloco a ser criado
                self.drawable.draw_pixbuf( self.gc, self.create_block.get_image()[0], 0, 0, self.mousex, self.mousey )
        
        # retângulo de selecão
        if self.selectrect_on == True:
            self.gc.set_line_attributes(1, gtk.gdk.LINE_DOUBLE_DASH, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
            self.drawable.draw_rectangle( self.gc, False, self.selectrect.x, self.selectrect.y, self.selectrect.w-1, self.selectrect.h-1 )
        
        return True

    ## carrega um projeto
    #  @param projectfile arquivo com o projeto
    
    def is_saved(self):
    	k = tempfile.TemporaryFile('w+', 0)
    	
    	current_project = self.save(k)
    	
    	if current_project == self.last_saved :
             k.flush()
             k.seek(0)
             return True
    		
        k.flush()
        k.seek(0)
        return False
    	
    
    def load_proj(self, projectfile):
        
        if os.path.exists(projectfile):
            p=open(projectfile,"r")
            self.load(p)
            p.close()
            self.save_proj(projectfile)
        else:
            print "file "+projectfile+" doesn't exist!"
        
        self.load_update()
        self.change_done()
        
    ## Função executada sempre após fazer um load no canvas
    def load_update(self):        
        self.first_expose == False
        self.startblock = self.find_startblock()
        self.unselect( self.get_children() )
        self.set_clicked(None)
        
    ## salva o estado atual do canvas em um arquivo de projeto
    #  @param projectfile arquivo de projeto
    def save_proj(self, projectfile):
        f = open(projectfile,"w")
        self.last_saved =self.save(f)
        f.close()
        
    def set_create_block(self, block):
        self.create_block = block
        
        # invalid position
        self.mousex = -1
        self.mousey = -1
