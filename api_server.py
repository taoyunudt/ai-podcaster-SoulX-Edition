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
    index_path = os.path.join(static_dir, "index_pro.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # 如果 Pro 版不存在，回退到原版
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
            "soulx": "1.0.0",
            "pro": "1.0.0"
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


class LLMScriptRequest(BaseModel):
    """LLM API 脚本生成请求"""
    api_key: str
    model: str = "qwen-turbo"
    content: str
    theme: Optional[str] = None
    duration_minutes: int = 5
    temperature: float = 0.7
    max_tokens: int = 2000


@app.post("/api/llm/generate/script", response_model=dict)
async def llm_generate_script(request: LLMScriptRequest):
    """
    使用第三方 LLM API 生成播客脚本
    
    支持自定义 LLM API（需要在 config.py 中配置）
    """
    try:
        info(f"📝 收到 LLM 脚本生成请求")
        
        # 构造 LLM API 提示
        theme = request.theme or doc_analyzer.extract_theme(request.content)
        
        system_prompt = """你是一位专业的播客主持人和嘉宾。请根据提供的主题和内容，生成一段自然、流畅的对话式播客脚本。

要求：
1. 生成 2 个角色的对话：主持人（智小宝）和嘉宾（智初）
2. 对话时长约 {duration_minutes} 分钟
3. 使用自然、口语化的中文表达
4. 适当添加语气词和情感标记：<|laughter|> 笑声，<|sigh|> 叹气
5. 保持对话的连贯性和吸引力
6. 每段对话不宜过长，保持自然的节奏

格式：
[S1] 主持人的台词
[S2] 嘉宾的台词
...（重复对话）
""".format(duration_minutes=request.duration_minutes)
        
        user_prompt = f"""
主题：{theme}

参考内容：
{request.content}

请根据以上信息生成播客脚本。
"""
        
        # 检查是否配置了 LLM API（使用阿里云通义千问）
        if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your_dashscope_api_key_here":
            raise HTTPException(
                status_code=500, 
                detail="未配置 LLM API 密钥。请在 config.py 中设置 DASHSCOPE_API_KEY。"
            )
        
        # 调用通义千问 API
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request.model,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            },
            "parameters": {
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
        }
        
        info(f"🤖 调用 LLM API 生成脚本...")
        
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 提取生成的脚本
        if result.get("output") and result["output"].get("text"):
            script = result["output"]["text"].strip()
            
            # 格式化脚本为对话格式
            formatted_script = script.replace("\n\n", "\n")
            
            info(f"✅ LLM 脚本生成成功，长度: {len(formatted_script)} 字符")
            
            return {
                "success": True,
                "script": formatted_script,
                "theme": theme,
                "duration_minutes": request.duration_minutes,
                "model": request.model,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        else:
            raise HTTPException(status_code=500, detail="LLM API 返回格式错误")

    except requests.exceptions.RequestException as e:
        error(f"❌ LLM API 调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM API 调用失败: {str(e)}")
    except Exception as e:
        error(f"❌ 脚本生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {str(e)}")


# 添加一个统一的脚本生成端点（兼容旧版和新版）
@app.post("/api/generate/script", response_model=ScriptResponse)
async def generate_script_v2(request: ScriptGenerationRequest):
    """
    增强的播客脚本生成
    
    支持两种模式：
    1. 旧模式（内部模板生成）- 无需 API 密钥
    2. 新模式（LLM API 生成）- 需要配置 DASHSCOPE_API_KEY
    """
    try:
        info(f"📝 收到脚本生成请求 (模式: {request.input_type})")
        
        # 检查是否配置了 LLM API
        use_llm = (DASHSCOPE_API_KEY and DASHSCOPE_API_KEY != "your_dashscope_api_key_here")
        
        if use_llm:
            # 使用 LLM API 生成
            llm_request = LLMScriptRequest(
                api_key=DASHSCOPE_API_KEY,
                content=request.content,
                theme=request.theme,
                duration_minutes=request.duration_minutes,
                temperature=0.7,
                max_tokens=2000
            )
            
            info("🤖 使用 LLM API 生成脚本...")
            
            try:
                llm_response = await llm_generate_script(llm_request)
                
                if llm_response["success"]:
                    return {
                        "success": True,
                        "script": llm_response["script"],
                        "dialogue": parse_dialogue(llm_response["script"]),
                        "theme": llm_response["theme"],
                        "duration_minutes": request.duration_minutes,
                        "estimated_duration": llm_response["duration_minutes"] * 60,
                        "model": llm_response["model"],
                        "mode": "llm_api"
                    }
            except HTTPException as e:
                # 如果 LLM API 失败，回退到内部模板
                info(f"⚠️ LLM API 失败，回退到内部模板: {e.detail}")
                use_llm = False
        
        # 回退到内部模板生成（无需 API）
        if not use_llm:
            info("📝 使用内部模板生成脚本...")
            
            if not request.theme:
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
                    "estimated_duration": result['estimated_duration'],
                    "mode": "internal_template"
                }
            else:
                raise HTTPException(status_code=500, detail=result.get('error', '脚本生成失败'))

    except HTTPException:
        raise
    except Exception as e:
        error(f"❌ 脚本生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


def parse_dialogue(script: str) -> list:
    """解析脚本为对话列表"""
    dialogue = []
    current_speaker = None
    current_text = ""
    
    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 检测说话人标记
        speaker_match = line.match(r'^\[S(\d+)\](.+)$')
        if speaker_match:
            # 保存之前的对话
            if current_speaker and current_text:
                dialogue.append({
                    "speaker": f"S{current_speaker}",
                    "text": current_text.strip()
                })
            
            current_speaker = int(speaker_match.group(1))
            current_text = speaker_match.group(2).strip()
        else:
            # 继续当前对话
            if line:
                current_text += " " + line
    
    # 保存最后一段对话
    if current_speaker and current_text:
        dialogue.append({
            "speaker": f"S{current_speaker}",
            "text": current_text.strip()
        })
    
    return dialogue


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
