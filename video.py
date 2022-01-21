import cv2
cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()

    # cv2.imshow('original', img)
    h, w = img.shape[0], img.shape[1]
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    goal_x = int(w / 2)
    goal_y = int(h / 2)

    color = (
        (35, 0, 0),  # Минимальная граница значений
        (70, 255, 255)  # Максимальная граница значений
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
    cv2.line(drawing, (int(w / 2), 0), (int(w / 2), h), (0, 0, 255), 3)
    cv2.line(drawing, (0, int(h / 2)), (w, int(h / 2)), (0, 0, 255), 3)
    cv2.line(drawing, (goal_x, y), (x, y), (255, 255, 255), 3)
    cv2.line(drawing, (x, goal_y), (x, y), (255, 255, 255), 3)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.putText(drawing, str(depth_er), (goal_x, y), font, 0.5, (255, 255, 255), 2)
    # cv2.putText(drawing, str(yaw_er), (x, goal_y), font, 0.5, (255, 255, 255), 2)
    cv2.imshow('contour', drawing)

    # cv2.imshow('rez', img)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break