#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management module
Load configuration from environment variables and .env file
"""

import os
from typing import Optional
from pathlib import Path

def load_env_file(env_path: str = ".env") -> None:
    """Load .env file into environment variables"""
    env_file = Path(env_path)
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def get_config(key: str, default: Optional[str] = None) -> str:
    """Get configuration value"""
    return os.environ.get(key, default)

class Config:
    """Configuration class"""
    
    def __init__(self):
        # Load .env file
        load_env_file()
        
        # API configuration
        # API key must come from environment; no hardcoded default
        self.OPENAI_API_KEY = get_config('OPENAI_API_KEY', '')
        self.OPENAI_BASE_URL = get_config('OPENAI_BASE_URL', 'https://api.gptplus5.com/v1')
        
        # Proxy configuration
        self.HTTP_PROXY = get_config('HTTP_PROXY', 'http://127.0.0.1:1082')
        self.HTTPS_PROXY = get_config('HTTPS_PROXY', 'http://127.0.0.1:1082')
        self.http_proxy = get_config('http_proxy', 'http://127.0.0.1:1082')
        self.https_proxy = get_config('https_proxy', 'http://127.0.0.1:1082')
        
        # GEE configuration
        self.GEE_PROJECT_ID = get_config('GEE_PROJECT_ID', 'data-center-location-analysis')
        self.GEE_SERVICE_ACCOUNT_KEY_PATH = get_config('GEE_SERVICE_ACCOUNT_KEY_PATH', './gee_service_account_key.json')
        
        # Server configuration
        self.BACKEND_PORT = int(get_config('BACKEND_PORT', '8000'))
        self.FRONTEND_PORT = int(get_config('FRONTEND_PORT', '3000'))
        
        # Other configuration
        self.DEBUG = get_config('DEBUG', 'false').lower() == 'true'
        self.LOG_LEVEL = get_config('LOG_LEVEL', 'INFO')
    
    def setup_proxy(self):
        """Set proxy environment variables"""
        os.environ['HTTP_PROXY'] = self.HTTP_PROXY
        os.environ['HTTPS_PROXY'] = self.HTTPS_PROXY
        os.environ['http_proxy'] = self.http_proxy
        os.environ['https_proxy'] = self.https_proxy
    
    def setup_openai_key(self):
        """Set OpenAI API key"""
        os.environ['OPENAI_API_KEY'] = self.OPENAI_API_KEY

# Global configuration instance
config = Config()