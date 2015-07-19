
#!/usr/bin/env python
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

# Centro de Tecnologia da Informação Renato Archer, Campinas-SP, Brasil
# Autor: Victor Matheus de Araujo Oliveira
# email: victormatheus@gmail.com
# data:  10/03/2009
# Projeto realizado com fundos do Conselho Nacional de Desenvolvimento Científico e Tecnológico (CNPQ)

# Esse código faz parte do projeto BR-Gogo, disponível em http://sourceforge.net/projects/br-gogo/
 
NAME="Blocos"
VERSION="0.3.2"
AUTHORS="""Main developer:
    Victor Matheus de Araujo Oliveira (victormatheus@gmail.com)

Br-Gogo Project:
    Josué Jr. Guimarães Ramos (josue.ramos@cti.gov.br)
    Felipe Augusto Silva (fel1310@gmail.com)
    Lucas Aníbal Tanure Alves (ltanure@gmail.com)
""",

import sys
import os

import serial
import cairo
import gobject

import gtk
from gtk import glade
import gettext
import locale

#Blocos files
import config
import lang

# register the gettext function for the whole interpreter as "_"
import __builtin__
__builtin__._ = gettext.gettext

import blockcanvas.commands  
#from communication.Communication import Comm
from blockcanvas.geom import *
import blockcanvas.block as block
from blockcanvas.commands import *
from blockcanvas.canvas import *
#from communication.Exceptions import *

def warning_message(text):
    """
    Dá uma mensagem de alerta
    """
    
    warning = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, text)
    response = warning.run()
    warning.destroy()

    return response   
    
class Main( object ):
    """
    Classe principal
    """

    def __init__(self):
        
        #----------------
        #atributos
        #----------------
        
        self.maxblockwidth = 0    # Tamanho horizontal do bloco mais largo
        self.project = None        # Nome do projeto atual aberto
        self.menu = {}            # Contém os tipos de blocos
        self.monitor = None
        self.textmode = None
        self.codegui = None
        
        self.load_widgets()
        
        self.generate_blocklist()
        
        self.get_lastproject()
        
        #Conecta Sinais aos Callbacks:        
        dic = {"gtk_main_quit" : self.quit}
        self.maingui.signal_autoconnect(dic)
        self.mainwindow.connect("delete-event", self.close)
        
    def quit_by_menu(self,widget):
        val=self.close(self,widget)
        if not val :
            self.quit(self)
        
    def close(self,widget,event = None):
    
        def showdialog(text, type):      
            dialog = gtk.MessageDialog(None, gtk.DIALOG_NO_SEPARATOR, type, gtk.BUTTONS_NONE, text)
            button_ok = dialog.add_button("OK",gtk.RESPONSE_OK)
            button_save = dialog.add_button("Save",gtk.RESPONSE_YES)
            button_cancel = dialog.add_button("Cancel",gtk.RESPONSE_CLOSE)
            
            value = dialog.run()
            dialog.hide()
            return value
        
        if not self.canvas.is_saved():   #o metodo is_saved() mostra se houve alguma alteração no programa.
            text = _("There are unsaved alterations in your project, press OK to close without saving, Save to save and close, or Cancel.")
            response = showdialog(text, gtk.DIALOG_DESTROY_WITH_PARENT)
            
            if response == gtk.RESPONSE_OK:
                return False
            elif response == gtk.RESPONSE_CLOSE:
                return True
            elif response == gtk.RESPONSE_YES:
                self.save_proj(self)
                return False
            
                    
    def quit(self, widget):
        """
        Sai do programa
        """

        gtk.main_quit()
        #salva o projeto atual para
        #abrir na próxima execução
        f = open("user.dat","w")
        f.write(self.project)
        f.close()

    def get_lastproject(self):
        """
        lê qual foi o último projeto e abre
        """
        
        try:
            if os.path.exists("user.dat"):
                f = open("user.dat","r+")
            else:
                f = open("user.dat","w+")
        except:
            self.set_project("")
            return
            
        projectfile = f.read()
        
        print projectfile
        
        if os.path.exists(projectfile):
            
            self.canvas.load_proj(projectfile)
            
            self.set_project(projectfile)
        
        else:

            self.set_project("")
                
        f.close()

    def set_project(self, name):

        self.project = name
        
        if self.project != "":
            self.mainwindow.set_title(self.project+" - "+NAME)
        else:
            self.mainwindow.set_title(_("<no title project>")+" - "+NAME)

    def hide_generatedCode(self, widget):
        self.wincode.destroy()
        self.codegui = None

    def show_generatedCode(self, widget):
        
        """
        mostra uma janela com o código gerado pelos blocos
        """

        if self.codegui:
            self.wincode.present()
        else:
            self.codegui = gtk.glade.XML(config.glade_dir+"code.glade" )
            self.wincode = self.codegui.get_widget("winCode")
            exitbutton = self.codegui.get_widget("btnExit")
            exitbutton.connect("clicked", self.hide_generatedCode)
            txtcode = self.codegui.get_widget("txtCode")        
            
            self.wincode.set_title(_("Code"))
            
            txtbuffer = gtk.TextBuffer()
            txtbuffer.set_text(self.canvas.get_code())
            
            txtcode.set_buffer(txtbuffer)

            self.wincode.show_all()
    
    def close_monitor(self, widget):
        self.monitor = None
        if self.textmode:
            self.textmode.monitor = None
        
    def show_monitor(self, widget):
        from monitor import BoardMonitor
        if self.monitor:
            self.monitor.window.present()
        else:
            self.monitor = BoardMonitor()
            if self.monitor.window:
                self.monitor.window.connect("destroy", self.close_monitor)
            else:
                self.monitor = None
                
            if self.textmode:
                self.textmode.monitor = self.monitor

    def close_textmode(self, widget):
        self.textmode = None
        
    def show_textmode(self, widget):
        if self.textmode:
            self.textmode.window.present()
        else:
            from textmode import TextMode
            self.textmode = TextMode(self.canvas, self.monitor)
            if self.textmode.window:
                self.textmode.window.connect("destroy", self.close_textmode)
            else:
                self.textmode = None
    
    def about(self, *args):
        """
        Mostra uma janela com informações sobre o programa
        """
        
        aboutgui = gtk.AboutDialog()        
        aboutgui.set_name(NAME)
        aboutgui.set_version(VERSION)
        #aboutgui.set_copyright(copyright)
        #aboutgui.set_comments(comments)
        #aboutgui.set_license(license)
        #aboutgui.set_wrap_license(license)
        #aboutgui.set_website(website)
        #aboutgui.set_website_label(website_label)
        aboutgui.set_authors(AUTHORS)
        #aboutgui.set_documenters(documenters)
        #aboutgui.set_artists(artists)
        #aboutgui.set_translator_credits(translator_credits)    
        aboutgui.set_logo(gtk.gdk.pixbuf_new_from_file("gui/splash.png"))
        #aboutgui.set_logo(self.gui.get_widget('imageMonitor').get_pixbuf())
        #aboutgui.set_logo_icon_name(icon_name)        
        aboutgui.run()
        aboutgui.destroy()

    def help(self, *args):
        import webbrowser
        webbrowser.open('http://br-gogo.sourceforge.net/')

    def load_widgets(self):
        
        def undo(*args):
            self.canvas.undo()
        
        """
        Carrega e configura a maioria dos widgets do programa
        """
        
        #janela principal
        self.maingui = gtk.glade.XML(config.glade_dir+"main.glade" )
        self.mainwindow = self.maingui.get_widget( "mainwindow" )
        self.mainwindow.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.mainwindow.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.mainwindow.connect("destroy", self.quit)
        self.maingui.get_widget( "statusbarVersion" ).push(0,_("Version")+' '+VERSION)
        #self.mainwindow.maximize()
        
        #labels das tabs de seleção de blocos
        label = [None]*8
        label[0] = self.maingui.get_widget( "lblControl"   )
        label[1] = self.maingui.get_widget( "lblFlow"      )
        label[2] = self.maingui.get_widget( "lblCondition" )
        label[3] = self.maingui.get_widget( "lblNumbers"   )
        label[4] = self.maingui.get_widget( "lblTime"      )
        label[5] = self.maingui.get_widget( "lblOthers"    )
        label[6] = self.maingui.get_widget( "lblProcedure" )
        label[7] = self.maingui.get_widget( "lblDisp" )
        
        map(lambda lbl: lbl.modify_font(pango.FontDescription("sans 13")), label)
        
        #em cada tab existe uma tree com seus respectivos blocos
        self.tree    = [None]*8
        self.tree[0] = self.maingui.get_widget("treecontrol")
        self.tree[1] = self.maingui.get_widget("treecond")
        self.tree[2] = self.maingui.get_widget("treeflow")
        self.tree[3] = self.maingui.get_widget("treenumbers")
        self.tree[4] = self.maingui.get_widget("treetime")
        self.tree[5] = self.maingui.get_widget("treeothers")
        self.tree[6] = self.maingui.get_widget("treeproc")
        self.tree[7] = self.maingui.get_widget("treedisp")
        
        #cria a treelist e a treefilter associada a cada tree
        self.treeList   = [None]*8
        self.treeList   = map( lambda i: gtk.TreeStore(gtk.gdk.Pixbuf), self.treeList )
        self.treeFilter = [None]*8
        self.treeFilter = map( lambda list: list.filter_new(), self.treeList )
        
        for i in xrange( len(self.tree) ):
            self.tree[i].set_model( self.treeFilter[i] )
            self.tree[i].get_selection().set_mode(gtk.SELECTION_SINGLE)
            
            column = gtk.TreeViewColumn(_("Tools"), gtk.CellRendererPixbuf() , pixbuf=0)
            self.tree[i].append_column(column)
            
            self.tree[i].connect("cursor-changed", self.treeblock_select, self.treeList[i] )
        
        self.downbutton = self.maingui.get_widget("downloadbutton")
        self.downbutton.connect("clicked", self.download)        
        
        #Nesse box serão colocadas as propriedades dos blocos
        self.PropBox = self.maingui.get_widget("BoxProperties")
        
        self.scrollCanvas = self.maingui.get_widget("scrollCanvas")
        self.canvas = Canvas(self.PropBox)
        self.scrollCanvas.add(self.canvas)
        
        self.menu_new = self.maingui.get_widget("menu_new")
        self.menu_new.connect("activate", self.new_proj)
        self.button_new = self.maingui.get_widget("button_new")
        self.button_new.connect("clicked", self.new_proj)
        
        self.menu_quit = self.maingui.get_widget("menu_quit")
        self.menu_quit.connect("activate", self.quit_by_menu)
        
        self.menu_save = self.maingui.get_widget("menu_save")
        self.menu_save.connect("activate", self.save_proj)
        self.button_save = self.maingui.get_widget("button_save")
        self.button_save.connect("clicked", self.save_proj)
        
        self.menu_saveas = self.maingui.get_widget("menu_saveas")
        self.menu_saveas.connect("activate", self.saveas_proj)
        
        self.menu_load = self.maingui.get_widget("menu_load")
        self.menu_load.connect("activate", self.load_proj)
        self.button_load = self.maingui.get_widget("button_load")
        self.button_load.connect("clicked", self.load_proj)
        
        self.menu_code = self.maingui.get_widget("menu_code")
        self.menu_code.connect("activate", self.show_generatedCode)
        self.button_code = self.maingui.get_widget("button_code")
        self.button_code.connect("clicked", self.show_generatedCode)
        
        self.menu_monitor = self.maingui.get_widget("menu_monitor")
        self.menu_monitor.connect("activate", self.show_monitor)
        self.button_monitor = self.maingui.get_widget("button_monitor")
        self.button_monitor.connect("clicked", self.show_monitor)        

        self.button_textmode = self.maingui.get_widget("button_textmode")
        self.button_textmode.connect("clicked", self.show_textmode) 
        
        self.menu_cut = self.maingui.get_widget("menu_cut")
        self.menu_cut.connect("activate", self.cut)
        
        self.menu_copy = self.maingui.get_widget("menu_copy")
        self.menu_copy.connect("activate", self.copy)
        
        self.menu_paste = self.maingui.get_widget("menu_paste")
        self.menu_paste.connect("activate", self.paste)
        
        self.menu_clear = self.maingui.get_widget("menu_clear")
        self.menu_clear.connect("activate", self.clear)
        
        self.menu_about = self.maingui.get_widget("menu_about")
        self.menu_about.connect("activate", self.about)
        
        self.menu_about = self.maingui.get_widget("menu_help")
        self.menu_about.connect("activate", self.help)

        self.menu_undo = self.maingui.get_widget("menu_undo")
        self.menu_undo.connect("activate", undo)
        
        self.mainwindow.show_all()
        
        self.movebar1 = self.maingui.get_widget("movebar1")
        self.movebar2 = self.maingui.get_widget("movebar2")
        

    def download(self, widget):
        
        """
        Envia o código gerado para a gogoBoard
        """
        
        from pyLogoCompiler import pyYacc
        from pyLogoCompiler.Communication import GoGoComms
 
        def showdialog(text, type):
           dialog = gtk.MessageDialog(None, gtk.DIALOG_NO_SEPARATOR, type, gtk.BUTTONS_NONE, text)
           #dialog.add_button("OK",gtk.RESPONSE_CLOSE)
           dialog.show()
           #dialog.destroy()
            
        v = self.canvas.code_ok()
        if v == 0:
            if self.monitor:
                self.GoGo = self.monitor.GoGo
            else:    
                self.GoGo = GoGoComms()
                self.GoGo.autoConnect()
                
            if self.GoGo.compile(self.canvas.get_code()):
                self.GoGo.download()
                if not self.monitor:
                    self.GoGo.closePort()
            else:
                if self.GoGo.returnByteCode() == None:
                    showdialog(_("Empty program."), gtk.MESSAGE_WARNING)
                else:
                    showdialog(_("There was a problem with the connection\nVerify that the board is properly connected with your computer"), gtk.MESSAGE_ERROR)
                    self.GoGo.closePort()
                return
            showdialog(_("Code successfully sent!\nClick the 'x' above to close"),gtk.MESSAGE_INFO)
            
        elif v == 1:
           showdialog(_("Some connections are missing in selected blocks"),gtk.MESSAGE_WARNING)
           
        elif v == 2:
           showdialog(_("Set Variable block only accepts variables"),gtk.MESSAGE_WARNING)      
    
    def cut(self, *args):
        """
        Evento de recortar blocos
        """
        self.canvas.cut()

    def copy(self, *args):
        """
        Evento de copiar blocos
        """
        self.canvas.copy()

    def paste(self, *args):
        """
        Evento de colar blocos
        """
        self.canvas.paste()

    def clear(self, *args):
        """
        Apaga todos os blocos da tela
        """
        self.canvas.clear()

    def add_block_tree(self, treelist, node, block):
        """
        Adiciona um ícone de bloco em uma treeview
        """
        pixbuf = block.get_menu_image()
        
        iter = treelist.append( node, [pixbuf,] )
        
        #Assim através de onde o mouse clicou
        #e de que lista está sendo usada, temos
        #o tipo de bloco que deve ser criado
        self.menu[(treelist, iter)] = block
        
        #atualiza a máxima largura de bloco
        if block.get_width() > self.maxblockwidth:
            self.maxblockwidth = block.get_width()
        
        return iter

    def del_block_tree(self, treelist, node):
        """
        Remove um ícone de bloco em uma treeview
        """
        treelist.remove( node )
        del self.menu[(treelist,node)]

    def generate_blocklist(self):
        
        """
        Cria árvores com listas de tipos de blocos
        para criar blocos do respectivo tipo
        """
        
        #newprocedure_block precisa saber qual é a
        #sua árvore, pois ele vai adicionar um ícone
        #para cada procedimento novo
        newprocedure_block.set_tree( self.treeList[6], self.add_block_tree, self.del_block_tree )
        
        #controle
        self.add_block_tree( self.treeList[0], None, on_block() )
        self.add_block_tree( self.treeList[0], None, off_block() )
        self.add_block_tree( self.treeList[0], None, brake_block() )
        self.add_block_tree( self.treeList[0], None, thisway_block() )
        self.add_block_tree( self.treeList[0], None, thatway_block() )
        self.add_block_tree( self.treeList[0], None, reverse_block() )
        self.add_block_tree( self.treeList[0], None, onfor_block() )
        self.add_block_tree( self.treeList[0], None, setpower_block() )
        self.add_block_tree( self.treeList[0], None, setposition_block() )
        
        #fluxo
        self.add_block_tree( self.treeList[2], None, if_block() )
        self.add_block_tree( self.treeList[2], None, ifelse_block() )
        self.add_block_tree( self.treeList[2], None, loop_block() )
        self.add_block_tree( self.treeList[2], None, repeat_block() )
        self.add_block_tree( self.treeList[2], None, wait_until_block() )
        self.add_block_tree( self.treeList[2], None, stop_block() )
        self.add_block_tree( self.treeList[2], None, while_block() )
       
        #comparação
        self.add_block_tree( self.treeList[1], None, comp_block() )
        self.add_block_tree( self.treeList[1], None, and_block() )
        self.add_block_tree( self.treeList[1], None, or_block() )
        self.add_block_tree( self.treeList[1], None, xor_block() )
        self.add_block_tree( self.treeList[1], None, not_block() )
        self.add_block_tree( self.treeList[1], None, switch_block() )
        
        #números
        self.add_block_tree( self.treeList[3], None, number_block() )
        self.add_block_tree( self.treeList[3], None, random_block() )
        self.add_block_tree( self.treeList[3], None, sensor_block() )
        self.add_block_tree( self.treeList[3], None, variable_block() )
        self.add_block_tree( self.treeList[3], None, set_variable_block() )
        self.add_block_tree( self.treeList[3], None, op_add_block() )
        self.add_block_tree( self.treeList[3], None, op_sub_block() )
        self.add_block_tree( self.treeList[3], None, op_mul_block() )
        self.add_block_tree( self.treeList[3], None, op_div_block() )
        self.add_block_tree( self.treeList[3], None, op_mod_block() )
        
        #outros
        self.add_block_tree( self.treeList[5], None, beep_block() )
        self.add_block_tree( self.treeList[5], None, comm_block() )
        self.add_block_tree( self.treeList[5], None, ledon_block() )
        self.add_block_tree( self.treeList[5], None, ledoff_block() )
        self.add_block_tree( self.treeList[5], None, show_block() )
        self.add_block_tree( self.treeList[5], None, send_block() ) 
        self.add_block_tree( self.treeList[5], None, recall_block() ) 
        self.add_block_tree( self.treeList[5], None, record_block() )  
        self.add_block_tree( self.treeList[5], None, resetdp_block() )  
      
        #tempo
        self.add_block_tree( self.treeList[4], None, time_block() )        
        self.add_block_tree( self.treeList[4], None, wait_block() )
        self.add_block_tree( self.treeList[4], None, resett_block() )
        self.add_block_tree( self.treeList[4], None, timer_block() )
        
        #procedimentos
        self.add_block_tree( self.treeList[6], None, newprocedure_block() )
        self.add_block_tree( self.treeList[6], None, endprocedure_block() )
        
        #disposicao
        self.add_block_tree( self.treeList[7], None, null_block() )
        self.add_block_tree( self.treeList[7], None, null2_block() )
        self.add_block_tree( self.treeList[7], None, null3_block() )
        
        #Posiciona as barras de acordo com o maior largura de bloco
        self.movebar1.set_position(self.maxblockwidth+100)
        self.movebar2.set_position(gtk.gdk.screen_width()*1/3-self.maxblockwidth+100)
        #self.canvas.set_size_request( gtk.gdk.screen_width()*2/3 - (self.maxblockwidth+100), 0 )

    def treeblock_select(self, tree, treelist):
        
        """
        Verifica qual é o tipo de bloco clicado na árvore
        e faz o canvas pedir a posição para a criação
        """
        (model, _iter) = tree.get_selection().get_selected()
        if _iter == None: return
        p = model.get_string_from_iter(_iter)        
        
        self.canvas.grab_focus()
        
        #descobre o tipo do bloco
        #através do caminho e da árvore
        for (t, it) in self.menu.keys():
            if t == treelist and p == t.get_string_from_iter(it):
                
                self.canvas.set_create_block( self.menu[ (t, it) ] )
                
                cursor = gtk.gdk.Cursor(gtk.gdk.display_get_default(), gtk.gdk.CROSS)
                self.mainwindow.window.set_cursor( cursor )
                break

    def new_proj(self, widget):
        
        """
        Tela para o usuário criar
        um novo projeto
        """
        
        dialog = gtk.FileChooserDialog("", None,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_NEW, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        proj = self.do_dialog(dialog)
        if proj and ((os.path.exists(proj) and warning_message(_("File %s will be overwritten, are you sure you want to proceed?") % proj) == gtk.RESPONSE_OK) or not os.path.exists(proj)):
           self.canvas.restart()
           self.canvas.save_proj( proj )
           self.set_project( proj )
                    
    def save_proj(self, widget):
        
        """
        Se o projeto nunca tiver sido salvo,
        pergunta onde salva, senão, salva em
        cima da versão antiga
        """
        
        if self.project == "":
            self.saveas_proj(None)
        else:
            self.canvas.save_proj(self.project)
            
    def saveas_proj(self, widget):
        
        """
        Tela para o usuário salvar
        o projeto em uso
        """
        
        dialog = gtk.FileChooserDialog(_("Save..."), None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        proj = self.do_dialog(dialog)
        
        if proj and ((os.path.exists(proj) and warning_message(_("File %s will be overwritten, are you sure you want to proceed?") % proj) == gtk.RESPONSE_OK) or not os.path.exists(proj)):
           self.canvas.save_proj( proj )
           self.set_project( proj )

    def load_proj(self, widget):
        
        """
        Tela para o usuário carregar
        um novo projeto e fechar o que
        estiver em uso
        """
        
        dialog = gtk.FileChooserDialog(_("Open..."), None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        proj = self.do_dialog(dialog)
        
        if os.path.exists(proj):
            self.canvas.load_proj(proj)
            self.set_project(proj)

    def do_dialog(self, dialog):
        
        """
        Abre uma tela de seleção
        de arquivo
        """
        
        result = ""
        filter = gtk.FileFilter()
        filter.add_pattern("*."+config.EXT)
        filter.set_name(_("project")+" "+config.EXT)
        dialog.add_filter(filter)
        
        if os.path.exists(self.project):
           dialog.set_current_folder( os.path.dirname(self.project) )
        else:
           home = os.getenv('USERPROFILE') or os.getenv('HOME')
           dialog.set_current_folder(home)
           
        response = dialog.run()
        if response == gtk.RESPONSE_OK: 
            result = dialog.get_filename()
            if result and os.path.splitext(result)[1] == "":
               result+="."+config.EXT 
        else:
            result = ""
        
        dialog.destroy()
        
        return result

  
if __name__ == "__main__":   
    import sys
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port",
                      help="define usb/serial port for",
                      metavar="PORT")
    parser.add_option("-l", "--choose_language", action="store_true",
                      dest="lang", default=False, help="show 'choose language  dialog")
    (options, args) = parser.parse_args()

    auto_lang = not options.lang
    
    if auto_lang:
        #system default language isn't supported
        lang.auto_language()
    else:
        lang.choose_language()

    blockcanvas.commands.menu_gfx   = "images/"+lang.language+"/menu_images/"
    blockcanvas.commands.block_gfx  = "images/"+lang.language+"/block_images/"
    blockcanvas.commands.glade_dir  = config.glade_dir

    Main()
    gtk.main()

