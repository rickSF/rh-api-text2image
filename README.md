# rh-api-text2image

> 【rh随风】RunningHub 文生图 Skill - 随风定制版

通过 RunningHub API 调用 AI 应用生成图片，支持自动轮询任务状态并获取结果。

## ✨ 功能特性

- **AI 应用模式**（推荐）：直接调用 RunningHub 平台封装好的 AI 应用
- **工作流模式**：支持自定义 ComfyUI 工作流
- **自动轮询**：提交任务后自动等待完成，无需手动查询
- **飞书集成**：生成后可上传至飞书文档

## 📋 前置要求

- Python 3.7+
- RunningHub API Key（[注册获取](https://www.runninghub.cn/?inviteCode=rh-v1382)，注册领 1000 RH 币）

## 🚀 快速开始

```bash
# 安装依赖
pip install requests

# 生成图片（AI 应用模式，推荐）
python scripts/comfyui_client.py --api-key "YOUR_API_KEY" --prompt "一只可爱的小狗在草地上玩耍"

# 使用指定 AI 应用
python scripts/comfyui_client.py --api-key "YOUR_API_KEY" --prompt "赛博朋克风格城市夜景" --ai-app-id "1995005060620935169"

# 使用工作流模式
python scripts/comfyui_client.py --api-key "YOUR_API_KEY" --prompt "1 girl in classroom" --mode workflow --workflow-id "1904136902449209346"
```

## 📖 参数说明

| 参数 | 必选 | 描述 | 默认值 |
| :--- | :--- | :--- | :--- |
| `--api-key` | ✅ | RunningHub API Key | 无 |
| `--prompt` | ✅ | 生成图片的提示词 | 无 |
| `--ai-app-id` | ❌ | AI 应用 ID | `1995005060620935169` |
| `--seed` | ❌ | 随机种子 | 随机 |
| `--upload-to-feishu` | ❌ | 生成后上传到飞书文档 | `false` |
| `--feishu-doc-id` | ❌ | 飞书文档 ID | 无 |
| `--show-docs` | ❌ | 显示 API 文档参考链接 | `false` |

## 🔗 API 文档参考

- [RunningHub API 文档首页](https://www.runninghub.cn/runninghub-api-doc-cn/)
- [AI 应用完整接入示例](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287339)
- [工作流完整接入示例](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287342)
- [接口错误码说明](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287338)

## 📁 文件结构

```
rh-api-text2image/
├── SKILL.md                  # Skill 定义文件
├── scripts/
│   └── comfyui_client.py     # 核心 Python 脚本
└── README.md
```

## ⚠️ 常见错误码

| 错误码 | 说明 | 解决方案 |
| :--- | :--- | :--- |
| 380 | 工作流不存在 | 检查 workflow-id |
| 381 | AI 应用不存在 | 检查 ai-app-id |
| 382 | API Key 无效 | 检查 api-key |
| 383 | API Key 过期 | 重新获取 |
| 384 | 有任务运行中 | 等待完成后再试 |
| 805 | 任务执行失败 | 查看 failedReason |

## 📄 License

MIT
