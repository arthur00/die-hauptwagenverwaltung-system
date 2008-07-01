from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Thread
import Queue
import sys
import random
import xmlrpclib

#Resumo da estrutura das principais variaveis:
#  activeNodes -> {"string:id" : string:port, ... }
#  queues      -> {"string:id" : Queue(), ... }
#  msg         -> {"'rl'" : int:timestamp, "'type'" : string:type, "'param'" : list:args}
#  bd          -> {"string:id" : dict:car  }
#  car         -> {"'id'" : string:id, "'car'" : string:car, "'motor'" : string:motor, "'cor'" : string:cor, "'preco'" : string:preco, "'acs'" : list of string:acs }

debug = False

class Server(Thread):
    def __init__(self, port, mentor):
        self.queues = {}
        self.activeNodes = {}
        self.id = str(0)
        self.rl = 0
        self.port = str(port)
        
        #inicia thread para a servidora
        Thread(name="Thread Servidora", target=self.server).start()

        if mentor <> 0:
            # Algum host ativo sera passado por parametro como mentor do novo host.
            self.myMentor = xmlrpclib.ServerProxy('http://localhost:'+str(mentor))
            # 'porta' : id
            self.rl, self.id, self.activeNodes = self.myMentor.getActiveList(self.port)
            #self.rl, self.id, self.activeNodes = self.getActiveList(self.port)
            if debug: print "Relogio Logico atual: " + str(self.rl)
            if debug: 
                for m, k in self.activeNodes.iteritems(): print "A porta " + k + " esta associada ao id " + m
            # Atualiza relogio logico
            self.rl = self.rl + 1
        
            self.db = {}

            for node in self.activeNodes.keys():
                # 'string:id' : fila
                self.queues[node] = Queue.Queue()
                
            print self.activeNodes
            self.getDB()
            if debug: 
                for m, k in self.db.iteritems(): print "DB: Parametro: " + str(m) + " || Valor: " + str(k)
                
        # mentor = 0 quando se trata do primeiro servidor a ser upado.
        else:
            self.myMentor = 0
            self.activeNodes = {self.id:self.port}
            self.db = {} 
            self.makeDB() # Aquela funcao de inicializar o BD aleatoriamente
            if debug: 
                for m, k in self.db.iteritems(): print "New DB: Parametro: " + str(m) + " || Valor: " + str(k)

            for node in self.activeNodes.keys():
                # 'string:id' : fila
                self.queues[node] = Queue.Queue()

        #inicia thread para o queueProcessor
        Thread(name="Thread Processadora das Filas", target=self.queueProcessor).start()
  

    #Funcao que deixara o servidor servindo eternamente
    def server(self):
        self.servidor = SimpleXMLRPCServer(("localhost",int(self.port)))
        self.servidor.register_instance(self)
        self.servidor.serve_forever()

    #define um novo id
    #Se um servidor capotar, seu ID sera reutilizado!!!
    def getNewId(self):
        newId = 0
        while str(newId) in self.activeNodes.keys():
             newId = newId + 1
        return str(newId)

    #retorna o relogio logico atual e a lista de portas e id's dos servidores disponiveis
    def getActiveList(self, port):
        newId = self.getNewId()
        self.activeNodes[newId] = port
        print "New service available in port " + port + " with ID: " + newId + " by mentor with ID: " + self.id

        self.queues[newId] = Queue.Queue()
        print self.queues[newId]
        for activeServerPort in self.activeNodes.values():
        # Atualiza dicionario de nos ativos nos outros servidores
            if (activeServerPort <> port) and (activeServerPort <> self.port):
                print "Atualizando activeNodes de " + activeServerPort
                activeServer = xmlrpclib.ServerProxy('http://localhost:'+activeServerPort)
                activeServer.updateActiveList(port,newId,self.id,self.rl)
        # Atualiza relogio logico
        self.rl = self.rl + 1
        print self.activeNodes
        return self.rl, newId, self.activeNodes

    # Atualiza dicionario de nos ativos
    def updateActiveList(self, port, id, fromid, rl):
        print "Updating Active Nodes List"
        print "New service available in port " + port + " with ID: " + str(id) + " by mentor with ID: " + str(fromid)
        # Adiciona um novo elemento no dicionario de filas e de nos ativos
        self.queues[id] = Queue.Queue()
        self.activeNodes[id] = port
        # Atualiza relogio logico
        if self.rl < rl: self.rl = rl + 1
        else: self.rl = self.rl + 1
        return True

    def queueProcessor(self):
        # Guarda o primeiro elemento de cada fila
        # queueHead  -> { "string:id" : dict:msg, ... }
        queuesHead = {}
        while True:
            for id,port in self.activeNodes.items():
                # Caso nao exista o primeiro elemento da fila
                if not queuesHead.has_key(id):
                    if (self.queues[id].empty()):
                        if (id == self.id):
                            msg = {'rl': self.rl, 'type': "ACK", 'param': "Cebola eh um viadinho"}
                            self.rl += 1
                            self.queues[self.id].put(msg)
                            if debug: print "Quero um ACK meu mesmo"
                        else:
                            waiting = 0
                            # Esperando a fila ter pelo menos um ACK
                            while (self.queues[id].empty()):
                                if (waiting == 0):
                                    if debug: print "Pede um ack pra "+port
                                    self.sendMsg(0, "requestACK", id)
                                    waiting = 1
                    queuesHead[id] = self.queues[id].get()
                    #print queuesHead[id]

            # Encontra a mensagem com o menor relogio logico
            earliest = self.id
            for id,msg in queuesHead.items():
                if msg['rl'] <= queuesHead[str(earliest)]['rl']:
                    #if id < earliest:
                    earliest = id
            earliestMsg = queuesHead.pop(earliest)

            #print earliestMsg

            # Processa mensagem!
            if earliestMsg['type'] == 'buy':
                print "So jogar na funcao de compra." # self.buy(earliestMsg['param'])

            elif earliestMsg['type'] == 'requestDB':
                print "BD requisitado"
                self.sendMsg(self.db, 'copyDB', earliest)
                
            elif earliestMsg['type'] == 'copyDB':
                print "BD recebido"
                self.db = earliestMsg['param']
                print self.db

            elif earliestMsg['type'] == 'requestACK':
                self.sendMsg(0, "ACK", earliest)

            elif earliestMsg['type'] == 'ACK':
                if debug: print "Acabei de receber um ACK. Estou tao feliz!!!"
                #print self.rl
            # E assim por diante

    def broadcastMsg(self, param, type):
        print "Broadcasting message"
        # Monta a mensagem
        msg = {'rl': self.rl, 'type': type, 'param': param}
        # Broadcast da mensagem
        for activeServerPort in self.activeNodes.values():
            if activeServerPort <> self.port:
                activeServer = xmlrpclib.ServerProxy('http://localhost:'+activeServerPort)
                activeServer.receiveMsg(self.id, msg)
                print "Se comunicou via broadcast com o server: " + activeServerPort
        # Atualiza relogio logico
        self.rl = self.rl + 1
        return True

    def sendMsg(self, param, type, id):
        print "Vai se comunicar com " + id
        # Monta a mensagem
        msg = {'rl': self.rl, 'type': type, 'param': param}
        activeServer = xmlrpclib.ServerProxy('http://localhost:'+self.activeNodes[id])
        activeServer.receiveMsg(self.id, msg)
        # Atualiza relogio logico
        self.rl = self.rl + 1
        return True

    def receiveMsg(self, id, msg):
        print "Recebendo mensagem de " + id
        # Atualiza relogio logico
        if self.rl < msg['rl']: self.rl = msg['rl'] + 1
        else: self.rl = self.rl + 1
        # Insere mensagem na fila correspondente
        self.queues[id].put(msg)
        return True

    # Esse eh pro cliente acessar
    def sell(self, param):
        # Param == id ?!?! vcs quem sabem
        # Tito: nao!!! param <> id
        self.broadcastMsg(param, "buy")
        return True

    # Esse aqui eh o que o server acessa quando ele processa uma mensagem de compra da fila!
    def buy(self,id):
        # Sei la
        return True


    # Funcao de criacao de um banco de dado
    def getDB(self):
        self.broadcastMsg(self.id, 'requestDB')
        return True

    def makeDB(self):
        self.inventory()
        i = 0
        while i < 24:
            self.newItem(random.choice(self.car),str(random.randint(1, 1000000)),random.choice(self.motor),random.choice(self.cor),str(random.randint(10000, 80000)), random.sample(self.acs,3))
            i+=1

    def inventory(self):
        self.car = ["Gol", "Vectra", "Panzer", "Fusca", "Bicicleta", "Moto Bis", "Land Rover", "Iate", "747", "Hammer", "Gurgel"]
        if debug: print self.car

        self.motor = ['XTEC 1.0 Flex','AZAP 1.6 Flex', 'AMT Turbo 2.6']
        if debug: print self.motor

        self.cor = ["Azul", "Verde", "Vermelho", "Laranja com pintas magenta", "Ciano"]
        if debug: print self.cor
        
        #Nao pode criar novos acessorios!!! Na verdade, tem q manter o numero exato de 6 acessorios (nao mais nem menos)...
        self.acs = ["Foguete", "Asa", "Vidro Eletrico", "Piloto Automatico", "Sistema de Submersao", "Rodas Quadradas"]
        if debug: print self.acs

        return (self.car, self.motor, self.cor, self.acs)

    def newItem(self,car,id,motor,cor,preco,acs):
        newdb = {}
        newdb["car"] = car
        newdb["id"] = id
        newdb["motor"] = motor
        newdb["cor"] = cor
        newdb["preco"] = preco
        newdb["acs"] = acs
        
        if (self.db.has_key(id) == False):
            if debug: print "Novo carro criado: " + str(newdb)
            self.db[id] = newdb

        
    def carFinder(self, tipo, arg):
        if debug: print "Evento Interno : Aqui se procura um produto no Banco de Dados"
        #Tipo pode ser:
        #     'id' : retorna especificacao do carro
        #     'car': retorna lista com todos os modelos desse carro
        #     'cor': retorna lista com todos os modelos dessa cor
        #     'acs': retorna lista com todos os modelos com esse conjunto de acessorios
        #     'tup': retorna lista com todos os modelos que satisfazem essa tupla
        
        # tipo: dicionario com "id", "car", "motor", "cor" e "acs" = a true ou false
        # arg: argumento do tipo com mesmo nome de dicionario. No caso de acs, uma lista [] de acessorios
        result = []
        newresult = []
        firstsearch = True
        if (tipo.has_key("id")):
            for k, v in self.db.iteritems():
                if k == arg["id"]:
                    result.append(v)
            if (result==[]):
                return ""
            else:
                firstsearch=False
        
        if (tipo.has_key("car")):
            for k, v in self.db.iteritems():
                if v["car"] == arg["car"]:
                    if (result.count(v) > 0 or firstsearch==True):
                        newresult.append(v)
            if (newresult==[]):
                return ""
            else:
                firstsearch=False
                result = newresult
                newresult = []
        
        if (tipo.has_key("motor")):
            for k, v in self.db.iteritems():
                if v["motor"] == arg["motor"]:
                    if (result.count(v) > 0 or firstsearch==True):
                        newresult.append(v)
            if (newresult==[]):
                return ""
            else:
                firstsearch=False
                result = newresult
                newresult = []
    
                    
        if (tipo.has_key("cor")):
            for k, v in self.db.iteritems():
                if v["cor"] == arg["cor"]:
                    if (result.count(v) > 0 or firstsearch==True):
                        newresult.append(v)
            if (newresult==[]):
                return ""
            else:
                firstsearch=False
                result = newresult
                newresult = []
                
        if (tipo.has_key("preco")):
            for k, v in self.db.iteritems():
                if int(v["preco"]) < int(arg["preco"]):
                    if (result.count(v) > 0 or firstsearch==True):
                        newresult.append(v)
            if (newresult==[]):
                return ""
            else:
                firstsearch=False
                result = newresult
                newresult = []
       

        if (tipo.has_key("acs")):
            for k, v in self.db.iteritems():
                for x in arg["acs"]:
                    foundall = False
                    if v["acs"].count(x) > 0:
                        foundall = True
                    else:
                        foundall = False
                        break
                if (foundall and (result.count(v) > 0 or firstsearch==True)):
                    newresult.append(v)
            if (newresult==[]):
                return ""
            else:
                firstsearch=False
                result = newresult
                newresult = []
        
        if result == []:
            return ""
        else:
            return result

if len(sys.argv) < 2 or len(sys.argv) > 4:
    print "Modo de uso: python server.py port <mentor> "
else:
    servFeliz = Server(int(sys.argv[1]), int(sys.argv[2]))
