#!/usr/bin/env python3
"""
GEE认证配置脚本 - 必需配置
系统必须使用GEE数据，请先完成GEE认证
"""

import os
import sys
import ee

def setup_gee_auth():
    """设置GEE认证"""
    print("=" * 60)
    print("Google Earth Engine 认证配置 - 必需步骤")
    print("=" * 60)
    print()
    print("⚠️  重要：本系统必须使用GEE数据！")
    print("请先完成以下步骤：")
    print()
    print("1. 访问 https://earthengine.google.com/")
    print("2. 注册Google账号并申请GEE访问权限")
    print("3. 创建Google Cloud项目")
    print("4. 启用Earth Engine API")
    print("5. 完成GEE认证")
    print()
    
    # 检查是否已经认证
    try:
        ee.Initialize(project='data-center-location-analysis')
        print("✅ GEE已认证，系统可以正常运行！")
        return True
    except Exception as e:
        print("❌ GEE未认证，请先完成认证步骤")
        print(f"错误信息: {e}")
        print()
        
        # 尝试认证
        try:
            print("正在尝试GEE认证...")
            ee.Authenticate()
            ee.Initialize(project='data-center-location-analysis')
            print("✅ GEE认证成功！")
            return True
        except Exception as auth_error:
            print(f"❌ GEE认证失败: {auth_error}")
            print()
            print("请手动完成以下步骤：")
            print("1. 在浏览器中访问: https://code.earthengine.google.com/")
            print("2. 登录您的Google账号")
            print("3. 接受GEE服务条款")
            print("4. 重新运行此脚本")
            return False

if __name__ == "__main__":
    success = setup_gee_auth()
    if not success:
        print("\n❌ 系统无法启动，请先完成GEE认证！")
        sys.exit(1)
    else:
        print("\n✅ 系统准备就绪，可以启动！")