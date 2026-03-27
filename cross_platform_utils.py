#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台工具类 - 统一处理跨平台系统命令执行和平台检测
"""

import subprocess
import platform
import sys
import os
import re
from typing import List, Dict, Any, Optional


class CrossPlatformUtils:
    """跨平台工具类 - 统一处理跨平台系统命令执行和平台检测"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.platform = platform.system()
        self.encoding = self._get_system_encoding()
    
    def _get_system_encoding(self) -> str:
        """获取系统默认编码"""
        if self.platform == "Windows":
            return "gbk"  # Windows系统使用GBK编码
        else:
            return "utf-8"  # macOS/Linux使用UTF-8编码
    
    def run_command(self, command: List[str], timeout: int = 10) -> str:
        """
        执行系统命令（智能编码检测版）
        
        Args:
            command: 命令列表
            timeout: 超时时间（秒）
            
        Returns:
            命令输出结果
        """
        try:
            # 智能编码检测：优先使用UTF-8，失败时回退到系统编码
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                # 如果UTF-8失败，尝试系统编码
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding=self.encoding,
                    errors="replace",
                    timeout=timeout
                )
                return result.stdout if result.returncode == 0 else ""
                
        except subprocess.TimeoutExpired:
            if self.debug_mode:
                print(f"⚠️  命令执行超时: {' '.join(command)}")
            return ""
        except Exception as e:
            if self.debug_mode:
                print(f"❌ 命令执行失败: {' '.join(command)} - {e}")
            return ""
    
    def run_command_with_fallback(self, commands_dict: Dict[str, List[str]], timeout: int = 10) -> str:
        """
        执行多平台命令（带回退机制）
        
        Args:
            commands_dict: 平台命令字典，键为平台名称，值为命令列表
            timeout: 超时时间（秒）
            
        Returns:
            命令输出结果
        """
        # 按优先级尝试：当前平台 -> 通用命令 -> 其他平台
        platforms_to_try = [self.platform, "common", "Darwin", "Windows", "Linux"]
        
        for platform_name in platforms_to_try:
            if platform_name in commands_dict:
                command = commands_dict[platform_name]
                result = self.run_command(command, timeout)
                if result and result.strip():
                    if self.debug_mode:
                        print(f"✅ 使用{platform_name}平台命令成功: {' '.join(command)}")
                    return result
        
        return ""
    
    def get_platform_info(self) -> Dict[str, str]:
        """获取平台信息"""
        return {
            'system': self.platform,
            'version': platform.release(),
            'machine': platform.machine(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor()
        }
    
    def is_windows(self) -> bool:
        """检查是否为Windows系统"""
        return self.platform == "Windows"
    
    def is_macos(self) -> bool:
        """检查是否为macOS系统"""
        return self.platform == "Darwin"
    
    def is_linux(self) -> bool:
        """检查是否为Linux系统"""
        return self.platform == "Linux"
    
    def detect_garbled_text(self, text: str) -> bool:
        """检测文本是否乱码"""
        if not text:
            return False
            
        garbled_patterns = [
            r'�',  # Unicode替换字符
            r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]',  # 控制字符
            r'[\ufffd]',  # Unicode替换字符
            r'[\ud800-\udfff]',  # 代理对字符
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                return True
        
        # 检测中文字符的异常组合
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_chars) > 10 and len(chinese_chars) > len(text) * 0.7:
            return True
            
        return False
    
    def safe_print(self, message: str):
        """安全打印函数，确保中文正确显示"""
        try:
            # 尝试直接打印
            print(message)
        except UnicodeEncodeError:
            # 如果编码失败，使用安全编码
            try:
                safe_message = message.encode('utf-8', errors='replace').decode('utf-8')
                print(safe_message)
            except:
                # 如果仍然失败，使用ASCII安全编码
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                print(safe_message)


# 全局工具实例
_cross_platform_utils = CrossPlatformUtils()


def get_cross_platform_utils() -> CrossPlatformUtils:
    """获取全局跨平台工具实例"""
    return _cross_platform_utils


def run_command(command: List[str], timeout: int = 10) -> str:
    """执行系统命令（便捷函数）"""
    return _cross_platform_utils.run_command(command, timeout)


def get_platform_info() -> Dict[str, str]:
    """获取平台信息（便捷函数）"""
    return _cross_platform_utils.get_platform_info()


def is_windows() -> bool:
    """检查是否为Windows系统（便捷函数）"""
    return _cross_platform_utils.is_windows()


def is_macos() -> bool:
    """检查是否为macOS系统（便捷函数）"""
    return _cross_platform_utils.is_macos()


def is_linux() -> bool:
    """检查是否为Linux系统（便捷函数）"""
    return _cross_platform_utils.is_linux()


if __name__ == '__main__':
    # 测试跨平台工具
    utils = CrossPlatformUtils(debug_mode=True)
    
    print("=== 跨平台工具测试 ===")
    print(f"平台信息: {utils.get_platform_info()}")
    print(f"系统编码: {utils.encoding}")
    
    # 测试命令执行
    if utils.is_windows():
        result = utils.run_command(["ipconfig"])
        print(f"ipconfig结果长度: {len(result)}")
    elif utils.is_macos():
        result = utils.run_command(["ifconfig"])
        print(f"ifconfig结果长度: {len(result)}")
    else:
        result = utils.run_command(["ifconfig"])
        print(f"ifconfig结果长度: {len(result)}")
    
    print("测试完成！")