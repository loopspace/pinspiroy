# pinspiroy - version for h320m

This is a fork of the original pinspiroy project adapted for the [Huion
Inspiroy H320M](https://www.huion.com/pen_tablet/H320M.html) tablet.
It was originally designed for the [Huion Inspiroy G10T](https://www.huiontablet.com/g10t.html) (which is now supported in the [DIGImend](https://digimend.github.io/) project). Note that this is not a kernel-level driver, it is a user-land implementation that creates virtual devices with uinput to mimic the tablet functionality.

## Requirements
- python2.7
- [pyusb](https://walac.github.io/pyusb/) (pip install pyusb)
- [python-evdev](https://github.com/gvalkov/python-evdev) (pip install evdev)
- [pygtk]() for screen size detection and pinwiz tool (available in via most package managers)

For distros newer than Ubuntu 16.04 you will have to append the following to your `/etc/udev/hwdb.d/61-evdev-local.hwdb` file (create the file if it does not already exist).
```
evdev:name:pinspiroy-pen*
 EVDEV_ABS_00=::5080
 EVDEV_ABS_01=::5080
```
Then run `#sudo systemd-hwdb update` to apply the changes. (thanks to [KaiJan57 for figuring this out](https://github.com/dannytaylor/pinspiroy/issues/6)).


## Usage

```
$ sudo python pinspiroy.py
```

It will look for a configuration file, called `.pinspiroy.ini`,
loading them from the current directory and the user's home directory.
Finally, it loads `config.ini` from the script directory.

Superuser privileges are required to read USB traffic.

## UDEV Installation

Getting this to run when the tablet is plugged in involves using
`udev`.  This requires copying the `pinspiroy.py` file and the scripts
in `udev/` to `/usr/local/bin` and the file `80-huion-h320m.rules` to
`/etc/udev/rules.d/`.  To use the rules without rebooting, use the
command `sudo udevadm control --reload`.

There were various hurdles to get this to work!  The first was
identifying the devices under `udev`.  The second was getting the
python script to run and stay running.  It turns out that `udev` does
not allow persistent scripts - it kills absolutely everything that it
starts.  To circumvent this I used the `at` daemon.

So the sequence of events is:

1. `udev` notices that the device has been plugged in and launches the
   `huion_added.sh` script.
2. This script schedules the `huion_launch.sh` script immediately via
   the `at` daemon.
3. The `huion_launch.sh` script launches the `pinspiroy.py` script
   (with the `quiet` flag) and saves its PID to
   `/var/run/pinspiroy.run`
4. When the device is unplugged, `udev` runs `huion_remove.sh` which
   looks in `/var/run/pinspiroy.py` for the PID of the `pinspiroy.py`
   script and sends it a TERM signal which closes it -- hopefully
   gracefully.

This meant removing the `gtk` dependency from the original script as
the display isn't set `pinspiroy.py`.

## Configuration

The format of the configuration file is:

```
[Settings]
LEFT_HANDED = False
PRESSURE_CURVE = False 
FULL_PRESSURE = 1.0 

[Buttons]
1: Ctrl+Alt+H
2: Space
3: M
4: Up
5: Down
6: Enter
7: Left
8: Right
9: Ctrl+S
10: Ctrl+Shift+Z
11: Ctrl+Z
```

The buttons are configured as follows: 1,2,3 are the top three;
4,5,6,7,8 are the "wheel"; 9,10,11 are the bottom three.

## Troubleshooting
This program requires the uinput module to be loaded. Either manually (_sudo modprobe uinput_)
or automatically on boot; [see the Arch wiki](https://wiki.archlinux.org/index.php/Kernel_modules).

**Insufficient permissions:** This program requires root access to read USB data (pyusb/libusb). You could add this to your sudoers file to run at start without password entry, but that is not recommended for security reasons.

**Pen not moving on contact, buttons and trackpad working:** This seems to be a problem with libinput requiring a pen resolution; changing the resolution with python-evdev doesn't seem to work. Check that you don't have a libinput driver catchall rule for tablets in your xorg.conf.d/. You may need a evdev driver catchall rule for tablets.

**Key error: NUM:** Run the debug.py file to see the array data the tablet is sending. The first array value should be 8. If it isn't (probably will be 10) the tablet isn't in full tablet mode. See usage section.

**Modules not found:** Make sure you're installing the modules with the same version of python you're running the script with.

Still working out some of the problems, but feel free to tweet @ me or open an issue.

## Thanks and Additional Reading
- Original code due to [Danny Taylor](https://github.com/dannytaylor)
- Thanks [@KaiJan57](https://github.com/KaiJan57) for the magic code to get around the Windows VM requirement and also the hwdb.d fix for recent distros.
- Thanks [@DevinPentecost](https://github.com/DevinPentecost) for general python help
- [event codes for uinput use can be found here](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h)
- [more event code information found here](https://www.kernel.org/doc/Documentation/input/event-codes.txt)
- [useful tutorial for writing a USB driver with PyUSB](https://www.linuxvoice.com/drive-it-yourself-usb-car-6/)
- [writing a uinput tablet driver in C](http://gerev.github.io/laptop-cintiq/)
