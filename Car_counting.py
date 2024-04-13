import sys
from ultralytics import YOLO #YOLOv8
import cv2
import math

# Phát hiện đối tượng
def get_object(frame):
    detected_frame = model(frame, stream=True)
    boxes = []

    for i in detected_frame:
        obj_pos = i.boxes
        for box in obj_pos:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            currentClass = classNames[cls]
            box = [x1, y1, w, h, conf, currentClass]
            boxes.append(box)

 
    return boxes

# Lấy thông tin đối tượng detect
def get_box_info_detect(box):
    x, y, w, h = int(box[0]), int(box[1]), int(box[2]), int(box[3])
    center_X = int((x + (x + w)) / 2.0)
    center_Y = int((y + (y + h)) / 2.0)
    conf = box[4]
    currentClass = box[5]
    return x, y, w, h, center_X, center_Y, conf, currentClass

# Lấy thông tin đối tượng trong danh sách tracker
def get_box_info(box):
    (x, y, w, h) = [int(v) for v in box]
    center_X = int((x + (x + w)) / 2.0)
    center_Y = int((y + (y + h)) / 2.0)
    return x, y, w, h, center_X, center_Y

# Kiểm tra đối tượng mới hay cũ
def is_old(center_Xd, center_Yd, boxes):
    for box_tracker in boxes:
        (xt, yt, wt, ht) = [int(c) for c in box_tracker]
        center_Xt, center_Yt = int((xt + (xt + wt)) / 2.0), int((yt + (yt + ht)) / 2.0)
        distance = math.sqrt((center_Xt - center_Xd) ** 2 + (center_Yt - center_Yd) ** 2)
        if distance < max_distance:
            return True
    return False

# Vẽ lazer line
def draw_line(event, x, y, flags, param):
    cv2.imshow('Video', frame)
    if event == cv2.EVENT_LBUTTONDOWN:
        laser_line[0], laser_line[1] = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        laser_line[2], laser_line[3] = x, y
        cv2.line(frame, (laser_line[0], laser_line[1]), (laser_line[2], laser_line[3]), (0, 0, 255), 4)
        cv2.imshow('Video', frame)
        
# Thiết lập kích thước cửa sổ hiển thị 
def windowSize(vid):
    width = int(vid.get(3))
    height = int(vid.get(4))

    aspect_ratio = width / height

    window_width = 1200
    window_height = int(window_width / aspect_ratio)
    if window_height > 780:
        window_height = 750
        window_width = int(window_height * aspect_ratio)

    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video', window_width, window_height)

# Vòng lặp chính
def process(video_path):
    frame_count = 0
    car_number = 0
    obj_cnt = 0
    curr_trackers = []

    vid = cv2.VideoCapture(video_path)
    windowSize(vid)

    while True:
        boxes = []
        laser_line_color = (0, 0, 255)

        ret, frame = vid.read()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Duyệt qua các đối tượng trong tracker
        old_trackers = curr_trackers
        curr_trackers = []

        for car in old_trackers:
            # Update tracker
            tracker = car['tracker']
            (_, box) = tracker.update(frame)
            boxes.append(box)

            new_obj = dict()
            new_obj['tracker_id'] = car['tracker_id']
            new_obj['tracker'] = tracker

            # Tính tâm đối tượng
            x, y, w, h, center_X, center_Y= get_box_info(box)
            cv2.circle(frame, (center_X, center_Y), 4, (255, 0, 255), -1)
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
            # cv2.putText(frame, "ID:" + str(car['tracker_id']), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)
            
            # So sánh tâm đối tượng với lazer line
            if center_Y > laser_line[1] and laser_line[0] < center_X < laser_line[2]:
                # Nếu vượt qua thì không track nữa mà đếm xe
                laser_line_color = (0, 255, 0)
                car_number += 1
            else:
                # Còn không thì track tiếp
                curr_trackers.append(new_obj)

        if frame_count % 50 == 0:
        # if frame_count % 1 == 0:
            # Detect đối tượng
            boxes_d = get_object(frame)

            for box in boxes_d:
                xd, yd, wd, hd, center_Xd, center_Yd, conf, currentClass = get_box_info_detect(box)
                # cv2.rectangle(frame, (xd, yd), (xd + wd, yd + hd), (0, 255, 255), 2)
                # cv2.putText(frame, currentClass + "(" + str(conf) + ")", (xd, yd), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 4)

                if center_Yd <= laser_line[1] - max_distance:

                    # Duyệt qua các box, nếu sai lệch giữa đối tượng được detect với đối tượng đã được track không quá max distance thì coi như 1 đôi tượng
                    if not is_old(center_Xd, center_Yd, boxes):
                        cv2.rectangle(frame, (xd, yd), ((xd + wd), (yd + hd)), (0, 255, 255), 2)
                        # Tạo đối tượng tracker mới
                        tracker = cv2.legacy.TrackerMOSSE_create()

                        obj_cnt += 1
                        new_obj = dict()
                        tracker.init(frame, tuple([box[0], box[1], box[2], box[3]]))

                        new_obj['tracker_id'] = obj_cnt
                        new_obj['tracker'] = tracker

                        curr_trackers.append(new_obj)
                    
        
        # Tang frame
        frame_count += 1
        # if frame_count == 100:
        #     break

        cv2.putText(frame, "Car number: " + str(car_number), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0 , 0), 3)
        cv2.line(frame, (laser_line[0], laser_line[1]), (laser_line[2], laser_line[3]), laser_line_color, 4)

        cv2.imshow("Video", frame)


    vid.release()
    cv2.destroyAllWindows

  
    
if __name__ == "__main__":
    # Khai báo các tham số
    max_distance = 80
    # max_distance = 30
    laser_line = [0, 0, 0, 0]
    model = YOLO("Yolo-Weights/best.pt")
    classNames = ["car", "container"]

    video_path = sys.argv[1]

    vid = cv2.VideoCapture(video_path)
    ret, frame = vid.read()
    windowSize(vid)
    cv2.setMouseCallback('Video', draw_line)
    cv2.waitKey(0)
    vid.release()
    cv2.destroyAllWindows()

    process(video_path)