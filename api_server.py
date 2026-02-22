# api_server.py - FastAPI 服务器

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import sys
import uuid
import tempfile
import shutil
from typing import List, Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from generator import generate_dialogue
from tts_qwen3 import Qwen3TTSEngine
from merger_advanced import merge_audio_advanced
from script_generator import generate_podcast_script
from utils.document_analyzer import DocumentAnalyzer
from utils.log_utils import info, error

app = FastAPI(title="AI 播客生成器 API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    info(f"✅ 静态文件目录挂载成功: {static_dir}")
else:
    info(f"⚠️  静态文件目录不存在: {static_dir}")

# 数据模型
class PodcastRequest(BaseModel):
    script: str


class ScriptGenerationRequest(BaseModel):
    content: str
    input_type: str  # text, url, word, pdf
    duration_minutes: int = 5
    theme: Optional[str] = None


class DialogueLine(BaseModel):
    speaker: str
    text: str


class PodcastResponse(BaseModel):
    success: bool
    dialogue: List[DialogueLine]
    audio_url: str
    duration: float
    message: str


class ScriptResponse(BaseModel):
    success: bool
    script: str
    dialogue: List[DialogueLine]
    theme: str
    duration_minutes: int
    estimated_duration: float


# TTS 引擎（全局实例）
tts_engine = None
doc_analyzer = None


@app.on_event("startup")
async def startup_event():
    global tts_engine, doc_analyzer
    info("🚀 FastAPI 服务器启动")
    tts_engine = Qwen3TTSEngine()
    doc_analyzer = DocumentAnalyzer()
    info("✅ TTS 引擎初始化完成")
    info("✅ 文档分析器初始化完成")


@app.get("/")
async def root():
    """重定向到前端页面"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI 播客生成器 API"}


@app.get("/soulx")
async def soulx_root():
    """SoulX Edition 前端页面"""
    index_path = os.path.join(static_dir, "index_soulx.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "SoulX Edition 前端未找到"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "versions": {
            "standard": "1.0.0",
            "soulx": "1.0.0"
        }
    }


class URLRequest(BaseModel):
    url: str


@app.post("/api/analyze/url", response_model=dict)
async def analyze_url(request: URLRequest):
    """分析网址内容"""
    try:
        result = doc_analyzer.analyze_url(request.url)
        if result:
            return {
                "success": True,
                **result
            }
        else:
            raise HTTPException(status_code=500, detail="网址分析失败")
    except Exception as e:
        error(f"网址分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/document", response_model=dict)
async def analyze_document(file: UploadFile = File(...)):
    """分析上传的文档"""
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        # 根据文件类型分析
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext == 'docx':
            result = doc_analyzer.analyze_word(tmp_path)
        elif file_ext == 'pdf':
            result = doc_analyzer.analyze_pdf(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式")

        # 删除临时文件
        os.unlink(tmp_path)

        if result:
            return {
                "success": True,
                **result
            }
        else:
            raise HTTPException(status_code=500, detail="文档分析失败")

    except HTTPException:
        raise
    except Exception as e:
        error(f"文档分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/script", response_model=ScriptResponse)
async def generate_script(request: ScriptGenerationRequest):
    """生成播客脚本"""
    try:
        info(f"📝 收到脚本生成请求")

        # 如果没有提供主题，从内容中提取
        theme = request.theme
        if not theme:
            theme = doc_analyzer.extract_theme(request.content)
            info(f"🎯 提取的主题: {theme}")
        else:
            theme = request.theme

        # 生成脚本
        result = generate_podcast_script(theme, request.duration_minutes)

        if result['success']:
            return {
                "success": True,
                "script": result['script'],
                "dialogue": result['dialogue'],
                "theme": theme,
                "duration_minutes": request.duration_minutes,
                "estimated_duration": result['estimated_duration']
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', '脚本生成失败'))

    except HTTPException:
        raise
    except Exception as e:
        error(f"脚本生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/audio", response_model=PodcastResponse)
async def generate_audio_from_script(request: PodcastRequest):
    """根据脚本生成音频"""
    if not request.script or len(request.script.strip()) == 0:
        raise HTTPException(status_code=400, detail="脚本内容不能为空")

    try:
        info(f"📝 收到音频生成请求，脚本长度: {len(request.script)} 字符")

        # 1. 生成对话
        dialogue = generate_dialogue(request.script)
        if not dialogue:
            raise HTTPException(status_code=500, detail="对话生成失败")

        info(f"✅ 成功生成 {len(dialogue)} 段对话")

        # 2. 转换为音频
        audio_files = []
        for i, line in enumerate(dialogue, 1):
            info(f"   [{i}/{len(dialogue)}] 正在生成语音...")
            audio_path = tts_engine.text_to_speech(line["text"], line["speaker"])
            if audio_path:
                audio_files.append(audio_path)
            else:
                error(f"   ❌ 语音生成失败: {line['text']}")

        if not audio_files:
            raise HTTPException(status_code=500, detail="音频生成失败")

        # 3. 合并音频
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)

        output_filename = f"podcast_{uuid.uuid4().hex[:8]}.mp3"
        output_file = os.path.join(output_dir, output_filename)

        info(f"🎵 正在合并音频...")
        merge_audio_advanced(
            audio_files,
            output_file,
            silence_duration=100,
            volume_adjustment=1.0,
            output_format="mp3",
            bitrate="128k"
        )

        # 4. 计算时长
        duration = len(dialogue) * 3.0

        info(f"✅ 播客生成完成: {output_filename}")

        return {
            "success": True,
            "dialogue": dialogue,
            "audio_url": f"/api/audio/{output_filename}",
            "duration": duration,
            "message": "播客生成成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        error(f"❌ 生成播客失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """获取生成的音频文件"""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    file_path = os.path.join(output_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="音频文件不存在")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
