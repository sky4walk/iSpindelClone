#!/usr/bin/python3
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from datetime import datetime
import _thread
import time
import json
import time
import os
import sys

filename = "iSpindel.csv"
srv_port = 9501
srv_host = "0.0.0.0"
rcv_buffer = 256
rcv_ack = chr(6)
rcv_nak = chr(21)
delim = ";"
nline = "\r\n"
 
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

  while 1:
    data = clientsock.recv(rcv_buffer)
    if "close" == data.rstrip():
      clientsock.send(rcv_ack)
      print(repr(addr) + " ACK sent. Closing.")
      break
    try:
      inpstr += str(data.rstrip())
      if inpstr[0] != "{":
        clientsock.send(rcv_nak)
        dbgprint(repr(addr) + " Not JSON.")
        break
      print(repr(addr) + " Input Str is now:" + inpstr)
      if inpstr.find("}") != -1:
        jinput = json.loads(inpstr)
        spindle_name = jinput["name"]
        spindle_id   = jinput["ID"]
        angle        = jinput["angle"]
        temperature  = jinput["temperature"]
        battery      = jinput["battery"]
        try:
          gravity   = jinput["gravity"]
          interval  = jinput["interval"]
          rssi      = jinput["RSSI"]
        except:
          print ("Consider updating your iSpindel's Firmware.")
        try:
          user_token = jinput["token"]
        except:
          user_token = "*"
        try:
          with open(filename, 'a') as csv_file:
            cdt = datetime.now()
            outstr  = cdt.strftime('%x %X') + delim
            outstr += str(spindle_name) + delim
            outstr += str(spindle_id) + delim
            outstr += str(angle) + delim
            outstr += str(temperature) + delim
            outstr += str(battery) + delim
            outstr += str(gravity) + delim
            outstr += user_token + delim
            outstr += str(interval) + delim
            outstr += str(rssi) + delim
            outstr += nline
            csv_file.writelines(outstr)
            print(repr(addr) + " CSV data written")
        except Exception as e:
          print(repr(addr) + " CSV Error: " + str(e))                        
    except Exception as e:
      print(repr(addr) + " Error: " + str(e))
      clientsock.send(rcv_nak)
      print(repr(addr) + " NAK sent")
      break
    clientsock.close()
    print(repr(addr) + " closed connection")
        
def main() :
  net_addr = (srv_host, srv_port)
  serversock = socket(AF_INET, SOCK_STREAM)
  serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  serversock.bind(net_addr)
  serversock.listen(5)
  while 1:
    print("waiting for connection on port: " + str(srv_port))
    clientsock, addr = serversock.accept()
    print("connected: " + str(addr))
    _thread.start_new_thread(recv_handler, (clientsock, addr))

if __name__ == "__main__":
  main()
