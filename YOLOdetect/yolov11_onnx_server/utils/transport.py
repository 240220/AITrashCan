# import serial as ser
import time
a = "test01"
# se =ser.Serial("/dev/ttyTHS1",9600,timeout=1)
while True:
    c = b'x05'
    print(c)
  #  se.write(a.encode())
    time.sleep(2)
    print("send ok")
   #  print(se.is_open)

# sudo apt-get install python3-serial
# sudo chmod 777 /dev/ttyTHS1