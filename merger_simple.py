# merger_simple.py - 简化音频合并模块

import os
from pydub import AudioSegment
from utils.log_utils import info, error, warning
from utils.file_utils import ensure_directory

def merge_audio(audio_files: list, output_file: str, silence_duration: int = 100):
    """
    简单的音频合并（只使用PyDub，添加静音间隔）

    Args:
        audio_files: 音频文件路径列表
        output_file: 输出文件路径
        silence_duration: 音频段之间的静音间隔（毫秒）

    Returns:
        str: 输出文件路径
    """

    info("🎵 正在合并音频文件...")

    if not audio_files:
        error("没有音频文件需要合并")
        return None

    # 验证音频文件并排序
    valid_audio_files = []
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file)
            if file_size > 1000:  # 至少1KB
                valid_audio_files.append(audio_file)
                info(f"   ✅ 文件: {os.path.basename(audio_file)} ({file_size} bytes)")
            else:
                warning(f"   ⚠️ 跳过文件（太小）: {os.path.basename(audio_file)}")
        else:
            warning(f"   ⚠️ 文件不存在: {audio_file}")

    if not valid_audio_files:
        error("没有有效的音频文件")
        return None

    info(f"   共 {len(valid_audio_files)} 个文件待合并")

    try:
        # 加载第一个音频
        first_file = valid_audio_files[0]
        ext = os.path.splitext(first_file)[1].lower()

        try:
            if ext == '.mp3':
                combined = AudioSegment.from_mp3(first_file)
            elif ext == '.wav':
                combined = AudioSegment.from_wav(first_file)
            else:
                combined = AudioSegment.from_file(first_file)

            info(f"   加载第一个音频: {os.path.basename(first_file)}")
        except Exception as e:
            error(f"   ❌ 加载音频文件失败: {str(e)}")
            return None

        # 依次拼接后续音频，添加静音间隔
        for i, audio_file in enumerate(valid_audio_files[1:], 1):
            ext = os.path.splitext(audio_file)[1].lower()
            try:
                if ext == '.mp3':
                    segment = AudioSegment.from_mp3(audio_file)
                elif ext == '.wav':
                    segment = AudioSegment.from_wav(audio_file)
                else:
                    segment = AudioSegment.from_file(audio_file)

                info(f"   拼接 {i+1}/{len(valid_audio_files)}: {os.path.basename(audio_file)}")

                # 添加静音间隔并拼接
                combined += AudioSegment.silent(duration=silence_duration) + segment
            except Exception as e:
                warning(f"   ⚠️ 跳过文件（加载失败）: {os.path.basename(audio_file)} - {str(e)}")
                continue

        # 导出最终音频
        output_dir = os.path.dirname(output_file)
        ensure_directory(output_dir)

        info(f"   正在导出到: {output_file}")
        try:
            combined.export(output_file, format='mp3')
        except Exception as e:
            error(f"   ❌ 导出音频失败: {str(e)}")
            return None

        # 验证输出文件
        if os.path.exists(output_file):
            final_size = os.path.getsize(output_file)
            info(f"   ✅ 导出成功！文件大小: {final_size} bytes ({final_size/1024:.1f} KB)")

            # 计算总时长
            total_duration = len(combined) / 1000.0  # 转换为秒
            info(f"   总时长: {total_duration:.2f} 秒")
        else:
            error(f"   ❌ 导出失败！")
            return None

        info(f"\n✅ 音频合并完成: {output_file}")
        info(f"   时长: {total_duration:.2f} 秒")
        info(f"   合并文件数: {len(valid_audio_files)}")

        return output_file

    except Exception as e:
        error(f"   ❌ 音频合并失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
