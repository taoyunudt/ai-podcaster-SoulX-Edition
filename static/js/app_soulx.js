// 声音管理数据
const voiceData = {
    1: { audio: null, text: '', active: false },
    2: { audio: null, text: '', active: false },
    3: { audio: null, text: '', active: false },
    4: { audio: null, text: '', active: false }
};

// 生成状态
let currentAudioBlob = null;
let currentAudioUrl = null;

// API 端点（SoulX-Podcast API）
const API_BASE = 'http://localhost:8000';

/**
 * 处理声音上传
 */
async function handleVoiceUpload(slotNumber, input) {
    const file = input.files[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith('audio/')) {
        showToast('请上传音频文件', 'error');
        return;
    }

    // 保存文件
    voiceData[slotNumber].audio = file;
    voiceData[slotNumber].name = file.name;

    // 更新预览
    updateVoicePreview(slotNumber, file);
    updateVoiceState(slotNumber);

    showToast(`说话人 ${slotNumber} 音频已上传`, 'success');
}

/**
 * 更新声音预览
 */
function updateVoicePreview(slotNumber, file) {
    const previewDiv = document.getElementById(`voice${slotNumber}-preview`);
    const audioPlayer = document.getElementById(`voice${slotNumber}-player`);

    if (file) {
        const url = URL.createObjectURL(file);
        audioPlayer.src = url;
        previewDiv.style.display = 'block';
    }
}

/**
 * 更新声音状态
 */
function updateVoiceState(slotNumber) {
    const data = voiceData[slotNumber];
    const slotElement = document.getElementById(`voice-slot-${slotNumber}`);
    const statusElement = document.getElementById(`voice${slotNumber}-status`);
    const statusText = statusElement.querySelector('.status-text');

    // 检查是否完整
    const hasAudio = data.audio !== null;
    const hasText = data.text.trim() !== '';
    const isActive = hasAudio && hasText;

    data.active = isActive;

    // 更新 UI
    if (isActive) {
        slotElement.classList.add('active');
        statusText.textContent = '✓ 准备就绪';
    } else if (hasAudio) {
        slotElement.classList.remove('active');
        statusText.textContent = '⚠️ 需要参考文本';
    } else if (hasText) {
        slotElement.classList.remove('active');
        statusText.textContent = '⚠️ 需要参考音频';
    } else {
        slotElement.classList.remove('active');
        statusText.textContent = '等待上传';
    }

    // 更新声音摘要
    updateVoiceSummary();
}

/**
 * 清空声音槽位
 */
function clearVoiceSlot(slotNumber) {
    // 清空数据
    voiceData[slotNumber] = { audio: null, text: '', active: false };

    // 清空输入
    document.getElementById(`voice${slotNumber}-audio`).value = '';
    document.getElementById(`voice${slotNumber}-text`).value = '';

    // 隐藏预览
    const previewDiv = document.getElementById(`voice${slotNumber}-preview`);
    const audioPlayer = document.getElementById(`voice${slotNumber}-player`);
    audioPlayer.src = '';
    previewDiv.style.display = 'none';

    // 更新状态
    updateVoiceState(slotNumber);

    showToast(`说话人 ${slotNumber} 已清空`, 'info');
}

/**
 * 更新声音摘要
 */
function updateVoiceSummary() {
    const summaryList = document.getElementById('voice-summary-list');
    const activeSlots = Object.entries(voiceData)
        .filter(([_, data]) => data.active)
        .map(([slot, _]) => `S${slot}`);

    if (activeSlots.length === 0) {
        summaryList.innerHTML = '<span class="empty-hint">暂无声音</span>';
        return;
    }

    summaryList.innerHTML = activeSlots
        .map(slot => `<span class="voice-tag">${slot}</span>`)
        .join('');
}

/**
 * 生成脚本模板
 */
function createScript() {
    const activeSlots = Object.entries(voiceData)
        .filter(([_, data]) => data.active)
        .map(([slot, data]) => ({ slot, text: data.text }));

    if (activeSlots.length < 2) {
        showToast('至少需要 2 个克隆的声音', 'error');
        return;
    }

    // 生成简单的播客开场
    const script = `[${activeSlots[0].slot}] 欢迎收听本期的播客节目！${activeSlots[0].text}
[${activeSlots[1].slot}] ${activeSlots[1].text}
[${activeSlots[0].slot}] 今天我们来聊聊人工智能的最新发展，特别是生成式AI的应用。
[${activeSlots[1].slot}] 确实，最近AI技术发展非常快，从ChatGPT到各种AI应用，都在改变我们的生活方式。`;

    document.getElementById('script-editor-textarea').value = script;
    showToast('脚本模板已生成', 'success');
}

/**
 * 插入示例脚本
 */
function insertExample() {
    const exampleScript = `[S1] 哈喽，AI时代的冲浪先锋们！欢迎收听《AI生活进行时》。
[S2] 哎，大家好呀！我是能唠，爱唠，天天都想唠的唠嗑！
[S1] 最近活得特别赛博朋克哈！以前老是觉得AI是科幻片儿里的，<|laughter|> 现在，现在连我妈都用AI写广场舞文案了。
[S2] 这个例子很生动啊。是的，特别是生成式AI哈，感觉都要炸了！诶，那我们今天就聊聊AI是怎么走进我们的生活的哈！`;

    document.getElementById('script-editor-textarea').value = exampleScript;
    showToast('示例脚本已插入', 'info');
}

/**
 * 清空脚本
 */
function clearScript() {
    document.getElementById('script-editor-textarea').value = '';
    showToast('脚本已清空', 'info');
}

/**
 * 生成音频
 */
async function generateAudio() {
    const script = document.getElementById('script-editor-textarea').value.trim();

    // 验证脚本
    if (!script) {
        showToast('请输入播客脚本', 'error');
        return;
    }

    // 获取活跃的声音
    const activeVoices = Object.entries(voiceData)
        .filter(([_, data]) => data.active)
        .map(([slot, data]) => ({ slot: parseInt(slot), data }));

    if (activeVoices.length < 1) {
        showToast('请至少克隆 1 个声音', 'error');
        return;
    }

    // 验证脚本中的说话人
    const usedSlots = [...new Set(script.match(/\[S(\d+)\]/g) || [])]
        .map(match => parseInt(match.match(/\d+/)[0]));

    const invalidSlots = usedSlots.filter(slot => !voiceData[slot].active);
    if (invalidSlots.length > 0) {
        showToast(`脚本中使用的说话人 S${invalidSlots.join(', S')} 尚未克隆`, 'error');
        return;
    }

    // 获取生成参数
    const params = {
        seed: parseInt(document.getElementById('seed-input').value) || 1988,
        temperature: parseFloat(document.getElementById('temperature-input').value) || 0.6,
        top_k: parseInt(document.getElementById('topk-input').value) || 100,
        top_p: parseFloat(document.getElementById('topp-input').value) || 0.9,
        repetition_penalty: 1.25
    };

    // 显示加载状态
    showLoading();
    showToast('正在生成音频，请稍候...', 'info');

    try {
        // 准备表单数据
        const formData = new FormData();

        // 添加音频文件（按脚本中使用的顺序）
        const usedVoices = usedSlots
            .sort((a, b) => a - b)
            .map(slot => ({ slot, data: voiceData[slot] }));

        usedVoices.forEach(({ data }) => {
            formData.append('prompt_audio', data.audio);
        });

        // 添加对应的参考文本
        const promptTexts = usedVoices.map(({ data }) => data.text);
        promptTexts.forEach(text => {
            formData.append('prompt_texts', text);
        });

        // 添加对话文本和参数
        formData.append('dialogue_text', script);
        formData.append('seed', params.seed);
        formData.append('temperature', params.temperature);
        formData.append('top_k', params.top_k);
        formData.append('top_p', params.top_p);
        formData.append('repetition_penalty', params.repetition_penalty);

        // 调用 API
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API 请求失败: ${response.status} - ${errorText}`);
        }

        // 获取音频 blob
        currentAudioBlob = await response.blob();
        currentAudioUrl = URL.createObjectURL(currentAudioBlob);

        // 显示结果
        showResult();

        showToast('音频生成成功！', 'success');

    } catch (error) {
        console.error('生成音频失败:', error);
        showToast(`生成失败: ${error.message}`, 'error');
        hideLoading();
    }
}

/**
 * 下载音频
 */
function downloadAudio() {
    if (!currentAudioBlob) {
        showToast('没有可下载的音频', 'error');
        return;
    }

    const url = URL.createObjectURL(currentAudioBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `podcast_${Date.now()}.wav`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('音频已开始下载', 'success');
}

/**
 * 重新生成
 */
function regenerateAudio() {
    if (confirm('确定要重新生成音频吗？这可能需要几分钟时间。')) {
        generateAudio();
    }
}

/**
 * 显示加载状态
 */
function showLoading() {
    document.getElementById('audio-loading').style.display = 'block';
    document.getElementById('audio-result').style.display = 'none';
    document.getElementById('audio-empty').style.display = 'none';
    document.getElementById('generate-audio-btn').disabled = true;
}

/**
 * 隐藏加载状态
 */
function hideLoading() {
    document.getElementById('audio-loading').style.display = 'none';
    document.getElementById('generate-audio-btn').disabled = false;
}

/**
 * 显示结果
 */
function showResult() {
    hideLoading();

    const audioElement = document.getElementById('audio-element');
    audioElement.src = currentAudioUrl;

    // 更新元数据
    const sizeMB = (currentAudioBlob.size / 1024 / 1024).toFixed(2);
    document.getElementById('audio-size').textContent = `${sizeMB} MB`;

    document.getElementById('audio-loading').style.display = 'none';
    document.getElementById('audio-result').style.display = 'block';
    document.getElementById('audio-empty').style.display = 'none';
}

/**
 * 显示 Toast 提示
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('SoulX Podcast Editor Loaded');
    updateVoiceSummary();
});
