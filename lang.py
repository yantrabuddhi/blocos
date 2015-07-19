import os
import locale, gettext
import gobject, gtk
from gtk import glade
import config

GETTEXT_DOMAIN = 'blocos'
LOCALE_PATH    = 'locale'

if os.name == 'nt':
    # windows hack for locale setting
    lang = os.getenv('LANG')
    if lang is None:
        default_lang, default_enc = locale.getdefaultlocale()
        if default_lang:
            lang = default_lang
    if lang:
        os.environ['LANG'] = lang

for module in [glade,gettext]:
    module.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
    module.textdomain(GETTEXT_DOMAIN)

try:
    language = locale.getdefaultlocale()[0]
except:
    language = None

def choose_language():
    languagegui = glade.XML(config.glade_dir+"languages.glade")
    
    store = gtk.ListStore(gobject.TYPE_STRING)
    combo = languagegui.get_widget("cmblang")
    combo.set_model(store)
    cell = gtk.CellRendererText()
    combo.pack_start(cell, True)
    combo.add_attribute(cell, 'text', 0)

    btnok   = languagegui.get_widget("btnok")
    
    keys = [n for n in config.registered_languages.keys()]
    keys.sort()
    
    for k in keys:
        store.append([k,])
        
    def btnok_clicked(*args):
        global language
        try:
            language = config.registered_languages[combo.get_active_text()]
        except:
            language = ""
        if language:
            try:
                locale.setlocale(locale.LC_ALL, (language, "utf8"))
            except locale.Error:
                 print locale
            lang = gettext.translation(GETTEXT_DOMAIN, LOCALE_PATH,
                                       languages=[language])
            lang.install()
            langwindow.destroy()
            gtk.main_quit()
    
    btnok.connect("clicked", btnok_clicked)
    
    langwindow = languagegui.get_widget("langwindow")
    langwindow.show_all()
    gtk.main()

def auto_language():
    if not language in config.registered_languages.values():
        choose_language()
