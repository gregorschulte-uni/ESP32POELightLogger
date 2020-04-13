import machine
import network
import ubinascii
import socket
import time
import onewire
import ds18x20
import apikey

ds_pin = machine.Pin(16)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()

print('Found DS devices: ', roms)

if len(roms)!=0:
    ds_sensor.convert_temp()

    for rom in roms:
        print(rom)
        print(ds_sensor.read_temp(rom))



adc = machine.ADC(machine.Pin(35))

adc.atten(machine.ADC.ATTN_11DB)

lan = network.LAN(mdc = machine.Pin(23), mdio = machine.Pin(18), power=machine.Pin(12), phy_type = network.PHY_LAN8720, phy_addr=0, clock_mode=network.ETH_CLOCK_GPIO17_OUT)

mac = ubinascii.hexlify(network.LAN().config('mac'),':').decode()
print(mac)

if lan.active(1):
    print("LAN Active")
    print(lan.ifconfig())
else:
    print("lan not active")
    
print("ipAdress:",lan.ifconfig()[0])



gotIP = False

while gotIP == False:
    if lan.ifconfig()[0]!='0.0.0.0':
        gotIP = True
    else:
        time.sleep(1)
        lan.active(1)
        print("ipAdress:",lan.ifconfig()[0])

        
    



def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()





while True:
    
    lightValue = 4095 - adc.read()
    if len(roms)!=0:
        ds_sensor.convert_temp()
        for rom in roms:
            print(rom)
            print(ds_sensor.read_temp(rom))
            temperatureValue = ds_sensor.read_temp(rom)
    urlString = 'http://api.thingspeak.com/update?api_key='+apikey.key
    urlString = urlString+'&field3='+str(lightValue)+'&field4='+str(temperatureValue)
    print(urlString)
    http_get(urlString)
    time.sleep(500)
    