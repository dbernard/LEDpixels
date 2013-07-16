#!/usr/bin/env python

import RPi.GPIO as GPIO, time, os
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

ledpixels = [0] * 25

def writestrip(pixels):
	'''
	Send LED color/toggle data to the LED strip
	'''
	spidev = file("/dev/spidev0.0", "w")
	for i in range(len(pixels)):
		spidev.write(chr((pixels[i]>>16) & 0xFF))
		spidev.write(chr((pixels[i]>>8) & 0xFF))
		spidev.write(chr(pixels[i] & 0xFF))
	spidev.close()
	time.sleep(0.002)

def Color(r, g, b):
	'''
	RGB representation of a LED color - each value on a scale of 1 - 255
	'''
	return ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)

def setpixelcolor(pixels, n, r, g, b):
	'''
	Set pixel (n) to the RGB color value formed by Color(r, g, b)
	'''
	if (n >= len(pixels)):
		return
	pixels[n] = Color(r,g,b)

def setpixelcolor(pixels, n, c):
	'''
	Set pixel (n) to the RGB color value given by the param (c)
	'''
	if (n >= len(pixels)):
		return
	pixels[n] = c

def colorwipe(pixels, c, delay):
	'''
	Step through each pixel in an LED stand and set it to Color (c)
	'''
	for i in range(len(pixels)):
		setpixelcolor(pixels, i, c)
		writestrip(pixels)
		time.sleep(delay)

def Wheel(WheelPos):
	if (WheelPos < 85):
		return Color(WheelPos * 3, 255 - WheelPos * 3, 0)
	elif (WheelPos < 170):
		WheelPos -= 85;
		return Color(255 - WheelPos * 3, 0, WheelPos * 3)
	else:
		WheelPos -= 170;
		return Color(0, WheelPos * 3, 255 - WheelPos * 3)

def rainbowCycle(pixels, wait):
	for j in range(256): # one cycle of all 256 colors in whe wheel
		for i in range(len(pixels)):
			setpixelcolor(pixels, i, Wheel( ((i * 256 / len(pixels)) + j) % 256) )
		writestrip(pixels)
		time.sleep(wait)

def singleColorChase(pixels, c, length, delay):
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
			setpixelcolor(pixels, (i+j)%(len(pixels)), c)
		if i > 0:
			setpixelcolor(pixels, (i-1), Color(0,0,0))
		writestrip(pixels)
		# Mod by len(pixels) to wrap around
		i = (i+1)%len(pixels)
		time.sleep(delay)

def overlappingChase(pixels, delay, colors=None):
	'''
	Light up a new pixel after (delay) seconds, wrapping around the strand
	back to pixel 1 when it reaches the end and generates a new color or 
	chooses randomly from the provided (colors) list.
	'''
	while True:
		if colors is not None:
			color = random.choice(colors)
		else:
			color = Color(random.randint(1, 255),
					random.randint(1, 255),
					random.randint(1, 255))
		for i in range(len(pixels)):
			setpixelcolor(pixels, i, color)
			writestrip(pixels)
			time.sleep(delay)

def randColorFade(pixels, wait):
	pass

colorwipe(ledpixels, Color(255, 0, 0), 0.05)
colorwipe(ledpixels, Color(0, 255, 0), 0.05)
colorwipe(ledpixels, Color(0, 0, 255), 0.05)

while True:
	try:
#		rainbowCycle(ledpixels, 0.00)
#		singleColorChase(ledpixels, Color(255, 0, 0), 3, 0.5)
		overlappingChase(ledpixels, 0.02)
	except (KeyboardInterrupt, SystemExit):
		print 'Exiting...'
		break

