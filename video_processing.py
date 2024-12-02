import cv2
import subprocess
import json
import os

# 设置 OpenPose 的可执行文件和模型路径
openpose_exe_path = "C:/OpenPose/bin/OpenPoseDemo.exe"  # 替换为实际路径
model_folder_path = "C:/OpenPose/models"  # 模型文件夹路径

def process_video_with_openpose(input_video_path, json_output_path, model_folder_path):
    print("开始调用 OpenPose 处理视频...")
    command = [
        openpose_exe_path,
        "--video", input_video_path,
        "--write_json", json_output_path,
        "--display", "0",
        "--model_folder", model_folder_path,
        "--num_gpu", "0",  # 禁用 GPU，只使用 CPU
        "--render_pose", "0"  # 禁用渲染
    ]
    try:
        subprocess.run(command, check=True)
        print("OpenPose 视频处理完成；JSON 输出已保存。")
    except subprocess.CalledProcessError as e:
        print(f"运行 OpenPose 时出错: {e}")

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




