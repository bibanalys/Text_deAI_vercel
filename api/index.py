import os
import uuid
from flask import Flask, request, jsonify, render_template
from vercel import blob

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))

def deduplicate_lines(text):
    """按行去重，保持原有顺序"""
    if not text:
        return ""
    lines = text.splitlines()
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    return '\n'.join(unique_lines)

def save_to_blob(content, prefix="result"):
    """将文本内容保存到 Vercel Blob，返回文件的访问 URL"""
    filename = f"{prefix}_{uuid.uuid4().hex}.txt"
    # 使用官方 SDK 的 upload_file 方法
    try:
        uploaded_file = blob.upload_file(
            path=filename,
            access="public",
            data=content.encode('utf-8')
        )
        return uploaded_file['url']
    except Exception as e:
        # 打印详细的错误日志，方便调试
        print(f"Blob upload error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': '未提供文本'}), 400

    user_text = data['text']
    try:
        # 保存原始输入到 Blob
        original_url = save_to_blob(user_text, prefix="input")
        if original_url:
            print(f"原始输入已保存至: {original_url}")

        result_text = deduplicate_lines(user_text)

        # 保存去重结果到 Blob
        result_url = save_to_blob(result_text, prefix="output")
        if result_url:
            print(f"去重结果已保存至: {result_url}")

        return jsonify({'result': result_text})
    except Exception as e:
        # 打印详细的错误日志到 Vercel Functions 控制台
        print(f"Processing error: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)