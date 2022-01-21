GNU
nano
2.9
.3
src / minigun_lego / src / gun_subscriber.py

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import Float32
from minigun_lego.msg import gun_message
import RPi.GPIO as GPIO

pwm_z = 12
pwm_y = 13

in1_z = 16
in2_z = 26

in1_y = 21
in2_y = 20

in3_x = 5
in4_x = 6
pwm_x = 11

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(pwm_z, GPIO.OUT)
GPIO.setup(pwm_y, GPIO.OUT)
GPIO.setup(in1_z, GPIO.OUT)
GPIO.setup(in2_z, GPIO.OUT)
GPIO.setup(in1_y, GPIO.OUT)
GPIO.setup(in2_y, GPIO.OUT)
GPIO.setup(in3_x, GPIO.OUT)
GPIO.setup(in4_x, GPIO.OUT)
GPIO.setup(pwm_x, GPIO.OUT)
k = 30
z = GPIO.PWM(pwm_z, 50)
z.start(0)
y = GPIO.PWM(pwm_y, 50)
y.start(0)


def limiter(value, min=-100, max=100):
    return min if value < min else max if value > max else value


def move(speed_y, speed_z):
    if speed_y < 0:
        GPIO.output(in1_y, GPIO.HIGH)
        GPIO.output(in2_y, GPIO.LOW)
    else:
        GPIO.output(in1_y, GPIO.LOW)
        GPIO.output(in2_y, GPIO.HIGH)
    if speed_z > 0:
        GPIO.output(in1_z, GPIO.HIGH)
        GPIO.output(in2_z, GPIO.LOW)
    else:
        GPIO.output(in1_z, GPIO.LOW)
        GPIO.output(in2_z, GPIO.HIGH)
    z.ChangeDutyCycle(abs(speed_z))
    y.ChangeDutyCycle(abs(speed_y))


def shot(status):
    if status == 'trigger':
        GPIO.output(in4_x, GPIO.HIGH)
        GPIO.output(in3_x, GPIO.LOW)
        GPIO.output(pwm_x, GPIO.HIGH)
    else:
        GPIO.output(in4_x, GPIO.LOW)
        GPIO.output(in3_x, GPIO.LOW)
        GPIO.output(pwm_x, GPIO.LOW)


def chatter_callback(message):
    global k
    # rospy.loginfo(message.status)
    speed_z = limiter(k * message.angular_y)
    speed_y = limiter(k * message.angular_z)
    # if message.shot == 'trigger':
    shot(message.shot)
    move(speed_y, speed_z)


def listener():
    rospy.init_node('gun_subscriber', anonymous=True)
    rospy.Subscriber('robot_speed_topic', gun_message, chatter_callback)
    rospy.spin()


if __name__ == '__main__':
    listener()

