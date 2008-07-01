from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Thread
from Queue import Queue
import xmlrpclib

#Resumo da estrutura das principais variaveis:
#  activeNodes -> {"int:id" : string:port, ... }
#  queues      -> {"string:id" : Queue(), ... }
#  msg         -> {"'rl'" : int:timestamp, "'type'" : string:type, "'param'" : list:args}
#  bd          -> {"string:id" : dict:car  }
#  car         -> {"'id'" : string:id, "'car'" : string:car, "'motor'" : string:motor, "'cor'" : string:cor, "'preco'" : string:preco, "'acs'" : list of string:acs }

debug = True

class Server(Thread):
    def __init__(self, port, mentor):
        self.queues = {}
        self.port = str(port)
        if mentor <> 0:
            # Algum host ativo sera passado por parametro como mentor do novo host.
            self.myMentor = xmlrpclib.ServerProxy('http://localhost:'+str(mentor))
            # 'porta' : id
            self.rl, self.id, self.activeNodes = self.mentor.getActiveList(self.port)
            if debug: print "Relogio Logico atual: " + str(self.rl)
            if debug: for m, k in self.activeNodes.iteritems(): print "A porta " + k + " esta associada ao id " + str(m)
            # Atualiza relogio logico
            self.rl = self.rl + 1
            self.db = {}
            self.getDB() 
            if debug: for m, k in self.db.iteritems(): print "DB: Parametro: " + str(m) + " || Valor: " + srt(k)
                
        # mentor = 0 quando se trata do primeiro servidor a ser upado.
        else:
            self.rl = 0
            self.myMentor = None
            self.activeNodes = {0:str(self.port)}
            self.db = {} 
            self.makeDB() # Aquela funcao de inicializar o BD aleatoriamente
            if debug: for m, k in self.db.iteritems(): print "New DB: Parametro: " + str(m) + " || Valor: " + srt(k)

        for node in self.activeNodes.keys():
            # 'id' : fila
            self.queues[str(node)] = Queue.Queue()

        #inicia thread para o queueProcessor
        Thread(name="Thread Processadora das Filas", target=queueProcessor)
  
        #inicia thread para a servidora
        Thread(name="Thread Servidora", target=server)

    #Funcao que deixara o servidor servindo eternamente
    def server(self):
        self.servidor = SimpleXMLRPCServer(("localhost",self.port))
        self.servidor.register_instance(self)
        self.servidor.serve_forever()

    #define um novo id
    #Se um servidor capotar, seu ID sera reutilizado!!!
    def getNewId(self):
        newId = 0
        while newId in self.activeNodes.keys():
             newId = newId + 1
        return newId

    #retorna o relogio logico atual e a lista de portas e id's dos servidores disponiveis
    def getActiveList(self, port):
        newId = self.getNewId()
        self.activeNodes[newId] = port
        print "New service available in port " + port + " with ID: " + str(newId) + " by mentor with ID: " + str(self.id)

        for activeServerPort in self.activeNodes.values():
            # Atualiza dicionario de nos ativos nos outros servidores
            if (activeServerPort <> port) and (activeServerPort <> self.port):
                activeServer = xmlrpclib.ServerProxy('http://localhost:'+activeServerPort)
                activeServer.updadeActiveList(port,newId,self.id,self.rl)
        # Atualiza relogio logico
        self.rl = self.rl + 1
        print self.activeNodes
        return self.rl, newId, self.activeNodes

    # Atualiza dicionario de nos ativos
    def updateActiveList(self, port, id, fromid, rl):
        print "Updating Active Nodes List"
        print "New service available in port " + str(port) + " with ID: " + id + " by mentor with ID: " + str(fromid)
        # Adiciona um novo elemento no dicionario de filas e de nos ativos
        self.queues[str(id)] = Queue.Queue()
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
            for port,id in self.activeNodes.items():
                # Caso nao exista o primeiro elemento da fila
                if not queuesHead.has_key(str(id)):
                    if (self.queues[str(id)].isEmpty):
                        if (id == self.id):

                            if debug: print "Quero um ACK meu mesmo"
                        else:
                            waiting = 0
                            # Esperando a fila ter pelo menos um ACK
                            while (self.queues[str(id)].isEmpty):
                                if (waiting == 0):
                                    if debug: print "Pede um ack pra "+port
                                    self.sendMsg(None, "requestACK", id)
                                    waiting = 1
                    queuesHead[str(id)] = self.queues.get(str(id))

            # Encontra a mensagem com o menor relogio logico
            earliest = self.id
            for id,msg in queuesHead.items():
                if msg['rl'] <= queuesHead[str(earliest)]['rl']:
                    if id < earliest:
                        earliest = id
            earliestMsg = queuesHead.pop(earliest)
            # Processa mensagem!
            if earliestMsg['type'] == 'buy':
                print "So jogar na funcao de compra." # self.buy(earliestMsg['param'])

            elif earliestMsg['type'] == 'requestDB':
                sendMsg(self.db, 'copyDB', earliest)
                
            elif earliestMsg['type'] == 'copyDB':
                self.db = earliestMsg['param']

            elif earliestMsg['type'] == 'requestACK':
                self.sendMsg(None, "ACK", earliest)

            elif earliestMsg['type'] == 'ACK':
                if debug: print "Acabei de receber um ACK. Estou tao feliz!!!"
            # E assim por diante

    def broadcastMsg(self, param, type):
        # Monta a mensagem
        msg = {'rl': self.rl, 'type': type, 'param': param}
        # Broadcast da mensagem
        for activeServerPort in self.activeNodes.keys():
            if activeServerPort <> str(self.port):
                activeServer = xmlrpclib.ServerProxy('http://localhost:'+str(activeServerPort))
                activeServer.receiveMsg(self.id, msg)
        # Atualiza relogio logico
        self.rl = self.rl + 1
        return True

    def sendMsg(self, param, type, id):
        # Monta a mensagem
        msg = {'rl': self.rl, 'type': type, 'param': param}
        activeServer = xmlrpclib.ServerProxy('http://localhost:'+activeNodes[str(id)])
        activeServer.receiveMsg(self.id, msg)
        # Atualiza relogio logico
        self.rl = self.rl + 1
        return True

    def receiveMsg(self, id, msg):
        # Atualiza relogio logico
        if self.rl < msg['rl']: self.rl = msg['rl'] + 1
        else: self.rl = self.rl + 1
        # Insere mensagem na fila correspondente
        self.queues[str(id)].put(msg)
        return True

    def getDB(self):
        self.broadcastMsg(self.id,'requestDB')
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
    def makeBD():
        makeItens()
        i = 0
        while i < 24:
            self.newItem(random.choice(self.car),str(random.randint(1, 1000000)),random.choice(self.motor),random.choice(self.cor),str(random.randint(10000, 80000)), random.sample(self.acs,3))
            i+=1

    def inventory():
        self.car = ["Gol", "Vectra", "Panzer", "Fusca", "Bicicleta", "Moto Bis", "Land Rover", "Iate", "747", "Hammer", "Gurgel"]
        if debug: print car

        self.motor = ['XTEC 1.0 Flex','AZAP 1.6 Flex', 'AMT Turbo 2.6']
        if debug: print motor

        self.cor = ["Azul", "Verde", "Vermelho", "Laranja com pintas magenta", "Ciano"]
        if debug: print cor
        
        #Nao pode criar novos acessorios!!! Na verdade, tem q manter o numero exato de 6 acessorios (nao mais nem menos)...
        self.acs = ["Foguete", "Asa", "Vidro Eletrico", "Piloto Automatico", "Sistema de Submersao", "Rodas Quadradas"]
        if debug: print acs

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
            if debug: print "Novo carro criado: " + newdb
            self.db[id] = bd

        
    def carFinder(self, tipo, arg):
        if debug: print "Evento Interno : Aqui se procura um produto no Banco de Dados"
        #Tipo pode ser:
        #     'id' : retorna especificacao do carro
        #     'car': retorna lista com todos os modelos desse carro
        #     'cor': retorna lista com todos os modelos dessa cor
        #     'acs': retorna lista com todos os modelos com esse conjunto de acessorios
        #     'tup': retorna lista com todos os modelos que satisfazem essa tupla
        
        # tipo: dicionario com "id", "car", "motor", "cor" e "acs" = a true ou false
        # arg: argumento do tipo com mesmo nome de dicionario. No caso de acs, uma lista [] de acessórios
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
