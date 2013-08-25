#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import os
import random

DEBUG = 1
GPIO.setmode(GPIO.BCM)


def slowspiwrite(clockpin, datapin, byteout):
    GPIO.setup(clockpin, GPIO.OUT)
    GPIO.setup(datapin, GPIO.OUT)
    for i in range(8):
        if (byteout & 0x80):
            GPIO.output(datapin, True)
        else:
            GPIO.output(clockpin, False)
        byte <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

SPICLK = 18
SPIDO = 17


class Strip(object):
    '''
    desc
    '''
    def __init__(self, pixelnum):
        self.pixels = [0] * pixelnum

    def writestrip(self):
        '''
        Send LED color/toggle data to the LED strip
        '''
        spidev = file("/dev/spidev0.0", "w")
        for i in range(len(self.pixels)):
            spidev.write(chr((self.pixels[i] >> 16) & 0xFF))
            spidev.write(chr((self.pixels[i] >> 8) & 0xFF))
            spidev.write(chr(self.pixels[i] & 0xFF))
        spidev.close()
        time.sleep(0.002)

    def Color(self, r, g, b):
        '''
        RGB representation of a LED color - each value on a scale of 1 - 255
        '''
        return ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)

    def setpixelrgb(self, n, r, g, b):
        '''
        Set pixel (n) to the RGB color value formed by Color(r, g, b)
        '''
        if (n >= len(self.pixels)):
            return
        self.pixels[n] = self.Color(r, g, b)

    def setpixelcolor(self, n, c):
        '''
        Set pixel (n) to the RGB color value given by the param (c)
        '''
        if (n >= len(self.pixels)):
            return
        self.pixels[n] = c

    def colorwipe(self, c, delay):
        '''
        Step through each pixel in an LED stand and set it to Color (c)
        '''
        for i in range(len(self.pixels)):
            self.setpixelcolor(i, c)
            self.writestrip()
            time.sleep(delay)

    def Wheel(self, WheelPos):
        if (WheelPos < 85):
            return self.Color(WheelPos * 3, 255 - WheelPos * 3, 0)
        elif (WheelPos < 170):
            WheelPos -= 85
            return self.Color(255 - WheelPos * 3, 0, WheelPos * 3)
        else:
            WheelPos -= 170
            return self.Color(0, WheelPos * 3, 255 - WheelPos * 3)

    def rainbowCycle(self, wait):
        for j in range(256):  # one cycle of all 256 colors in the wheel
            for i in range(len(self.pixels)):
                self.setpixelcolor(i, self.Wheel(
                    ((i * 256 / len(self.pixels)) + j) % 256))
            self.writestrip()
            time.sleep(wait)

    def singleColorChase(self, c, length, delay):
        '''
        Light up (length) pixels and shift them +1 every (delay) seconds, 
        wrapping around when they reach the end of the strand.
        '''
        i = 0
        while True:
            for j in range(length):
                # lights up (length)*pixels
                # NEED TO shift over +1 -> turn off pixel (i)
                # Need to mod the target pixel by len(pixels) to wrap around
                self.setpixelcolor((i+j) % (len(self.pixels)), c)
            if i > 0:
                self.setpixelcolor((i-1), self.Color(0, 0, 0))
            self.writestrip()
            # Mod by len(pixels) to wrap around
            i = (i+1) % len(self.pixels)
            time.sleep(delay)

    def overlappingChase(self, delay, colors=None):
        '''
        Light up a new pixel after (delay) seconds, wrapping around the strand
        back to pixel 1 when it reaches the end and generates a new color or 
        chooses randomly from the provided (colors) list.
        '''
        while True:
            if colors is not None:
                color = random.choice(colors)
            else:
                color = self.Color(random.randint(1, 255),
                                    random.randint(1, 255),
                                    random.randint(1, 255))
            for i in range(len(self.pixels)):
                self.setpixelcolor(i, color)
                self.writestrip()
                time.sleep(delay)

Strip = Strip(25)
Strip.colorwipe(Strip.Color(255, 0, 0), 0.05)
Strip.colorwipe(Strip.Color(0, 255, 0), 0.05)
Strip.colorwipe(Strip.Color(0, 0, 255), 0.05)

while True:
    try:
        Strip.rainbowCycle(0.00)
        #Strip.singleColorChase(Strip.Color(255, 0, 0), 3, 0.1)
        #Strip.overlappingChase(0.02)
    except (KeyboardInterrupt, SystemExit):
        print '\r\n --Exiting-- \r\n'
        Strip.colorwipe(Strip.Color(0, 0, 0), 0)
        break

