#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py - AI播客生成器主程序

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from generator import generate_dialogue, display_dialogue
from tts_qwen3 import Qwen3TTSEngine as TTSEngine
from merger_simple import merge_audio
from merger_advanced import merge_audio_advanced
from utils.file_utils import read_file, get_output_path
from utils.log_utils import info, warning, error, critical


def main(script_file: str, output_file: str = None):
    """
    主流程：根据脚本生成播客音频

    Args:
        script_file: 脚本文件路径
        output_file: 输出音频文件路径

    Returns:
        bool: 生成是否成功
    """

    # 默认输出到桌面
    if output_file is None:
        output_file = get_output_path("AI播客测试.mp3")

    info("="*60)
    info("🎙️ AI播客生成器")
    info("="*60)

    try:
        # 1. 读取脚本
        info(f"\n📖 正在读取脚本: {script_file}")

        if not os.path.exists(script_file):
            error(f"脚本文件不存在: {script_file}")
            return False

        script = read_file(script_file)
        info(f"✅ 脚本读取完成 (约 {len(script)} 字符)")

        # 2. 生成对话
        dialogue = generate_dialogue(script)

        if not dialogue:
            error("对话生成失败")
            return False

        # 显示生成的对话
        display_dialogue(dialogue)

        # 3. 转换为音频
        info("🎙️ 正在转换语音...")
        tts = TTSEngine()
        audio_files = []

        for i, line in enumerate(dialogue, 1):
            info(f"   [{i}/{len(dialogue)}] 正在处理...")
            audio_path = tts.text_to_speech(line['text'], line['speaker'])

            if audio_path:
                audio_files.append(audio_path)
                info(f"   ✓ 语音生成成功")
            else:
                warning(f"   ⚠️ 跳过该段语音生成")

        if not audio_files:
            error("\n❌ 没有成功生成任何音频文件")
            return False

        # 4. 合并音频
        info(f"\n🎵 正在合并音频文件（共 {len(audio_files)} 个）...")
        
        # 使用高级合并功能
        # 可根据需要调整参数
        merge_audio_advanced(
            audio_files,
            output_file,
            silence_duration=100,  # 静音间隔
            volume_adjustment=1.0,  # 音量调整
            background_music=None,  # 背景音乐路径
            bgm_volume=0.3,  # 背景音乐音量
            output_format='mp3',  # 输出格式
            bitrate='128k'  # 比特率
        )

        # 5. 完成
        info("\n" + "="*60)
        info("🎉 播客生成完成！")
        info(f"📍 输出文件: {output_file}")
        info(f"📊 统计信息:")
        info(f"   - 原始脚本: {len(script)} 字符")
        info(f"   - 生成对话: {len(dialogue)} 条")
        info(f"   - 音频片段: {len(audio_files)} 个")
        info("="*60)

        return True

    except Exception as e:
        critical(f"❌ 程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def batch_process(script_files: list, output_dir: str = None):
    """
    批处理多个脚本文件

    Args:
        script_files: 脚本文件路径列表
        output_dir: 输出目录

    Returns:
        int: 成功处理的文件数
    """
    if output_dir is None:
        output_dir = get_output_path("")

    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    total_count = len(script_files)

    info(f"\n🚀 开始批处理 {total_count} 个脚本文件")
    info(f"� 输出目录: {output_dir}")

    for i, script_file in enumerate(script_files, 1):
        info(f"\n" + "-"*60)
        info(f"处理文件 {i}/{total_count}: {os.path.basename(script_file)}")
        info("-"*60)

        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(script_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.mp3")

        if main(script_file, output_file):
            success_count += 1
            info(f"✅ 文件处理成功: {base_name}")
        else:
            error(f"❌ 文件处理失败: {base_name}")

    info(f"\n" + "="*60)
    info(f"📊 批处理完成")
    info(f"总文件数: {total_count}")
    info(f"成功数: {success_count}")
    info(f"失败数: {total_count - success_count}")
    info(f"成功率: {success_count/total_count*100:.1f}%")
    info("="*60)

    return success_count


if __name__ == '__main__':
    # 使用测试脚本生成播客到output文件夹
    test_script = "今天我们来聊聊人工智能的发展。AI技术在过去几年突飞猛进，特别是大语言模型的出现，给我们的生活带来了很大的变化。人工智能已经在各个领域得到了广泛应用，从智能助手到自动驾驶，从医疗诊断到教育辅助，AI的身影无处不在。未来，随着技术的不断进步，人工智能将会给我们的生活带来更多的便利和惊喜。"
    
    # 生成临时脚本文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_script)
        temp_script_path = f.name
    
    try:
        # 设置输出路径到output文件夹
        output_path = os.path.join(os.path.dirname(__file__), 'output', 'AI播客-人工智能发展.mp3')
        
        # 执行生成
        info(f"开始生成播客到: {output_path}")
        success = main(temp_script_path, output_path)
        
        if success:
            info("播客生成成功！")
            sys.exit(0)
        else:
            error("播客生成失败！")
            sys.exit(1)
    finally:
        # 清理临时文件
        if os.path.exists(temp_script_path):
            os.unlink(temp_script_path)
