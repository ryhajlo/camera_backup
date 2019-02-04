#!/usr/bin/python3
import time
import board
import busio
import digitalio
import smbus
import sys
import os
import errno
import adafruit_bmp280
import adafruit_ccs811
from Adafruit_IO import Client, RequestError
import RPi.GPIO as GPIO
from timeout import timeout

def main(args):
    aio = Client('ryhajlo', 'b5fe0936d9a84629a2d49cd45858fc67')
    CCS811_RESET_GPIO = 17
    GPIO.setup(CCS811_RESET_GPIO, GPIO.OUT)
    GPIO.output(CCS811_RESET_GPIO, True)

    i2c_bus = busio.I2C(board.SCL, board.SDA)
    try:
        ccs811_sensor = adafruit_ccs811.CCS811(i2c_bus)

        while not ccs811_sensor.data_ready:
            pass
        temp = ccs811_sensor.temperature
        ccs811_sensor.temp_offset = temp - 25.0
        print("CCS811 temperature offset: " + str(temp))
        # Read three times
        for x in range(0, 3):
            print("Reading " + str(x))
            while not ccs811_sensor.data_ready:
                pass
            eco2 = ccs811_sensor.eco2
            tvoc = ccs811_sensor.tvoc
            temperature = ccs811_sensor.temperature
            time.sleep(0.5)
        while True:
            print("Gathering Data")
            gather_data(aio, ccs811_sensor)
            print("Sleeping for 60 seconds")
            time.sleep(60)
    except RuntimeError:
        GPIO.output(CCS811_RESET_GPIO, False)
        sys.exit("Resetting CCS811")

@timeout(55, os.strerror(errno.ETIMEDOUT))
def gather_data(aio, ccs811_sensor):
    (temperature, pressure) = get_bmp280_data()

    if temperature < 120 and temperature > 20 and pressure > 950 and pressure < 1070:
        try:
            aio.send('pressure', pressure)
        except RequestError:
            print("Cannot send temperature data")

    print('Internal Temperature: {} degrees F'.format(temperature))
    print('Pressure: {}hPa'.format(pressure))

    temperature = get_arduino_temperature(0x0A)
    if temperature and temperature < 150 and temperature > 20:
        print("Temperature: " + str(temperature))
        try:
            aio.send('external-temperature', str(temperature))
        except RequestError:
            print("Cannot send data")
    else:
        print("No temperature read")
    print('External Temperature: {} degrees F'.format(temperature))
    
    moisture = get_arduino_moisture(0x0A)
    if moisture < 32000:
        print("moisture-0x0a: " + str(moisture))
        try:
            aio.send('moisture-0x0a', str(moisture))
        except RequestError:
            print("Cannot send data")
    else:
        print("No moisture-0x0a read")
    
    (eco2, tvoc, temperature) = get_ccs811_data(ccs811_sensor)
    if temperature and temperature < 150 and temperature > 20:
        print("Temperature: " + str(temperature))
        try:
            aio.send('ccs811-eco2', str(eco2))
            aio.send('ccs811-tvoc', str(tvoc))
        except RequestError:
            print("Cannot send data")
    print("CO2: %1.0f PPM" % eco2)
    print("TVOC: %1.0f PPM" % tvoc)
    print("Temp: %0.1f C" % temperature)

def get_bmp280_data():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.D4)
    bmp280_sensor = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs)
    print("Reading temperature from BMP280")
    temperature = bmp280_sensor.temperature * 1.8 + 32.0
    print("Reading pressure from BMP280")
    pressure = bmp280_sensor.pressure
    return (temperature, pressure)

def get_ccs811_data(ccs811_sensor):
    """Read from the CCS811"""
    print("Reading CCS811")
    
    # Read three times
    for x in range(0, 3):
        print("Reading " + str(x))
        while not ccs811_sensor.data_ready:
            pass
        eco2 = ccs811_sensor.eco2
        tvoc = ccs811_sensor.tvoc
        temperature = ccs811_sensor.temperature
        time.sleep(0.5)
    while not ccs811_sensor.data_ready:
        pass
    eco2 = ccs811_sensor.eco2
    tvoc = ccs811_sensor.tvoc
    temperature = ccs811_sensor.temperature * 1.8 + 32.0
    print("CO2: %1.0f PPM" % eco2)
    print("TVOC: %1.0f PPM" % tvoc)
    print("Temp: %0.1f F" % temperature)
    
    return (eco2, tvoc, temperature)

def get_arduino_temperature(device_address):
    """Read temperature from arduino"""
    print("Reading arduino temperature")
    bus=smbus.SMBus(1)
    data_array = bus.read_i2c_block_data(device_address, 0x01, 4)

    raw_temperature = data_array[0]
    raw_temperature |= data_array[1] << 8
    raw_temperature |= data_array[2] << 16
    raw_temperature |= data_array[3] << 24
    return (raw_temperature/10000.0) * 1.8 + 32.0

def get_arduino_moisture(device_address):
    """Read temperature from arduino"""
    print("Reading arduino temperature")
    bus=smbus.SMBus(1)
    moisture = bus.read_word_data(device_address, 0x02)
    return moisture

if __name__ == "__main__":
    main(sys.argv[1:])

