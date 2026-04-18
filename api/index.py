import os
from flask import Flask, request, jsonify, render_template

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
        result_text = deduplicate_lines(user_text)
        return jsonify({'result': result_text})
    except Exception as e:
        # 打印详细错误到日志
        print(f"Processing error: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)