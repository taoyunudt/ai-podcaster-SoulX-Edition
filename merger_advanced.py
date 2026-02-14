# merger_advanced.py - 高级音频合并模块

import os
from pydub import AudioSegment
from utils.log_utils import info, error, warning
from utils.file_utils import ensure_directory

class AdvancedMerger:
    """高级音频合并器"""

    def __init__(self):
        pass

    def merge_audio(
        self,
        audio_files: list,
        output_file: str,
        silence_duration: int = 100,
        volume_adjustment: float = 1.0,
        background_music: str = None,
        bgm_volume: float = 0.3,
        output_format: str = 'mp3',
        bitrate: str = '128k'
    ) -> str:
        """
        高级音频合并功能

        Args:
            audio_files: 音频文件路径列表
            output_file: 输出文件路径
            silence_duration: 音频段之间的静音间隔（毫秒）
            volume_adjustment: 音量调整系数（1.0为原始音量）
            background_music: 背景音乐文件路径
            bgm_volume: 背景音乐音量系数（相对于主音频）
            output_format: 输出格式（mp3, wav等）
            bitrate: 输出比特率（如 '128k', '192k'）

        Returns:
            str: 输出文件路径
        """

        info("🎵 高级音频合并器")
        info("="*60)

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
        info(f"   静音间隔: {silence_duration}ms")
        info(f"   音量调整: {volume_adjustment:.2f}x")
        if background_music:
            info(f"   背景音乐: {os.path.basename(background_music)}")
            info(f"   背景音乐音量: {bgm_volume:.2f}x")
        info(f"   输出格式: {output_format}")
        info(f"   比特率: {bitrate}")

        try:
            # 加载并合并所有音频
            combined = None
            total_duration = 0

            for i, audio_file in enumerate(valid_audio_files):
                ext = os.path.splitext(audio_file)[1].lower()
                try:
                    if ext == '.mp3':
                        segment = AudioSegment.from_mp3(audio_file)
                    elif ext == '.wav':
                        segment = AudioSegment.from_wav(audio_file)
                    else:
                        segment = AudioSegment.from_file(audio_file)

                    # 调整音量
                    segment = segment.apply_gain(20 * (volume_adjustment - 1))

                    info(f"   处理 {i+1}/{len(valid_audio_files)}: {os.path.basename(audio_file)}")
                    info(f"      时长: {len(segment)/1000:.2f}秒")

                    if combined is None:
                        combined = segment
                    else:
                        # 添加静音间隔并拼接
                        combined += AudioSegment.silent(duration=silence_duration) + segment

                    total_duration += len(segment) + (silence_duration if i > 0 else 0)

                except Exception as e:
                    warning(f"   ⚠️ 跳过文件（加载失败）: {os.path.basename(audio_file)} - {str(e)}")
                    continue

            if combined is None:
                error("没有成功加载任何音频文件")
                return None

            # 添加背景音乐
            if background_music and os.path.exists(background_music):
                try:
                    info("   添加背景音乐...")
                    bgm = AudioSegment.from_file(background_music)

                    # 调整背景音乐音量
                    bgm = bgm.apply_gain(20 * (bgm_volume - 1))

                    # 循环背景音乐以匹配总时长
                    if len(bgm) < len(combined):
                        # 计算需要循环的次数
                        loop_count = len(combined) // len(bgm) + 1
                        bgm = bgm * loop_count

                    # 截取与主音频相同长度的背景音乐
                    bgm = bgm[:len(combined)]

                    # 混合主音频和背景音乐
                    combined = combined.overlay(bgm)
                    info("   背景音乐添加成功")

                except Exception as e:
                    warning(f"   ⚠️ 添加背景音乐失败: {str(e)}")

            # 导出最终音频
            output_dir = os.path.dirname(output_file)
            ensure_directory(output_dir)

            info(f"   正在导出到: {output_file}")
            info(f"   总时长: {total_duration/1000:.2f}秒")

            try:
                # 设置导出参数
                export_params = {
                    'format': output_format
                }
                if output_format == 'mp3':
                    export_params['bitrate'] = bitrate

                combined.export(output_file, **export_params)
            except Exception as e:
                error(f"   ❌ 导出音频失败: {str(e)}")
                return None

            # 验证输出文件
            if os.path.exists(output_file):
                final_size = os.path.getsize(output_file)
                info(f"   ✅ 导出成功！文件大小: {final_size} bytes ({final_size/1024:.1f} KB)")
            else:
                error(f"   ❌ 导出失败！")
                return None

            info(f"\n✅ 音频合并完成: {output_file}")
            info(f"   时长: {len(combined)/1000:.2f} 秒")
            info(f"   合并文件数: {len(valid_audio_files)}")

            return output_file

        except Exception as e:
            error(f"   ❌ 音频合并失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


# 创建全局实例
advanced_merger = AdvancedMerger()

# 便捷函数
def merge_audio_advanced(*args, **kwargs):
    return advanced_merger.merge_audio(*args, **kwargs)
