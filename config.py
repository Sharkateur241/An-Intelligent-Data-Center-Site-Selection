#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
从环境变量和.env文件加载配置
"""

import os
from typing import Optional
from pathlib import Path

def load_env_file(env_path: str = ".env") -> None:
    """加载.env文件到环境变量"""
    env_file = Path(env_path)
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def get_config(key: str, default: Optional[str] = None) -> str:
    """获取配置值"""
    return os.environ.get(key, default)

class Config:
    """配置类"""
    
    def __init__(self):
        # 加载.env文件
        load_env_file()
        
        # API 配置
        # API key must come from environment; no hardcoded default
        self.OPENAI_API_KEY = get_config('OPENAI_API_KEY', '')
        self.OPENAI_BASE_URL = get_config('OPENAI_BASE_URL', 'https://api.gptplus5.com/v1')
        
        # 代理配置
        self.HTTP_PROXY = get_config('HTTP_PROXY', 'http://127.0.0.1:1082')
        self.HTTPS_PROXY = get_config('HTTPS_PROXY', 'http://127.0.0.1:1082')
        self.http_proxy = get_config('http_proxy', 'http://127.0.0.1:1082')
        self.https_proxy = get_config('https_proxy', 'http://127.0.0.1:1082')
        
        # GEE 配置
        self.GEE_PROJECT_ID = get_config('GEE_PROJECT_ID', 'data-center-location-analysis')
        self.GEE_SERVICE_ACCOUNT_KEY_PATH = get_config('GEE_SERVICE_ACCOUNT_KEY_PATH', './gee_service_account_key.json')
        
        # 服务器配置
        self.BACKEND_PORT = int(get_config('BACKEND_PORT', '8000'))
        self.FRONTEND_PORT = int(get_config('FRONTEND_PORT', '3000'))
        
        # 其他配置
        self.DEBUG = get_config('DEBUG', 'false').lower() == 'true'
        self.LOG_LEVEL = get_config('LOG_LEVEL', 'INFO')
    
    def setup_proxy(self):
        """设置代理环境变量"""
        os.environ['HTTP_PROXY'] = self.HTTP_PROXY
        os.environ['HTTPS_PROXY'] = self.HTTPS_PROXY
        os.environ['http_proxy'] = self.http_proxy
        os.environ['https_proxy'] = self.https_proxy
    
    def setup_openai_key(self):
        """设置OpenAI API密钥"""
        os.environ['OPENAI_API_KEY'] = self.OPENAI_API_KEY

# 全局配置实例
config = Config()
