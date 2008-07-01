from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Thread
import xmlrpclib
import Queue

#Resumo da estrutura das principais variaveis:
#  activeNodes -> {"string:port" : string:id, ... }
#  queues      -> {"string:id" : Queue(), ... }
#  msg         -> {"'rl'" : int:timestamp, "'type'" : string:type, "'param'" : list:args}
#  bd          -> { , ...  }

debug = True

class Server(Thread):
    def __init__(self, port, mentor):
        self.queues = {}
        self.port = port
        if mentor <> 0:
            # Algum host ativo sera passado por parametro como mentor do novo host.
            self.myMentor = xmlrpclib.ServerProxy('http://localhost:'+str(mentor))
            # 'porta' : id
            self.rl, self.activeNodes = self.mentor.getActiveList(self.port)
            if debug: print "Relogio Logico atual: " + str(self.rl)
            if debug: for m, k in self.activeNodes.iteritems(): print "A porta " + m + " esta associada ao id " + k
            # Atualiza relogio logico
            self.rl = self.rl + 1
            self.db = {}
            self.getDB() 
            if debug: for m, k in self.db.iteritems(): print "DB: Parametro: " + str(m) + " || Valor: " + srt(k)
                
        # mentor = 0 quando se trata do primeiro servidor a ser upado.
        else:
            self.rl = 0
            self.myMentor = None
            self.activeNodes = {str(self.port):0}
            self.db = {} # Aquela funcao de inicializar o BD aleatoriamente
            self.makeDB()
            if debug: for m, k in self.db.iteritems(): print "New DB: Parametro: " + str(m) + " || Valor: " + srt(k)


        for node in self.activeNodes.values():
            # 'id' : fila
            self.queues[str(node)] = Queue.Queue()
        self.id = self.activeNodes[self.port]

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
        while newId in self.activeNodes.values():
             newId = newId + 1
        return newId

    #retorna o relogio logico atual e a lista de portas e id's dos servidores disponiveis
    def getActiveList(self, port):
        newId = self.getNewId()
        self.activeNodes[str(port)] = newId
        print "New service available in port " + str(port) + " with ID: " + str(newId) + " by mentor with ID: " + str(self.id)

        for activeServerPort in self.activeNodes.keys():
            # Atualiza dicionario de nos ativos nos outros servidores
            if (activeServerPort <> str(port)) and (activeServerPort <> str(self.port)):
                activeServer = xmlrpclib.ServerProxy('http://localhost:'+str(activeServerPort))
                activeServer.updadeActiveList(port,newId,self.id,self.rl)
        # Atualiza relogio logico
        self.rl = self.rl + 1
        print self.activeNodes
        return self.rl,self.activeNodes

    # Atualiza dicionario de nos ativos
    def updateActiveList(self, port, id, fromid, rl):
        print "Updating Active Nodes List"
        print "New service available in port " + str(port) + " with ID: " + id + " by mentor with ID: " + str(fromid)
        # Adiciona um novo elemento no dicionario de filas e de nos ativos
        self.queues[str(id)] = Queue.Queue()
        self.activeNodes[str(port)] = id
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
                            print "Quero um ACK meu mesmo"
                        else:
                            waiting = 0
                            # Esperando a fila ter pelo menos um ACK
                            while (self.queues[str(id)].isEmpty):
                                if (waiting == 0):
                                    print "Pede um ack pra "+port
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
                sendDBCopy(earliestMsg['param'])

            elif earliestMsg['type'] == 'copyDB':
                self.db = earliestMsg['param']
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
        broadcastMsg(self.port,'requestDB')
        return True

    def sendDBCopy(self,port):
        msg = {'rl': self.rl, 'type': 'copyDB', 'param': self.db}
        activeServer = xmlrpclib.ServerProxy('http://localhost:' + str(port))
        activeServer.receiveMsg(self.id, msg)
        # Atualiza relogio logico
        self.rl = self.rl + 1
        return True

    # Esse eh pro cliente acessar
    def sell(self, param):
        # Param == id ?!?! vcs quem sabem
        self.broadcastMsg(param, "buy")
        return True

    # Esse aqui eh o que o server acessa quando ele processa uma mensagem de compra da fila!
    def buy(self,id):
        # Sei la
        return True



