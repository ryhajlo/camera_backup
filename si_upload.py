#!/usr/bin/python3
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
import board
import busio
import adafruit_si7021
from Adafruit_IO import Client, RequestError

def main(args):
    """Main function. Read from the sensor and upload it to adafruit."""
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_si7021.SI7021(i2c)

    temperature = sensor.temperature
    humidity = sensor.relative_humidity

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    if humidity is not None and temperature is not None:
        # Convert the temperature to Fahrenheit.
        temperature = temperature * 9/5.0 + 32
        print('Temp={0:0.1f}F  Humidity={1:0.1f}%'.format(temperature, humidity))
        
        # Upload the data
        aio = Client('ryhajlo', 'b5fe0936d9a84629a2d49cd45858fc67')
        
        try:
            aio.send('indoor-temperature', temperature)
        except RequestError:
            print("Cannot send temperature data")
        try:
            aio.send('indoor-humidity', humidity)
        except RequestError:
            print("Cannot send humidity data")
    else:
        print('Failed to get reading. Try again!')
        sys.exit(1)
    
if __name__ == "__main__":
    main(sys.argv[1:])
