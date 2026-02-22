// 全局状态管理
const appState = {
    inputType: 'text', // text, document, url
    sourceContent: '',
    scriptContent: '',
    scriptGenerated: false,
    currentTab: 'voice', // voice, params, history
    
    // 声音克隆数据
    voiceData: {
        1: { audio: null, text: '', active: false },
        2: { audio: null, text: '', active: false },
        3: { audio: null, text: '', active: false },
        4: { audio: null, text: '', active: false }
    },
    
    // 生成参数
    params: {
        seed: 1988,
        temperature: 0.6,
        top_k: 100,
        top_p: 0.9,
        repetition_penalty: 1.25
    },
    
    // 音频数据
    currentAudioBlob: null,
    currentAudioUrl: null,
    audioGeneratedTime: null,
    
    // 历史记录
    history: [],
    
    // LLM API 配置
    llmAPIKey: '' // 需要在 config.py 中配置
};

// API 端点配置
const API_BASE = 'http://localhost:8001';
const SOULX_API_BASE = 'http://localhost:8000';

// 工具函数
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// ==================== 输入源管理 ====================

function toggleInputType(type) {
    appState.inputType = type;
    
    // 隐藏所有输入组
    document.getElementById('text-input-group').style.display = 'none';
    document.getElementById('document-input-group').style.display = 'none';
    document.getElementById('url-input-group').style.display = 'none';
    
    // 显示选中的输入组
    document.getElementById(`${type}-input-group`).style.display = 'flex';
}

function clearText() {
    document.getElementById('content-textarea').value = '';
    updateCharCount();
    showToast('文本已清空', 'info');
}

function updateCharCount() {
    const text = document.getElementById('content-textarea').value;
    document.getElementById('char-count').textContent = `${text.length} 字`;
}

// ==================== 文档处理 ====================

function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    // 显示文件信息
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-info').style.display = 'flex';
    
    // 读取文件内容
    const reader = new FileReader();
    
    reader.onload = function(e) {
        appState.sourceContent = e.target.result;
        document.getElementById('preview-text').textContent = e.target.result.substring(0, 500);
        document.getElementById('content-preview').style.display = 'block';
        showToast(`文档 "${file.name}" 上传成功`, 'success');
    };
    
    reader.onerror = function() {
        showToast('文档读取失败', 'error');
    };
    
    // 根据文件类型选择读取方式
    if (file.name.endsWith('.docx')) {
        // DOCX 需要后端处理
        uploadDocumentToServer(file);
    } else if (file.name.endsWith('.pdf')) {
        // PDF 需要后端处理
        uploadDocumentToServer(file);
    } else {
        // TXT 直接读取
        reader.readAsText(file);
    }
}

async function uploadDocumentToServer(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE}/api/analyze/document`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            appState.sourceContent = result.content;
            document.getElementById('preview-text').textContent = result.content.substring(0, 500);
            document.getElementById('content-preview').style.display = 'block';
            showToast('文档分析成功', 'success');
        }
    } catch (error) {
        showToast('文档分析失败: ' + error.message, 'error');
    }
}

function clearFile() {
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').style.display = 'none';
    document.getElementById('content-preview').style.display = 'none';
    document.getElementById('preview-text').textContent = '';
    appState.sourceContent = '';
    showToast('文档已清空', 'info');
}

// ==================== 网址分析 ====================

async function analyzeUrl() {
    const url = document.getElementById('url-input').value.trim();
    if (!url) {
        showToast('请输入网址', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/analyze/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });
        
        const result = await response.json();
        
        if (result.success) {
            appState.sourceContent = result.content;
            document.getElementById('url-preview-text').textContent = result.content.substring(0, 500);
            document.getElementById('url-preview').style.display = 'block';
            showToast('网址内容分析成功', 'success');
        }
    } catch (error) {
        showToast('网址分析失败: ' + error.message, 'error');
    }
}

// ==================== 脚本生成 ====================

function updateDurationLabel() {
    const duration = document.getElementById('duration-slider').value;
    document.getElementById('duration-value').textContent = duration;
}

async function generateScript() {
    // 获取内容
    let content = '';
    
    if (appState.inputType === 'text') {
        content = document.getElementById('content-textarea').value.trim();
    } else {
        content = appState.sourceContent;
    }
    
    if (!content) {
        showToast('请先输入内容或上传文档', 'error');
        return;
    }
    
    // 获取参数
    const theme = document.getElementById('script-theme').value.trim();
    const durationMinutes = parseInt(document.getElementById('duration-slider').value);
    
    // 显示加载状态
    document.getElementById('script-loading').style.display = 'block';
    document.getElementById('script-editor-container').style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/api/generate/script`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content,
                input_type: appState.inputType,
                duration_minutes: durationMinutes,
                theme: theme || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            appState.scriptContent = result.script;
            document.getElementById('script-editor-textarea').value = result.script;
            appState.scriptGenerated = true;
            
            // 显示脚本编辑器
            document.getElementById('script-loading').style.display = 'none';
            document.getElementById('script-editor-container').style.display = 'flex';
            
            // 更新状态
            updateScriptStatus();
            
            showToast('脚本生成成功！', 'success');
            
            // 自动添加到历史
            addToHistory(result.script, theme);
        }
    } catch (error) {
        console.error('脚本生成失败:', error);
        document.getElementById('script-loading').style.display = 'none';
        document.getElementById('script-editor-container').style.display = 'flex';
        showToast('脚本生成失败: ' + error.message, 'error');
    }
}

function insertExample() {
    const exampleScript = `[S1] 欢迎收听本期的播客节目！
[S2] 很高兴能在这里和大家聊天。
[S1] 今天我们来聊聊人工智能的最新发展。
[S2] 确实，最近AI技术发展非常快，<|laughter|> 感觉每天都有新东西！
[S1] 是啊，从ChatGPT到各种AI应用，都在改变我们的生活方式。
[S2] 诶，那我们就深入聊聊这个话题吧！`;
    
    document.getElementById('script-editor-textarea').value = exampleScript;
    updateScriptStatus();
    showToast('示例脚本已插入', 'info');
}

function clearScript() {
    document.getElementById('script-editor-textarea').value = '';
    appState.scriptGenerated = false;
    updateScriptStatus();
    showToast('脚本已清空', 'info');
}

function formatScript() {
    const script = document.getElementById('script-editor-textarea').value;
    if (!script) return;
    
    // 格式化：确保每行一个对话，说话人标记后有空格
    const formatted = script
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .join('\n\n');
    
    document.getElementById('script-editor-textarea').value = formatted;
    showToast('脚本已格式化', 'info');
}

function updateScriptStatus() {
    const script = document.getElementById('script-editor-textarea').value;
    const dialogueCount = (script.match(/\[S\d+\]/g) || []).length;
    
    document.getElementById('dialogue-count').textContent = `${dialogueCount} 轮对话`;
    
    if (appState.scriptGenerated) {
        document.getElementById('script-status').textContent = '✓ 已生成';
        document.getElementById('script-status').style.color = '#10b981';
    } else if (script.trim().length > 0) {
        document.getElementById('script-status').textContent = '已编辑';
        document.getElementById('script-status').style.color = '#f59e0b';
    } else {
        document.getElementById('script-status').textContent = '等待生成...';
        document.getElementById('script-status').style.color = '#999';
    }
}

// ==================== 标签页切换 ====================

function switchTab(tabName) {
    appState.currentTab = tabName;
    
    // 更新标签按钮状态
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // 更新内容区域
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}-content`).classList.add('active');
}

// ==================== 声音克隆管理 ====================

async function handleVoiceUpload(slotNumber, input) {
    const file = input.files[0];
    if (!file) return;
    
    // 验证文件类型
    if (!file.type.startsWith('audio/')) {
        showToast('请上传音频文件', 'error');
        return;
    }
    
    // 保存文件
    appState.voiceData[slotNumber].audio = file;
    appState.voiceData[slotNumber].name = file.name;
    
    // 更新预览
    updateVoicePreview(slotNumber, file);
    updateVoiceState(slotNumber);
    
    showToast(`说话人 ${slotNumber} 音频已上传`, 'success');
}

function updateVoicePreview(slotNumber, file) {
    const previewDiv = document.getElementById(`voice${slotNumber}-preview`);
    const audioPlayer = document.getElementById(`voice${slotNumber}-player`);
    
    if (file) {
        const url = URL.createObjectURL(file);
        audioPlayer.src = url;
        previewDiv.style.display = 'block';
    }
}

function updateVoiceState(slotNumber) {
    const data = appState.voiceData[slotNumber];
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

function clearVoiceSlot(slotNumber) {
    appState.voiceData[slotNumber] = { audio: null, text: '', active: false };
    
    document.getElementById(`voice${slotNumber}-audio`).value = '';
    document.getElementById(`voice${slotNumber}-text`).value = '';
    
    const previewDiv = document.getElementById(`voice${slotNumber}-preview`);
    const audioPlayer = document.getElementById(`voice${slotNumber}-player`);
    audioPlayer.src = '';
    previewDiv.style.display = 'none';
    
    updateVoiceState(slotNumber);
    showToast(`说话人 ${slotNumber} 已清空`, 'info');
}

function updateVoiceSummary() {
    const summaryList = document.getElementById('voice-summary-list');
    const activeSlots = Object.entries(appState.voiceData)
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

// ==================== 音频生成 ====================

async function generateAudio() {
    const script = document.getElementById('script-editor-textarea').value.trim();
    
    // 验证脚本
    if (!script) {
        showToast('请先生成或编辑播客脚本', 'error');
        switchTab('voice');
        return;
    }
    
    // 获取活跃的声音
    const activeVoices = Object.entries(appState.voiceData)
        .filter(([_, data]) => data.active)
        .map(([slot, data]) => ({ slot: parseInt(slot), data }));
    
    if (activeVoices.length < 1) {
        showToast('请至少克隆 1 个声音', 'error');
        switchTab('voice');
        return;
    }
    
    // 验证脚本中的说话人
    const usedSlots = [...new Set(script.match(/\[S(\d+)\]/g) || [])]
        .map(match => parseInt(match.match(/\d+/)[0]));
    
    const invalidSlots = usedSlots.filter(slot => !appState.voiceData[slot].active);
    if (invalidSlots.length > 0) {
        showToast(`脚本中使用的说话人 S${invalidSlots.join(', S')} 尚未克隆`, 'error');
        switchTab('voice');
        return;
    }
    
    // 获取生成参数
    appState.params = {
        seed: parseInt(document.getElementById('seed-input').value) || 1988,
        temperature: parseFloat(document.getElementById('temperature-input').value) || 0.6,
        top_k: parseInt(document.getElementById('topk-input').value) || 100,
        top_p: parseFloat(document.getElementById('topp-input').value) || 0.9,
        repetition_penalty: 1.25
    };
    
    // 显示加载状态
    document.getElementById('audio-loading').style.display = 'block';
    document.getElementById('audio-result').style.display = 'none';
    document.getElementById('audio-empty').style.display = 'none';
    document.getElementById('generate-audio-btn').disabled = true;
    
    showToast('正在生成音频，请稍候...', 'info');
    
    try {
        const startTime = Date.now();
        
        // 准备表单数据
        const formData = new FormData();
        
        // 添加音频文件（按脚本中使用的顺序）
        const usedVoices = usedSlots
            .sort((a, b) => a - b)
            .map(slot => ({ slot, data: appState.voiceData[slot] }));
        
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
        formData.append('seed', appState.params.seed);
        formData.append('temperature', appState.params.temperature);
        formData.append('top_k', appState.params.top_k);
        formData.append('top_p', appState.params.top_p);
        formData.append('repetition_penalty', appState.params.repetition_penalty);
        
        // 调用 SoulX-Podcast API
        const response = await fetch(`${SOULX_API_BASE}/generate`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API 请求失败: ${response.status} - ${errorText}`);
        }
        
        // 获取音频 blob
        appState.currentAudioBlob = await response.blob();
        appState.currentAudioUrl = URL.createObjectURL(appState.currentAudioBlob);
        appState.audioGeneratedTime = Date.now() - startTime;
        
        // 显示结果
        showResult();
        
        showToast('音频生成成功！', 'success');
        
    } catch (error) {
        console.error('生成音频失败:', error);
        showToast(`生成失败: ${error.message}`, 'error');
        hideLoading();
    }
}

function downloadAudio() {
    if (!appState.currentAudioBlob) {
        showToast('没有可下载的音频', 'error');
        return;
    }
    
    const url = URL.createObjectURL(appState.currentAudioBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `podcast_${Date.now()}.wav`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('音频已开始下载', 'success');
}

function regenerateAudio() {
    if (confirm('确定要重新生成音频吗？这可能需要几分钟时间。')) {
        generateAudio();
    }
}

function hideLoading() {
    document.getElementById('audio-loading').style.display = 'none';
    document.getElementById('generate-audio-btn').disabled = false;
}

function showResult() {
    hideLoading();
    
    const audioElement = document.getElementById('audio-element');
    audioElement.src = appState.currentAudioUrl;
    
    // 更新元数据
    const sizeMB = (appState.currentAudioBlob.size / 1024 / 1024).toFixed(2);
    const timeMinutes = (appState.audioGeneratedTime / 60000).toFixed(2);
    
    document.getElementById('audio-size').textContent = `${sizeMB} MB`;
    document.getElementById('audio-time').textContent = `${timeMinutes} 分钟`;
    
    document.getElementById('audio-loading').style.display = 'none';
    document.getElementById('audio-result').style.display = 'block';
    document.getElementById('audio-empty').style.display = 'none';
    
    // 添加到历史记录
    addToHistoryFromCurrent();
}

// ==================== 历史记录管理 ====================

function addToHistory(script, theme) {
    const historyItem = {
        id: generateId(),
        script: script,
        theme: theme || '自定义主题',
        timestamp: Date.now(),
        date: new Date().toLocaleString('zh-CN')
    };
    
    appState.history.unshift(historyItem);
    
    // 只保留最近 50 条记录
    if (appState.history.length > 50) {
        appState.history = appState.history.slice(0, 50);
    }
    
    // 保存到 localStorage
    localStorage.setItem('podcast_history', JSON.stringify(appState.history));
    
    // 更新历史列表显示
    updateHistoryList();
}

function addToHistoryFromCurrent() {
    const script = document.getElementById('script-editor-textarea').value;
    const theme = document.getElementById('script-theme').value || '自定义主题';
    
    if (script.trim().length > 0) {
        addToHistory(script, theme);
    }
}

function updateHistoryList() {
    const historyList = document.getElementById('history-list');
    
    if (appState.history.length === 0) {
        historyList.innerHTML = '<div class="empty-hint">暂无历史记录</div>';
        return;
    }
    
    historyList.innerHTML = appState.history.map(item => `
        <div class="history-item" onclick="loadFromHistory('${item.id}')">
            <div class="history-header">
                <span class="history-theme">${item.theme}</span>
                <span class="history-date">${item.date}</span>
            </div>
            <div class="history-script">${item.script.substring(0, 200)}...</div>
        </div>
    `).join('');
}

function loadFromHistory(id) {
    const item = appState.history.find(h => h.id === id);
    if (!item) return;
    
    document.getElementById('script-editor-textarea').value = item.script;
    document.getElementById('script-theme').value = item.theme;
    appState.scriptContent = item.script;
    
    updateScriptStatus();
    showToast('已加载历史脚本', 'info');
}

function clearHistory() {
    if (confirm('确定要清空所有历史记录吗？')) {
        appState.history = [];
        localStorage.removeItem('podcast_history');
        updateHistoryList();
        showToast('历史记录已清空', 'info');
    }
}

// ==================== 初始化 ====================

function initApp() {
    // 从 localStorage 加载历史记录
    const savedHistory = localStorage.getItem('podcast_history');
    if (savedHistory) {
        try {
            appState.history = JSON.parse(savedHistory);
        } catch (e) {
            console.error('加载历史记录失败:', e);
        }
    }
    
    // 初始化历史列表
    updateHistoryList();
    
    // 初始化脚本状态
    updateScriptStatus();
    
    // 初始化声音摘要
    updateVoiceSummary();
    
    console.log('AI 播客生成器 Pro 已初始化');
}

// 监听文本输入
document.getElementById('content-textarea').addEventListener('input', updateCharCount);

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);
