#import socket module
from socket import *
import sys # In order to terminate the program

def webServer(port=13331):

   serverSocket = socket(AF_INET, SOCK_STREAM)
   #Prepare a server socket
   #Fill in start
   serverSocket.bind(('localhost', port))
   serverSocket.listen(5)
   #Fill in end

   while True:
     #Establish the connection
     connectionSocket, addr = serverSocket.accept()
     try:
       message = connectionSocket.recv(1024).decode()
       filename = message.split()[1]
       f = open(filename[1:], "r")
       outputdata = f.read()
       f.close()
       
       connectionSocket.send(bytes('HTTP/1.0 200 OK\r\n\r\n','UTF-8'))

       for i in range(0, len(outputdata)):
         connectionSocket.send(outputdata[i].encode())
       connectionSocket.send("\r\n\r\n".encode())
       connectionSocket.close()


     except IOError:
       connectionSocket.send(bytes('HTTP/1.1 404 File Not Found\r\n\r\n','UTF-8'))
       connectionSocket.send(bytes('404 File Not Found','UTF-8'))
       connectionSocket.close()
      
      
   serverSocket.close()
   sys.exit()  # Terminate the program after sending the corresponding data


if __name__ == "__main__":

   webServer(13331)