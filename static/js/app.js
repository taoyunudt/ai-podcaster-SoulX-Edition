// API 基础 URL
const API_BASE_URL = 'http://localhost:8000';

// 全局状态
let currentScript = '';
let currentTheme = '';
let currentDuration = 5;
let currentAudioUrl = '';

// DOM 元素
const contentTextarea = document.getElementById('content-textarea');
const urlInput = document.getElementById('url-input');
const fileInput = document.getElementById('file-input');
const durationSlider = document.getElementById('duration-slider');
const durationValue = document.getElementById('duration-value');
const themeInput = document.getElementById('theme-input');
const previewText = document.getElementById('preview-text');
const contentPreview = document.getElementById('content-preview');

const scriptEditorTextarea = document.getElementById('script-editor-textarea');
const scriptLoading = document.getElementById('script-loading');
const scriptResult = document.getElementById('script-result');
const scriptEmpty = document.getElementById('script-empty');
const scriptTheme = document.getElementById('script-theme');
const scriptDuration = document.getElementById('script-duration');

const audioLoading = document.getElementById('audio-loading');
const audioResult = document.getElementById('audio-result');
const audioEmpty = document.getElementById('audio-empty');
const audioElement = document.getElementById('audio-element');
const audioDialogueCount = document.getElementById('audio-dialogue-count');
const audioDuration = document.getElementById('audio-duration');
const audioProgressText = document.getElementById('audio-progress-text');

// 工具函数：显示 Toast 提示
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 输入类型切换
document.querySelectorAll('input[name="inputType"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        // 隐藏所有输入组
        document.getElementById('text-input-group').style.display = 'none';
        document.getElementById('url-input-group').style.display = 'none';
        document.getElementById('document-input-group').style.display = 'none';

        // 显示选中的输入组
        const inputType = e.target.value;
        if (inputType === 'text') {
            document.getElementById('text-input-group').style.display = 'block';
        } else if (inputType === 'url') {
            document.getElementById('url-input-group').style.display = 'block';
        } else if (inputType === 'document') {
            document.getElementById('document-input-group').style.display = 'block';
        }
    });
});

// 时长滑块
durationSlider.addEventListener('input', (e) => {
    currentDuration = parseInt(e.target.value);
    durationValue.textContent = currentDuration;
});

// 分析网址
document.getElementById('analyze-url-btn').addEventListener('click', async () => {
    const url = urlInput.value.trim();
    if (!url) {
        showToast('请输入网址', 'error');
        return;
    }

    try {
        showToast('正在分析网址...', 'success');
        const response = await fetch(`${API_BASE_URL}/api/analyze/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        const result = await response.json();
        if (result.success) {
            contentPreview.style.display = 'block';
            previewText.textContent = result.summary || result.content || result.title;
            showToast('网址分析完成', 'success');
        } else {
            throw new Error('分析失败');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('网址分析失败', 'error');
    }
});

// 文档上传
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        showToast('正在分析文档...', 'success');
        const response = await fetch(`${API_BASE_URL}/api/analyze/document`, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        if (result.success) {
            contentPreview.style.display = 'block';
            previewText.textContent = result.summary || result.content || result.title;
            showToast('文档分析完成', 'success');
        } else {
            throw new Error('分析失败');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('文档分析失败', 'error');
    }
});

// 拖拽上传
const fileDropZone = document.getElementById('file-drop-zone');

fileDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDropZone.style.borderColor = '#667eea';
    fileDropZone.style.background = '#f0f4ff';
});

fileDropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    fileDropZone.style.borderColor = '#ddd';
    fileDropZone.style.background = 'white';
});

fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDropZone.style.borderColor = '#ddd';
    fileDropZone.style.background = 'white';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        // 触发 change 事件
        const event = new Event('change');
        fileInput.dispatchEvent(event);
    }
});

// 获取输入内容
function getInputContent() {
    const inputType = document.querySelector('input[name="inputType"]:checked').value;

    if (inputType === 'text') {
        return contentTextarea.value.trim();
    } else if (inputType === 'url') {
        return urlInput.value.trim();
    } else if (inputType === 'document') {
        // 对于文档上传，我们使用预览文本作为内容
        return previewText.textContent;
    }

    return '';
}

// 生成脚本
document.getElementById('generate-script-btn').addEventListener('click', async () => {
    const content = getInputContent();
    if (!content) {
        showToast('请输入内容或上传文档', 'error');
        return;
    }

    const inputType = document.querySelector('input[name="inputType"]:checked').value;
    const theme = themeInput.value.trim() || null;

    scriptLoading.style.display = 'block';
    scriptEmpty.style.display = 'none';
    scriptResult.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate/script`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content,
                input_type: inputType,
                duration_minutes: currentDuration,
                theme,
            }),
        });

        const result = await response.json();
        if (result.success) {
            currentScript = result.script;
            currentTheme = result.theme;

            scriptEditorTextarea.value = result.script;
            scriptTheme.textContent = result.theme;
            scriptDuration.textContent = `${result.duration_minutes} 分钟`;

            scriptLoading.style.display = 'none';
            scriptResult.style.display = 'block';
            scriptEmpty.style.display = 'none';

            showToast('脚本生成成功', 'success');
        } else {
            throw new Error(result.detail || '生成失败');
        }
    } catch (error) {
        console.error('Error:', error);
        scriptLoading.style.display = 'none';
        scriptEmpty.style.display = 'block';
        showToast('脚本生成失败', 'error');
    }
});

// 重新生成脚本
document.getElementById('regenerate-script-btn').addEventListener('click', () => {
    document.getElementById('generate-script-btn').click();
});

// 监听脚本编辑
scriptEditorTextarea.addEventListener('input', (e) => {
    currentScript = e.target.value;
});

// 生成音频
document.getElementById('generate-audio-btn').addEventListener('click', async () => {
    const script = scriptEditorTextarea.value.trim();
    if (!script) {
        showToast('请先生成脚本', 'error');
        return;
    }

    audioLoading.style.display = 'block';
    audioEmpty.style.display = 'none';
    audioResult.style.display = 'none';
    audioProgressText.textContent = '正在生成音频，请稍候...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate/audio`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                script,
            }),
        });

        const result = await response.json();
        if (result.success) {
            currentAudioUrl = `${API_BASE_URL}${result.audio_url}`;
            audioElement.src = currentAudioUrl;

            audioDialogueCount.textContent = result.dialogue.length;
            audioDuration.textContent = `${result.duration.toFixed(1)} 秒`;

            audioLoading.style.display = 'none';
            audioResult.style.display = 'block';
            audioEmpty.style.display = 'none';

            showToast('音频生成成功', 'success');
        } else {
            throw new Error(result.detail || '生成失败');
        }
    } catch (error) {
        console.error('Error:', error);
        audioLoading.style.display = 'none';
        audioEmpty.style.display = 'block';
        showToast('音频生成失败', 'error');
    }
});

// 下载音频
document.getElementById('download-audio-btn').addEventListener('click', () => {
    if (currentAudioUrl) {
        const a = document.createElement('a');
        a.href = currentAudioUrl;
        a.download = `podcast_${Date.now()}.mp3`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showToast('下载已开始', 'success');
    }
});

// 重新开始
document.getElementById('start-over-btn').addEventListener('click', () => {
    // 清空所有状态
    contentTextarea.value = '';
    urlInput.value = '';
    fileInput.value = '';
    themeInput.value = '';
    previewText.textContent = '';
    contentPreview.style.display = 'none';
    scriptEditorTextarea.value = '';
    currentScript = '';
    currentTheme = '';
    currentAudioUrl = '';
    audioElement.src = '';

    // 重置显示
    scriptLoading.style.display = 'none';
    scriptResult.style.display = 'none';
    scriptEmpty.style.display = 'block';

    audioLoading.style.display = 'none';
    audioResult.style.display = 'none';
    audioEmpty.style.display = 'block';

    showToast('已重置', 'success');
});
