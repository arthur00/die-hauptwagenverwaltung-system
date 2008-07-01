from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib

from threading import Thread
from Queue import Queue
import random
import time

def fillQueue():
    a = 0
    print "Entrou na Criadora"
    while (a < n):
        time.sleep(random.randint(0, 5))
        z = random.choice(list)
        m = random.randint(5, 1000)
        print getname() + " " + str(m) + " created in Queue " + z 
        z.put(m)
        a += 1

def processQueue():
    a = 0
    print "Entrou na Processadora"
    while (a < n):
        time.sleep(random.randint(0, 1))
        if not queue.empty():
            m = queue.get()
            print "Number: " + str(m) + " processed"
        a += 1

def servidora():
    feliz = SimpleXMLRPCServer(("localhost",8056))
    feliz.register_instance(self)
    feliz.serve_forever()    

n = 10
list = []
list.append(Queue())
list.append(Queue())
list.append(Queue())
list.append(Queue())
list.append(Queue())

Thread(name="Servidora", target=servidora)
time.sleep(1)

m = xmlrpclib.ServerProxy('http://localhost:'+'8056')
m.fillQueue()


#print "Queue criada"
#for i in range(0,1):
#    t = Thread(name="Criadora %d" % i, target=fillQueue).start()

#time.sleep(5)
#Thread(name="Processadora", target=processQueue).start()

        
