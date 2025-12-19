import http.server
import socketserver
import os
import json
import urllib.parse
import mimetypes
import sys
from flask import Flask, send_file, jsonify, render_template, send_from_directory

# --- 配置 ---
PORT = 8000  # 网站的端口号，在宝塔中会被覆盖
MEDIA_FOLDER = 'media'  # 存放媒体文件的文件夹名

# 确保媒体文件夹存在
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)
    print(f"已创建 '{MEDIA_FOLDER}' 文件夹")

# 创建Flask应用
app = Flask(__name__, static_folder='.', static_url_path='')

# 设置媒体文件的MIME类型
mimetypes.add_type('audio/wav', '.wav')
mimetypes.add_type('application/pdf', '.pdf')

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/files')
def get_files():
    files_list = {
        "pdfs": [],
        "audios": []
    }
    
    if os.path.exists(MEDIA_FOLDER):
        for filename in os.listdir(MEDIA_FOLDER):
            try:
                if filename.lower().endswith('.pdf'):
                    files_list["pdfs"].append(filename)
                elif filename.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a', '.aac')):
                    files_list["audios"].append(filename)
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
    
    # 对文件进行排序，以便每次刷新顺序一致
    files_list["pdfs"].sort()
    files_list["audios"].sort()
    
    return jsonify(files_list)

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

# 宝塔UWSGI入口点
application = app

# 如果直接运行此脚本，则启动开发服务器
if __name__ == '__main__':
    print(f"服务器正在运行中...")
    print(f"请在浏览器中打开: http://localhost:{PORT}")
    print(f"将你的 PDF 和音频文件拖入 '{MEDIA_FOLDER}' 文件夹，然后刷新浏览器即可查看。")
    print("支持的格式: PDF, WAV, MP3, OGG, M4A, AAC")
    print("要停止服务器，请按 Ctrl+C")
    app.run(host='0.0.0.0', port=PORT, debug=True)