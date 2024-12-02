from flask import Flask, request, jsonify
import time
from datetime import datetime
import uuid
import os
import json
from openpose_processing import process_video_with_openpose, extract_skeleton_data

app = Flask(__name__)

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    if 'username' not in request.form:
        return jsonify({"error": "No username provided"}), 400

    video_file = request.files['video']
    username = request.form['username']
    filename = request.form.get('filename')  # 从前端获取文件名
    if not filename:
        filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # 获取当前时间并格式化为字符串
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 替换成您指定的路径
    base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
    user_folder = os.path.join(base_directory, username)
    os.makedirs(user_folder, exist_ok=True)

    # 使用生成或指定的文件名保存视频
    input_video_path = os.path.join(user_folder, f"{filename}.mp4")

    # 保存上传的视频文件
    video_file.save(input_video_path)

    # 调用 OpenPose 处理视频
    model_folder_path = "C:\\OpenPose\\models\\"  # 替换为实际路径
    skeleton_data = None
    if not process_video_with_openpose(input_video_path, None, model_folder_path):
        # 如果处理失败，删除已保存的视频文件
        os.remove(input_video_path)
        return jsonify({"error": "Failed to process video with OpenPose"}), 500

    # 提取骨架数据
    skeleton_data = extract_skeleton_data(input_video_path)

    # 保存视频的上传时间、文件名和骨架数据到 metadata.json 中
    metadata_file = os.path.join(user_folder, "metadata.json")
    metadata = {"filename": filename, "upload_time": upload_time, "skeleton_data": skeleton_data}
    
    # 将信息追加写入 metadata.json 文件
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, list):  # 如果不是列表，初始化为空列表
                    data = []
        except json.JSONDecodeError:
            data = []  # 如果文件损坏或为空，重新初始化为列表
    else:
        data = []

    # 追加新数据
    data.append(metadata)

    with open(metadata_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)  # 确保使用原始字符串

    # 返回处理成功信息
    return jsonify({"message": "Video processed successfully", "filename": filename}), 200


# 获取用户的视频列表，包含对应的 skeleton_data
@app.route('/get_videos', methods=['GET'])
def get_videos():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
    user_folder = os.path.join(base_directory, username)
    metadata_file = os.path.join(user_folder, "metadata.json")

    if not os.path.exists(metadata_file):
        return jsonify([]), 200

    # 读取 metadata.json 文件内容
    try:
        with open(metadata_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error reading metadata: {e}")
        return jsonify({"error": "Failed to read metadata", "details": str(e)}), 500

    # 返回视频列表
    return jsonify(data), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

