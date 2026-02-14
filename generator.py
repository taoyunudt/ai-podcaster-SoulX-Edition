# generator.py - 对话生成模块

import dashscope
from dashscope import Generation
from config import DASHSCOPE_API_KEY, DASHSCOPE_MODEL
from utils.log_utils import info, error, warning

def generate_dialogue(script: str) -> list:
    """
    根据脚本生成双人对话

    Args:
        script: 原始脚本文本

    Returns:
        list: 对话列表，格式: [{'speaker': 'host', 'text': '...'}, ...]
    """
    info("🤖 正在调用阿里云百炼生成对话...")

    if not script or len(script.strip()) == 0:
        error("脚本内容为空")
        return []

    prompt = f"""
你是一个专业的播客对话生成器。请将以下播客脚本转换为自然、口语化的双人对话。

【对话风格要求 - 非常重要】
1. 模拟真实对话场景：
   - 两人互相呼应，不是各说各的
   - 加入反问、确认、共鸣等互动
   - 有来有往，不是单方面陈述

2. 口语化处理：
   - 用"嗯"、"啊"、"哦"等语气词
   - 用"对吧"、"是吧"等反问
   - 用"说真的"、"你看"、"你知道吗"等引导词
   - 避免书面语，用口语替代（如"因此"→"所以"，"然而"→"不过"）

3. 节奏和停顿：
   - 每段控制在15-35字（短句更自然）
   - 适当留白，不要满嘴输出
   - 加入思考语气（"嗯..."、"让我想想"）

4. 角色区分：
   - 主持人：引导话题，语气稳重但有亲和力
   - 嘉宾：好奇提问，语气活泼有参与感

【输出格式】
- 每行以 [主持人] 或 [嘉宾] 开头
- 每段15-35字，便于语音生成
- 保持原文核心信息不变

【原始脚本】
{script}

【直接输出对话，不要其他内容】
"""

    try:
        if not DASHSCOPE_API_KEY:
            error("DASHSCOPE_API_KEY 未配置")
            return []

        if not DASHSCOPE_MODEL:
            error("DASHSCOPE_MODEL 未配置")
            return []

        response = Generation.call(
            model=DASHSCOPE_MODEL,
            prompt=prompt,
            api_key=DASHSCOPE_API_KEY,
            result_format='message'
        )

        if response.status_code == 200:
            if not response.output or not response.output.choices:
                error("API返回结果格式错误")
                return []

            dialogue_text = response.output.choices[0].message.content
            dialogue = parse_dialogue(dialogue_text)
            info(f"✅ 成功生成 {len(dialogue)} 段对话")
            return dialogue
        else:
            error(f"百炼API调用失败: {response.message}")
            return []

    except Exception as e:
        error(f"❌ 对话生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def parse_dialogue(text: str) -> list:
    """
    解析对话文本

    Args:
        text: 对话文本

    Returns:
        list: 解析后的对话列表
    """
    dialogue = []

    if not text:
        warning("对话文本为空")
        return dialogue

    try:
        for line in text.strip().split('\n'):
            line = line.strip()

            if not line:
                continue

            # 解析说话人
            if line.startswith('[主持人]'):
                speaker = 'host'
                content = line[5:].strip()
            elif line.startswith('[嘉宾]'):
                speaker = 'guest'
                content = line[5:].strip()
            elif line.startswith('[男]'):
                speaker = 'host'
                content = line[3:].strip()
            elif line.startswith('[女]'):
                speaker = 'guest'
                content = line[3:].strip()
            else:
                # 如果没有标记，默认为主持人
                speaker = 'host'
                content = line

            if content:
                dialogue.append({
                    'speaker': speaker,
                    'text': content
                })

        if not dialogue:
            warning("解析后对话列表为空")

        return dialogue
    except Exception as e:
        error(f"对话解析失败: {str(e)}")
        return []


def display_dialogue(dialogue: list):
    """
    打印对话内容

    Args:
        dialogue: 对话列表
    """
    info("\n" + "="*60)
    info("📝 生成的对话内容:")
    info("="*60)

    if not dialogue:
        warning("对话内容为空")
        info("="*60 + "\n")
        return

    for i, line in enumerate(dialogue, 1):
        speaker_name = "主持人" if line['speaker'] == 'host' else "嘉宾"
        info(f"{i}. [{speaker_name}] {line['text']}")

    info("="*60 + "\n")


if __name__ == '__main__':
    # 测试
    test_script = """
    今天我们来聊聊人工智能的发展。
    AI技术在过去几年突飞猛进。
    是的，特别是大语言模型的出现。
    """

    dialogue = generate_dialogue(test_script)
    display_dialogue(dialogue)
