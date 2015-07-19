#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk

import pango
import os

#from communication.Communication import Comm
from pyLogoCompiler import pyYacc
from pyLogoCompiler.Communication import GoGoComms

def message(text, dialog_type, buttons_type):
    """
    Dá uma mensagem de alerta
    """
    
    warning = gtk.MessageDialog(None, gtk.DIALOG_MODAL, dialog_type, buttons_type, text)
    response = warning.run()
    warning.destroy()

    return response   

class TextMode(object):        
    def quit(self, widget):
        self.window = None
        del self

    def __init__(self, canvas, monitor):
        self.canvas = canvas
        self.monitor = monitor
        
        #Carrega a interface a partir do arquivo glade
        self.gui = gtk.glade.XML('gui/text.glade')
        self.window = self.gui.get_widget('mainWindow')  
        
        self.filename = None
        
        self.textviewLogoProcedures = self.gui.get_widget('textviewLogoProcedures')
        self.textviewByteCodes = self.gui.get_widget('textviewByteCodes')
        self.textviewByteCodes.modify_font(pango.FontDescription('monospace').set_size(1252))

        # Buffers das caixas de texto
        self.LogoProceduresBuffer = gtk.TextBuffer()
        self.ByteCodesBuffer = gtk.TextBuffer()
        self.textviewLogoProcedures.set_buffer(self.LogoProceduresBuffer)
        self.textviewByteCodes.set_buffer(self.ByteCodesBuffer)

        self.LogoProceduresBuffer.set_modified(False)
        
        self.radiobuttonDecimal = self.gui.get_widget("radiobuttonDecimal")
        
        self.statusbar = self.gui.get_widget('statusbar')
        self.statusbar_cid = self.statusbar.get_context_id(_("Logo Procedures Editor"))
        self.reset_default_status()
        
        #Conecta Sinais aos Callbacks:        
        dic = {"gtk_main_quit" : gtk.main_quit}
        self.gui.signal_autoconnect(dic)    
        self.gui.signal_autoconnect(self)
        
        self.window.connect("destroy", self.quit)
        
        #Exibe toda interface:
        self.window.show_all() 
        
################    
    # When the window is requested to be closed, we need to check if they have 
    # unsaved work. We use this callback to prompt the user to save their work 
    # before they exit the application. From the "delete-event" signal, we can 
    # choose to effectively cancel the close based on the value we return.
    def on_mainWindow_delete_event(self, widget, event, data=None):
    
        if self.check_for_save(): self.on_save_menu_item_activate(None, None)
        return False # Propogate event
    
    # Called when the user clicks the 'New' menu. We need to prompt for save if 
    # the file has been modified, and then delete the buffer and clear the  
    # modified flag.    
    def on_new_menu_activate(self, menuitem, data=None):
    
        if self.check_for_save(): self.on_save_menu_activate(None, None)
        
        # clear editor for a new file
        buff = self.textviewLogoProcedures.get_buffer()
        buff.set_text("")
        buff.set_modified(False)
        
        self.ByteCodesBuffer.set_text("")
        
        self.filename = None
        self.reset_default_status()
    
    # Called when the user clicks the 'Open' menu. We need to prompt for save if 
    # thefile has been modified, allow the user to choose a file to open, and 
    # then call load_file() on that file.    
    def on_open_menu_activate(self, menuitem, data=None):
        
        if self.check_for_save(): self.on_save_menu_activate(None, None)
        
        filename = self.get_open_filename()
        if filename: self.load_file(filename)
       
    # Called when the user clicks the 'Save' menu. We need to allow the user to choose 
    # a file to save if it's an untitled document, and then call write_file() on that 
    # file.
    def on_save_menu_activate(self, menuitem, data=None):
        
        if self.filename == None: 
            filename = self.get_save_filename()
            if filename: self.write_file(filename)
        else: self.write_file(None)
        
    # Called when the user clicks the 'Save As' menu. We need to allow the user 
    # to choose a file to save and then call write_file() on that file.
    def on_save_as_menu_activate(self, menuitem, data=None):
        
        filename = self.get_save_filename()
        if filename: self.write_file(filename)
    
    # Called when the user clicks the 'Quit' menu. We need to prompt for save if 
    # the file has been modified and then break out of the GTK+ main loop          
    def on_quit_menu_activate(self, menuitem, data=None):

        if self.check_for_save(): self.on_save_menu_activate(None, None)
        self.window.destroy()
    
    # Called when the user clicks the 'Cut' menu.
    def on_cut_menu_activate(self, menuitem, data=None):

        buff = self.textviewLogoProcedures.get_buffer();
        buff.cut_clipboard (gtk.clipboard_get(), True);
        
    # Called when the user clicks the 'Copy' menu.    
    def on_copy_menu_activate(self, menuitem, data=None):
    
        buff = self.textviewLogoProcedures.get_buffer();
        buff.copy_clipboard (gtk.clipboard_get());
    
    # Called when the user clicks the 'Paste' menu.    
    def on_paste_menu_activate(self, menuitem, data=None):
    
        buff = self.textviewLogoProcedures.get_buffer();
        buff.paste_clipboard (gtk.clipboard_get(), None, True);
    
    # Called when the user clicks the 'Delete' menu.    
    def on_delete_menu_activate(self, menuitem, data=None):
        
        buff = self.textviewLogoProcedures.get_buffer();
        buff.delete_selection (False, True);
   

    # We call error_message() any time we want to display an error message to 
    # the user. It will both show an error dialog and log the error to the 
    # terminal window.
    def error_message(self, message):
    
        # log to terminal window
        print message
        
        # create an error message dialog and display modally to the user
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
        
        dialog.run()
        dialog.destroy()
        
    # This function will check to see if the text buffer has been
    # modified and prompt the user to save if it has been modified.
    def check_for_save (self):
    
        ret = False
        buff = self.textviewLogoProcedures.get_buffer()
        
        if buff.get_modified():

            # we need to prompt for save
            message = _("Do you want to save the changes you have made?")
            dialog = gtk.MessageDialog(self.window,
                                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, 
                                       message)
            dialog.set_title(_("Save?"))
            
            if dialog.run() == gtk.RESPONSE_NO: ret = False
            else: ret = True
            
            dialog.destroy()
        
        return ret

    def check_for_overwrite (self):
    
        ret = False
        buff = self.textviewLogoProcedures.get_buffer()
        
        if buff.get_modified():

            # we need to prompt for save
            message = _("This file already exists. Want to overwrite?")
            dialog = gtk.MessageDialog(self.window,
                                       gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, 
                                       message)
            dialog.set_title(_("Overwrite?"))
            
            if dialog.run() == gtk.RESPONSE_NO: ret = False
            else: ret = True
            
            dialog.destroy()
        
        return ret         
    
    # We call get_open_filename() when we want to get a filename to open from the
    # user. It will present the user with a file chooser dialog and return the 
    # filename or None.    
    def get_open_filename(self):
        
        filename = None
        chooser = gtk.FileChooserDialog(_("Open File..."), self.window,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.add_pattern("*."+"logo")
        filter.set_name(_("project")+" logo")
        chooser.add_filter(filter)                                         
        try:
            os.path.exists(self.filename)
            chooser.set_current_folder( os.path.dirname(self.filename) )
        except:
            home = os.getenv('USERPROFILE') or os.getenv('HOME')
            chooser.set_current_folder(home)
                                         
        response = chooser.run()
        if response == gtk.RESPONSE_OK: filename = chooser.get_filename()
        chooser.destroy()
        
        return filename
    
    # We call get_save_filename() when we want to get a filename to save from the
    # user. It will present the user with a file chooser dialog and return the 
    # filename or None.    
    def get_save_filename(self):
    
        filename = None
        chooser = gtk.FileChooserDialog(_("Save File..."), self.window,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_SAVE, gtk.RESPONSE_OK))
                                         
                                         
        filter = gtk.FileFilter()
        filter.add_pattern("*."+"logo")
        filter.set_name(_("project")+" logo")
        chooser.add_filter(filter)                                         
        try:
            os.path.exists(self.filename)
            chooser.set_current_folder( os.path.dirname(self.filename) )
        except:
            home = os.getenv('USERPROFILE') or os.getenv('HOME')
            chooser.set_current_folder(home)
           
        response = chooser.run()
        if response == gtk.RESPONSE_OK: filename = chooser.get_filename()
        chooser.destroy()
        
        if os.path.exists(filename):
            if self.check_for_overwrite():
                return filename
        else:
            if not '.' in filename:
                return filename+".logo"
            else:
                message = _("The file may not have dot")
                self.error_message(message)
                
    # We call load_file() when we have a filename and want to load it into the 
    # buffer for the GtkTextView. The previous contents are overwritten.    
    def load_file(self, filename):
    
        # add Loading message to status bar and ensure GUI is current
        self.statusbar.push(self.statusbar_cid, _("Loading %s") % filename)
        while gtk.events_pending(): gtk.main_iteration()
        
        try:
            # get the file contents
            fin = open(filename, "r")
            text = fin.read()
            fin.close()
            
            # disable the text view while loading the buffer with the text
            self.textviewLogoProcedures.set_sensitive(False)
            buff = self.textviewLogoProcedures.get_buffer()
            buff.set_text(text)
            buff.set_modified(False)
            self.textviewLogoProcedures.set_sensitive(True)
            
            # now we can set the current filename since loading was a success
            self.filename = filename
            
        except:
            # error loading file, show message to user
            self.error_message (_("Could not open file: %s") % filename)
            
        # clear loading status and restore default 
        self.statusbar.pop(self.statusbar_cid)
        self.reset_default_status()

    def write_file(self, filename):
    
        # add Saving message to status bar and ensure GUI is current
        if filename: 
            self.statusbar.push(self.statusbar_cid, _("Saving %s") % filename)
        else:
            self.statusbar.push(self.statusbar_cid, _("Saving %s") % self.filename)
            
        while gtk.events_pending(): gtk.main_iteration()
        
        try:
            # disable text view while getting contents of buffer
            buff = self.textviewLogoProcedures.get_buffer()
            self.textviewLogoProcedures.set_sensitive(False)
            text = buff.get_text(buff.get_start_iter(), buff.get_end_iter())
            self.textviewLogoProcedures.set_sensitive(True)
            buff.set_modified(False)
            
            # set the contents of the file to the text from the buffer
            if filename: fout = open(filename, "w")
            else: fout = open(self.filename, "w")
            fout.write(text)
            fout.close()
            
            if filename: self.filename = filename

        except:
            # error writing file, show message to user
            self.error_message (_("Could not save file: %s") % filename)
        
        # clear saving status and restore default     
        self.statusbar.pop(self.statusbar_cid)
        self.reset_default_status()
        
    def reset_default_status(self):        
        if self.filename:
            status = _("File: %s") % os.path.basename(self.filename)
        else:
            status = _("File:")+"(UNTITLED)"
        
        self.statusbar.pop(self.statusbar_cid)
        self.statusbar.push(self.statusbar_cid, status)
        
##############     
    def button_get_from_blocks_clicked_cb(self, widget):
        if self.LogoProceduresBuffer.get_char_count() > 1:
            if message(_("The procedures will be overwritten, are you sure you want to proceed?"), gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO) == gtk.RESPONSE_YES:
                self.LogoProceduresBuffer.set_text(self.canvas.get_code())
        else:
            self.LogoProceduresBuffer.set_text(self.canvas.get_code())
            
    def button_compile_clicked_cb(self, widget):
        from pyLogoCompiler.Communication import GoGoComms
        
        if self.monitor:
            self.GoGo = self.monitor.GoGo
        else:
            self.GoGo = GoGoComms()
        
        text = self.LogoProceduresBuffer.get_text(self.LogoProceduresBuffer.get_start_iter(),self.LogoProceduresBuffer.get_end_iter())
        result, ERCP = self.GoGo.compile(text)

        if result:
            byteCodes = self.GoGo.returnByteCode()
            
            if self.radiobuttonDecimal.get_active():
                self.ByteCodesBuffer.set_text(str(byteCodes))
            else:
                temp = []
                for  x in byteCodes:
                    temp.append(hex(x))
                self.ByteCodesBuffer.set_text(str(temp).upper().replace('X', 'x'))
        else:
            text = "ERROR->Look for a text containing one of the words: "+ERCP[0]
            message(_(text), gtk.MESSAGE_WARNING, gtk.BUTTONS_OK)
        return result
        
    def button_download_clicked_cb(self, widget):
        if self.button_compile_clicked_cb(widget):
            if not self.monitor:
                self.GoGo.autoConnect()
            
            self.GoGo.download()
            
            if not self.monitor:
                self.GoGo.closePort()