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

from block import *
from dock import *
from config import *
import gobject,gtk

# Procedimento geral para criar um novo bloco:
# Herde a classe Block novo bloco
# Tenha em mente que as seguintes funções são chamadas nessa ordem:
#    * '__init__' para criar o bloco (claro :P)
#    * propriedades do bloco carregadas se necessário
#    * é atribuído um canvas ao bloco, a partir de agora operações gráficas tem efeito
#    * a função 'create' é chamada, coloque nela tudo relacionado à exibição das propriedades
#      como label e gtk.widgets que serão exibidos no canvas
#    * 'create_gui' é chamada coloque nela a configuração dos gtk.widgets da barra de propriedades
#      associada ao bloco, lembre-se que ela tem que retornar uma referência a um gtk.container
#      que tenha todos os gtk.widgets
#    * quando o bloco for apagado, 'remove' será chamada

font_type = "sans"

block_gfx = ""
menu_gfx  = ""
glade_dir = ""




class recall_block(Block):
    def __init__(self):
        global block_gfx, menu_gfx
        Block.__init__(self)
        self.set_image(block_gfx+"recall.png", menu_gfx+"recall.png")
        
        self.dock_parent = Dock( Rect(0, 0, 20, 22), C_type.NUMBER, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock( self.dock_parent )
        
        self.dock_next = Dock( Rect(77-20, 0, 20, 22), C_type.NUMBER, C_form.MASC)
        self.add_dock( self.dock_next )
        
        
        self.add_code("recall\n")
        self.add_code(self.dock_next)
        
        
        
        
class resetdp_block (Block):
    def __init__(self):
        Block.__init__(self)
        self.set_image(block_gfx+"resetdp.png",menu_gfx+"resetdp.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.add_code("resetdp ")
        self.add_code("\n")
        self.add_code(self.dock_next)        

class record_block (Block):
    def __init__(self):
        Block.__init__(self)
        self.set_image(block_gfx+"record.png",menu_gfx+"record.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 30, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)

        self.n_next    = Dock( Rect(73, 9, 40, 22),  C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n_next)
        
        self.add_code("record ")
        self.add_code(self.n_next)
        self.add_code("\n")
        self.add_code(self.dock_next)


class while_block( Block ):

    def __init__(self):
        global block_gfx, menu_gfx
        Block.__init__(self)
        self.set_image(block_gfx+"while.png", menu_gfx+"while.png")
        
        self.create_property("while", "" )

        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.dock_next   = Dock( Rect(20, 69, 30, 20),  C_type.NORMAL, C_form.MASC )
        self.while_next     = Dock( Rect(92, 30, 30, 20),  C_type.NORMAL, C_form.MASC, C_flow.TO_CHILD )
        self.cond_next   = Dock( Rect(71, 0, 20, 39),   C_type.LOGIC,  C_form.FEM, C_flow.TO_CHILD )
        
        self.add_dock( self.dock_parent )
        self.add_dock( self.dock_next )
        self.add_dock( self.while_next )
        self.add_dock( self.cond_next )

        self.add_code( "while " )
        self.add_code(self.cond_next)
        self.add_code("[\n")
        self.add_code(self.while_next)
        self.add_code("]\n")
        self.add_code(self.dock_next)




class newprocedure_block( Block ):

    lst = []

    addfunc  = None
    remfunc  = None
    treelist = None

    @staticmethod
    def set_tree(tl, addfunc, remfunc):
        newprocedure_block.treelist = tl
        newprocedure_block.addfunc  = addfunc
        newprocedure_block.remfunc  = remfunc

    @staticmethod
    def get_list():
        return newprocedure_block.lst

    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"nproc.png", menu_gfx+"nproc.png")
        
        self.create_property("procedure", "" )
        
        self.block = procedure_block()
        self.block.set_procedure( self.get_procedure() )
        
        self.label1 = label(-1, -1, self.get_procedure(), font_type, 14, 'white')        
        self.add_label(self.label1)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.add_code("to ")
        self.add_code( self.get_procedure )
        self.add_code("\n")
        self.add_code(self.dock_next)
        self.add_code("end\n")
        
    def create(self):
        self.node = newprocedure_block.addfunc( self.treelist, None, self.block )
        self.set_procedure( self.give_name() )
        newprocedure_block.lst.append( self )
    
    def remove(self):
        
        l = []
        for block in self.canvas.get_children()[:]:
            if type(block) == procedure_block:
                if block.get_procedure() == self.get_procedure():
                    self.canvas.remove( block )
                    
        if self in newprocedure_block.lst:
            newprocedure_block.lst.remove( self )
            
        newprocedure_block.remfunc( self.treelist, self.node )

    def update_menuimage(self):

        self.block.lock = True
        
        self.block.canvas = self.canvas
        
        newprocedure_block.treelist.set( self.node, 0, self.block.make_image() )
        
        self.block.canvas = None
        
        self.block.lock = False

    def get_procedure(self):
        return self.get_property('procedure')

    def set_procedure(self, name):
        
        oldname = self.get_procedure()
        
        for nproc in newprocedure_block.lst:
            if nproc != self and nproc.get_procedure() == name:
                name = self.give_name()
                
        self.set_property('procedure', name)
        self.label1.set_text( name )
        
        self.block.set_procedure( name )
        self.update_menuimage()
        
        for block in self.canvas.get_children():
            if type(block) == procedure_block:
                if block.get_procedure() == oldname:
                    block.set_procedure( name )
        
    def give_name(self):
        
        names = []
        for nproc in newprocedure_block.lst:
            if nproc != self:
                names.append( nproc.get_procedure() )
        
        if  self.get_procedure() != "" and not self.get_procedure() in names:
            return self.get_procedure()

        i = 0
        ok = False
        while ok == False:
            newname = "proc"+str(i)
            if newname in names:
                i += 1
            else:
                ok = True
        
        return newname

    def create_gui(self):
         
        gui = gtk.glade.XML(glade_dir+"procedure.glade", "container")
        c = gui.get_widget("container")
        
        self.txt = gui.get_widget("entryProc")
        
        self.txt.set_text( self.get_property("procedure") )
        
        self.txt.connect("focus-out-event", self.update)
        self.txt.connect("activate", self.update)
        
        #-------------------------
        
        self.update_menuimage()
        
        return c

    def update(self, *args):
          
        proc_name = self.txt.get_text().rstrip().split()[0]
        
        if proc_name != "":
            self.set_procedure( proc_name )
        
        self.txt.set_text( self.get_procedure() )
        
        self.update_menuimage()

class procedure_block(Block):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"proc.png", menu_gfx+"proc.png")
        
        self.label1 = label(-1, -1, '', font_type, 14, 'white')        
        self.add_label(self.label1)
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.create_property("procedure", "")
        
        self.add_code( self.get_procedure )
        self.add_code( "\n" )
        self.add_code(self.dock_next)

    def create(self):
        self.label1.set_text( self.get_property('procedure') )
        
    def set_procedure(self, name):
        self.label1.set_text( name )
        self.set_property('procedure', name)
    
    def get_procedure(self):
        return self.get_property('procedure')

class std_block(Block):
    def __init__(self, img, menuimg, code):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+img, menu_gfx+menuimg)
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.add_code(code)
        self.add_code(self.dock_next)



class null2_block(Block):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"null2.png", menu_gfx+"null2.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(91, 18, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.add_code(self.dock_next)


class null3_block(Block):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"null3.png", menu_gfx+"null3.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 81, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.add_code(self.dock_next)


class start_block(Block):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"nproc.png", menu_gfx+"nproc.png")
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.label1 = label(-1, -1, _("Start"), font_type, 14, 'white')
        self.add_label( self.label1 )
        
        self.add_code("to start\n")
        self.add_code(self.dock_next)
        self.add_code("end\n")

        self.erasable = False
        
class null_block(std_block):
    def __init__(self):
        std_block.__init__(self, "null.png", "null.png","")

class resett_block(std_block):
     def __init__(self):
        std_block.__init__(self, "resettimer.png", "resettimer.png","reset\n")

class beep_block(std_block):
     def __init__(self):
        std_block.__init__(self, "beep.png", "beep.png","beep\n")

class ledon_block(std_block):
     def __init__(self):
        std_block.__init__(self, "ledon.png", "ledon.png","ledon\n")

class ledoff_block(std_block):
     def __init__(self):
        std_block.__init__(self, "ledoff.png", "ledoff.png","ledoff\n")

class wait_block(Block):
    
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        
        self.set_image(block_gfx+"wait.png", menu_gfx+"wait.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 30, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)

        self.n_next    = Dock( Rect(73, 9, 40, 22),  C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n_next)

        self.add_code("wait ")
        self.add_code(self.n_next)
        self.add_code("\n")
        self.add_code(self.dock_next)

class motors_block(Block):

    def __init__(self, image_block, image_menu, key, code, n, label_text):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        
        self.key = key
        self.label_text = label_text
        
        self.set_image(block_gfx+image_block, menu_gfx+image_menu)
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)
        
        self.label1 = label(-1, -1, '', font_type, n, 'white')
        self.add_label(self.label1)
        
        self.motors="a"
        self.create_property("motorsid", "a")

    def create(self):
        self.label1.set_text( self.key+"-"+self.get_property("motorsid") )
        self.motors = self.get_property("motorsid")
        
    def get_motors(self):
        return self.motors
        
    def create_gui(self):
        
        gui = gtk.glade.XML(glade_dir+"motors.glade", "container")
        c = gui.get_widget("container")
        
        boxOpt = gui.get_widget("boxOpt")
        
        label = gui.get_widget("lblInfo")
        label.set_text(self.label_text)
        
        self.opt = {gui.get_widget("cbA"):'a',gui.get_widget("cbB"):'b',\
        gui.get_widget("cbC"):'c',gui.get_widget("cbD"):'d'}
        
        for m in self.opt.keys():
            if self.opt[m] in self.get_property("motorsid"):
                m.set_active(True)
                
        for m in self.opt.keys():
            m.connect("toggled",self.update)
            
        return c
    
    def update(self, opt):
        self.motors = ""
        for m in self.opt.keys():
            if m.get_active():
                self.motors+=self.opt[m]
        self.motors = list(self.motors)
        self.motors.sort()
        self.motors = "".join(self.motors)
        self.set_property("motorsid", self.motors)
        self.label1.set_text( self.key+"-"+self.motors )
        
class motors_block_(motors_block):
    def __init__(self, image_block, image_menu, key, code, n, label_text):
        motors_block.__init__(self, image_block, image_menu, key, code, n, label_text)
        self.add_code(self.get_motors)
        self.add_code(", "+code+"\n")
        self.add_code(self.dock_next)

class on_block(motors_block_):
    def __init__(self):
        motors_block_.__init__(self, "null.png", "on.png", _("ON"), "on", 8, _("Which motors should be turned on?"))

class off_block(motors_block_):
    def __init__(self):
        motors_block_.__init__(self,  "null.png",  "off.png", _("OFF"), "off", 8, _("Which motors should be turned off?"))
        
class brake_block(motors_block_):
    def __init__(self):
        motors_block_.__init__(self,  "null.png",  "brake.png", _("BRAKE"), "brake", 8, _("Which motors should be braked?"))

class thisway_block(motors_block_):
    def __init__(self):
        motors_block_.__init__(self,  "null.png",  "thisway.png", _("CW"), "thisway", 8, _("Which motors should turn clockwise?"))

class thatway_block(motors_block_):
    def __init__(self):
        motors_block_.__init__(self,  "null.png",  "thatway.png", _("antiCW"), "thatway", 8, _("Which motors should turn anticlockwise?"))

class reverse_block(motors_block_):
    def __init__(self):
        motors_block_.__init__(self,  "null.png",  "reverse.png", _("REV"), "rd", 8, _("Which motors should be reversed?"))

class motor_number_block(motors_block):
    
    def __init__(self, image_block, image_menu, key, code, n, label_text):
        motors_block.__init__(self, image_block, image_menu, key, code, n, label_text)
        self.label1.x = 3
        self.dock_next.get_rect().y=30
        self.n_next = Dock( Rect(73, 9, 40, 22),  C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n_next)
        
        self.add_code(self.get_motors)
        self.add_code(", "+code+" ")
        self.add_code(self.n_next)
        self.add_code("\n")
        self.add_code(self.dock_next)

class onfor_block(motor_number_block):
    def __init__(self):
        motor_number_block.__init__(self, "motor_number.png" , "onfor.png", _("ONfor"), "onfor", 8, _("Which motors should be turned on for a while?"))

class setpower_block(motor_number_block):
    def __init__(self):
        motor_number_block.__init__(self, "motor_number.png" , "setpower.png", _("POW"), "setpower", 8, _("Change power of which motors?"))

class setposition_block(motor_number_block):
    def __init__(self):
        motor_number_block.__init__(self, "motor_number.png" , "setsvh.png", _("POS"), "setsvh", 8, _("Change position of which motors?"))


class if_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"if.png", menu_gfx+"if.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.dock_next   = Dock( Rect(20, 69, 30, 20),  C_type.NORMAL, C_form.MASC )
        self.if_next     = Dock( Rect(92, 30, 30, 20),  C_type.NORMAL, C_form.MASC, C_flow.TO_CHILD )
        self.cond_next   = Dock( Rect(71, 0, 20, 39),   C_type.LOGIC,  C_form.FEM, C_flow.TO_CHILD )
        
        self.add_dock( self.dock_parent )
        self.add_dock( self.dock_next )
        self.add_dock( self.if_next )
        self.add_dock( self.cond_next )
        
        self.add_code("if ")
        #self.add_code(" (")
        self.add_code(self.cond_next)
        #self.add_code(") ")
        self.add_code("[\n")
        self.add_code(self.if_next)
        self.add_code("]\n")
        self.add_code(self.dock_next)




class ifelse_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"ifelse.png", menu_gfx+"ifelse.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.dock_next   = Dock( Rect(20, 69, 30, 20),  C_type.NORMAL, C_form.MASC )
        self.if_next     = Dock( Rect(92, 30, 30, 20),  C_type.NORMAL, C_form.MASC, C_flow.TO_CHILD )
        self.else_next   = Dock( Rect(174, 30, 30, 20), C_type.NORMAL, C_form.MASC, C_flow.TO_CHILD )
        self.cond_next   = Dock( Rect(71, 0, 20, 39),   C_type.LOGIC,  C_form.FEM, C_flow.TO_CHILD )
        
        self.add_dock( self.dock_parent )
        self.add_dock( self.dock_next )
        self.add_dock( self.if_next )
        self.add_dock( self.cond_next )
        self.add_dock( self.else_next )
        
        self.add_code("ifelse ")
        #self.add_code(" (")
        self.add_code(self.cond_next)
        #self.add_code(") ")
        self.add_code("[\n")
        self.add_code(self.if_next)
        self.add_code("]\n")
        self.add_code("[\n")
        self.add_code(self.else_next)
        self.add_code("]\n")
        self.add_code(self.dock_next)

class wait_until_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"waituntil.png", menu_gfx+"waituntil.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        
        self.cond_next   = Dock( Rect(72, 0, 20, 39),   C_type.LOGIC,  C_form.FEM, C_flow.TO_CHILD )
        
        self.add_dock( self.dock_parent )
        self.add_dock( self.dock_next )
        self.add_dock( self.cond_next )
        
        self.add_code("waituntil [")
        self.add_code(self.cond_next)
        self.add_code("x]") # o x será degenerado na identação
        self.add_code("\n")
        
        self.add_code(self.dock_next)


class repeat_block( Block ):
     def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"repeat.png", menu_gfx+"repeat.png")
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.dock_next   = Dock( Rect(20, 69, 30, 20),  C_type.NORMAL, C_form.MASC )

        self.n_next      = Dock( Rect(76, 9, 40, 22),  C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.case_next   = Dock( Rect(92, 30, 30, 20), C_type.NORMAL, C_form.MASC, C_flow.TO_CHILD )
        
        
        self.add_dock( self.dock_parent )
        self.add_dock( self.dock_next )
        self.add_dock( self.n_next )
        self.add_dock( self.case_next )
        
        self.add_code("repeat ")
        self.add_code(self.n_next)
        self.add_code("[\n")
        self.add_code(self.case_next)
        self.add_code("]\n")
        
        self.add_code(self.dock_next)


class loop_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"loop.png", menu_gfx+"loop.png")
        
        self.dock_parent = Dock( Rect(20, -9, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.loop_next   = Dock( Rect(92, -9, 30, 20),  C_type.NORMAL, C_form.MASC, C_flow.TO_CHILD )
        
        self.add_dock( self.dock_parent )
        self.add_dock( self.loop_next )
        
        self.add_code("loop [\n")
        self.add_code(self.loop_next)
        self.add_code("]\n")


class stop_block(Block):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+'stop.png', menu_gfx+'stop.png')
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.add_code('stop\n')

class endprocedure_block(Block):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+'endproc.png', menu_gfx+'endproc.png')
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
class comp_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"comp.png", menu_gfx+"comp.png")
        
        self.dock_parent = Dock( Rect(0, 0, 20, 39), C_type.LOGIC, C_form.MASC, C_flow.TO_PARENT )
        self.dock_next   = Dock( Rect(202-20, 0, 20, 39),  C_type.LOGIC, C_form.MASC )
        
        self.n1 = Dock( Rect(10, 8, 40, 22), C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.n2 = Dock( Rect(115, 8, 40, 22), C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )

        self.add_dock( self.dock_parent )
        self.add_dock( self.dock_next )
        self.add_dock( self.n1 )
        self.add_dock( self.n2 )
        
        V = [_("="),_("<"),_(">")]
        
        self.comp = "="
        self.label1 = label(-1, -1, _("="), font_type, 13, 'white')
        self.add_label(self.label1)
        
        self.add_code(self.dock_parent)

        self.add_code("[")
        self.add_code(self.n1)
        self.add_code(" ")
        self.add_code(self.get_comp)
        self.add_code(" ")
        self.add_code(self.n2)
        self.add_code("x]") # o x será degenerado na identação
        self.add_code(self.dock_next)
        
        self.create_property("comp", "=")

    def get_comp(self):
        return self.comp

    def create_gui(self):
        
        gui = gtk.glade.XML(glade_dir+"comp.glade", "container")
        c = gui.get_widget("container")
        
        self.opt={gui.get_widget("optE"):"=", gui.get_widget("optL"):"<",\
        gui.get_widget("optM"):">"}
        
        for m in self.opt.keys():
            m.connect("toggled",self.update)
            if self.opt[m]==self.get_property("comp"):
                m.set_active(True)
        
        return c

    def update(self, p):
        
        if not p.get_active():
            return
        self.comp=self.opt[p]
        self.set_property("comp",self.opt[p])
        self.label1.set_text(_(self.opt[p]))
        
class bool_block( Block ):
    def __init__(self, image_block, image_menu, operation):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+image_block, menu_gfx+image_menu)
        
        self.n1 = Dock( Rect(-3, 0, 20, 39), C_type.LOGIC, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.n1)
        
        self.n2 = Dock( Rect(34, 0, 20, 39), C_type.LOGIC, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n2)
        
        self.add_code(" "+operation+" ")
        self.add_code(self.n2)

class and_block( bool_block ):
    def __init__(self):
        bool_block.__init__(self, "booland.png", "booland.png", "and")
        
class or_block( bool_block ):
    def __init__(self):
        bool_block.__init__(self, "boolor.png", "boolor.png", "or")

class xor_block( bool_block ):
    def __init__(self):
        bool_block.__init__(self, "boolxor.png", "boolxor.png", "xor")

class not_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"not.png", menu_gfx+"not.png")
        
        self.n1 = Dock( Rect(0, 0, 20, 39), C_type.LOGIC, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock(self.n1)
        
        self.n2 = Dock( Rect(55, 0, 20, 39), C_type.LOGIC, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n2)
        
        self.add_code("not ")
        self.add_code(self.n2)
        self.add_code("")      

class sensor_block( Block ):
    
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"sensor.png", menu_gfx+"sensor.png")    
                
        self.dock_parent = Dock( Rect(0, 0, 20, 22), C_type.NUMBER, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock( self.dock_parent )
        
        self.dock_next = Dock( Rect(77-20, 0, 20, 22), C_type.NUMBER, C_form.MASC)
        self.add_dock( self.dock_next )
        
        self.sensor = 1

        text = _("sensor")+" "+str(self.sensor)
        
        self.label1 = label(-1, -1, '', font_type, 10, 'white')
        self.add_label(self.label1)

        self.add_code("sensor")
        self.add_code(self.get_sensor)
        self.add_code(self.dock_next)

        self.create_property("sensor_id")
        self.set_property("sensor_id", self.sensor)

    def create(self):
        self.label1.set_text( _("sensor")+" "+str( self.get_property("sensor_id") ) )

    def get_sensor(self):
        return str(self.sensor)

    def create_gui(self):
        
        global n_sensors
        
        gui = gtk.glade.XML(glade_dir+"sensor.glade", "container")
        c = gui.get_widget("container")
        
        boxOpt = gui.get_widget("boxOpt")

        self.optlist = []
        
        for i in xrange(n_sensors):
            
            sensor_i = i + 1
            
            opt = gtk.RadioButton(None, _("sensor")+" "+str(sensor_i) )
            boxOpt.pack_start(opt)
            opt.show()
            
            self.optlist.append(opt)
            
        for opt in self.optlist[1:]:
            opt.set_group(self.optlist[0])
            
        i = 0
        for opt in self.optlist:
            sensor_i = i+1
            if self.get_property("sensor_id") == sensor_i:
                opt.set_active(True)
            
            opt.connect("toggled", self.update)
            i += 1
        
        self.update(None)
        
        return c    
        
    def update(self, p):
        
        i = 0
        for opt in self.optlist:
            if opt.get_active() == True:
                sensor_i = i+1
                self.sensor = sensor_i
                self.set_property("sensor_id", self.sensor)
                text = _("sensor")+" "+str(self.sensor)
                self.label1.set_text(text)
                return
            i += 1


class switch_block( Block ):
    
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"switch.png", menu_gfx+"switch.png")    
                
        self.dock_parent = Dock( Rect(0, 0, 20, 39), C_type.LOGIC, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock( self.dock_parent )
        
        self.dock_next   = Dock( Rect(105-20, 0, 20, 39),  C_type.LOGIC, C_form.MASC )
        self.add_dock( self.dock_next )
        
        self.switch = 1

        text = _("switch")+" "+str(self.switch)
        
        self.label1 = label(-1, -1, '', font_type, 10, 'white')
        self.add_label(self.label1)

        self.add_code("switch")
        self.add_code(self.get_switch)
        self.add_code(self.dock_next)

        self.create_property("switch_id")
        self.set_property("switch_id", self.switch)

    def create(self):
        self.label1.set_text( _("switch")+" "+str( self.get_property("switch_id") ) )

    def get_switch(self):
        return str(self.switch)

    def create_gui(self):
        
        global n_sensors
        
        gui = gtk.glade.XML(glade_dir+"sensor.glade", "container")
        c = gui.get_widget("container")
        
        boxOpt = gui.get_widget("boxOpt")

        self.optlist = []
        
        for i in xrange(n_sensors):
            
            switch_i = i + 1
            
            opt = gtk.RadioButton(None, _("switch")+" "+str(switch_i) )
            boxOpt.pack_start(opt)
            opt.show()
            
            self.optlist.append(opt)
            
        for opt in self.optlist[1:]:
            opt.set_group(self.optlist[0])
            
        i = 0
        for opt in self.optlist:
            switch_i = i+1
            if self.get_property("switch_id") == switch_i:
                opt.set_active(True)
            
            opt.connect("toggled", self.update)
            i += 1
        
        self.update(None)
        
        return c    
        
    def update(self, p):
        
        i = 0
        for opt in self.optlist:
            if opt.get_active() == True:
                switch_i = i+1
                self.switch = switch_i
                self.set_property("switch_id", self.switch)
                text = _("switch")+" "+str(self.switch)
                self.label1.set_text(text)
                return
            i += 1


class timer_block( Block ):

    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"time.png", menu_gfx+"timer.png")
                
        self.dock_parent = Dock( Rect(0, 0, 20, 22), C_type.NUMBER, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock( self.dock_parent )
        
        self.dock_next = Dock( Rect(77-20, 0, 20, 22), C_type.NUMBER, C_form.MASC)
        self.add_dock( self.dock_next )
        
        self.text="timer"
        
        self.label1 = label(-1, -1, '', font_type, 10, 'white')
        self.add_label(self.label1)
               
        
        self.add_code(self.get_text)        
        self.add_code(self.dock_next)
        
        
        
    def create(self):
        self.label1.set_text(_("timer-ds"))

    def get_text(self):
        return self.text
    
    def create_gui(self):
        
        gui = gtk.glade.XML(glade_dir+"timer.glade", "container")
        c = gui.get_widget("container")
        
        boxOpt = gui.get_widget("boxOpt")
        
        self.opt1 = gtk.RadioButton(None, _("Timer in ms, max time : 1 minute"))
        self.opt2 = gtk.RadioButton(None, _("Timer in ds, max time : 100 minute"))
        boxOpt.pack_start(self.opt1)
        self.opt1.show()
        boxOpt.pack_start(self.opt2)
        self.opt2.show()
        self.opt2.set_group(self.opt1)
        
        self.opt2.set_active(True)
        
        self.opt2.connect("toggled", self.update)
        self.opt1.connect("toggled", self.update)
        
        self.update(None)
        
        
        return c    
        
    def update(self, p):
    
    
        if self.opt1.get_active() == True:
            
            self.text="timerms"
            self.label1.set_text(_("timer-ms"))
        if self.opt2.get_active() == True:
            self.text="timer"
            self.label1.set_text(_("timer-ds"))
        return
        

class num_block( Block ):
    def __init__(self, info, vmin, vmax, menuimg, blockimg):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+blockimg, menu_gfx+menuimg)
        
        self.dock_parent = Dock( Rect(0, 0, 20, 22), C_type.NUMBER, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock( self.dock_parent )
        
        self.dock_next = Dock( Rect(77-20, 0, 20, 22), C_type.NUMBER, C_form.MASC)
        self.add_dock( self.dock_next )
        
        self.label1 = label(-1, -1, '', font_type, 10, 'white')
        self.add_label(self.label1)
        
        self.label_text=info
        self.vmin = vmin
        self.vmax = vmax
        
        self.n = 0
        self.create_property("number", 0)
        
        self.add_code( self.get_number )
        self.add_code(self.dock_next)
        
    def create(self):
        self.label1.set_text( str(self.get_property('number')) )

    def create_gui(self):
        
        global vmax
        
        gui = gtk.glade.XML(glade_dir+"number.glade", "container")
        c = gui.get_widget("container")
        
        gui.get_widget("lblInfo").set_text(self.label_text)
        
        self.spin = gui.get_widget("spinNumber")
        
        self.spin.set_range(self.vmin, self.vmax)
        self.spin.set_value(self.get_property("number"))
        self.spin.connect("value-changed", self.update)
        
        self.n = self.get_property("number")
        
        return c

    def get_number(self):
        return self.n

    def update(self, p):
        self.n = int( self.spin.get_text() )
        self.label1.set_text(str(self.n))
        self.set_property("number", self.n)

class number_block( num_block ):

    def __init__(self):
        global max_value
        num_block.__init__(self, _("Insert the number"),0,max_value,"number.png","number.png")

class time_block( num_block ):

    def __init__(self):
        global max_value
        num_block.__init__(self, _("Insert time delay (tenths of second)"),0,max_value,"time.png","time.png")
        
class random_block( Block ):

    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"random.png", menu_gfx+"random.png")
                
        self.dock_parent = Dock( Rect(0, 0, 20, 22), C_type.NUMBER, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock( self.dock_parent )
        
        self.dock_next = Dock( Rect(77-20, 0, 20, 22), C_type.NUMBER, C_form.MASC)
        self.add_dock( self.dock_next )
        
        self.add_code( 'random' )
        self.add_code(self.dock_next)
        
class show_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"show.png", menu_gfx+"show.png")

        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)

        self.n_next = Dock( Rect(73, 9, 40, 22),  C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n_next)

        self.add_code('show ')
        self.add_code(self.n_next)
        self.add_code("\n")
        self.add_code(self.dock_next)

class send_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"send.png", menu_gfx+"send.png")

        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)

        self.n_next = Dock( Rect(73, 9, 40, 22),  C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n_next)

        self.add_code('send ')
        self.add_code(self.n_next)
        self.add_code("\n")
        self.add_code(self.dock_next)
        
class set_variable_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"setvar.png", menu_gfx+"setvar.png")

        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 29, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)

        self.varconn = Dock( Rect(3, 11, 40, 22), C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.varconn)
        
        self.n2 = Dock( Rect(94, 11, 40, 22), C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n2)

        self.add_code('make "')
        self.add_code(self.get_variable)
        self.add_code(" ")
        self.add_code(self.n2)
        self.add_code("\n")
        self.add_code(self.dock_next)
        
    def get_variable(self):
        if self.varconn.get_enabled() == False:
            # syntax problem: it's possible to put a number block in the place of a variable one
            if type(self.varconn.get_destiny_block()) == variable_block:
                return self.varconn.get_destiny_block().get_variable()
            else:
                return ""
        else:
            return ""
            
class variable_block( Block ):

    lst = []
    liststore=gtk.ListStore(gobject.TYPE_STRING)

    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        
        self.set_image(block_gfx+"variable.png", menu_gfx+"variable.png") 
        
        self.dock_parent = Dock( Rect(0, 0, 20, 22), C_type.NUMBER, C_form.MASC, C_flow.TO_PARENT )
        self.add_dock( self.dock_parent )
        
        self.dock_next = Dock( Rect(77-20, 0, 20, 22), C_type.NUMBER, C_form.MASC)
        self.add_dock( self.dock_next )
        
        self.label1 = label(-1, -1, "", font_type, 10, 'black')
        self.add_label(self.label1)
        
        self.create_property("variable", "")
        
        self.add_code(":")
        self.add_code(self.get_variable)
        self.add_code(self.dock_next)
        
    def give_name(self):
        
        names = []
        for var in variable_block.lst:
            if var != self:
                names.append( var.get_variable() )
        
        if self.get_variable() != "" and not self.get_variable() in names:
            return self.get_variable()
        
        i = 0
        ok = False
        while ok == False:
            newname = "var"+str(i)
            if newname in names:
                i += 1
            else:
                ok = True
        
        return newname
        
    @staticmethod
    def get_list():
        return variable_block.lst

    @staticmethod
    def get_names():

        #get the list of all variable names being used
        s = set()
        for v in variable_block.get_list():
            s.add(v.get_variable())
        return s

    @staticmethod
    def refresh_names():
        variable_block.liststore.clear()
        for var in variable_block.get_names():
            variable_block.liststore.append((var,))

    def create(self):
        
        if self.get_property("variable")=='':
            self.set_variable( self.give_name() )
        else:
            self.set_variable( self.get_property("variable") )
        
        variable_block.lst.append( self )
        
        variable_block.refresh_names()
        

    def remove(self):
        if self in variable_block.lst:
            variable_block.lst.remove( self )
        
        variable_block.refresh_names()

    def get_variable(self):
        return self.get_property("variable") 

    def create_gui(self):
         
        gui = gtk.glade.XML(glade_dir+"variable.glade", "container")
        c = gui.get_widget("container")
        
        self.txtnewvar = gui.get_widget("txtnewvar")
        
        varbox = gui.get_widget("varbox")
        self.combovar=gtk.combo_box_entry_new_text()
        self.combovar.set_model(variable_block.liststore)
        varbox.add(self.combovar)
        
        self.txtnewvar.set_text(self.get_property("variable"))
        
        self.combovar.connect("changed", self.updatecombo)
        self.txtnewvar.connect("activate", self.updatetxt)
        
        return c

    def set_variable(self, var):
        self.set_property("variable", var)
        
        self.label1.set_text(var)
        
    def updatecombo(self, *args):
          
        it = self.combovar.get_active_iter()
        
        if it != None:
            self.set_variable(variable_block.liststore.get_value(it, 0))
        #else:
        #    self.combovar.child.set_text(self.get_property("variable"))

    def updatetxt(self, *args):
        
        var_name = self.txtnewvar.get_text().rstrip().split()[0]
        
        if var_name != "":
            self.set_variable(var_name)
        else:
            self.txtnewvar.set_text(self.get_property("variable"))
            
        variable_block.refresh_names()
        
class number_operation_block( Block ):
     def __init__(self, image_block, image_menu, operation):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+image_block, menu_gfx+image_menu)
        
        self.n1 = Dock( Rect(-10, 4, 20, 22), C_type.NUMBER, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.n1)
        
        self.n2 = Dock( Rect(29, 4, 20, 22), C_type.NUMBER, C_form.FEM, C_flow.TO_CHILD )
        self.add_dock(self.n2)
        
        self.add_code(self.n1)
        self.add_code(operation)
        self.add_code(self.n2)

class op_add_block( number_operation_block ):
    def __init__(self):
        number_operation_block.__init__(self,  "opadd.png", "opadd.png", "+")

class op_sub_block( number_operation_block ):
    def __init__(self):
        number_operation_block.__init__(self,  "opsub.png", "opsub.png", "-")

class op_mul_block( number_operation_block ):
    def __init__(self):
        number_operation_block.__init__(self,  "opmul.png", "opmul.png", "*")

class op_div_block( number_operation_block ):
    def __init__(self, container = None):
        number_operation_block.__init__(self,  "opdiv.png", "opdiv.png", "/")

class op_mod_block( number_operation_block ):
    def __init__(self, container = None):
        number_operation_block.__init__(self,  "opmod.png", "opmod.png", "%")
        
class comm_block( Block ):
    def __init__(self):
        global block_gfx, menu_gfx
        
        Block.__init__(self)
        self.set_image(block_gfx+"comm.png", menu_gfx+"comm.png")   
        
        self.dock_parent = Dock( Rect(20, -10, 30, 20), C_type.NORMAL, C_form.FEM, C_flow.TO_PARENT )
        self.add_dock(self.dock_parent)
        
        self.dock_next = Dock( Rect(20, 76, 30, 20), C_type.NORMAL, C_form.MASC )
        self.add_dock(self.dock_next)

        self.textbuffer = gtk.TextBuffer()
        self.textview = gtk.TextView(self.textbuffer)
        self.textview.set_size_request(120, 65)
        self.textview.set_wrap_mode( gtk.WRAP_WORD )
        self.add_widget(self.textview, 6, 13)
        
        self.create_property("text", "")

        self.textview.get_buffer().connect("changed", self.update_text)

        self.add_code(self.dock_parent)
        self.add_code(self.dock_next)

    def create(self):
        self.textbuffer.set_text( self.get_property("text") )

    def update_text(self, *args):
        
        self.set_property("text", self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter() ) )

# Associação do tipo com uma string
Block.new_block_type("startblock"  , start_block  )
Block.new_block_type("newprocblock", newprocedure_block  )
Block.new_block_type("procblock"   , procedure_block  )
Block.new_block_type("endprocblock", endprocedure_block  )
Block.new_block_type("nullblock"   , null_block   )
Block.new_block_type("null2block"  , null2_block   )
Block.new_block_type("null3block"  , null3_block   )
Block.new_block_type("onblock"     , on_block     )
Block.new_block_type("offblock"    , off_block    )
Block.new_block_type("brakeblock"  , brake_block  )
Block.new_block_type("thiswayblock", thisway_block)
Block.new_block_type("thatwayblock", thatway_block)
Block.new_block_type("reverseblock", reverse_block)

Block.new_block_type("onforblock"   , onfor_block   )
Block.new_block_type("setpowerblock", setpower_block)
Block.new_block_type("setposition", setposition_block)

Block.new_block_type("ifblock"       , if_block        )
Block.new_block_type("ifelseblock"   , ifelse_block    )
Block.new_block_type("loopblock"     , loop_block      )
Block.new_block_type("repeatblock"   , repeat_block    )
Block.new_block_type("waituntilblock", wait_until_block)
Block.new_block_type("stopblock"     , stop_block)
Block.new_block_type("whileblock"     , while_block)

Block.new_block_type("compblock", comp_block)
Block.new_block_type("andblock" , and_block )
Block.new_block_type("orblock"  , or_block  )
Block.new_block_type("xorblock" , xor_block )
Block.new_block_type("notblock" , not_block )

Block.new_block_type("numberblock"       , number_block       )
Block.new_block_type("randomblock"       , random_block       )
Block.new_block_type("sensorblock"       , sensor_block       )
Block.new_block_type("switchblock"       , switch_block       )
Block.new_block_type("setvariableblock"  , set_variable_block )
Block.new_block_type("variableblock"     , variable_block     )

Block.new_block_type("opaddblock" , op_add_block)
Block.new_block_type("opsubblock" , op_sub_block)
Block.new_block_type("opmulblock" , op_mul_block)
Block.new_block_type("opdivblock" , op_div_block)
Block.new_block_type("opmodblock" , op_mod_block)

Block.new_block_type("beepblock" , beep_block)
Block.new_block_type("commblock" , comm_block)
Block.new_block_type("ledonblock" , ledon_block)
Block.new_block_type("ledoffblock" , ledoff_block)
Block.new_block_type("show_block" , show_block)
Block.new_block_type("send_block" , send_block)
Block.new_block_type("record_block" , record_block)
Block.new_block_type("recall_block" , recall_block)
Block.new_block_type("resetdp_block" , resetdp_block)

Block.new_block_type("timeblock"   , time_block  )
Block.new_block_type("waitblock"   , wait_block  )
Block.new_block_type("resettblock" , resett_block)
Block.new_block_type("timerblock"  , timer_block )
