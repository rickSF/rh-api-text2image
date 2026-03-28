---
name: rh-api-text2image
description: >
  【rh随风】RunningHub rh文生图 - 随风定制版。
  
  触发关键词："rh随风 生图"、"rh随风 生成图片"、"rh随风 画一张"。
  
  使用 RunningHub API 调用 ComfyUI 工作流或 AI 应用生成图片。
  支持工作流和 AI 应用两种模式，生成完成后自动发送图片。
  
  注意：
  - 必须在提示词前加 "rh随风" 才能触发此 skill
  - 此操作包含长轮询，请耐心等待脚本执行完成
  - Windows 环境使用 PowerShell 直接调用 API（无需 python3）
---

# ComfyUI API - RunningHub 图像生成

## 概览

此技能允许用户通过 RunningHub (RunningHub.cn) 的 API 执行 ComfyUI 任务或使用 AI 应用生成图片。它封装了任务创建和结果轮询的过程，使用户能够轻松地生成图片。

**重要提示：**
- 此技能执行时间较长（通常需要几秒到几分钟），脚本会自动轮询直至完成。
- 请勿在短时间内重复调用，以免产生不必要的 API 消耗和重复任务。
- 仅在用户明确发出生成图片指令时使用。

主要功能：
- 支持 **ComfyUI 工作流** 模式（使用 workflow-id）
- 支持 **AI 应用** 模式（使用 ai-app-id，推荐）
- 自动轮询任务状态直至完成
- 获取生成图片的 URL
- 生成完成后可上传至飞书文档

## API 参考文档

遇到问题时可查阅以下官方文档：

- **RunningHub API 文档首页**: https://www.runninghub.cn/runninghub-api-doc-cn/
- **AI 应用完整接入示例**: https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287339
- **AI 应用完整接入示例（高阶版）**: https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287340
- **工作流完整接入示例**: https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287342
- **接口错误码说明**: https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287338

## 配置要求

在使用此技能之前，您必须拥有 RunningHub 的 API Key。

1. 访问 [RunningHub](https://www.runninghub.cn/?inviteCode=rh-v1382) 并注册/登录账号。粉丝注册福利，注册领1000RH币。
2. 在个人中心或开发者设置中获取您的 API Key。
3. 如果您没有提供 API Key，技能脚本将无法执行并报错。请确保在调用时通过 `--api-key` 参数提供有效的 Key。

## 使用方法

此技能主要通过 Python 脚本 `scripts/comfyui_client.py` 使用。

### 运行脚本

```bash
python scripts/comfyui_client.py --api-key "YOUR_API_KEY" --prompt "YOUR_PROMPT" [OPTIONS]
```

### 参数说明

| 参数 | 必选 | 描述 | 默认值 |
| :--- | :--- | :--- | :--- |
| `--api-key` | 是 | RunningHub 的 API Key | 无 |
| `--prompt` | 是 | 生成图片的提示词 | 无 |
| `--mode` | 否 | 运行模式：`workflow` 或 `ai-app` | `ai-app` |
| `--workflow-id` | 否 | ComfyUI 工作流 ID（mode=workflow 时使用） | 1904136902449209346 |
| `--ai-app-id` | 否 | AI 应用 ID（mode=ai-app 时使用） | 1995005060620935169 |
| `--seed` | 否 | 随机种子 | 随机 |
| `--upload-to-feishu` | 否 | 生成后上传到飞书文档 | false |
| `--feishu-doc-id` | 否 | 飞书文档 ID（用于上传） | 无 |

### 示例

**使用 AI 应用生成图片（默认）：**

```bash
python scripts/comfyui_client.py --api-key "abc123xyz" --prompt "一只可爱的小狗在草地上玩耍"
```

**使用指定 AI 应用：**

```bash
python scripts/comfyui_client.py --api-key "abc123xyz" --prompt "赛博朋克风格的城市夜景" --ai-app-id "1995005060620935169"
```

**使用工作流模式：**

```bash
python scripts/comfyui_client.py --api-key "abc123xyz" --prompt "1 girl in classroom" --mode workflow --workflow-id "1904136902449209346"
```

**生成后上传到飞书文档：**

```bash
python scripts/comfyui_client.py --api-key "abc123xyz" --prompt "美丽的风景画" --upload-to-feishu --feishu-doc-id "doc_id_here"
```

## 模式说明

### AI 应用模式（推荐）

AI 应用是 RunningHub 提供的封装好的应用，使用更简单：

- **默认 AI 应用 ID**: `1995005060620935169`
- **API 端点**: `POST /task/openapi/ai-app/run`
- **获取应用 ID**: 打开 AI 应用页面，URL 中的数字即为应用 ID
  - 例如：`https://www.runninghub.cn/ai-detail/1995005060620935169`
  - 应用 ID: `1995005060620935169`

**AI 应用参数传递机制：**

脚本会自动处理 AI 应用的参数传递：

1. **获取节点信息**: 脚本首先调用 `/api/webapp/apiCallDemo` 获取 AI 应用的节点列表
2. **自动识别文本节点**: 查找 `fieldType` 为 `STRING` 的节点（通常是 `prompt` 或 `value` 字段）
3. **更新提示词**: 将用户的提示词更新到正确的节点的 `fieldValue` 字段

**示例节点结构：**
```json
{
  "nodeId": "12",
  "nodeName": "RH_TextInput",
  "fieldName": "value",
  "fieldValue": "用户输入的提示词",
  "fieldType": "STRING",
  "description": "文本输入"
}
```

**注意：** 不同的 AI 应用可能有不同的节点结构，脚本会自动适配。

### 工作流模式

直接使用 ComfyUI 工作流：

- **默认工作流 ID**: `1904136902449209346`
- **API 端点**: `POST /task/openapi/create`
- **获取工作流 ID**: 打开工作流页面，URL 中的数字即为工作流 ID
  - 例如：`https://www.runninghub.cn/#/workflow/1850925505116598274`
  - 工作流 ID: `1850925505116598274`

## API 参考

### 1. AI 应用 - 发起任务

- **URL**: `https://www.runninghub.cn/task/openapi/ai-app/run`
- **Method**: `POST`
- **Content-Type**: `application/json`

**请求体示例:**

```json
{
  "apiKey": "your-api-key",
  "webappId": "1995005060620935169",
  "nodeInfoList": [
    {
      "nodeId": "6",
      "fieldName": "text",
      "fieldValue": "一只可爱的小狗"
    }
  ]
}
```

### 2. 工作流 - 发起任务

- **URL**: `https://www.runninghub.cn/task/openapi/create`
- **Method**: `POST`
- **Content-Type**: `application/json`

**请求体示例:**

```json
{
  "apiKey": "your-api-key",
  "workflowId": "1904136902449209346",
  "nodeInfoList": [
    {
      "nodeId": "6",
      "fieldName": "text",
      "fieldValue": "1 girl in classroom"
    },
    {
      "nodeId": "3",
      "fieldName": "seed",
      "fieldValue": "1231231"
    }
  ]
}
```

### 3. 查询结果

- **URL**: `https://www.runninghub.cn/task/openapi/outputs`
- **Method**: `POST`
- **Content-Type**: `application/json`

**请求体示例:**

```json
{
    "apiKey": "your-api-key",
    "taskId": "task-id-returned-from-create"
}
```

**响应示例:**

```json
{
    "code": 0,
    "msg": "success",
    "data": [
        {
            "fileUrl": "https://rh-images.xiaoyaoyou.com/.../output/....png",
            "fileType": "png",
            "taskCostTime": "83",
            "nodeId": "12"
        }
    ]
}
```

## 错误码说明

常见错误码及解决方案：

| 错误码 | 说明 | 解决方案 |
| :--- | :--- | :--- |
| 380 | WORKFLOW_NOT_EXISTS | 工作流 ID 不存在，检查 workflow-id 是否正确 |
| 381 | WEBAPP_NOT_EXISTS | AI 应用 ID 不存在，检查 ai-app-id 是否正确 |
| 382 | APIKEY_INVALID | API Key 无效，检查 api-key 是否正确 |
| 383 | APIKEY_EXPIRED | API Key 已过期，请重新获取 |
| 384 | APIKEY_TASK_IS_RUNNING | 当前有任务正在运行，请等待完成后再试 |
| 805 | TASK_FAILED | 任务执行失败，查看 failedReason 获取详情 |

更多错误码请参考：[接口错误码说明](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287338)

## 资源

### scripts/
- `comfyui_client.py`: 核心 Python 脚本，用于处理 API 请求、参数构造和轮询逻辑。

## 飞书文档上传

生成图片后，可以通过 `--upload-to-feishu` 参数将图片上传到飞书文档：

1. 使用 `--upload-to-feishu` 启用上传功能
2. 使用 `--feishu-doc-id` 指定目标飞书文档 ID
3. 脚本会自动下载图片并上传到指定文档

如果不指定 `--feishu-doc-id`，脚本会在生成完成后询问用户是否需要上传。
