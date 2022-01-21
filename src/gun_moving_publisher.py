#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from minigun_lego.msg import gun_message
import os, struct, array
from fcntl import ioctl


def robot_motion_commander():
    pub = rospy.Publisher('robot_speed_topic', gun_message, queue_size=10)
    data = gun_message()
    rospy.init_node('gun_moving_publisher', anonymous=True)
    rospy.loginfo("Starting motion")
    r = rospy.Rate(100)  # 1hz

    # Iterate over the joystick devices.
    # # ('Available devices:')

    for fn in os.listdir('/dev/input'):
        if fn.startswith('js'):
            pass
            # print('  /dev/input/%s' % (fn))

    # We'll store the states here.
    axis_states = {}
    button_states = {}

    # These constants were borrowed from linux/input.h
    axis_names = {
        0x00: 'x',
        0x01: 'y',
        0x02: 'z',
        0x03: 'rx',
        0x04: 'ry',
        0x05: 'rz',
        0x06: 'throttle',
        0x07: 'rudder',
        0x08: 'wheel',
        0x09: 'gas',
        0x0a: 'brake',
        0x10: 'hat0x',
        0x11: 'hat0y',
        0x12: 'hat1x',
        0x13: 'hat1y',
        0x14: 'hat2x',
        0x15: 'hat2y',
        0x16: 'hat3x',
        0x17: 'hat3y',
        0x18: 'pressure',
        0x19: 'distance',
        0x1a: 'tilt_x',
        0x1b: 'tilt_y',
        0x1c: 'tool_width',
        0x20: 'volume',
        0x28: 'misc',
    }

    button_names = {
        0x120: 'trigger',
        0x121: 'thumb',
        0x122: 'thumb2',
        0x123: 'top',
        0x124: 'top2',
        0x125: 'pinkie',
        0x126: 'base',
        0x127: 'base2',
        0x128: 'base3',
        0x129: 'base4',
        0x12a: 'base5',
        0x12b: 'base6',
        0x12f: 'dead',
        0x130: 'a',
        0x131: 'b',
        0x132: 'c',
        0x133: 'x',
        0x134: 'y',
        0x135: 'z',
        0x136: 'tl',
        0x137: 'tr',
        0x138: 'tl2',
        0x139: 'tr2',
        0x13a: 'select',
        0x13b: 'start',
        0x13c: 'mode',
        0x13d: 'thumbl',
        0x13e: 'thumbr',

        0x220: 'dpad_up',
        0x221: 'dpad_down',
        0x222: 'dpad_left',
        0x223: 'dpad_right',

        # XBox 360 controller uses these codes.
        0x2c0: 'dpad_left',
        0x2c1: 'dpad_right',
        0x2c2: 'dpad_up',
        0x2c3: 'dpad_down',
    }

    axis_map = []
    button_map = []

    # Open the joystick device.
    fn = '/dev/input/js2'
    # print('Opening %s...' % fn)
    jsdev = open(fn, 'rb')

    # Get the device name.
    # buf = bytearray(63)
    buf = array.array('B', [0] * 64)
    ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf)  # JSIOCGNAME(len)
    js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
    print('Device name: %s' % js_name)

    # Get number of axes and buttons.
    buf = array.array('B', [0])
    ioctl(jsdev, 0x80016a11, buf)  # JSIOCGAXES
    num_axes = buf[0]

    buf = array.array('B', [0])
    ioctl(jsdev, 0x80016a12, buf)  # JSIOCGBUTTONS
    num_buttons = buf[0]

    # Get the axis map.
    buf = array.array('B', [0] * 0x40)
    ioctl(jsdev, 0x80406a32, buf)  # JSIOCGAXMAP

    for axis in buf[:num_axes]:
        axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
        axis_map.append(axis_name)
        axis_states[axis_name] = 0.0

    # Get the button map.
    buf = array.array('H', [0] * 200)
    ioctl(jsdev, 0x80406a34, buf)  # JSIOCGBTNMAP

    for btn in buf[:num_buttons]:
        btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
        button_map.append(btn_name)
        button_states[btn_name] = 0

    # print('%d axes found: %s' % (num_axes, ', '.join(axis_map)))
    # print('%d buttons found: %s' % (num_buttons, ', '.join(button_map)))

    while not rospy.is_shutdown():

        # Main event loop

        evbuf = jsdev.read(8)
        if evbuf:
            time, value, type, number = struct.unpack('IhBB', evbuf)

            if type & 0x01:
                button = button_map[number]
                if button:
                    if button == 'thumb2':
                        status = 'auto'
                    else:
                        status = 'manual'
                    data.mode = status
                    button_states[button] = value
                    if value and status == 'manual':
                        data.shot = button
                    else:
                        data.shot = ''

            if type & 0x02:
                axis = axis_map[number]
                if axis and status == 'manual':
                    fvalue = value / 32767.0
                    axis_states[axis] = fvalue
                    print(axis_states['x'], axis_states['y'])
                    # print("%s: %.3f" % (axis, fvalue
                    data.angular_z = axis_states['y']
                    data.angular_y = axis_states['x']

                    # print("%s: %.3f" % (axis, fvalue))

        # data.speed = 0.5
        # data.angle = 9.0
        # rospy.loginfo((data.speed, data.angle))

        pub.publish(data)
        r.sleep()


if __name__ == '__main__':
    try:
        robot_motion_commander()
    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")

