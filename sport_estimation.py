import cv2
import numpy as np
import json

def initialize_video(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError("Video cannot be opened")
    print(initialize_video)
    return cap

def setup_output_writer(cap, filename='C:/Users/123/Desktop/csi6900/opStudy/OutputVideo/output_video.mp4'):
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(setup_output_writer)
    return cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

def process_video_frames(cap, out):
    net = cv2.dnn.readNetFromCaffe("C:/Users/123/Desktop/csi6900/backendgoogle_colab/openpose/models/pose/body_25/pose_deploy.prototxt",
                                   "C:/Users/123/Desktop/csi6900/backendgoogle_colab/openpose/models/pose/body_25/pose_iter_584000.caffemodel")
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    pairs = [[1, 8], [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [8, 9], [9, 10], [10, 11], [11, 22],
             [22, 23], [11, 24], [8, 12], [12, 13], [13, 14], [14, 19], [19, 20], [14, 21], [0, 15],
             [0, 16], [15, 17], [16, 18], [1,0]]

    all_points = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_points = extract_keypoints(frame, net)
        draw_skeleton(frame, frame_points, pairs)
        out.write(frame)
        all_points.append(frame_points)
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames")
    print(process_video_frames)
    return all_points

def extract_keypoints(frame, net):
    input_blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (368, 368), (0, 0, 0), swapRB=False, crop=False)
    net.setInput(input_blob)
    output = net.forward()
    height = frame.shape[0]
    points = []
    for i in range(25):
        heat_map = output[0, i, :, :]
        _, conf, _, point = cv2.minMaxLoc(heat_map)
        if conf > 0.1:
            x = int((point[0] / output.shape[3]) * frame.shape[1])
            y = int((point[1] / output.shape[2]) * frame.shape[0])
            # 调整坐标，使得原点在左下角
            adjusted_y = height - y
            points.append((x, adjusted_y))
        else:
            points.append(None)
    return points

def draw_skeleton(frame, points, pairs):
    # 获取帧的高度，以调整坐标系原点到左下角
    height = frame.shape[0]
    # 定义一个最大合理距离，用于避免错误连接（根据需要调整）
    max_distance_threshold = height / 4  # 这个值可以根据实际视频内容调整
    for partA, partB in pairs:
        if points[partA] is not None and points[partB] is not None:
            # 转换坐标系，使原点在左下角
            adjusted_pointA = (points[partA][0], height - points[partA][1])
            adjusted_pointB = (points[partB][0], height - points[partB][1])
            # 计算两点之间的欧几里得距离
            distance = np.linalg.norm(np.array(adjusted_pointA) - np.array(adjusted_pointB))
            # 检查是否在合理的距离范围内，避免误连线
            if distance < max_distance_threshold:
                # 画线
                cv2.line(frame, adjusted_pointA, adjusted_pointB, (0, 255, 0), 2)
                # 在每个关键点旁边显示坐标
                cv2.putText(frame, f"{adjusted_pointA}", adjusted_pointA, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 1)
                cv2.putText(frame, f"{adjusted_pointB}", adjusted_pointB, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 1)
def save_keypoints(all_points, filename='C:/Users/123/Desktop/csi6900/opStudy/OutputVideo/keypoints.json'):
    with open(filename, 'w') as f:
        json.dump(all_points, f)
    print(save_keypoints)
try:
    cap = initialize_video('C:/Users/123/Desktop/csi6900/opStudy/video/00f8e9a1c8862eefc073342f333391f5.mp4')
    out = setup_output_writer(cap)
    all_points = process_video_frames(cap, out)
    save_keypoints(all_points)
finally:
    cap.release()
    out.release()
    print("视频处理完成并保存")