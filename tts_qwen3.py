# tts_qwen3.py - Qwen3 TTS引擎

import os
import time
import dashscope
from dashscope.audio.tts_v2 import *
from config import QWEN3_TTS_MODEL, DASHSCOPE_API_KEY
from utils.log_utils import info, error, warning
from utils.file_utils import ensure_directory

class Qwen3TTSEngine:
    """Qwen3 TTS引擎（使用qwen3-tts-instruct-flash-realtime模型）"""

    def __init__(self):
        self.api_key = DASHSCOPE_API_KEY
        dashscope.api_key = self.api_key
        # 设置 WebSocket API URL（北京地域）
        dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
        self.audio_dir = os.path.join(os.path.dirname(__file__), 'audio')
        ensure_directory(self.audio_dir)

        # 模型名称
        self.model = QWEN3_TTS_MODEL

    def text_to_speech(self, text: str, speaker: str) -> str:
        """
        将文本转换为语音

        Args:
            text: 要转换的文本
            speaker: 说话人角色 ('host' 或 'guest')

        Returns:
            str: 音频文件路径
        """

        # 参数验证
        if not text or len(text.strip()) == 0:
            warning(f"   ❌ 文本内容为空")
            return None

        if not self.api_key:
            error(f"   ❌ DASHSCOPE_API_KEY 未配置")
            return None

        try:
            # 生成唯一的文件名
            timestamp = int(time.time() * 1000)
            filename = f"{speaker}_{timestamp}.mp3"
            file_path = os.path.join(self.audio_dir, filename)

            # 发送文本
            info(f"   🎤 正在生成 [{speaker}] 的语音...")
            info(f"      文本: {text[:50]}..." if len(text) > 50 else f"      文本: {text}")
            info(f"      模型: {self.model}")

            # 尝试使用 qwen3 模型
            audio_data = self._try_qwen3_model(text, speaker)

            if audio_data:
                # 写入音频数据
                with open(file_path, 'wb') as f:
                    f.write(audio_data)

                file_size = os.path.getsize(file_path)
                info(f"   ✓ 语音生成成功: {filename} ({file_size} bytes)")
                return file_path
            else:
                # 如果 qwen3 模型失败，使用备选方案
                info(f"   ⚠️ Qwen3 模型失败，使用备选方案...")
                return self._fallback_tts(text, speaker)

        except Exception as e:
            error(f"   ❌ TTS转换失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 发生异常时使用备选方案
            return self._fallback_tts(text, speaker)

    def _try_qwen3_model(self, text: str, speaker: str) -> bytes:
        """
        尝试使用 qwen3 模型进行语音合成

        Args:
            text: 要转换的文本
            speaker: 说话人角色

        Returns:
            bytes: 音频数据
        """
        try:
            # 根据模型选择正确的音色
            # 对于 qwen3-tts-instruct-flash-realtime，使用 longanyang 等音色
            voice = "longanyang"  # 使用 longanyang 音色，符合 cosyvoice-v3 系列模型的要求

            # 实例化 SpeechSynthesizer，并在构造方法中传入模型、音色等请求参数
            info(f"   📤 实例化 SpeechSynthesizer")
            info(f"      模型: {self.model}")
            info(f"      音色: {voice}")

            synthesizer = SpeechSynthesizer(model=self.model, voice=voice)

            # 发送待合成文本，获取二进制音频
            info(f"   � 调用 synthesizer.call() 方法")
            audio = synthesizer.call(text)

            # 首次发送文本时需建立 WebSocket 连接，因此首包延迟会包含连接建立的耗时
            info(f"   � 请求ID: {synthesizer.get_last_request_id()}")
            info(f"   � 首包延迟: {synthesizer.get_first_package_delay()} 毫秒")

            if audio:
                info(f"   ✅ 成功获取音频数据: {len(audio)} bytes")
                return audio
            else:
                error(f"   ❌ Qwen3 模型未返回音频数据")
                return None

        except Exception as e:
            error(f"   ❌ Qwen3 模型调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _fallback_tts(self, text: str, speaker: str) -> str:
        """
        备选 TTS 方案（使用 edge-tts）

        Args:
            text: 要转换的文本
            speaker: 说话人角色

        Returns:
            str: 音频文件路径
        """
        try:
            # 生成唯一的文件名
            timestamp = int(time.time() * 1000)
            filename = f"{speaker}_{timestamp}_fallback.mp3"
            file_path = os.path.join(self.audio_dir, filename)

            info(f"   🎤 使用备选 TTS 方案...")

            # 使用 edge-tts（免费的 TTS 服务）
            import edge_tts

            # 选择声音
            voice = "zh-CN-XiaoxiaoNeural" if speaker == "host" else "zh-CN-YunxiNeural"

            info(f"   🗣️ 使用 edge-tts 声音: {voice}")

            # 使用线程池来运行异步代码
            import asyncio
            import concurrent.futures

            async def save_audio():
                communicate = edge_tts.Communicate(text, voice)
                with open(file_path, "wb") as f:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])

            # 在新线程中运行异步代码，避免事件循环冲突
            def run_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(save_audio())
                finally:
                    loop.close()

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_in_thread)
                future.result(timeout=30)  # 30秒超时

            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                info(f"   ✓ 备选方案语音生成成功: {filename} ({file_size} bytes)")
                return file_path
            else:
                error(f"   ❌ 备选方案生成的音频文件为空")
                return None

        except Exception as e:
            error(f"   ❌ 备选方案失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


# 保持兼容性
TTSEngine = Qwen3TTSEngine
