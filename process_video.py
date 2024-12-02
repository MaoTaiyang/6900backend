import cv2
import subprocess
import json
import os

# 设置 OpenPose 可执行文件和文件路径
openpose_exe_path = "C:\\OpenPose\\bin\\OpenPoseDemo.exe"  # 替换为实际路径
input_video_path = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\video\\ac80798f46578a7cc7b5c68d1b8724fd.mp4"  # 输入视频路径
output_video_path = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\OutputVideo\\output_video.avi"  # 输出视频路径，使用 AVI 格式
json_output_path = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\OutputVideo\\json_folder"  # 输出 JSON 文件夹路径
model_folder_path = "C:\\OpenPose\\models\\"  # 模型文件夹路径

def process_video_with_openpose(input_video_path, output_video_path, json_output_path, model_folder_path):
    # 构建 OpenPose 命令
    command = [
        openpose_exe_path,
        "--video", input_video_path,
        "--write_video", output_video_path,
        "--write_json", json_output_path,
        "--display", "0",  # 禁止实时显示以防止 OpenCV GUI 错误
        "--model_folder", model_folder_path
    ]

    # 调用 OpenPose 处理视频
    try:
        subprocess.run(command, check=True)
        print("OpenPose 视频处理完成，输出已保存。")
    except subprocess.CalledProcessError as e:
        print(f"运行 OpenPose 时出错: {e}")

def draw_coordinates_on_video(video_path, json_folder_path, output_video_path_with_coordinates):
    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频")

    # 获取视频参数
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 设置输出视频编写器
    out = cv2.VideoWriter(output_video_path_with_coordinates,
                          cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # 逐帧读取视频和对应的 JSON 文件
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        json_file_path = os.path.join(json_folder_path, f"frame_{frame_count:012d}_keypoints.json")
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                data = json.load(f)
                if 'people' in data and len(data['people']) > 0:
                    for person in data['people']:
                        keypoints = person['pose_keypoints_2d']
                        for i in range(0, len(keypoints), 3):
                            x = int(keypoints[i])
                            y = int(keypoints[i + 1])
                            confidence = keypoints[i + 2]
                            if confidence > 0.1:  # 仅绘制置信度较高的关键点
                                # 调整 y 坐标，使得原点在左下角
                                adjusted_y = frame_height - y
                                # 绘制点
                                cv2.circle(frame, (x, adjusted_y), 5, (0, 255, 0), -1)
                                # 在点旁边标注坐标
                                cv2.putText(frame, f"({x}, {adjusted_y})", (x + 5, adjusted_y - 5),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # 绘制坐标轴
        cv2.line(frame, (0, frame_height), (frame_width, frame_height), (0, 0, 255), 2)  # x 轴
        cv2.line(frame, (0, 0), (0, frame_height), (0, 0, 255), 2)  # y 轴

        # 写入带标注的输出视频
        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()
    print("视频处理并保存带坐标的输出完成")

# 调用 OpenPose 处理视频
process_video_with_openpose(input_video_path, output_video_path, json_output_path, model_folder_path)

# 绘制坐标和坐标系并输出视频
output_video_path_with_coordinates = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\OutputVideo\\output_video_with_coordinates.mp4"
draw_coordinates_on_video(output_video_path, json_output_path, output_video_path_with_coordinates)
