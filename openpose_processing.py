import cv2
import subprocess
import json
import os

# 设置 OpenPose 可执行文件和文件路径
openpose_exe_path = "C:\\OpenPose\\bin\\OpenPoseDemo.exe"  # 替换为实际路径
# input_video_path = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\video\\ac80798f46578a7cc7b5c68d1b8724fd.mp4"  # 输入视频路径
#output_video_path = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\OutputVideo\\output_video.avi"  # 输出视频路径，使用 AVI 格式
# json_output_path = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\OutputVideo\\json_folder"  # 输出 JSON 文件夹路径
model_folder_path = "C:\\OpenPose\\models\\"  # 模型文件夹路径


def process_video_with_openpose(input_video_path, json_output_path, model_folder_path):
    # 确保输出文件夹存在
    output_video_path_local = "C:\\Users\\123\\Desktop\\csi6900\\opStudy\\OutputVideo\\output_video.avi"  # 输出视频路径，使用 AVI 格式
    #os.makedirs(os.path.dirname(output_video_path_local), exist_ok=True)
    #os.makedirs(json_output_path, exist_ok=True)

    # 构建 OpenPose 命令
    command = [
        openpose_exe_path,
        "--video", input_video_path,
        "--write_video", output_video_path_local,
        "--write_json", json_output_path,
        "--display", "0",  # 禁止实时显示以防止 OpenCV GUI 错误
        "--render_pose", "0",  # 再次尝试添加
        "--model_folder", model_folder_path,
        #"--write_video", output_video_path,  # 输出骨架视频路径
    ]

    # 调用 OpenPose 处理视频
    try:
        #subprocess.run(command, check=True)
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"OpenPose 视频处理完成，视频存储在: {output_video_path_local}")
        print(f"OpenPose 输出: {result.stdout.decode('utf-8')}")


        # subprocess.run(command, check=True)
        print("OpenPose 视频处理完成，输出已保存。")
    except subprocess.CalledProcessError as e:
        print(f"运行 OpenPose 时出错: {e}")
        return False
    return True


def extract_skeleton_data(json_output_path):
    skeleton_data = []
    for filename in sorted(os.listdir(json_output_path)):
        if filename.endswith(".json"):
            file_path = os.path.join(json_output_path, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
                frame_skeletons = []
                for person in data.get("people", []):
                    keypoints = person.get("pose_keypoints_2d", [])
                    frame_skeletons.append(keypoints)
                skeleton_data.append({
                    "frame": filename,
                    "skeletons": frame_skeletons
                })
    return skeleton_data






