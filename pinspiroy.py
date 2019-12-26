#!/usr/bin/python

from evdev import UInput, ecodes, events, AbsInfo, util
import sys,os,imp,time,imp,math
import usb.core
import usb.util

import signal
import argparse
import ConfigParser

parser = argparse.ArgumentParser(description='Install the Huion Inspiroy H320M handler.')
parser.add_argument('-q', '--quiet', required=False, action='store_true', help='Suppress output')

args = parser.parse_args()

if args.quiet:
    def do_output(s):
        pass
else:
    def do_output(s):
        print(s)

config = ConfigParser.RawConfigParser()
config.read([os.path.dirname(os.path.realpath(sys.argv[0])) + '/config.ini',os.path.expanduser('~/.pinspiroy.ini'),'./.pinspiroy.ini'])

g = {
    'LEFT_HANDED': False,
    'PRESSURE_CURVE': False,
    'FULL_PRESSURE': 1.0,
    'BUTTONS': [],
    'RBUTTONS': []
}

for b in range(11):
    g['BUTTONS'].append([])
    g['RBUTTONS'].append([])

if config.has_section('Settings'):

    if config.has_option('Settings','LEFT_HANDED'):
        g['LEFT_HANDED'] = config.getboolean('Settings','LEFT_HANDED')

    if config.has_option('Settings','PRESSURE_CURVE'):
        g['PRESSURE_CURVE'] = config.get('Settings','PRESSURE_CURVE')

    if config.has_option('Settings','FULL_PRESSURE'):
        g['FULL_PRESSURE'] = config.getfloat('Settings','FULL_PRESSURE')

    if config.has_option('Settings','MONITOR_X'):
        g['MONITOR_X'] = config.getint('Settings','MONITOR_X')

    if config.has_option('Settings','MONITOR_Y'):
        g['MONITOR_Y'] = config.getint('Settings','MONITOR_Y')

    if config.has_option('Settings','MONITOR_W'):
        g['MONITOR_W'] = config.getint('Settings','MONITOR_W')

    if config.has_option('Settings','MONITOR_H'):
        g['MONITOR_H'] = config.getint('Settings','MONITOR_H')

if config.has_section('Buttons'):

    for b in range(11):
        if config.has_option('Buttons', str(b+1)):
            g['BUTTONS'][b] = config.get('Buttons', str(b+1)).upper().split('+')


for b in range(11):
        for k in range(len(g['BUTTONS'][b])):
                if g['BUTTONS'][b][k] == 'CTRL' or g['BUTTONS'][b][k] == 'ALT' or g['BUTTONS'][b][k] == 'SHIFT':
                        g['BUTTONS'][b][k] = 'LEFT' + g['BUTTONS'][b][k]
                
        rb = g['BUTTONS'][b][:]
        rb.reverse()
        g['RBUTTONS'][b] = rb
        
#tablet config values
PEN_MAX_X = 45720
PEN_MAX_Y = 28580 
PEN_MAX_Z = 8191 	#pressure

#specify capabilities for a virtual device
#one for each device:
#pen/pad, and buttons

#pressure sensitive pen tablet area with 2 stylus buttons and no eraser
cap_pen = {
	ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_TOOL_PEN, ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2],
	ecodes.EV_ABS: [
		(ecodes.ABS_X, AbsInfo(0,0,PEN_MAX_X,0,0,5080)), #value, min, max, fuzz, flat, resolution
		(ecodes.ABS_Y, AbsInfo(0,0,PEN_MAX_Y,0,0,5080)),
		(ecodes.ABS_PRESSURE, AbsInfo(0,0,PEN_MAX_Z,0,0,0)),
		(ecodes.ABS_RX, AbsInfo(0,0,256,0,0,60)), #value, min, max, fuzz, flat, resolution
		(ecodes.ABS_RY, AbsInfo(0,0,256,0,0,60)),
        ],
	ecodes.EV_MSC: [ecodes.MSC_SCAN], #not sure why, but it appears to be needed
	}

#buttons must be defined in the same sequential order as in the Linux specs
#https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h

cap_btn = {
	ecodes.EV_KEY: [ecodes.KEY_ESC,
					ecodes.KEY_1,ecodes.KEY_2,ecodes.KEY_3,ecodes.KEY_4,ecodes.KEY_5,ecodes.KEY_6,ecodes.KEY_7,ecodes.KEY_8,ecodes.KEY_9,ecodes.KEY_0,
					ecodes.KEY_Q,ecodes.KEY_W,ecodes.KEY_E,ecodes.KEY_R,ecodes.KEY_T,ecodes.KEY_Y,ecodes.KEY_U,ecodes.KEY_I,ecodes.KEY_O,ecodes.KEY_P,ecodes.KEY_A,ecodes.KEY_S,ecodes.KEY_D,ecodes.KEY_F,ecodes.KEY_G,ecodes.KEY_H,ecodes.KEY_J,ecodes.KEY_K,ecodes.KEY_L,ecodes.KEY_Z,ecodes.KEY_X,ecodes.KEY_C,ecodes.KEY_V,ecodes.KEY_B,ecodes.KEY_N,ecodes.KEY_M,
					ecodes.KEY_MINUS,ecodes.KEY_EQUAL,ecodes.KEY_BACKSPACE,ecodes.KEY_TAB,ecodes.KEY_LEFTBRACE,ecodes.KEY_RIGHTBRACE,ecodes.KEY_ENTER,ecodes.KEY_LEFTCTRL,ecodes.KEY_SEMICOLON,ecodes.KEY_APOSTROPHE,ecodes.KEY_GRAVE,ecodes.KEY_LEFTSHIFT,ecodes.KEY_BACKSLASH,
					ecodes.KEY_COMMA,ecodes.KEY_DOT,ecodes.KEY_SLASH,ecodes.KEY_RIGHTSHIFT,ecodes.KEY_KPASTERISK,ecodes.KEY_LEFTALT,ecodes.KEY_SPACE,ecodes.KEY_CAPSLOCK,ecodes.KEY_F1,ecodes.KEY_F2,ecodes.KEY_F3,ecodes.KEY_F4,ecodes.KEY_F5,ecodes.KEY_F6,ecodes.KEY_F7,ecodes.KEY_F8,ecodes.KEY_F9,ecodes.KEY_F10,
					ecodes.KEY_NUMLOCK,ecodes.KEY_SCROLLLOCK,ecodes.KEY_KP7,ecodes.KEY_KP8,ecodes.KEY_KP9,ecodes.KEY_KPMINUS,ecodes.KEY_KP4,ecodes.KEY_KP5,ecodes.KEY_KP6,ecodes.KEY_KPPLUS,ecodes.KEY_KP1,ecodes.KEY_KP2,ecodes.KEY_KP3,ecodes.KEY_KP0,ecodes.KEY_KPDOT,
					ecodes.KEY_RIGHTALT,ecodes.KEY_LINEFEED,ecodes.KEY_HOME,ecodes.KEY_UP,ecodes.KEY_PAGEUP,ecodes.KEY_LEFT,ecodes.KEY_RIGHT,ecodes.KEY_END,ecodes.KEY_DOWN,ecodes.KEY_PAGEDOWN,ecodes.KEY_INSERT, ecodes.KEY_DELETE,
					ecodes.BTN_MOUSE, ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE]
	}

# create our 3 virtual devices
vpen 	= UInput(cap_pen, 	name="pinspiroy-pen", 		version=0x3)
vbtn	= UInput(cap_btn, 	name="pinspiroy-button", 	version=0x5)

time.sleep(0.1) # needed due to some xserver feature 

cbtn = -1 # hold current button

# reverse button order for LH setting
btn_switch_LH = [11,10,9,4,5,6,7,8,3,2,1]

# input specific functions
def id_btn(data):
        btn = data[5]*256 + data[4]
        n = -1
        while btn != 0:
                btn = btn >> 1
                n += 1
        if n == -1:
                undo_btn()
                return
	if g['LEFT_HANDED']:
                n = btn_switch_LH[n]
        do_btn(n)

def do_btn(btn):
        global cbtn
        cbtn = btn
        for k in g['BUTTONS'][btn]:
                vbtn.write(ecodes.EV_KEY,getattr(ecodes,'KEY_' + k),1)
        vbtn.syn()

def undo_btn():
        if cbtn == -1:
                return
        for k in g['RBUTTONS'][cbtn]:
                vbtn.write(ecodes.EV_KEY,getattr(ecodes,'KEY_' + k),0)
        vbtn.syn()
                
def pressure_curve(z):
	z = z/g['FULL_PRESSURE']
	if z > PEN_MAX_Z:
		z = PEN_MAX_Z
	if g['PRESSURE_CURVE'] == 'LINEAR':
		pass
	elif g['PRESSURE_CURVE'] == 'HARD':
		z = z*z/PEN_MAX_Z
	elif g['PRESSURE_CURVE'] == 'SOFT':
		z = z*math.sqrt(z)/math.sqrt(PEN_MAX_Z)
	return int(math.floor(z))

#handler for pen input
def id_pen(data):
        
	x = data[3]*256 + data[2]
	y = data[5]*256 + data[4]
	z = data[7]*256 + data[6]

        rx = data[10]
        ry = data[11]
        
	if g['PRESSURE_CURVE']:
		z = pressure_curve(z)
	#rotate coordinates if left handed
	if g['LEFT_HANDED']:
		x = PEN_MAX_X-x
		y = PEN_MAX_Y-y

	vpen.write(ecodes.EV_ABS, ecodes.ABS_X, x)
	vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, y)
	vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, z)
	vpen.write(ecodes.EV_ABS, ecodes.ABS_RX, rx)
	vpen.write(ecodes.EV_ABS, ecodes.ABS_RY, ry)


        if data[1] & 1 == 1:
                # pen is touching pad
		vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 1)
        elif data[1] & 1 == 0:
		vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
                
        if data[1] & 2 == 2:
                # stylus button 1
		vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, 1)
        elif data[1] & 2 == 0:
		vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, 0)
                
        if data[1] & 4 == 4:
                # stylus button 2
		vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, 1)
        elif data[1] & 4 == 0:
		vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, 0)

	vpen.write(ecodes.EV_KEY, ecodes.BTN_TOOL_PEN, 1)

	vpen.syn() #sync all inputs together

def clear():
        undo_btn()
        vpen.write(ecodes.EV_KEY, ecodes.BTN_TOOL_PEN, 0)
        vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
        vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, 0)
        vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, 0)
        vpen.syn()

# get unidentified huion USB device
# boilerplate USB data reading from pyusb library
dev = usb.core.find(idVendor=0x256c, idProduct=0x006d)
interface = 0
endpoint = dev[0][(0,0)][0]

try:
	usb.util.get_string(dev, 0xc8, 1033)
	do_output('Graphics tablet enabled.')
except:
	do_output('')

if dev.is_kernel_driver_active(interface) is True:
	dev.detach_kernel_driver(interface)
	usb.util.claim_interface(dev, interface)
	do_output('interface 0 grabbed')
interface = 1
if dev.is_kernel_driver_active(interface) is True:
	dev.detach_kernel_driver(interface)
	usb.util.claim_interface(dev, interface)
	do_output('interface 1 grabbed')

do_output('pinspiroy should be running!')

def gracefulExit(signum,frame):
    do_output("Exiting gracefully")
    usb.util.release_interface(dev, interface)
    sys.exit(0)

signal.signal(signal.SIGTERM, gracefulExit)
signal.signal(signal.SIGINT, gracefulExit)

while True:
	try:
		# data received as array of [0,255] ints
		data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
                if data[1] & 64 == 64:
                        id_btn(data)
                elif data[1] & 128 == 128:
                        id_pen(data)
                else:
                        clear()

	except usb.core.USBError as e:
		data = None
		if e.args == ('Operation timed out',):
				continue
