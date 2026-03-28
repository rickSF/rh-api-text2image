#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RunningHub ComfyUI / AI 应用 图片生成客户端
支持工作流模式和 AI 应用模式
"""
import time
import json
import argparse
import sys
import urllib.request
import urllib.error
import os
import tempfile

# 设置 stdout 编码为 utf-8，避免 Windows 控制台乱码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# RunningHub API 基础 URL
BASE_URL = "https://www.runninghub.cn"

# API 文档参考链接
API_DOCS = {
    "home": "https://www.runninghub.cn/runninghub-api-doc-cn/",
    "ai_app_example": "https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287339",
    "ai_app_advanced": "https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287340",
    "workflow_example": "https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287342",
    "error_codes": "https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287338"
}

def print_api_docs():
    """打印 API 文档参考链接"""
    print("\n📚 API 参考文档:", file=sys.stderr)
    print(f"  首页: {API_DOCS['home']}", file=sys.stderr)
    print(f"  AI应用示例: {API_DOCS['ai_app_example']}", file=sys.stderr)
    print(f"  工作流示例: {API_DOCS['workflow_example']}", file=sys.stderr)
    print(f"  错误码说明: {API_DOCS['error_codes']}", file=sys.stderr)

def make_request(url, data=None, method='POST'):
    """发送 HTTP 请求的辅助函数"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'OpenClaw-ComfyUI-Skill/1.0'
    }
    
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
    else:
        data_bytes = None

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误: {e.code} - {e.reason}", file=sys.stderr)
        try:
            error_body = e.read().decode('utf-8')
            print(f"错误详情: {error_body}", file=sys.stderr)
        except:
            pass
        return None
    except Exception as e:
        print(f"请求失败: {str(e)}", file=sys.stderr)
        return None

def create_task_workflow(api_key, workflow_id, prompt, seed=None):
    """使用工作流模式创建任务"""
    url = f"{BASE_URL}/task/openapi/create"
    
    node_info_list = [
        {
            "nodeId": "6",
            "fieldName": "text",
            "fieldValue": prompt
        }
    ]
    
    if seed:
        node_info_list.append({
            "nodeId": "3",
            "fieldName": "seed",
            "fieldValue": str(seed)
        })
    
    payload = {
        "apiKey": api_key,
        "workflowId": workflow_id,
        "nodeInfoList": node_info_list
    }
    
    print(f"正在使用工作流 {workflow_id} 创建任务...", file=sys.stderr)
    return make_request(url, payload)

def get_ai_app_nodes(api_key, ai_app_id):
    """获取 AI 应用的节点信息"""
    url = f"{BASE_URL}/api/webapp/apiCallDemo?apiKey={api_key}&webappId={ai_app_id}"
    
    try:
        headers = {
            'User-Agent': 'OpenClaw-ComfyUI-Skill/1.0'
        }
        req = urllib.request.Request(url, headers=headers, method='GET')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result and result.get('code') == 0:
                node_info_list = result.get('data', {}).get('nodeInfoList', [])
                return node_info_list
            else:
                print(f"获取 AI 应用节点信息失败: {result.get('msg')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"获取 AI 应用节点信息失败: {str(e)}", file=sys.stderr)
        return None

def create_task_ai_app(api_key, ai_app_id, prompt, seed=None):
    """使用 AI 应用模式创建任务"""
    url = f"{BASE_URL}/task/openapi/ai-app/run"
    
    # 首先获取 AI 应用的节点信息
    print(f"正在获取 AI 应用 {ai_app_id} 的节点信息...", file=sys.stderr)
    node_info_list = get_ai_app_nodes(api_key, ai_app_id)
    
    if not node_info_list:
        print("无法获取 AI 应用节点信息，使用默认配置", file=sys.stderr)
        # 使用默认配置
        node_info_list = [
            {
                "nodeId": "6",
                "fieldName": "text",
                "fieldValue": prompt
            }
        ]
    else:
        print(f"获取到 {len(node_info_list)} 个节点", file=sys.stderr)
        # 查找文本输入节点并更新提示词
        text_node_found = False
        for node in node_info_list:
            # 查找文本类型的节点（通常是 prompt 或 text 字段）
            if node.get('fieldType') == 'STRING' and 'prompt' in node.get('fieldName', '').lower():
                node['fieldValue'] = prompt
                text_node_found = True
                print(f"更新提示词节点: {node.get('nodeId')} - {node.get('fieldName')}", file=sys.stderr)
                break
            elif node.get('fieldType') == 'STRING' and 'text' in node.get('fieldName', '').lower():
                node['fieldValue'] = prompt
                text_node_found = True
                print(f"更新提示词节点: {node.get('nodeId')} - {node.get('fieldName')}", file=sys.stderr)
                break
        
        # 如果没有找到特定的文本节点，使用第一个 STRING 类型节点
        if not text_node_found:
            for node in node_info_list:
                if node.get('fieldType') == 'STRING':
                    node['fieldValue'] = prompt
                    text_node_found = True
                    print(f"更新第一个文本节点: {node.get('nodeId')} - {node.get('fieldName')}", file=sys.stderr)
                    break
        
        # 如果还是没有找到，添加一个新的节点
        if not text_node_found:
            node_info_list.append({
                "nodeId": "6",
                "fieldName": "text",
                "fieldValue": prompt
            })
    
    if seed:
        node_info_list.append({
            "nodeId": "3",
            "fieldName": "seed",
            "fieldValue": str(seed)
        })
    
    payload = {
        "apiKey": api_key,
        "webappId": ai_app_id,
        "nodeInfoList": node_info_list
    }
    
    print(f"正在使用 AI 应用 {ai_app_id} 创建任务...", file=sys.stderr)
    return make_request(url, payload)

def get_task_outputs(api_key, task_id):
    """获取任务输出结果"""
    url = f"{BASE_URL}/task/openapi/outputs"
    
    payload = {
        "apiKey": api_key,
        "taskId": task_id
    }
    
    return make_request(url, payload)

def wait_for_completion(api_key, task_id, timeout=300, interval=5):
    """轮询任务直至完成"""
    start_time = time.time()
    print(f"正在等待任务 {task_id} 完成...", file=sys.stderr)
    
    while time.time() - start_time < timeout:
        result = get_task_outputs(api_key, task_id)
        
        if result and result.get('code') == 0:
            data = result.get('data')
            if data and isinstance(data, list) and len(data) > 0:
                return data
        elif result and result.get('code') != 0:
            code = result.get('code')
            msg = result.get('msg', '')
            print(f"API 返回错误: {code} - {msg}", file=sys.stderr)
            
            # 处理特定错误码
            if code == 380:
                print("错误: 工作流不存在，请检查 workflow-id 是否正确", file=sys.stderr)
                print_api_docs()
            elif code == 381:
                print("错误: AI 应用不存在，请检查 ai-app-id 是否正确", file=sys.stderr)
                print_api_docs()
            elif code == 382:
                print("错误: API Key 无效，请检查 api-key 是否正确", file=sys.stderr)
            elif code == 384:
                print("提示: 当前有任务正在运行，请等待完成后再试", file=sys.stderr)
            elif code == 805:
                print("错误: 任务执行失败", file=sys.stderr)
                if result.get('data') and result['data'].get('failedReason'):
                    print(f"失败原因: {result['data']['failedReason']}", file=sys.stderr)
            
            # 对于致命错误，直接返回
            if code in [380, 381, 382, 805]:
                return None
        
        time.sleep(interval)
        print(".", end="", flush=True, file=sys.stderr)
    
    print("\n等待任务完成超时", file=sys.stderr)
    return None

def download_image(url, output_dir=None):
    """下载图片到本地"""
    try:
        if output_dir is None:
            # 默认下载路径
            default_dir = r"E:\aicode\openclaw\rh-out"
            if os.path.exists(default_dir):
                output_dir = default_dir
            else:
                # 如果目录不存在，创建它
                try:
                    os.makedirs(default_dir, exist_ok=True)
                    output_dir = default_dir
                except:
                    output_dir = tempfile.gettempdir()
        
        # 从 URL 提取文件名
        filename = url.split('/')[-1]
        if not filename:
            filename = f"generated_image_{int(time.time())}.png"
        
        filepath = os.path.join(output_dir, filename)
        
        # 下载图片
        urllib.request.urlretrieve(url, filepath)
        print(f"图片已下载到: {filepath}", file=sys.stderr)
        return filepath
    except Exception as e:
        print(f"下载图片失败: {str(e)}", file=sys.stderr)
        return None

def upload_to_feishu_doc(image_path, doc_id=None):
    """上传图片到飞书文档"""
    try:
        # 检查是否安装了必要的依赖
        import subprocess
        
        # 使用 feishu_doc_media 工具上传
        # 注意：这里假设在 OpenClaw 环境中，可以通过命令行调用
        print(f"准备上传图片到飞书文档...", file=sys.stderr)
        
        if doc_id:
            print(f"目标文档 ID: {doc_id}", file=sys.stderr)
        
        # 返回图片路径，让调用者处理上传
        return image_path
    except Exception as e:
        print(f"准备上传失败: {str(e)}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(
        description='RunningHub ComfyUI / AI 应用 图片生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认 AI 应用生成图片
  python comfyui_client.py --api-key "xxx" --prompt "一只小狗"
  
  # 使用指定 AI 应用
  python comfyui_client.py --api-key "xxx" --prompt "夜景" --ai-app-id "1995005060620935169"
  
  # 生成后上传到飞书
  python comfyui_client.py --api-key "xxx" --prompt "风景" --upload-to-feishu --feishu-doc-id "doc_id"
        """
    )
    parser.add_argument('--api-key', required=True, help='RunningHub API Key')
    # 已固定为 AI 应用模式，无需指定 --mode
    parser.add_argument('--ai-app-id', default='1995005060620935169',
                        help='AI 应用 ID (默认: 1995005060620935169)')
    parser.add_argument('--prompt', required=True, help='用于生成图片的文本提示词')
    parser.add_argument('--seed', help='生成用的种子 (可选)')
    parser.add_argument('--upload-to-feishu', action='store_true',
                        help='生成后上传到飞书文档')
    parser.add_argument('--feishu-doc-id', help='飞书文档 ID（用于上传）')
    parser.add_argument('--output-dir', default=r"E:\aicode\openclaw\rh-out",
                        help='图片下载目录（默认: E:\aicode\openclaw\rh-out）')
    parser.add_argument('--show-docs', action='store_true',
                        help='显示 API 文档参考链接')
    
    args = parser.parse_args()
    
    # 显示文档链接
    if args.show_docs:
        print_api_docs()
        return
    
    # 固定使用 AI 应用模式
    create_res = create_task_ai_app(args.api_key, args.ai_app_id, args.prompt, args.seed)
    mode_name = "AI 应用"
    mode_id = args.ai_app_id
    
    if not create_res or create_res.get('code') != 0:
        print(f"创建任务失败", file=sys.stderr)
        if create_res:
            print(json.dumps(create_res, indent=2, ensure_ascii=False), file=sys.stderr)
            # 显示文档帮助
            if create_res.get('code') in [380, 381]:
                print_api_docs()
        sys.exit(1)
        
    task_data = create_res.get('data', {})
    task_id = task_data.get('taskId')
    
    if not task_id:
        print("未返回 taskId", file=sys.stderr)
        sys.exit(1)
        
    print(f"\n任务创建成功。任务 ID: {task_id}", file=sys.stderr)
    
    outputs = wait_for_completion(args.api_key, task_id)
    
    if outputs:
        image_urls = []
        for item in outputs:
            if 'fileUrl' in item and item['fileUrl']:
                image_urls.append(item['fileUrl'])
        
        if image_urls:
            # 输出结果
            for url in image_urls:
                print(f"{url}\n")
                print(f"![生成结果]({url})\n")
            
            print("图片已生成完成！")
            
            # 下载图片
            downloaded_paths = []
            for url in image_urls:
                path = download_image(url, args.output_dir)
                if path:
                    downloaded_paths.append(path)
            
            # 处理飞书上传
            if args.upload_to_feishu or args.feishu_doc_id:
                print("\n📤 飞书文档上传选项已启用", file=sys.stderr)
                if args.feishu_doc_id:
                    print(f"目标文档: {args.feishu_doc_id}", file=sys.stderr)
                for path in downloaded_paths:
                    print(f"图片路径: {path}", file=sys.stderr)
                    # 返回上传信息，让调用者处理实际的上传操作
                    print(f"FEISHU_UPLOAD:{path}")
                    if args.feishu_doc_id:
                        print(f"FEISHU_DOC_ID:{args.feishu_doc_id}")
            else:
                # 询问用户是否上传到飞书
                print("\n💡 提示: 如需上传到飞书文档，请使用 --upload-to-feishu 参数")
                print("   或使用 --feishu-doc-id 指定目标文档")
                for path in downloaded_paths:
                    print(f"FEISHU_UPLOAD_READY:{path}")
            
        else:
            print("任务完成，但未在返回数据中找到图片链接。", file=sys.stderr)
            sys.exit(1)
    else:
        print("未收到任何输出结果", file=sys.stderr)
        print_api_docs()
        sys.exit(1)

if __name__ == "__main__":
    main()
