# -*- coding: utf-8 -*-

# Este arquivo é parte do programa Monitor
# Monitor é um software livre; você pode redistribui-lo e/ou 
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
# Projeto realizado com fundos do Conselho Nacional de Desenvolvimento Científico e Tecnológico (CNPQ)

# Esse código faz parte do projeto BR-Gogo, disponível em http://sourceforge.net/projects/br-gogo/

try:
    from kiwi import tasklet
except ImportError:
    print 'Kiwi precisa ser instalado:'
    print "http://ftp.gnome.org/pub/GNOME/binaries/win32/kiwi/kiwi-1.9.21.win32.exe"
    raw_input()
    



from Tab import Tab


class ConsoleTab(Tab):
    def __init__(self,gui,Comunic,statusbar,liststoreSensorsTypes,sensorTypes):
        ### Board Console
        self.Comunic=Comunic
        self.statusbar=statusbar
        self.gui=gui
        self.sensorTypes=sensorTypes
        
        self.motorA=gui.get_widget("checkbuttonMotorA")
        self.motorB=gui.get_widget("checkbuttonMotorB")
        self.motorC=gui.get_widget("checkbuttonMotorC")
        self.motorD=gui.get_widget("checkbuttonMotorD")    
        self.motorPowerWidget=gui.get_widget("spinbuttonMotorPower")
        
        self.entryMinPwmDuty=gui.get_widget("entryMinPwmDuty")
        self.entryMaxPwmDuty=gui.get_widget("entryMaxPwmDuty")
        self.hscalePwmDuty=gui.get_widget("hscalePwmDuty")
        # Good limits for servos
        self.minDuty = 20
        self.maxDuty = 45
        self.hscalePwmDuty.set_range(self.minDuty,self.maxDuty)
        self.motorsActivated=""
        self.buttonSetPwmDuty=gui.get_widget("buttonSetPwmDuty")
        
        self.radiobuttonBurstFast=gui.get_widget("radiobuttonBurstFast")
        self.radiobuttonBurstSlow=gui.get_widget("radiobuttonBurstSlow")
        self.entryRefreshRate=gui.get_widget("entryRefreshRate")
        
        self.sensorBars=(
        gui.get_widget("progressbar1"),
        gui.get_widget("progressbar2"),
        gui.get_widget("progressbar3"),
        gui.get_widget("progressbar4"),
        gui.get_widget("progressbar5"),
        gui.get_widget("progressbar6"),
        gui.get_widget("progressbar7"),
        gui.get_widget("progressbar8"),
        )
        
        self.entrySensors=(
        gui.get_widget("entrySensor1"),
        gui.get_widget("entrySensor2"),
        gui.get_widget("entrySensor3"),
        gui.get_widget("entrySensor4"),
        gui.get_widget("entrySensor5"),
        gui.get_widget("entrySensor6"),
        gui.get_widget("entrySensor7"),
        gui.get_widget("entrySensor8"),
        )
        self.checkbuttonSensors=(
        gui.get_widget("checkbuttonSensor1"),
        gui.get_widget("checkbuttonSensor2"),
        gui.get_widget("checkbuttonSensor3"),
        gui.get_widget("checkbuttonSensor4"),
        gui.get_widget("checkbuttonSensor5"),
        gui.get_widget("checkbuttonSensor6"),
        gui.get_widget("checkbuttonSensor7"),
        gui.get_widget("checkbuttonSensor8")
        )
        
        self.comboboxSensors=(
        gui.get_widget("comboboxSensor1"),
        gui.get_widget("comboboxSensor2"),
        gui.get_widget("comboboxSensor3"),
        gui.get_widget("comboboxSensor4"),
        gui.get_widget("comboboxSensor5"),
        gui.get_widget("comboboxSensor6"),
        gui.get_widget("comboboxSensor7"),
        gui.get_widget("comboboxSensor8")    
        )
        for i in self.comboboxSensors:
            i.set_model(liststoreSensorsTypes)
        
        self.sensorValues=[0]*8    
            
        self.burstModeOnOff=False
        self.refreshMode=False
        self.refreshRate=1000
        
        ###/Board Console
            
    def taskleted(func):
        def new(*args,**kwargs):
            tasklet.Tasklet(func(*args,**kwargs))
        return new
    
    
    @taskleted
    def showStatusMsg(self,context,msg):        
        context_id=self.statusbar.get_context_id(context)        
        msg_id=self.statusbar.push(context_id,msg)
        timeout=tasklet.WaitForTimeout(1000)
        yield timeout
        self.statusbar.remove(context_id,msg_id)
        tasklet.get_event()
        
    def setDisconnected(self):
            self.showWarning("Gogo desconectada")
            self.statusbar.push(0,"Gogo desconectada")
            self.Comunic.closePort()

            
    def buttonBeep_clicked_cb(self, widget):
        try:
            self.Comunic.beep()
            self.showStatusMsg("Misc","Beep")
        except:
            self.setDisconnected()

            
    def buttonLedOn_clicked_cb(self, widget):
        try:
            self.Comunic.ledOn()
            self.showStatusMsg("Misc","Led On")
        except:
            self.setDisconnected()
  
  
    def buttonLedOff_clicked_cb(self, widget):
        try:
            self.Comunic.ledOff()
            self.showStatusMsg("Misc","Led Off")
        except:
            self.setDisconnected()
        
    
    def buttonRun_clicked_cb(self, widget):
        try:
            self.Comunic.run()
            self.showStatusMsg("Cmd","Run")
        except:
            self.setDisconnected()        
        
    def checkbuttonMotor_toggled_cb(self,widget):
        m=""
        if self.motorA.get_active():
            m=m+'a'
        if self.motorB.get_active():
            m=m+'b'
        if self.motorC.get_active():
            m=m+'c'
        if self.motorD.get_active():
            m=m+'d'
        try:
            self.Comunic.talkToMotor(m)
            self.motorsActivated=m
            self.showStatusMsg("Motor","Controlar motores: "+m)
        except:
            self.showStatusMsg("Motor","Controlar motores: "+m)
        
        
        
    def buttonMotorControlOn_clicked_cb(self, widget):        
        try:
            self.Comunic.motorOn()    
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" Ligados")
        except:
            self.setDisconnected()
    
    def buttonMotorControlOff_clicked_cb(self, widget):
        try:
            self.Comunic.motorOff()
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" Desligados")
        except:
            self.setDisconnected()
    
    def buttonMotorControlBreak_clicked_cb(self, widget):
        try:
            self.Comunic.motorBreak()
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" Brecados")
        except:
            self.setDisconnected()
        
    def buttonMotorControlCoast_clicked_cb(self, widget):
        try:
            self.Comunic.motorCoast()
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" Parados")
        except:
            self.setDisconnected()
    
    def buttonPowerSet_clicked_cb(self, widget):
        try:
            power=self.motorPowerWidget.get_value_as_int()
            self.Comunic.setMotorPower(power)
            self.showStatusMsg("Motor","Pontência dos Motores "+self.motorsActivated+" definida para "+str(power))
        except:
            self.setDisconnected()
    
    def buttonMotorControlThisway_clicked_cb(self, widget):
        try:
            self.Comunic.motorThisway()
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" para lá")
        except:
            self.setDisconnected()
        
    def buttonMotorControlThatway_clicked_cb(self, widget):
        try:
            self.Comunic.motorThatway()
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" para cá")
        except:
            self.setDisconnected()
        
    def buttonMotorControlReverse_clicked_cb(self, widget):
        try:
            self.Comunic.motorReverse()
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" revertidos")
        except:
            self.setDisconnected()
    
    
    
    def entryMinPwmDuty_changed_cb(self,widget):
        try:
            self.minDuty=int(widget.get_text())
        except:
            return
        else:
            if self.minDuty>self.maxDuty:
                self.minDuty=self.maxDuty-1
            if self.minDuty<0:
                self.minDuty=0
            try:
                self.hscalePwmDuty.set_range(self.minDuty,self.maxDuty)
            except:
                print self.minDuty,self.maxDuty            
        
    def entryMaxPwmDuty_changed_cb(self,widget):
        try:
            self.maxDuty=int(widget.get_text())
        except:
            return
        else:
            if self.maxDuty<self.minDuty:
                self.maxDuty=self.minDuty+1
            if self.maxDuty>255:
                self.maxDuty=255            
            try:
                self.hscalePwmDuty.set_range(self.minDuty,self.maxDuty)
            except:
                print self.minDuty,self.maxDuty
    
    def buttonSetPwmDuty_clicked_cb(self,widget):
        try:
            duty=int(self.hscalePwmDuty.get_value())
            self.Comunic.setPwmDuty(duty)
            self.showStatusMsg("Motor","Motores "+self.motorsActivated+" de passo: "+str(duty))
        except:
            self.setDisconnected()
    
    def get_sensor_value(self,sensorNumber):
        print 'get_sensor_value'
        try:
            return self.Comunic.readSensor(sensorNumber)
        except:
            self.burstModeOnOff = False
            self.refreshMode =  False
            #self.showWarning("Gogo desconectada##")
            #self.statusbar.push(0,"Gogo desconectada")
        #return sensorNumber*100
    
    def get_sensor_text(self,sensorNumber,value):        
        stype=self.comboboxSensors[sensorNumber].get_active()    
        if stype>=0:
            return self.sensorTypes[stype].get_text(value)            
        else:
            return str(value)
        
    
    
    def buttonRefreshAll_clicked_cb(self,widget):
        self.refreshMode = True
        for i in range(8):
            if self.refreshMode:
                value=self.get_sensor_value(i)
                if value>-1:
                    self.sensorValues[i]=value
                    self.entrySensors[i].set_text(self.get_sensor_text(i,value))
                    self.sensorBars[i].set_fraction(self.sensorValues[i]/1023.0)
        self.showStatusMsg("Sensor","Valor dos sensores atualizado")    
        
        #print self.Comunic.readSensor(0)
    
    def refreshSensors(self):
        while self.burstModeOnOff:
            timeout = tasklet.WaitForTimeout(self.refreshRate)
            for i in range(8):
                if self.checkbuttonSensors[i].get_active() and self.burstModeOnOff:
                    value=self.get_sensor_value(i)
                    if value>-1:
                        self.sensorValues[i]=value
                        self.entrySensors[i].set_text(self.get_sensor_text(i,value))
                        self.sensorBars[i].set_fraction(self.sensorValues[i]/1023.0)
            yield timeout
            tasklet.get_event()
    
    
    def burstMode(self):
        if self.radiobuttonBurstFast.get_active():
            self.entryRefreshRate.set_text("20")
            self.refreshRate=50
            self.showStatusMsg("Sensor","Leitura de sensores a 20hz")
        if self.radiobuttonBurstSlow.get_active():
            self.entryRefreshRate.set_text("5")
            self.refreshRate=200
            self.showStatusMsg("Sensor","Leitura de sensores a 5hz")


    def buttonSensorBurstOn_clicked_cb(self,widget):
        self.burstMode()
        self.burstModeOnOff=True
        tasklet.run(self.refreshSensors())
        
    def radiobuttonBurstFast_toggled_cb(self,widget):
        self.burstMode()
            
    def radiobuttonBurstSlow_toggled_cb(self,widget):
        self.burstMode()
    
    def buttonSensorBurstOff_clicked_cb(self,widget):    
        
        self.entryRefreshRate.set_text("0")
        self.burstModeOnOff=False
        self.showStatusMsg("Sensor","Leitura de sensores desligada")
