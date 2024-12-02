import os

base_directory = "C:\\Users\\123\\Desktop\\csi6900\\userdata"
username = "maoziyang1998@gmail.com"
foldername = "1731905664_43571bd0"
json_folder_path = os.path.join(base_directory, username, foldername)

print("检查路径:", json_folder_path)
print("路径是否存在:", os.path.exists(json_folder_path))
print("路径是否是文件夹:", os.path.isdir(json_folder_path))
