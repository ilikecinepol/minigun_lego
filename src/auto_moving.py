  GNU nano 4.8                                                                                                                                                                                                                                                                                                                                                                                                                                                  auto_guidance.py                                                                                                                                                                                                                                                                                                                                                                                                                                                            
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import rospy
from minigun_lego.msg import gun_message
import os, struct, array
from fcntl import ioctl

cap = cv2.VideoCapture(0)


def videostreaming():
    global cap
    pub = rospy.Publisher('robot_speed_topic', gun_message, queue_size=10)
    data = gun_message()
    rospy.init_node('gun_moving_publisher', anonymous=True)
    # rospy.loginfo("Starting motion")
    r = rospy.Rate(100)  # 1hz
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # cv2.imshow('original', img)
    try:
        h, w = img.shape[0], img.shape[1]
        hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        goal_x = int(w / 2)
        goal_y = int(h / 2)
    except:
        pass
    color = (
        (50, 50, 55),  # Минимальная граница значений
        (80, 255, 197)  # Максимальная граница значений
    )
    img_mask = cv2.inRange(hsv_image, color[0], color[1])
    contours, _ = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    drawing = img.copy()
    if contours:
        for cnt in contours:
            # с помощью данного условия мы можем отсеять слишком маленькие контуры, у которых слишком маленькая площадь
            area = cv2.contourArea(cnt)
            if cv2.contourArea(cnt) < 1000:
                continue

            print(cv2.contourArea(cnt))
            cv2.drawContours(drawing, [cnt], 0, (0, 0, 255), 2)

            # Определяем геометрический центр контура с момощью "моментов изображения"
            moments = cv2.moments(cnt)

            try:
                x = int(moments['m10'] / moments['m00'])
                y = int(moments['m01'] / moments['m00'])
                cv2.circle(drawing, (x, y), 4, (0, 255, 255), -1)
                # print(x, y)s
                # depth_er = keep_depth(goal_y, y)
                # yaw_er = set_yaw(goal_x, x)
                if area > 15000:
                    pass
            except ZeroDivisionError:
                pass
    try:
        cv2.line(drawing, (int(w / 2), 0), (int(w / 2), h), (0, 0, 255), 3)
        cv2.line(drawing, (0, int(h / 2)), (w, int(h / 2)), (0, 0, 255), 3)
        cv2.line(drawing, (goal_x, y), (x, y), (255, 255, 255), 3)
        cv2.line(drawing, (x, goal_y), (x, y), (255, 255, 255), 3)
        font = cv2.FONT_HERSHEY_SIMPLEX
        data.angular_z =(goal_y - y)  / 2 
        data.angular_y = (x - goal_x) / 15  
        rospy.loginfo(data.angular_y)
        rospy.loginfo(data.angular_z)
        # cv2.putText(drawing, str(depth_er), (goal_x, y), font, 0.5, (255, 255, 255), 2)
        # cv2.putText(drawing, str(yaw_er), (x, goal_y), font, 0.5, (255, 255, 255), 2)
    except:
        pass
    pub.publish(data)
    r.sleep()


if __name__ == '__main__':
    while not rospy.is_shutdown():
        try:
            videostreaming()
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
        except rospy.ROSInterruptException:
            rospy.loginfo("node terminated")
