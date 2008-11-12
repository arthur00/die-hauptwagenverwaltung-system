#! /usr/bin/env python
# -*- coding: UTF8 -*-"
# Oh Noes!
# Oh Yeeeaas
# EEEEEE
# Arriba Muchacho
# Yo Soy Mancuso Miguelito
# Adam West and Claudecir
# UFAIL
from wx import ImageFromStream, BitmapFromImage
from wx.lib.splitter import MultiSplitterWindow
import  string as _string
import  wx
import xmlrpclib
from os.path import join as opj 
import copy


class MainFrame(wx.Frame):
        def __init__(self, parent, id, title):
            
            frame = wx.Frame.__init__(self, parent, id, title,
                              wx.DefaultPosition, (1280, 768))
    
            # Creates the Windows Division
            self.server = xmlrpclib.ServerProxy('http://localhost:8000')
            #
            inventory = self.server.inventory()
            self.initcars = inventory[0]
            self.initmotors = inventory[1]
            self.initcolors = inventory[2]
            self.initacs = inventory[3]
            
            splitter = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
            self.splitter = splitter
            wsizer = wx.BoxSizer(wx.HORIZONTAL)
            wsizer.Add(splitter, 1, wx.EXPAND)
            self.SetSizer(wsizer)
    
    
            p1 = SamplePane(splitter, "white")
            splitter.AppendWindow(p1, 350)
    
            p2 = SamplePane(splitter, "white")
            p2.SetMinSize(p2.GetBestSize())
            splitter.AppendWindow(p2, 360)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            str = "die Hauptwagenverwaltung-System"
            text = wx.StaticText(p2, -1, str)
            font = wx.Font(21, wx.SWISS, wx.NORMAL, wx.NORMAL)
            text.SetFont(font)
            
            button = wx.Button(p2, 20, "Start", (50, 50))
            button.Bind(wx.EVT_BUTTON, self.Start)

            city = wx.StaticText(p2, -1, "Entre com a sua localizacao:")
            sampleList = ['Sao Paulo', 'Campinas', 'São José dos Campos','São Vicente']
            self.ch_city = wx.Choice(p2,-1,choices=sampleList)


            sizer.Add(text,0,wx.CENTER|wx.TOP,30)
            sizer.Add(city,0,wx.CENTER|wx.TOP,200)
            sizer.Add(self.ch_city,0,wx.CENTER|wx.TOP,10)
            sizer.Add(button,0,wx.CENTER|wx.TOP,30)
            
            p2.SetSizer(sizer)
            p2.SetAutoLayout(1)
            p2.Layout()
            
            bsizer = wx.BoxSizer(wx.VERTICAL)
            
            p1.SetSizer(bsizer)
            p1.SetAutoLayout(1)
            p1.Layout()
            
            self.main = p2
            self.border = p1
            self.msizer = sizer
            self.bsizer = bsizer
            
            self.Show(True)

        def Start(self,evt):
            "TODO: Nao usar DeleteWindows"
            self.msizer.DeleteWindows()
            str = "die Hauptwagenverwaltung-System"
            text = wx.StaticText(self.main, -1, str)
            font = wx.Font(21, wx.SWISS, wx.NORMAL, wx.NORMAL)
            text.SetFont(font)
            self.msizer.Add(text,0,wx.CENTER|wx.TOP,30)
            self.AlreadyChosen = False
            #sampleList = ["Gol", "Vectra", "Panzer", "Fusca", "Bicicleta", "Moto Bis", "Land Rover", "Iate", "747", "Hammer", "Gurgel", "Todos"]
            sampleList = self.initcars
            choicetxt = wx.StaticText(self.border, -1, "Escolha o modelo do carro:")
            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
            choicetxt.SetFont(font)
            self.ch_car = wx.Choice(self.border, -1, choices = sampleList)
            self.Bind(wx.EVT_CHOICE, self.CarChosen, self.ch_car)
            self.bsizer.Add(choicetxt,0,wx.CENTER|wx.TOP,10)
            self.bsizer.Add(self.ch_car,0,wx.CENTER|wx.TOP,10)
            
            self.main.Layout()
            self.bsizer.Layout()

        def CarChosen(self,evt):
            if self.AlreadyChosen == False:
                self.AlreadyChosen = True
                
                
                #sampleList = ['XTEC 1.0 Flex','AZAP 1.6 Flex', 'AMT Turbo 2.6', "Todos"]
                sampleList = self.initmotors
                self.ch_motor = wx.Choice(self.border,-1,choices = sampleList)
                
                #sampleList = ["Azul", "Verde", "Vermelho", "Laranja com pintas cor-de-rosa", "Todos"]
                sampleList = self.initcolors
                self.ch_color = wx.Choice(self.border, -1, choices = sampleList)
                
                cor =wx.StaticText(self.border,-1,"Cor:")
                motor = wx.StaticText(self.border,-1,"Motor:")
                
                self.modelcolorbox = wx.FlexGridSizer(cols=2, hgap=4, vgap=4)
                self.modelcolorbox.AddMany([ motor, cor, 
                                            self.ch_motor , self.ch_color
                        ])

                choicetxt = wx.StaticText(self.border, -1, "Escolha os opcionais \n   para o " + evt.GetString() + ":")
                
                #sampleList = ['Ar Condicionado','Trio Eletrico','Farol de Neblina','Roda de Liga Leve']
                """
                cb1 = wx.CheckBox(self.border, -1, "Foguete")
                cb2 = wx.CheckBox(self.border, -1, "Asa")
                cb3 = wx.CheckBox(self.border, -1, "Vidro Eletrico")
                cb4 = wx.CheckBox(self.border, -1, "Rodas Quadradas")
                cb5 = wx.CheckBox(self.border, -1, "Sistema de Submersao")
                cb6 = wx.CheckBox(self.border, -1, "Piloto Automatico")                
                """ 
                cb1 = wx.CheckBox(self.border, -1, self.initacs[0])
                cb2 = wx.CheckBox(self.border, -1, self.initacs[1])
                cb3 = wx.CheckBox(self.border, -1, self.initacs[2])
                cb4 = wx.CheckBox(self.border, -1, self.initacs[3])
                cb5 = wx.CheckBox(self.border, -1, self.initacs[4])
                cb6 = wx.CheckBox(self.border, -1, self.initacs[5])                
                
                self.optionalbox = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
                self.optionalbox.AddMany([ cb1 , cb2,
                          cb3,cb4,
                          cb5,cb6,
                        ])
                self.foguete = cb1
                self.asa = cb2
                self.vidro_eletrico = cb3
                self.rodas_quadradas = cb4
                self.sistema_submersao = cb5
                self.piloto_automatico = cb6
                
                button = wx.Button(self.border, 20, "Buscar", (50, 50))
                button.Bind(wx.EVT_BUTTON, self.Search)

                self.bsizer.Add(self.modelcolorbox,0,wx.CENTER|wx.TOP,20)
                self.bsizer.Add(choicetxt,0,wx.CENTER|wx.TOP,20)
                self.bsizer.Add(self.optionalbox,0,wx.CENTER|wx.TOP,20)
                self.bsizer.Add(button,0,wx.CENTER|wx.TOP,30)
            

            
                self.bsizer.Layout()
                self.msizer.Layout()
                self.Searched = False
        
        def Search(self,evt):
            if self.Searched == True:
                self.msizer.DeleteWindows()
                str = "die Hauptwagenverwaltung-System"
                text = wx.StaticText(self.main, -1, str)
                font = wx.Font(21, wx.SWISS, wx.NORMAL, wx.NORMAL)
                text.SetFont(font)
                self.msizer.Add(text,0,wx.CENTER|wx.TOP,30)
                self.Searched = False
            
            if self.Searched == False:
                self.Searched = True
                opcionais = []
                if self.foguete.GetValue() == True:
                    opcionais.append(self.foguete.GetLabel())
                if self.asa.GetValue() == True:
                    opcionais.append(self.asa.GetLabel())
                if self.vidro_eletrico.GetValue() == True:
                    opcionais.append(self.vidro_eletrico.GetLabel())
                if self.piloto_automatico.GetValue() == True:
                    opcionais.append(self.piloto_automatico.GetLabel())
                if self.sistema_submersao.GetValue() == True:
                    opcionais.append(self.sistema_submersao.GetLabel())
                if self.rodas_quadradas.GetValue() == True:
                    opcionais.append(self.rodas_quadradas.GetLabel())
                motor = self.ch_motor.GetCurrentSelection()
                cor = self.ch_color.GetCurrentSelection()
                car = self.ch_car.GetCurrentSelection()
                tipo = {}
                arg = {}
                if motor != "Todos":
                    tipo["motor"] = True
                    arg["motor"] = self.initmotors[motor]
                if cor != "Todos":
                    tipo["cor"] = True
                    arg["cor"] = self.initcolors[cor]
                if car != "Todos":
                    tipo["car"] = True
                    arg["car"] = self.initcars[car]
                if opcionais != []:
                    tipo["acs"] = True
                    arg["acs"] = opcionais
                
                
                
                " Busca o carro aqui "
                
                
                result = self.server.carFinder(tipo,arg)
                self.results = wx.FlexGridSizer(cols=3, hgap=6, vgap=20)
                
                
                for item in result:
                    img = wx.Image(opj('img/porsche25.jpg'), wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
                    self.img_car = wx.StaticBitmap(self.main, -1, img,size=(img.GetWidth(), img.GetHeight()))
                    resultsbox = wx.BoxSizer(wx.VERTICAL)
                    carro = wx.StaticText(self.main, -1, "Carro: " + item["car"] + " - " + item["motor"])
                    serie = wx.StaticText(self.main, -1, "Numero de Serie: " + item["id"])
                    cor = wx.StaticText(self.main, -1, "Cor: " + item["cor"])
                    opt = "Kit Básico"
                    for z in item["acs"]:
                        opt = opt + ", " + z
                    acss = wx.StaticText(self.main, -1, "Opcionais: " + opt)
                    preco = wx.StaticText(self.main, -1, "Preço à Vista: R$ " + item["preco"])
                    finaliz = wx.Button(self.main,20,"Reservar",(50,50))
                    finaliz.Bind(wx.EVT_BUTTON, self.Finish)
                    self.mapper = {}
                    self.mapper[finaliz.GetId()] = item["id"]
                    resultsbox.AddMany( ( (carro,0,wx.CENTER|wx.TOP,0),  (serie,0,wx.CENTER|wx.TOP,5), (cor,0,wx.CENTER|wx.TOP,5) , (acss,0,wx.CENTER|wx.TOP,5) , (preco,0,wx.CENTER|wx.TOP,5) ))
                    self.results.AddMany([ self.img_car ,resultsbox,finaliz])
                
                """
                
                
                
                " Retorna os Valores aqui "
                
                
                resultsbox = wx.BoxSizer(wx.VERTICAL)
                conc = wx.StaticText(self.main, -1, "Concessionaria: MI5 Racer Motors")
                serie = wx.StaticText(self.main, -1, "Numero de Serie: 397f9XX92")
                prazo = wx.StaticText(self.main, -1, "Prazo para entrega: 2 meses")
                preco = wx.StaticText(self.main, -1, "Preço à Vista: R$ 10.000")
                resultsbox.AddMany( ( (conc,0,wx.CENTER|wx.TOP,0),  (serie,0,wx.CENTER|wx.TOP,5), (prazo,0,wx.CENTER|wx.TOP,5) , (preco,0,wx.CENTER|wx.TOP,5) ))
                
                resultsbox2 = wx.BoxSizer(wx.VERTICAL)
                conc2 = wx.StaticText(self.main, -1, "Concessionaria: Shiro Motors")
                serie2 = wx.StaticText(self.main, -1, "Numero de Serie: 4OXLD1337H4X0R")
                prazo2 = wx.StaticText(self.main, -1, "Prazo para entrega: 3 meses")
                preco2 = wx.StaticText(self.main, -1, "Preço à Vista: R$ 10.000")
                resultsbox2.AddMany( ((conc2,0,wx.CENTER|wx.TOP,0),  (serie2,0,wx.CENTER|wx.TOP,5), (prazo2,0,wx.CENTER|wx.TOP,5), (preco2,0,wx.CENTER|wx.TOP,5)))
                
                finaliz = wx.Button(self.main,20,"Reservar",(50,50))
                finaliz2 = wx.Button(self.main,20,"Reservar",(50,50))
                finaliz.Bind(wx.EVT_BUTTON, self.End)
                finaliz2.Bind(wx.EVT_BUTTON, self.End)
                
                
                if result != "":
                    self.results = wx.FlexGridSizer(cols=3, hgap=6, vgap=20)
                    self.results.AddMany([ self.img_car ,resultsbox,finaliz,
                                          self.img_car2,resultsbox2,finaliz2
                                ])
                        
                    
                """
                if result != "":
                    self.msizer.Add(self.results,0,wx.LEFT|wx.TOP,50)                
                    self.msizer.Layout()
        
        def Finish(self,evt):
            #print self.mapper[evt.Id]            
            self.server.clientBuy(self.mapper[evt.Id])
                
        def End(self,evt):
            self.msizer.DeleteWindows()
            
            img = wx.Image(opj('img/porsche50.jpg'), wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
            img_car = wx.StaticBitmap(self.main, -1, img,size=(img.GetWidth(), img.GetHeight()))
            self.price = 10000
            str = "Obrigado pela Preferencia!"
            text = wx.StaticText(self.main, -1, str)
            font = wx.Font(21, wx.SWISS, wx.NORMAL, wx.NORMAL)
            text.SetFont(font)
            
            forma = wx.StaticText(self.main, -1, "Escolha a forma de Pagamento:")
            sampleList = ['À vista', 'Entrada + Parcelas']
            self.ch_forma = wx.Choice(self.main,-1,choices=sampleList)
            self.Bind(wx.EVT_CHOICE, self.Payment, self.ch_forma)
            self.PaymentChosen = False
            
            
            
            self.msizer.Add(text,0,wx.CENTER|wx.TOP,80)
            self.msizer.Add(img_car,0,wx.CENTER|wx.TOP,30)
            self.msizer.Add(forma,0,wx.CENTER|wx.TOP,20)
            self.msizer.Add(self.ch_forma,0,wx.CENTER|wx.TOP,20)
            
            self.msizer.Layout()
            
        def Payment(self,evt):
            if self.PaymentChosen == False:
                self.PaymentChosen = True
                if evt.GetString() == 'Entrada + Parcelas':
                    self.entrada = wx.StaticText(self.main,-1,"Entrada:")
                    self.nparcelas = wx.StaticText(self.main,-1,"Numero de Parcelas:")
                    self.entr = wx.TextCtrl(self.main, -1, "0",size=(100,-1))
                    self.nparc = wx.TextCtrl(self.main, -1, "0",size=(100,-1))

                    self.button1 = wx.Button(self.main, 20, "Calcular", (50, 50))
                    self.button1.Bind(wx.EVT_BUTTON, self.CalcPayment)
                    self.Calculated = False
                    
                    self.paymentgrid = wx.FlexGridSizer(cols=3, hgap=6, vgap=6)
                    self.paymentgrid.AddMany([ self.entrada, self.nparcelas, (0,0),
                                              self.entr, self.nparc, self.button1
                            ])

                    
                    
                    self.msizer.Add(self.paymentgrid,0,wx.CENTER|wx.TOP,10)
                    self.msizer.Layout()
            
        def CalcPayment(self,evt):
            if self.Calculated == False:
                self.Calculated = True
                self.precoparcela = wx.StaticText(self.main,-1,"Valor da Parcela:")
                self.valort = wx.StaticText(self.main,-1,"Valor Total:")
                parcelas = int(self.nparc.GetValue())
                
                precot = self.price * 1.05
                precop = self.price / parcelas 
                self.precotf =  wx.StaticText(self.main,-1,str(precot))
                self.precopf =  wx.StaticText(self.main,-1,str(precop))
                
                self.paymentgrid.AddMany([ (0,0) , (0,0) , (0,0), 
                                          (0,0) , (0,0) , (0,0),
                                           self.precoparcela,self.valort,(0,0),
                                           self.precopf,self.precotf,(0,0)
                                          ])
                
                self.msizer.Layout()
            else:
                parcelas = int(self.nparc.GetValue())
                self.paymentgrid.Clear()
                
                precot = self.price * 1.05
                precop = self.price / parcelas 
                
                self.precotf =  wx.StaticText(self.main,-1,str(precot))
                self.precopf =  wx.StaticText(self.main,-1,str(precop))
                
                self.paymentgrid.AddMany([ self.entrada, self.nparcelas, (0,0),
                                            self.entr, self.nparc, self.button1,
                                          (0,0) , (0,0) , (0,0), 
                                          (0,0) , (0,0) , (0,0),
                                           self.precoparcela,self.valort,(0,0),
                                           self.precopf,self.precotf,(0,0)
                                          ])
                
                self.paymentgrid.Layout()
   
class SamplePane(wx.Panel):
    """
    Just a simple test window to put into the splitter.
    """
    def __init__(self, parent, colour):
        wx.Panel.__init__(self, parent, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour(colour)
        

def __test():

    class MyApp(wx.App):
        def OnInit(self):
            wx.InitAllImageHandlers()
            frame = MainFrame(None, -1, "PlotCanvas")
            #frame.Show(True)
            self.SetTopWindow(frame)
            return True


    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    __test()
    