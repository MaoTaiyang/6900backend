import cv2
import subprocess
import json
import os

# 设置 OpenPose 可执行文件和文件路径
openpose_exe_path = "C:\\OpenPose\\bin\\OpenPoseDemo.exe"  # 替换为实际路径
input_video_path = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\video\\00f8e9a1c8862eefc073342f333391f5.mp4"  # 输入视频路径
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

# 检查 JSON 数据
def check_json_data(json_folder_path, num_frames_to_check=5):
    for frame_count in range(num_frames_to_check):
        # 修改文件名格式以匹配实际生成的文件名
        json_file_path = os.path.join(json_folder_path, f"00f8e9a1c8862eefc073342f333391f5_{frame_count:012d}_keypoints.json")
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                data = json.load(f)
                print(f"检查帧 {frame_count} 的 JSON 文件: {json_file_path}")
                if 'people' in data and len(data['people']) > 0:
                    for person_index, person in enumerate(data['people']):
                        keypoints = person['pose_keypoints_2d']
                        print(f"  人 {person_index}: 关键点数量 = {len(keypoints)//3}")
                        for i in range(0, len(keypoints), 3):
                            x = keypoints[i]
                            y = keypoints[i + 1]
                            confidence = keypoints[i + 2]
                            print(f"    关键点 {i//3}: x = {x}, y = {y}, 置信度 = {confidence}")
                else:
                    print(f"  帧 {frame_count} 中没有检测到 'people' 数据或数据为空。")
        else:
            print(f"  帧 {frame_count} 的 JSON 文件未找到: {json_file_path}")

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

        # 修改文件名格式以匹配实际生成的文件名
        json_file_path = os.path.join(json_folder_path, f"00f8e9a1c8862eefc073342f333391f5_{frame_count:012d}_keypoints.json")
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                data = json.load(f)
                if 'people' in data and len(data['people']) > 0:
                    for person in data['people']:
                        keypoints = person['pose_keypoints_2d']
                        for i in range(0, len(keypoints), 3):
                            x = keypoints[i]
                            y = keypoints[i + 1]
                            confidence = keypoints[i + 2]

                            # 检查是否为有效的关键点并且置信度足够高
                            if confidence > 0.1 and x > 0 and y > 0:
                                # 将坐标转换为整数并确保在视频范围内
                                x = int(x)
                                y = int(y)
                                if 0 <= x < frame_width and 0 <= y < frame_height:
                                    # 绘制点（无坐标调整，保持原始坐标）
                                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                                    # 在点旁边标注坐标
                                    cv2.putText(frame, f"({x}, {y})", (x + 5, y - 5),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # 绘制坐标轴
        cv2.arrowedLine(frame, (0, frame_height), (frame_width - 10, frame_height), (0, 255, 0), 4)  # x 轴
        cv2.arrowedLine(frame, (0, 10), (0, frame_height), (0, 255, 0), 4)  # y 轴

        # 写入带标注的输出视频
        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()
    print("视频处理并保存带坐标的输出完成")

# 运行 OpenPose 处理视频
process_video_with_openpose(input_video_path, output_video_path, json_output_path, model_folder_path)

# 检查 JSON 数据
check_json_data(json_output_path)

# 绘制坐标和坐标系并输出视频
output_video_path_with_coordinates = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\OutputVideo\\output_video_with_coordinates.mp4"
draw_coordinates_on_video(output_video_path, json_output_path, output_video_path_with_coordinates)
