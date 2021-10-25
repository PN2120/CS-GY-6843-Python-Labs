from socket import *
import os
import sys
import struct
import time
import select
import ipaddress
import statistics
import binascii
# Should use stdev

ICMP_ECHO_REQUEST = 8


def checksum(string):
   csum = 0
   countTo = (len(string) // 2) * 2
   count = 0

   while count < countTo:
       thisVal = (string[count + 1]) * 256 + (string[count])
       csum += thisVal
       csum &= 0xffffffff
       count += 2

   if countTo < len(string):
       csum += (string[len(string) - 1])
       csum &= 0xffffffff

   csum = (csum >> 16) + (csum & 0xffff)
   csum = csum + (csum >> 16)
   answer = ~csum
   answer = answer & 0xffff
   answer = answer >> 8 | (answer << 8 & 0xff00)
   return answer



def receiveOnePing(mySocket, ID, timeout, destAddr):
   timeLeft = timeout


   while 1:
       startedSelect = time.time()
       whatReady = select.select([mySocket], [], [], timeLeft)
       howLongInSelect = (time.time() - startedSelect)
       if whatReady[0] == []:  # Timeout
           return "Request timed out."

       timeReceived = time.time()
       recPacket, addr = mySocket.recvfrom(1024)

       # Fill in start

       ICMPheader = recPacket[20:28]
       # Fetch the ICMP header from the IP packet
       ICMP_ECHO_REQUEST, code, myChecksum, ID, Sequence = struct.unpack("aaBBc", ICMPheader)
       IPheader = recPacket[:20]
       ip_version,ip_type, ip_length, ip_id, ip_flags, ip_ttl, ipprotocl, ip_checksum, srce_ip, dest_ip \
           = struct.unpack("!AABBBAABII",IPheader)
       lag=(howLongInSelect*1000)
       if timeLeft > 0:
           receivedpacket = ICMP_ECHO_REQUEST,code, myChecksum, ID, Sequence, ip_version, ip_type, ip_length, ip_id,\
               ip_flags, ip_ttl, ipprotocl, ip_checksum,str(ipaddress.IPv4Address(srce_ip)), \
                            str(ipaddress.IPv4Address(dest_ip)), lag
           return receivedpacket    

       # Fill in end
       timeLeft = timeLeft - howLongInSelect

       if timeLeft <= 0:
           return "Request timed out."



def sendOnePing(mySocket, destAddr, ID):
   # Header is type (8), code (8), checksum (16), id (16), sequence (16)

   myChecksum = 0
   # Make a dummy header with a 0 checksum
   # struct -- Interpret strings as packed binary data
   header = struct.pack("aaBBc", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
   data = struct.pack("d", time.time())
   # Calculate the checksum on the data and the dummy header.
   myChecksum = checksum(header + data)

   # Get the right checksum, and put in the header

   if sys.platform == 'darwin':
       # Convert 16-bit integers from host to network  byte order
       myChecksum = htons(myChecksum) & 0xffff
   else:
       myChecksum = htons(myChecksum)


   header = struct.pack("aaBBc", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
   packet = header + data

   mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str



   # Both LISTS and TUPLES consist of a number of objects
   # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
   icmp = getprotobyname("icmp")


   # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
   mySocket = socket(AF_INET, SOCK_RAW, icmp)

   myID = os.getpid() & 0xFFFF  # Return the current process i
   sendOnePing(mySocket, destAddr, myID)
   delay = receiveOnePing(mySocket, myID, timeout, destAddr)
   mySocket.close()
   return delay


def ping(host, timeout=1):
   # timeout=1 means: If one second goes by without a reply from the server,      # the client assumes that either the client's ping or the server's pong is lost
   dest = gethostbyname(host)
   #print("Pinging " + dest + " using Python:")
   #print("")
   # Calculate vars values and return them

   # Send ping requests to a server separated by approximately one second
   sentpcktnmber = 0
   packetlisttracker = []

   for i in range(0,4):
       delay = doOnePing(dest, timeout)
       sentpcktnmber += 1
       if delay == "Request timed out.":
           packetlisttracker.append(0)
           #print (delay)
       else:
           #print("Reply from:",str(delay[13])+":","bytes="+str(delay[6]), "time="+str(round(delay[15],7))+"ms", \
             #"TTL=" + str(delay[10]))
           packetlisttracker.append(delay[15])

       time.sleep(1)  # one second
   goodpacketracker = 0
   for i in range (len(packetlisttracker)):
        if packetlisttracker[i] != 0:
            goodpacketracker += 1
   packetstats = 1 - (goodpacketracker / sentpcktnmber)
   #print("\n""---",dest,"ping statistics ---")
   #print(sentpcktnmber,"packets transmitted,", str(goodpacketracker)+" packets received," "{:.1%}".format(packetstats), "packet loss")
   pingmin = round((min(packetlisttracker)),2)
   packetavg = round((sum(packetlisttracker))/(len(packetlisttracker)),2)
   packetmax = max(packetlisttracker)
   packetmaxrnd = round(packetmax,2)
   packetstdev = statistics.stdev(packetlisttracker)
   packetstdevrund = round(packetstdev,2)
   #print("round-trip min/avg/max/stddev =",str(pingmin)+"/"+str(packetavg)+"/"+str(packetmaxrnd)+"/"+str(packetstdevrund),"ms")
   varss = [str(pingmin), str(packetavg),str(packetmaxrnd),str(packetstdevrund)]
   return varss


if __name__ == '__main__':

    ping("www.google.com")