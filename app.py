from flask import Flask, request, jsonify
import tempfile
import time  # 用于生成时间戳
from datetime import datetime  # 用于获取当前时间
import uuid  # 用于生成唯一 ID
import os
import json
import shutil
from flask import send_file
from flask import Flask, jsonify
from urllib.parse import unquote
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


    filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    # 获取当前时间并格式化为字符串
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    # 替换成您指定的路径
    base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
    user_folder = os.path.join(base_directory, username)
    os.makedirs(user_folder, exist_ok=True)


    # 使用生成或指定的文件名保存视频和 JSON 文件
    input_video_path = os.path.join(user_folder, f"{filename}.mp4")
    json_output_file = os.path.join(user_folder, f"{filename}")


    # 保存上传的视频文件
    video_file.save(input_video_path)

    # 调用 OpenPose 处理视频
    model_folder_path = "C:\\OpenPose\\models\\"  # 替换为实际路径
    print(f"Processing video: {input_video_path} with OpenPose model at {model_folder_path}")

    try:
        if not process_video_with_openpose(input_video_path, json_output_file, model_folder_path):
            # 如果处理失败，删除已保存的视频文件
            os.remove(input_video_path)
            return jsonify({"error": "Failed to process video with OpenPose"}), 500
    except Exception as e:
        # 捕获其他可能的错误
        os.remove(input_video_path)
        return jsonify({"error": "An error occurred during video processing", "details": str(e)}), 500
    # 构造视频访问 URL
    video_url = f"http://10.0.0.67:5000/videos/{username}/{filename}.mp4"
    # json_folder_path = "C:/Users/123/Desktop/csi6900/userdata/maoziyang1998@gmail.com/1731897783_74b9ca21"
    skeleton_data_url = f"http://10.0.0.67:5000/get_skeleton_data/{username}/{filename}"
    # # 提取骨架数据
    # skeleton_data = extract_skeleton_data(json_output_file)

    # 保存视频的上传时间和文件名信息到 metadata.json 中

    metadata = {"filename": filename,
                "upload_time": upload_time,
                "video_url": video_url,
                "skeleton_data_url": skeleton_data_url}
    metadata_file = os.path.join(user_folder, "metadata.json")
    # 将信息追加写入 metadata.json 文件
    # 初始化数据列表
    data = []

    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data, list):  # 如果不是列表，初始化为空列表
                    data = []
        except json.JSONDecodeError:
            data = []  # 如果文件损坏或为空，重新初始化为列表


    # 添加新数据
    data.append(metadata)

    # 写入 metadata.json 文件
    try:
        with open(metadata_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing metadata.json: {e}")
        return jsonify({"error": "Failed to save metadata"}), 500


    # # 写入 metadata.json 文件（带异常处理）
    # try:
    #     with open(metadata_file, 'w', encoding='utf-8') as file:
    #         json.dump(data, file, indent=4, ensure_ascii=False)
    # except Exception as e:
    #     print(f"Error writing metadata.json: {e}")
    #     return jsonify({"error": "Failed to save metadata"}), 500



    # 返回骨架数据
    return jsonify({
        "message": "Video processed successfully",
        "filename": filename,
        "video_url": video_url,
        "skeleton_data_url": skeleton_data_url
    }), 200







@app.route('/videos/<username>/<filename>', methods=['GET'])
def serve_video(username, filename):
    base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
    user_folder = os.path.join(base_directory, username)
    video_path = os.path.join(user_folder, filename)

    if not os.path.exists(video_path):
        return jsonify({"error": "File not found"}), 404
    # 通过 Flask 发送文件
    return send_file(video_path, mimetype='video/mp4')






@app.route('/get_skeleton_data/<username>/<foldername>', methods=['GET'])
def serve_skeleton_data(username, foldername):
    # 解码路径参数
    original_foldername = foldername
    foldername = unquote(foldername).strip()  # 移除多余空格
    print(f"Original Foldername: {original_foldername}")
    print(f"Decoded Foldername: {foldername}")




    """
    提供指定用户和文件夹中的骨架数据
    """
    # 基础路径
    base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
    user_folder = os.path.join(base_directory, username)
    json_folder_path = os.path.join(user_folder, foldername)

    print(f"Constructed JSON folder path: {json_folder_path}")
    print(f"Path exists: {os.path.exists(json_folder_path)}")
    print(f"Is directory: {os.path.isdir(json_folder_path)}")



    # 检查文件夹是否存在
    if not os.path.exists(json_folder_path) or not os.path.isdir(json_folder_path):
        return jsonify({"error": "JSON folder not found"}), 404

    # 合并所有 JSON 文件的骨架数据
    skeleton_data = []
    try:
        for file in sorted(os.listdir(json_folder_path)):  # 按文件名排序，确保顺序一致
            if file.endswith(".json"):  # 只处理 JSON 文件
                file_path = os.path.join(json_folder_path, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    # 验证是否存在 "people" 键并包含骨架数据
                    if "people" in file_data and len(file_data["people"]) > 0:
                        skeleton_data.append(file_data["people"][0]["pose_keypoints_2d"])
    except Exception as e:
        return jsonify({"error": f"Error reading JSON files: {str(e)}"}), 500

    # 返回合并后的 skeleton_data
    return jsonify({"skeleton_data": skeleton_data}), 200











# 获取用户的视频列表，按时间排序
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
            metadata = json.load(file)
    except Exception as e:
        return jsonify({"error": "Failed to read metadata", "details": str(e)}), 500



    video_list = []

    for item in metadata:
        filename = item.get("filename", "unknown")
        video_url = item.get("video_url", "unknown")
        upload_time = item.get("upload_time", "unknown")
        skeleton_data_url = item.get("skeleton_data_url", "unknown")
        json_folder_path = os.path.join(user_folder, filename)  # 骨架数据文件夹路径

        # 检查文件和文件夹是否存在
        video_path = os.path.join(user_folder, f"{filename}.mp4")
        if os.path.exists(video_path) and os.path.exists(json_folder_path):
            # skeleton_data = load_skeleton_data_from_folder(json_folder_path)
            video_list.append({
                "filename": filename,
                "video_url": video_url,
                "upload_time": upload_time,
                "jsonFolderPathUrl": skeleton_data_url  # 返回文件夹路径，供后续使用
            })

    # 按上传时间排序（降序）
    video_list = sorted(video_list, key=lambda x: x.get("upload_time", ""), reverse=True)
    print("Video list being returned:", video_list)
    return jsonify(video_list), 200




# @app.route('/get_skeleton_data', methods=['GET'])
# def get_skeleton_data():
#     """
#     根据用户名和视频文件名返回对应的骨架数据
#     """
#     username = request.args.get('username')
#     filename = request.args.get('filename')  # 视频文件名（不含扩展名）
#
#     if not username or not filename:
#         return jsonify({"error": "Username and filename are required"}), 400
#
#     # 骨架数据文件夹路径
#     base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
#     user_folder = os.path.join(base_directory, username)
#     json_folder_path = os.path.join(user_folder, filename)
#
#     # 检查骨架数据文件夹是否存在
#     if not os.path.exists(json_folder_path) or not os.path.isdir(json_folder_path):
#         return jsonify({"error": "Skeleton data not found"}), 404
#
#     # 加载骨架数据
#     skeleton_data = load_skeleton_data_from_folder(json_folder_path)
#     return jsonify({"filename": filename, "skeleton_data": skeleton_data}), 200
#
#
# def load_skeleton_data_from_folder(json_folder_path):
#     """
#     加载骨架数据文件夹中的所有 JSON 文件
#     """
#     skeleton_data_list = []
#     if os.path.exists(json_folder_path) and os.path.isdir(json_folder_path):
#         for filename in os.listdir(json_folder_path):
#             if filename.endswith('.json'):
#                 file_path = os.path.join(json_folder_path, filename)
#                 try:
#                     with open(file_path, 'r', encoding='utf-8') as json_file:
#                         data = json.load(json_file)
#                         skeleton_data_list.append(data)
#                 except json.JSONDecodeError:
#                     print(f"Error decoding JSON from {file_path}")
#                 except Exception as e:
#                     print(f"An error occurred while reading {file_path}: {str(e)}")
#     return skeleton_data_list



# 删除视频和对应的 JSON 文件
@app.route('/delete_video', methods=['POST'])
def delete_video():
    username = request.form['username']
    filename = request.form['filename']

    base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
    user_folder = os.path.join(base_directory, username)
    video_path = os.path.join(user_folder, f"{filename}.mp4")
    json_folder_path = os.path.join(user_folder, f"{filename}")  # 文件夹路径
    metadata_file = os.path.join(user_folder, "metadata.json")

    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(json_folder_path) and os.path.isdir(json_folder_path):
        shutil.rmtree(json_folder_path)  # 递归删除文件夹
        print(f"Deleted JSON folder: {json_folder_path}")

        # 更新 metadata.json 文件
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # 移除 metadata.json 中对应的记录
                data = [item for item in data if item['filename'] != filename]

                with open(metadata_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    print(f"Updated metadata.json: {metadata_file}")

            except Exception as e:
                print(f"Error updating metadata.json: {e}")
                return jsonify({"error": "Failed to update metadata.json"}), 500

        return jsonify({"message": "Video and associated data deleted successfully"}), 200


# 重命名视频和 JSON 文件
@app.route('/rename_video', methods=['POST'])
def rename_video():
    username = request.form['username']
    old_filename = request.form['old_filename']
    new_filename = request.form['new_filename']

    base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
    user_folder = os.path.join(base_directory, username)
    old_video_path = os.path.join(user_folder, f"{old_filename}.mp4")
    old_json_path = os.path.join(user_folder, f"{old_filename}")
    new_video_path = os.path.join(user_folder, f"{new_filename}.mp4")
    new_json_path = os.path.join(user_folder, f"{new_filename}")
    metadata_file = os.path.join(user_folder, "metadata.json")

    if os.path.exists(old_video_path):
        os.rename(old_video_path, new_video_path)
    if os.path.exists(old_json_path):
        os.rename(old_json_path, new_json_path)

    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as file:
            data = json.load(file)
        for item in data:
            if item['filename'] == old_filename:
                item['filename'] = new_filename
        with open(metadata_file, 'w') as file:
            json.dump(data, file, indent=4)

    return jsonify({"message": "Video renamed successfully"}), 200




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)





# def load_skeleton_data_from_folder(json_folder_path):
#     skeleton_data_list = []
#     if os.path.exists(json_folder_path) and os.path.isdir(json_folder_path):
#         for filename in os.listdir(json_folder_path):
#             if filename.endswith('.json'):
#                 file_path = os.path.join(json_folder_path, filename)
#                 try:
#                     with open(file_path, 'r', encoding='utf-8') as json_file:
#                         data = json.load(json_file)
#                         skeleton_data_list.append(data)
#                 except json.JSONDecodeError:
#                     print(f"Error decoding JSON from {file_path}")
#                 except Exception as e:
#                     print(f"An error occurred while reading {file_path}: {str(e)}")
#     return skeleton_data_list


#     for file_name in os.listdir(user_folder):
#         if file_name.endswith('.mp4'):
#             video_name = os.path.splitext(file_name)[0]  # 获取视频文件名（不带扩展名）
#             video_path = os.path.join(user_folder, file_name)
#             json_path = os.path.join(user_folder, f"{video_name}")  # 同名 JSON 文件路径
#             video_url = f"http://127.0.0.1:5000/{username}/{file_name}"  # 构造视频的 URL
#             skeleton_data = load_skeleton_data_from_folder(json_path)
#
#             # 从 metadata.json 获取对应的视频上传时间
#             upload_time = next((item["upload_time"] for item in metadata if item["filename"] == video_name), "未知时间")
#
#             # # 尝试加载与视频同名的 JSON 文件
#             # skeleton_data = None
#             # if os.path.exists(json_path):
#             #     try:
#             #         with open(json_path, 'r', encoding='utf-8') as json_file:
#             #             skeleton_data = json.load(json_file)
#             #     except json.JSONDecodeError:
#             #         skeleton_data = None  # 如果 JSON 文件解析失败，设置为 None
#
#             # 添加视频信息到列表
#             video_list.append({
#                 "filename": video_name,
#                 "video_url": f"http://10.0.0.67:5000/videos/{username}/{file_name}",  # 返回视频的 HTTP URL
#                 "upload_time": upload_time,  # 包含 upload_time
#                 "skeleton_data": skeleton_data
#
#             })
#     print("Metadata content:", metadata)
#     print("Video list being returned:", video_list)
#     # 返回视频列表
#     return jsonify(video_list), 200
#
# def load_skeleton_data_from_folder(json_folder_path):
#     skeleton_data_list = []
#     if os.path.exists(json_folder_path) and os.path.isdir(json_folder_path):
#         for filename in os.listdir(json_folder_path):
#             if filename.endswith('.json'):
#                 file_path = os.path.join(json_folder_path, filename)
#                 try:
#                     with open(file_path, 'r', encoding='utf-8') as json_file:
#                         data = json.load(json_file)
#                         skeleton_data_list.append(data)
#                 except json.JSONDecodeError:
#                     print(f"Error decoding JSON from {file_path}")
#                 except Exception as e:
#                     print(f"An error occurred while reading {file_path}: {str(e)}")
#     return skeleton_data_list