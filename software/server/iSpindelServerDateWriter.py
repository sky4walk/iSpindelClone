#!/usr/bin/python3
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from datetime import datetime
import _thread
import time
import json
import time
import os
import sys

#-------------variablen------------------
filepath   = "/home/pi/Diskstation/Andre/projekte/"
srv_port   = 9501
delim      = ","
nline      = "\r\n"
rcv_buffer = 256
#-------------variablen------------------
 
def recv_handler(clientsock, addr) :
  inpstr = ""
  spindle_name = ""
  spindle_id = 0
  angle = 0.0
  temperature = 0.0
  battery = 0.0
  gravity = 0.0
  user_token = ""
  interval = 0
  rssi = 0
  inpstr = ""
  
  while 1:
    data = clientsock.recv(rcv_buffer)
    inpstr += str(data.rstrip().decode("utf-8"))
    if not data: break    

   
  clientsock.close()
  
  if inpstr[0] == "{":
    if inpstr.find("}") != -1:
      jinput = json.loads(inpstr)
      spindle_name = jinput["name"]
      spindle_id   = jinput["ID"]
      angle        = jinput["angle"]
      temperature  = jinput["temperature"]
      battery      = jinput["battery"]
      try:
        gravity = jinput['gravity']
        interval = jinput['interval']
        rssi = jinput['RSSI']
      except:
        print("old fw")
      try:
        user_token = jinput['token']
      except:
        user_token = '*'        
      try:
        with open(filepath+str(spindle_name)+".csv", 'a') as csv_file:
          cdt = datetime.now()
          outstr  = cdt.strftime("D:%x,C:%X") + delim
          outstr += "A:"+str(angle)       + delim
          outstr += "G:"+str(gravity)     + delim
          outstr += "T:"+str(temperature) + delim
          outstr += "B:"+str(battery)     + delim
          outstr += "I:"+str(interval)    + delim
          outstr += nline
          csv_file.writelines(outstr)
          print(outstr)
          print(repr(addr) + " CSV data written")
      except IOError:
        print(repr(addr) + " CSV Error: ")
    
def main() :
  net_addr = ("0.0.0.0", srv_port)
  serversock = socket(AF_INET, SOCK_STREAM)
  serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  serversock.bind(net_addr)
  serversock.listen(5)
  while 1:
    print("waiting for connection on port: " + str(srv_port))
    clientsock, addr = serversock.accept()
    print("connected: " + str(addr))
    _thread.start_new_thread(recv_handler, (clientsock, addr))

main()
