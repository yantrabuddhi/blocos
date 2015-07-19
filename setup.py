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

from distutils.core import setup
import py2exe
import glob

includes = ['encodings', 'encodings.utf-8',]

files = [
    ('images',['images/arrow.png']),
    ('',['COPYING']),
    ]

dirs = ['gui',
        'images/en_US/block_images',
        'images/en_US/menu_images',
        'images/pt_BR/block_images',
        'images/pt_BR/menu_images',
        'images/es_ES/block_images',
        'images/es_ES/menu_images',
        'images/ca_ES/block_images',
        'images/ca_ES/menu_images',
        'locale/en_US/LC_MESSAGES',
        'locale/pt_BR/LC_MESSAGES',
        'locale/ca_ES/LC_MESSAGES',
        'locale/es_ES/LC_MESSAGES',
        ]

for d in dirs:
    files.append( (d, glob.glob(d+'/*')) )


setup(
    name = 'Blocos',
    description = 'Controle da gogoboard através de blocos',
    version = '0.3.2',

    windows = [
                  {
                      'script': 'Blocos.py',
                      #'icon_resources': [(1, "blocos.ico")],
                  }
              ],

    options = {
        'py2exe': {
            'packages':'encodings',
            'includes': 'cairo, pango, pangocairo, atk, gobject',
        }
    },
    
    data_files=files,
    
    py_modules=[
                   'Blocos',
                   'config',
                   'lang',
                   'blockcanvas.__init__',
                   'blockcanvas.block',
                   'blockcanvas.canvas',
                   'blockcanvas.commands',
                   'blockcanvas.config',
                   'blockcanvas.container',
                   'blockcanvas.dock',
                   'blockcanvas.geom',
                   'pyCricketLogoCompiler.__init__',
                   'pyCricketLogoCompiler.parsetab',
                   'pyCricketLogoCompiler.pyCricketLex',
                   'pyCricketLogoCompiler.Communication',
                   'pyCricketLogoCompiler.pyCricketEditor',
                   'pyCricketLogoCompiler.pyCricketYacc',
                   'pyCricketLogoCompiler/ply.yacc',
                   'pyCricketLogoCompiler/ply.lex',
               ]
)
