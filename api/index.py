import os
import uuid
import tempfile
from flask import Flask, request, jsonify, render_template

# 尝试导入 Vercel Python SDK
try:
    # 官方推荐用法，但需要本地文件路径
    from vercel import blob
    USE_VERCEL_SDK = True
    print("Successfully imported Vercel Python SDK")
except ImportError:
    # 如果官方SDK导入失败，尝试使用非官方 vercel_blob
    try:
        import vercel_blob
        USE_VERCEL_SDK = False
        print("Successfully imported vercel_blob (unofficial SDK)")
    except ImportError:
        # 如果两者都失败，则回退到纯去重模式（不保存到云端）
        USE_VERCEL_SDK = None
        print("Warning: No Vercel Blob SDK available, running in dedup-only mode")

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
    
    # 如果没有可用的 SDK，跳过保存
    if USE_VERCEL_SDK is None:
        print(f"Skipping blob save (no SDK available): {filename}")
        return None
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # 使用官方 SDK
        if USE_VERCEL_SDK:
            # 官方 SDK 需要使用本地文件路径
            uploaded_file = blob.upload_file(
                local_path=tmp_file_path,    # 指定临时文件的路径
                path=filename,               # 指定在 Blob 存储中的路径
                access="public",             # 设置为公开访问
            )
            print(f"File uploaded via official SDK: {uploaded_file.get('url')}")
            return uploaded_file.get('url')
        
        # 使用非官方 SDK (vercel_blob)
        else:
            with open(tmp_file_path, 'rb') as f:
                file_bytes = f.read()
                resp = vercel_blob.put(filename, file_bytes)
                # 非官方 SDK 返回的可能是字典或字符串 URL
                if isinstance(resp, dict):
                    blob_url = resp.get('url')
                else:
                    blob_url = str(resp)
                print(f"File uploaded via vercel_blob: {blob_url}")
                return blob_url
                
    except Exception as e:
        print(f"Blob upload error: {e}")
        return None
    finally:
        # 清理临时文件
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

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
        # 1. 去重处理
        result_text = deduplicate_lines(user_text)

        # 2. 尝试保存到 Vercel Blob（如果 SDK 可用）
        blob_url = save_to_blob(result_text, prefix="output")
        if blob_url:
            print(f"Result saved to Blob: {blob_url}")

        # 3. 向前端返回去重后的文本
        return jsonify({'result': result_text})
    except Exception as e:
        print(f"Processing error: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)