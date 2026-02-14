# config.example.py - API配置示例
# 复制此文件为 config.py 并填入你的真实密钥

# 阿里云百炼 API Key（用于生成对话）
DASHSCOPE_API_KEY = "your_dashscope_api_key_here"

# 阿里云语音合成 AppKey（用于生成语音）
TTS_APPKEY = "your_tts_appkey_here"

# 阿里云 AccessKey（用于TTS API调用）
ALI_ACCESS_KEY_ID = "your_access_key_id_here"
ALI_ACCESS_KEY_SECRET = "your_access_key_secret_here"

# 说话人配置（使用阿里云Sambert推荐的声音）
SPEAKERS = {
    "host": "zhixiaobao",      # 主持人 - 智小宝
    "guest": "zhichu"          # 嘉宾 - 智初
}

# TTS参数
TTS_CONFIG = {
    "format": "wav",
    "sample_rate": 16000,
    "volume": 50,
    "speech_rate": 0.8
}

# 百炼模型配置
DASHSCOPE_MODEL = "qwen-turbo"

# Qwen3 TTS模型配置
QWEN3_TTS_MODEL = "qwen3-tts-instruct-flash-realtime"
QWEN3_TTS_CONFIG = {
    "format": "wav",
    "sample_rate": 24000,
    "volume": 50,
    "speed": 1.0
}
