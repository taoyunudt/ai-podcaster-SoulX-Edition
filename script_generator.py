# script_generator.py - 根据主题和时长生成脚本

from dashscope import Generation
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL
from utils.log_utils import info, error


def generate_podcast_script(theme: str, duration_minutes: int = 5) -> dict:
    """
    根据主题和时长生成播客脚本

    Args:
        theme: 播客主题
        duration_minutes: 时长（分钟），1-10

    Returns:
        dict: {script, dialogue, estimated_duration}
    """
    try:
        # 计算需要的字数（平均每分钟 150-200 字，对话形式需要更多）
        target_length = duration_minutes * 180  # 每分钟 180 字

        info(f"📝 正在生成播客脚本...")
        info(f"   主题: {theme}")
        info(f"   时长: {duration_minutes} 分钟")
        info(f"   目标字数: 约 {target_length} 字")

        prompt = f"""
你是一个专业的播客脚本创作者。请根据以下主题创作一个双人对话脚本。

【主题】
{theme}

【要求】
1. 时长: {duration_minutes} 分钟（约 {target_length} 字）
2. 对话形式: 主持人 + 嘉宾
3. 内容要求:
   - 围绕主题展开讨论
   - 有起承转合，有观点有讨论
   - 口语化，适合播客
   - 有互动感和真实感

4. 每段控制在 20-40 字，方便语音生成

【输出格式】
- 直接输出对话内容
- 每行以 [主持人] 或 [嘉宾] 开头
- 不要任何开场白和结束语
- 不要任何说明文字

【直接开始输出对话】
"""

        response = Generation.call(
            model=DASHSCOPE_MODEL,
            prompt=prompt,
            api_key=DASHSCOPE_API_KEY,
            result_format='message'
        )

        if response.status_code == 200:
            if not response.output or not response.output.choices:
                error("API返回结果格式错误")
                return {
                    'success': False,
                    'error': 'API返回结果格式错误'
                }

            script_text = response.output.choices[0].message.content.strip()

            # 解析对话
            dialogue = []
            for line in script_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line.startswith('[主持人]'):
                    dialogue.append({
                        'speaker': 'host',
                        'text': line[5:].strip()
                    })
                elif line.startswith('[嘉宾]'):
                    dialogue.append({
                        'speaker': 'guest',
                        'text': line[5:].strip()
                    })

            # 计算实际时长（平均每段 3 秒）
            estimated_duration = len(dialogue) * 3.0

            info(f"✅ 脚本生成完成")
            info(f"   实际字数: {len(script_text)} 字")
            info(f"   对话段数: {len(dialogue)} 段")
            info(f"   预估时长: {estimated_duration:.1f} 秒")

            return {
                'success': True,
                'script': script_text,
                'dialogue': dialogue,
                'theme': theme,
                'duration_minutes': duration_minutes,
                'estimated_duration': estimated_duration
            }
        else:
            error(f"脚本生成失败: {response.message}")
            return {
                'success': False,
                'error': response.message
            }

    except Exception as e:
        error(f"❌ 脚本生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def refine_script(script: str) -> dict:
    """
    优化和润色脚本

    Args:
        script: 原始脚本

    Returns:
        dict: {success, refined_script, dialogue}
    """
    try:
        info(f"🔧 正在优化脚本...")

        prompt = f"""
请优化以下播客脚本，使其更加口语化、自然流畅。

【要求】
1. 保持原意和结构不变
2. 让对话更加自然，像真人聊天
3. 适当加入语气词和互动
4. 每段控制在 20-40 字

【原始脚本】
{script}

【优化后的脚本】
"""

        response = Generation.call(
            model=DASHSCOPE_MODEL,
            prompt=prompt,
            api_key=DASHSCOPE_API_KEY,
            result_format='message'
        )

        if response.status_code == 200:
            if not response.output or not response.output.choices:
                error("API返回结果格式错误")
                return {
                    'success': False,
                    'error': 'API返回结果格式错误'
                }

            refined_script = response.output.choices[0].message.content.strip()

            # 解析对话
            dialogue = []
            for line in refined_script.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line.startswith('[主持人]'):
                    dialogue.append({
                        'speaker': 'host',
                        'text': line[5:].strip()
                    })
                elif line.startswith('[嘉宾]'):
                    dialogue.append({
                        'speaker': 'guest',
                        'text': line[5:].strip()
                    })

            info(f"✅ 脚本优化完成")

            return {
                'success': True,
                'refined_script': refined_script,
                'dialogue': dialogue
            }
        else:
            error(f"脚本优化失败: {response.message}")
            return {
                'success': False,
                'error': response.message
            }

    except Exception as e:
        error(f"❌ 脚本优化失败: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
