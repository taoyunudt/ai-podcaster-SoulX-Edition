# AI 播客生成器 - SoulX Edition

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

基于 SoulX-Podcast 的 AI 播客生成器，支持零样本声音克隆和高保真音频生成。

## ✨ 核心功能

### 🎤 零样本声音克隆
- **快速克隆**：只需上传 5-30 秒参考音频即可克隆声音
- **多说话人**：支持最多 4 个不同的说话人
- **文本对齐**：提供准确的参考文本，提高克隆质量
- **实时预览**：上传后立即播放和验证

### 🎵 高保真音频生成
- **1.7B 模型**：使用 SoulX-Podcast 开源模型
- **自然流畅**：生成播客风格的自然对话音频
- **方言支持**：支持普通话、四川话、河南话、粤语
- **情感标记**：支持 `<|laughter|>`、`<|sigh|>` 等副语言标记

### 📝 脚本编辑器
- **简单易用**：直观的三栏布局
- **说话人标记**：使用 `[S1]`、`[S2]` 等标记不同说话人
- **情感标记**：支持笑声、叹气等情感表达
- **快速模板**：一键生成播客开场脚本

### 🔧 参数调优
- **随机种子**：控制生成随机性
- **温度**：调整生成多样性（0.1-2.0）
- **Top-K**：限制采样词数（1-500）
- **Top-P**：核采样参数（0.0-1.0）

## 🚀 快速开始

### 前置条件

#### 系统要求
- **操作系统**：macOS / Linux / Windows
- **Python 版本**：Python 3.9 或更高
- **内存**：建议 16GB 以上
- **磁盘空间**：至少 10GB

#### 必需软件
- **FFmpeg**（音频处理）
  ```bash
  # macOS
  brew install ffmpeg
  
  # Ubuntu/Debian
  sudo apt install ffmpeg
  ```

- **SoulX-Podcast**（音频生成引擎）
  ```bash
  git clone https://github.com/Soul-AILab/SoulX-Podcast.git
  cd SoulX-Podcast
  ```

### 部署步骤

#### 1. 克隆项目
```bash
git clone https://github.com/taoyunudt/ai-podcaster-SoulX-Edition.git
cd ai-podcaster-SoulX-Edition
```

#### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置 SoulX-Podcast

**注意**：本项目需要 SoulX-Podcast 作为音频生成引擎。

```bash
# 在 SoulX-Podcast 目录下
cd ~/projects/SoulX-Podcast

# 安装 SoulX-Podcast 依赖
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 下载模型
mkdir -p pretrained_models
huggingface-cli download --resume-download Soul-AILab/SoulX-Podcast-1.7B \
  --local-dir pretrained_models/SoulX-Podcast-1.7B
```

#### 5. 启动服务

**方式一：使用启动脚本（推荐）**
```bash
./start_soulx.sh
```

**方式二：手动启动**
```bash
# 终端 1：启动 SoulX-Podcast API
cd ~/projects/SoulX-Podcast
source venv/bin/activate
python run_api.py --model pretrained_models/SoulX-Podcast-1.7B --port 8000

# 终端 2：启动 ai-podcaster
cd ~/projects/ai-podcaster-SoulX-Edition
source venv/bin/activate
python3 api_server.py
```

#### 6. 访问应用

打开浏览器访问：
```
http://localhost:8001/soulx
```

## 📖 使用指南

### 步骤 1：声音克隆

1. **选择声音槽位**：说话人 1-4
2. **上传参考音频**：
   - 格式：WAV/MP3/M4A
   - 时长：5-30 秒
   - 质量：清晰、无背景噪音
3. **输入参考文本**：
   - 准确对应音频内容
   - 避免拼写错误
4. **等待状态更新**：显示"✓ 准备就绪"
5. **重复克隆**：可以克隆最多 4 个声音

### 步骤 2：编辑脚本

**格式：**
```
[S1] 欢迎收听本期的播客节目！
[S2] 很高兴能在这里和大家聊天！
[S1] 今天我们来聊聊人工智能的最新发展。
[S2] 确实，最近AI技术发展非常快，<|laughter|> 感觉每天都有新东西！
```

**快捷操作：**
- **📝 插入示例**：插入预设的示例脚本
- **🗑️ 清空**：清空脚本内容
- **📝 生成脚本模板**：自动创建开场脚本

### 步骤 3：生成音频

1. **调整参数**（可选）：
   - 随机种子：控制随机性
   - 温度：0.6（推荐）
   - Top-K：100（推荐）
   - Top-P：0.9（推荐）

2. **点击生成**：`🎵 生成音频`

3. **等待完成**：3-10 分钟（取决于对话长度）

4. **播放和下载**：
   - 在线播放生成的音频
   - 点击下载保存到本地

## 🎯 技术架构

### 系统组件

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  SoulX Frontend │    │ ai-podcaster API │    │ SoulX-Podcast API│
│  (HTML/CSS/JS) │    │  (FastAPI)       │    │  (PyTorch)      │
└────────┬────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                     │                      │
         │ HTTP                │ HTTP                │
         └─────────────────────┴──────────────────────┘
                            Port 8001               Port 8000
```

### 技术栈

**前端：**
- HTML5 + CSS3 + JavaScript（纯静态）
- 三栏响应式布局
- FormData 文件上传

**后端：**
- FastAPI + Uvicorn
- 静态文件服务
- 代理转发到 SoulX-Podcast API

**音频生成：**
- SoulX-Podcast 1.7B 模型
- PyTorch + MPS 加速
- HuggingFace Transformers

## 📊 性能参考

**测试环境：**
- 设备：Apple MacBook Air (M1/M2/M3)
- 内存：16GB
- 模型：SoulX-Podcast 1.7B

**生成时间：**
- 4 轮对话：约 6 分钟
- 8 轮对话：约 12 分钟
- 12 轮对话：约 18 分钟

**音频质量：**
- 采样率：24kHz
- 格式：WAV（无损）
- 文件大小：约 0.5-1.5 MB/分钟

## 🆚 版本对比

| 特性 | 标准版 | SoulX Edition |
|------|--------|---------------|
| 声音克隆 | ❌ 不支持 | ✅ 零样本克隆 |
| 音频质量 | 流畅自然 | 高保真播客 |
| 方言支持 | 标准普通话 | ✅ 多方言 |
| 情感标记 | 有限 | ✅ 丰富 |
| 网络依赖 | 需要（API） | ✅ 本地化 |
| 使用成本 | 按量付费 | ✅ 完全免费 |
| 数据隐私 | 上传云端 | ✅ 完全本地 |
| 定制能力 | 有限 | ✅ 高度可定制 |

## 📁 项目结构

```
ai-podcaster-SoulX-Edition/
├── static/                      # 前端静态文件
│   ├── index_soulx.html        # SoulX Edition 主界面
│   ├── css/
│   │   └── style_soulx.css     # SoulX Edition 样式
│   └── js/
│       └── app_soulx.js         # SoulX Edition 逻辑
├── api_server.py                # FastAPI 后端服务
├── start_soulx.sh              # 一键启动脚本
├── SOULX_GUIDE.md              # SoulX 使用指南
├── INTEGRATION_REPORT.md        # 集成报告
├── DEPLOYMENT_COMPLETE.md       # 部署完成报告
├── requirements.txt             # Python 依赖
├── config.py                   # 配置文件（标准版）
├── config.example.py           # 配置文件示例
├── generator.py                # 对话生成器（标准版）
├── tts_qwen3.py               # 千问 TTS 引擎（标准版）
├── merger_advanced.py          # 音频合并模块
├── script_generator.py         # 播客脚本生成器
└── README.md                  # 本文件
```

## 🛠️ 常见问题

### Q: 声音克隆不成功
**A:** 检查以下几点：
- 参考音频是否清晰、无噪音
- 参考文本是否准确对应音频内容
- 音频文件格式是否支持（推荐 WAV）
- 音频时长是否合适（5-30 秒）

### Q: 生成时间过长
**A:** 取决于：
- 对话长度：减少对话轮数
- 硬件性能：Apple Silicon 已优化
- 参数设置：尝试更简单的参数

### Q: 音频质量不佳
**A:** 尝试优化：
- 提高参考音频质量
- 准确对应参考文本
- 调整温度参数
- 尝试不同的随机种子

### Q: SoulX-Podcast API 连接失败
**A:** 检查：
- SoulX-Podcast API 是否运行在端口 8000
- 网络连接是否正常
- 模型是否已下载完成

## 📝 开发指南

### 本地开发
```bash
# 1. 克隆项目
git clone https://github.com/taoyunudt/ai-podcaster-SoulX-Edition.git
cd ai-podcaster-SoulX-Edition

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动开发服务器
python3 api_server.py
```

### 添加新功能
- **前端**：修改 `static/` 下的文件
- **后端 API**：修改 `api_server.py`
- **集成 SoulX**：参考 `SOULX_GUIDE.md`

### 代码风格
项目遵循 PEP 8 Python 编码规范。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 👥 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📧 联系方式

- **作者**：taoyunudt
- **GitHub**：https://github.com/taoyunudt
- **项目地址**：https://github.com/taoyunudt/ai-podcaster-SoulX-Edition

## 🙏 致谢

- [SoulX-Podcast](https://github.com/Soul-AILab/SoulX-Podcast) - 提供强大的 TTS 能力
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [FFmpeg](https://ffmpeg.org/) - 强大的音频处理工具

## 📅 更新日志

### v1.0.0 (2026-02-22)

✨ **初始版本发布**

- ✨ 完整的 SoulX-Podcast 集成
- ✨ 零样本声音克隆功能（最多 4 个说话人）
- ✨ 高保真音频生成（1.7B 模型）
- ✨ 三栏响应式布局 Web 界面
- ✨ 脚本编辑器（支持说话人标记和情感标记）
- ✨ 丰富的生成参数调优
- ✨ 完全本地化推理（无需 API 密钥）
- ✨ 详细的文档和部署指南
- ✨ 一键启动脚本

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

---

**Made with ❤️ by taoyunudt**
