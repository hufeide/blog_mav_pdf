import http.server
import socketserver
import os
import json
import urllib.parse
import mimetypes

# --- 配置 ---
PORT = 8000  # 网站的端口号
MEDIA_FOLDER = 'media'  # 存放媒体文件的文件夹名

# 确保媒体文件夹存在
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)
    print(f"已创建 '{MEDIA_FOLDER}' 文件夹")

# --- 服务器核心逻辑 ---
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"收到请求: {self.path}")
        
        # 处理API请求
        if self.path.startswith('/api/files'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
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
            
            files_list["pdfs"].sort()
            files_list["audios"].sort()
            
            self.wfile.write(json.dumps(files_list, ensure_ascii=False).encode('utf-8'))
            return
            
        # 处理媒体文件请求
        elif self.path.startswith('/' + MEDIA_FOLDER + '/'):
            file_path = urllib.parse.unquote(self.path[1:])
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type is None:
                    if file_path.lower().endswith('.pdf'):
                        content_type = 'application/pdf'
                    elif file_path.lower().endswith('.wav'):
                        content_type = 'audio/wav'
                    else:
                        content_type = 'application/octet-stream'
                
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {e}")
                    self.send_error(500, f"内部服务器错误: {str(e)}")
                    return
        
        # 处理根路径请求
        elif self.path == '/':
            self.path = '/index.html'
        
        # 处理其他静态文件请求
        try:
            return super().do_GET()
        except Exception as e:
            print(f"处理请求 {self.path} 时出错: {e}")
            self.send_error(500, f"内部服务器错误: {str(e)}")

# --- 启动服务器 ---
def run_server():
    handler = CustomHandler
    # 设置正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"工作目录: {os.getcwd()}")
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"服务器正在运行中...")
        print(f"请在浏览器中打开: http://0.0.0.0:{PORT}")
        print(f"将你的 PDF 和音频文件拖入 '{MEDIA_FOLDER}' 文件夹，然后刷新浏览器即可查看。")
        print(f"支持的格式: PDF, WAV, MP3, OGG, M4A, AAC")
        print(f"要停止服务器，请按 Ctrl+C")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()