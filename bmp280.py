#!/usr/bin/python3
import board
import busio
import digitalio
import adafruit_bmp280
from Adafruit_IO import Client, RequestError

aio = Client('ryhajlo', 'b5fe0936d9a84629a2d49cd45858fc67')

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D4)
sensor = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs)

temperature = sensor.temperature * 1.8 + 32.0
pressure = sensor.pressure

try:
    aio.send('internal-temperature', temperature)
except RequestError:
    print("Cannot send temperature data")

try:
    aio.send('pressure', pressure)
except RequestError:
    print("Cannot send temperature data")
    
print('Temperature: {} degrees F'.format(temperature)) 
print('Pressure: {}hPa'.format(pressure))
