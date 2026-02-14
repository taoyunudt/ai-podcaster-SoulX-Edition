# utils/file_utils.py - 文件操作工具

import os
from docx import Document

def read_file(file_path: str) -> str:
    """
    读取文件内容

    Args:
        file_path: 文件路径

    Returns:
        str: 文件文本内容

    Raises:
        FileNotFoundError: 文件不存在
        Exception: 读取文件失败
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if file_path.endswith('.docx'):
        return read_docx(file_path)
    else:
        return read_text(file_path)

def read_text(file_path: str) -> str:
    """
    读取文本文件

    Args:
        file_path: 文件路径

    Returns:
        str: 文件文本内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        with open(file_path, 'r', encoding='gbk') as f:
            return f.read()

def read_docx(file_path: str) -> str:
    """
    读取Word文档内容

    Args:
        file_path: 文档路径

    Returns:
        str: 文档文本内容
    """
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def get_output_path(default_name: str = "AI播客测试.mp3") -> str:
    """
    获取默认输出路径（桌面）

    Args:
        default_name: 默认文件名

    Returns:
        str: 输出文件路径
    """
    desktop = os.path.expanduser("~/Desktop")
    return os.path.join(desktop, default_name)

def ensure_directory(directory: str):
    """
    确保目录存在

    Args:
        directory: 目录路径
    """
    os.makedirs(directory, exist_ok=True)

def get_file_size(file_path: str) -> int:
    """
    获取文件大小

    Args:
        file_path: 文件路径

    Returns:
        int: 文件大小（字节）
    """
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0
