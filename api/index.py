import os
import uuid
from flask import Flask, request, jsonify, render_template
from vercel_blob import put

# 设置模板文件夹为上级目录的 templates 文件夹
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
    file_bytes = content.encode('utf-8')
    blob_info = put(filename, file_bytes)
    return blob_info.get('url')

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
        # 可选：保存原始输入
        original_url = save_to_blob(user_text, prefix="input")
        print(f"原始输入已保存至: {original_url}")

        result_text = deduplicate_lines(user_text)

        # 保存去重结果
        result_url = save_to_blob(result_text, prefix="output")
        print(f"去重结果已保存至: {result_url}")

        return jsonify({'result': result_text})
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
# 确保 Vercel 可以找到 Flask 实例
app = app