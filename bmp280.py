#!/usr/bin/python3
import board
import busio
import digitalio
import pigpio
import sys
import adafruit_bmp280
from Adafruit_IO import Client, RequestError

def main(args):
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

    print('Internal Temperature: {} degrees F'.format(temperature)) 
    print('Pressure: {}hPa'.format(pressure))
        
    temperature = get_arduino_temperature(0x08)
    if temperature and temperature < 150 and temperature > -150:
        print("Temperature: " + str(temperature))
        try:
            aio.send('external-temperature', str(temperature))
        except RequestError:
            print("Cannot send data")
    else:
        print("No temperature read")

    print('External Temperature: {} degrees F'.format(temperature)) 

def get_arduino_temperature(device_address):
    """Read temperature from arduino"""
    pi = pigpio.pi()
    h = pi.i2c_open(1, device_address)

    pi.i2c_write_device(h, [0x01])
    (count, data) = pi.i2c_read_device(h, 2)
    pi.i2c_close(h)

    if count >= 2:
        raw_temperature = data[1] << 8
        raw_temperature |= data[0]

        return (raw_temperature/10.0) * 1.8 + 32.0
    else:
        return None

if __name__ == "__main__":
    main(sys.argv[1:])

