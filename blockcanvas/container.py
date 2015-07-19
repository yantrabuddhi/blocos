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

from xml.dom import minidom, Node
import copy
from geom import *
import commands
from dock import *
import block
import time

class Block_container(object):

    """Esta classe contém as operações lógicas que podem ser feitas
    sobre vários blocos"""

    def __init__(self):
        
        ## Lista com todos os blocos
        self.blocks = []
        ## Blocos que serão "colados"
        self.buffer = []
        ## Blocos selecionados
        self.selected = set()
        ## Bloco que encabeça os selecionados
        self.master = None
    
    ## Retorna todos os blocos que não tem pai
    #  @return set com os blocos
    def get_top_blocks(self):
        l = set()
        for block in self.get_children():
            t = block.get_top()
            l.add(t)
        return l

    ## Verifica se existem blocos com conexões abertas
    #  numa arvore de blocos
    #  @param block bloco cuja árvore será analizada
    #  @return (resp, bloco) resp é um bool que tem se não há conexões abertas\n
    #                        bloco tem o primeiro bloco encontrado com conexões vazias
    #                        (no outro caso, o bloco é inútil)
    def dock_ok(self, block):
        
        r = True
        b = []

        for dock in block.get_docks(False):
            
            if dock.get_enabled() == True:
                if dock.get_format()==C_form.FEM:
                    r = False
                    b.append(block)
            else:
                k = self.dock_ok( dock.get_destiny_block() )
                r = ( r & k[0] )
                if k[1] != []:
                    b = k[1]
        return r, b
    
    ## Apaga todos os blocos do container
    def clear(self):
        map(lambda block: self.remove(block, True), self.get_children()[:] )
    
    ## Copia os blocos selecionados
    def copy(self):
        self.buffer = []
        
        self.b_disconnect( self.get_selected() )
        
        self.buffer = self.copy_group( self.get_selected() )
        
        self.b_connect( self.get_selected() )
    
    ## Coloca um grupo de blocos em um buffer
    #  @param group lista com os blocos
    #  @return lista com os blocos copiados
    def copy_group(self, group):
        
        #cpdict = {}
        buffer = []
        
        for block in group:
            if type(block) == commands.start_block or type(block) == commands.newprocedure_block:
                newblock = commands.newprocedure_block()
                newblock.set_position( block.get_position() )
                newblock.layer = block.layer
            else:
                newblock = block.copy()
                
            buffer.append( newblock )
        #    cpdict[block] = newblock
        
        #for block in group:
        #    cpblock = cpdict[block]
        #    for i in range( len( block.get_docks() ) ):
        #        dock_orig    = block.get_docks()[i]
        #        dock_orig_cp = cpblock.get_docks()[i]
        #        dest_dock    = dock_orig.get_destiny_conn()
        #        if dest_dock is not None:
        #            dest_block = dock_orig.get_destiny_block()
        #            j = dest_block.get_docks().index(dest_dock)
        #            dest_dock_cp = cpdict[dest_block].get_docks()[j]
        #            dock_orig_cp.connect( dest_dock_cp )
        
        return buffer
    
    ## Recorta os blocos selecionados
    def cut(self):
        self.copy()
        
        map(lambda block: self.remove(block), copy.copy( self.get_selected() ) )

    ## Cola os blocos copiados
    def paste(self):
        block = None
        cpblocks = []
        
        cpblocks = self.copy_group( self.buffer )
        
        for block in cpblocks:
            block.set_position( block.get_position() + Vector(20, 20) )
            block.put_aux( self, block.get_x(), block.get_y() )
            
        self.buffer = cpblocks
        self.unselect( self.get_children() )
        self.select( self.buffer )
        self.set_group( block )
        self.sort_blocks()
    
    ## Muda a prioridade de renderização de uma lista
    #  de blocos
    #  @param _list lista de blocos
    #  @param n prioridade
    def set_layer(self, _list, n):
        for b in _list:
            b.layer = n
        self.sort_blocks()
    
    def sort_blocks(self):
        self.blocks.sort( lambda block1,block2: cmp(block1.layer, block2.layer) )

    ## Gera o código a partir de uma árvore de blocos
    #  @param block bloco que terá sua árvore percorrida
    #  @return string com o código
    def code(self, block, text = ""):

        for value in block.code:
            if isinstance(value, Dock):
                #tem mais código no destino daquela conexão
                if value.get_enabled() == False and value.get_flow() != C_flow.TO_PARENT:
                    text = self.code( value.get_destiny_block(), text )
                    
            elif isinstance(value, str ) or isinstance(value, int ) or isinstance(value, float ):
                #só texto para adicionar
                text = text + str(value)
                    
            else: #só pode então ser uma função
                #o texto aqui é o valor de retorno da função
                text = text + str( value() )
        
        return text
        
    ## Carrega o dicionario de propriedades dos blocos
    #  a partir de um arquivo XML
    #  @param loadfile arquivo .xml que será carregado
    def load(self, loadfile):
        
        self.clear()
        
        loaddoc  = minidom.parse(loadfile)
        mainnode = loaddoc.documentElement
        
        for blocknode in mainnode.childNodes:
            if blocknode.nodeType == Node.ELEMENT_NODE:
                btype = blocknode.attributes.get('type').value
                
                try:
                    newblock = block.Block.dict_blockref[btype]()
                except KeyError:
                    print "type "+btype+" was not found!"
                    newblock = Block()
                
                for propnode in blocknode.childNodes:
                    if propnode.nodeType == Node.ELEMENT_NODE:
                        name  = propnode.attributes.get('name').value
                        type  = propnode.attributes.get('type').value
                        try:
                            value = propnode.firstChild.nodeValue
                        except:
                            value = ""
                        
                        if type == 'bool':
                            if value == 'True':
                                newblock.create_property( name, True )
                            else:
                                newblock.create_property( name, False )
                        elif type == 'int':
                            newblock.create_property( name, int(value) )
                        elif type == 'float':
                            newblock.create_property( name, float(value) )
                        elif type == 'string':
                            newblock.create_property( name, str(value) )
                            
                newblock.put_aux(self, newblock.get_x(), newblock.get_y())
            self.b_connect_overlay()
        
    ## Salva o estado atual do canvas em um arquivo XML
    #  @param file arquivo .xml em que será salvo
    def save(self, file):
        savedoc  = minidom.getDOMImplementation().createDocument(None, "blocks", None)
        mainnode = savedoc.documentElement
        
        for block in self.get_children():
            blocknode = savedoc.createElement("block")
            mainnode.appendChild(blocknode)
            
            blocknode.setAttribute("type", str( block.get_type() ) )   
            
            for name in block.properties.keys():
                propnode = savedoc.createElement("prop")
                blocknode.appendChild(propnode)
                
                propnode.setAttribute("name", name)
                
                prop = block.get_property(name)
                
                if isinstance(prop, bool ):
                    propnode.setAttribute("type", "bool")
                elif isinstance(prop, int ):
                    propnode.setAttribute("type", "int")
                elif isinstance(prop, float ):
                    propnode.setAttribute("type", "float")
                elif isinstance(prop, str ):
                    propnode.setAttribute("type", "string")
                    
                valuenode = savedoc.createTextNode( str(prop) )
                
                propnode.appendChild(valuenode)
        
        
        file.write( savedoc.toxml() )
        return savedoc.toxml()
        
    ## Adiciona um bloco no canvas
    #  @param block bloco que será adicionado
    def add(self, block):
            self.blocks.append(block)
            self.sort_blocks()
    
    ## Remove um bloco do canvas
    #  @param block bloco que será removido
    #  @param IGNORE_RFLAG se for True, apaga até mesmo blocos
    #  especiais (como o startblock)
    def remove(self, block, IGNORE_RFLAG=False):
        
        if block.erasable == True or IGNORE_RFLAG == True:
            
            for dock in block.get_docks():
                dock.disconnect()
            try:
                self.blocks.remove(block)
            except ValueError:
                pass
            self.selected -= set( (block,) )
            
            block.kill_gui()
            block.kill_widgets()
            block.mark_dirty()
            
            block.remove()
            
    ## Remove os blocos selecionados
    def remove_selected(self):
        map(lambda block: self.remove(block), copy.copy( self.get_selected() ) )
    
    ## Retorna uma lista com todos os blocos do canvas
    #  @return lista com os blocos
    def get_children(self):
        return self.blocks
    
    ## Seleciona um grupo de blocos
    #  @param _list lista com os blocos que serão selecionados
    def select(self, _list):
        
        for block in _list:
            block.selected = True
            
        self.selected |= set(_list)

    ## Desseleciona um grupo de blocos
    #  @param _list lista com os blocos que serão selecionados        
    def unselect(self, _list):
        
        for block in _list:
            block.selected = False
        
        self.selected -= set(_list)
    
    ## Retorna os blocos selecionados no container
    #  @return lista com os blocos
    def get_selected(self):
        return self.selected

    ## Retorna as possíveis conexões entre um grupo de blocos e os restantes
    #  no container
    #  @param _list lista com o grupo de blocos
    #  @return conjunto de 2-uplas com as possíveis conexões
    def possible_docks(self, _list):
        
        possible_docks = self.get_free_docks( self.get_children() )
        group_possible_docks = self.get_free_docks(_list)
        
        possible_docks = possible_docks - group_possible_docks
        
        dock_done = set()
        
        for dock2 in group_possible_docks:
            for dock1 in possible_docks:
                if dock1.is_possible_to_connect(dock2) == True:
                    dock_done.add( (dock2, dock1) )
        
        return dock_done
    
    ## Conecta um grupo ao restante dos blocos
    #  @param _list grupo
    def b_connect(self, _list):
        
        docks = self.possible_docks(_list)
            
        for dock1, dock2 in docks:
            dock1.connect( dock2 )    

    ## Conecta as conexões que estiverem exatamente sobrepostas
    def b_connect_overlay(self):
        l = self.get_free_docks( self.get_children() )
        for dock1 in l:
            for dock2 in l:
                if dock1.get_absposition() == dock2.get_absposition() and dock1.is_possible_to_connect(dock2):
                    dock1.connect(dock2)

    ## Desconecta um grupo de blocos do todo no canvas
    #  @param _list grupo
    def b_disconnect(self, _list):
        for block in _list:
            for dock in block.get_docks(True):
                if dock.get_enabled() == False\
                and not dock.get_destiny_block() in _list:
                    dock.disconnect()

    ## Retorna todas as conexões livres num grupo de blocos
    #  @param _list grupo
    def get_free_docks(self, _list):
        
        possible_docks = set()
        
        for block in _list:
            for dock in block.get_docks(True):
                if dock.get_enabled() == True:
                    possible_docks.add(dock)
                    
        return possible_docks
    
    ## Verifica se os blocos selecionados estão sendo atraídos por
    #  alguma conexão externa e os move para  alinhar com ela
    def magnetic(self):
        
        d = None
        
        def func(k):
            for dock1, dock2 in k:
                d = dock2.get_distance( dock1 )
                
                for block in self.get_selected():
                    block.translate(d)
                return d
        
        #group leader has priority
        if not self.master is None:
            dock = self.possible_docks( (self.master,) )
            func( dock )
        
        #group
        dock = self.possible_docks( self.get_selected() )
        func( dock )
        
        return d
    
    ## Encontra um bloco em uma posição
    #  @param pos vetor com a posição
    #  @return Bloco ou None, se não houver nada na posição
    def find(self, pos):
        
        self.get_children().reverse()
        
        for block in self.get_children():
            if block.is_at_xy_pixel(pos):
                return block
        
        self.get_children().reverse()
        
        return None

    ## Define que os blocos selecionados serão
    #  um grupo à parte
    #  @param master líder do grupo
    def set_group(self, master):
        
        self.b_connect_overlay()
        
        self.master = master
        
        # é importante que o grupo seja desenhado acima dos outros blocos
        # então eles tem que estar no fim da lista de blocos
        self.sort_blocks()
        maxlayer = self.get_children()[-1].layer
        
        if maxlayer > 1000000:
            self.realloc_layers()
            self.sort_blocks()
            maxlayer = self.get_children()[-1].layer

        if len(self.get_selected()) > 0:
            mingrouplayer = min( [block.layer for block in self.get_selected()] )
        else:
            mingrouplayer = 0
        
        for block in self.get_selected():
            block.set_layer( maxlayer + block.layer - mingrouplayer + 1 )
        
        self.b_disconnect( self.get_selected() )
        
        self.sort_blocks()

    ## Faz o grupo destacado voltar a fazer parte dos blocos
    #  normais
    def unset_group(self):

        self.magnetic()
        
        ok = True
        down = True
        for block1 in self.get_selected():
        
            if ok == False:
                break
        
            if block1.get_x() < 0 or block1.get_y() < 0:
                ok = False

        self.b_connect_overlay()

        self.master = None
        
        return not ok

    # Duvido muito que isso seja chamado alguma vez
    def realloc_layers(self):
        l = list( self.get_top_blocks() )
        l.sort( lambda block1,block2: cmp(block1.layer, block2.layer) )
        
        i = 0
        for b in l:
            self.set_layer(b.get_tree(), i)
            i += 1
