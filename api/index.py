import os
import uuid
from flask import Flask, request, jsonify, render_template
# 1. 关键修改：使用官方推荐的导入方式
from vercel import blob

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))

def deduplicate_lines(text):
    # ... (你的去重逻辑保持不变) ...
    return unique_text

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': '未提供文本'}), 400

    user_text = data['text']
    try:
        # 1. 去重处理
        result_text = deduplicate_lines(user_text)

        # 2. 使用官方 SDK 上传结果
        # 生成唯一文件名
        filename = f"result_{uuid.uuid4().hex}.txt"
        # 2.1 调用官方 SDK 的 put 方法上传文件
        # 注意：这里的参数名是 path 和 body
        uploaded_blob = blob.put(path=filename, body=result_text.encode('utf-8'), access="public")
        
        # 2.2 可选：打印出上传后的文件URL，方便调试
        print(f"File uploaded to Vercel Blob: {uploaded_blob['url']}")

        # 3. 向前端返回去重后的文本
        return jsonify({'result': result_text})
    except Exception as e:
        # 打印详细的错误信息到Vercel日志
        print(f"Error in /process: {str(e)}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500