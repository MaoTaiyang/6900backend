from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile

from video_processing import process_video_with_openpose, extract_skeleton_data, model_folder_path

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 定义后端视频处理接口
@app.route('/process_video', methods=['POST'])
def process_video_route():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']

    # 创建临时文件夹保存视频及生成的数据
    with tempfile.TemporaryDirectory() as temp_dir:
        input_video_path = os.path.join(temp_dir, "input_video.mp4")
        json_output_path = os.path.join(temp_dir, "json_output")

        os.makedirs(json_output_path, exist_ok=True)

        video_file.save(input_video_path)

        try:
            # 调用 OpenPose 进行视频处理
            process_video_with_openpose(input_video_path, json_output_path, model_folder_path)

            # 提取骨架数据
            skeleton_data = extract_skeleton_data(json_output_path)

            # 返回骨架数据供前端使用
            return jsonify({
                "message": "视频处理完成",
                "skeleton_data": skeleton_data
            }), 200
        except Exception as e:
            print(f"视频处理失败: {e}")
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
1









