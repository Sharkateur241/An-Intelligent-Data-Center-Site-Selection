# Google Earth Engine 真实数据配置完整指南

## 🎯 目标
配置GEE使用真实卫星数据，替换模拟数据。

## 📋 当前问题
1. **缺少Google Cloud项目**: GEE需要关联Google Cloud项目
2. **API未启用**: 需要启用Earth Engine API
3. **权限配置**: 需要正确配置项目权限

## 🚀 解决步骤

### 步骤1: 创建Google Cloud项目

1. **访问Google Cloud Console**
   - 打开: https://console.cloud.google.com/
   - 使用您的Google账号登录

2. **创建新项目**
   - 点击项目选择器
   - 点击"新建项目"
   - 项目名称: `data-center-location-analysis`
   - 点击"创建"

3. **记录项目ID**
   - 项目ID格式: `data-center-location-analysis-xxxxx`
   - 记下这个项目ID，稍后需要用到

### 步骤2: 启用Earth Engine API

1. **进入API库**
   - 在Google Cloud Console中
   - 导航到"API和服务" > "库"

2. **搜索并启用API**
   - 搜索"Earth Engine API"
   - 点击"启用"

3. **等待启用完成**
   - 通常需要几分钟时间

### 步骤3: 配置Earth Engine

1. **访问Earth Engine**
   - 打开: https://earthengine.google.com/
   - 使用相同Google账号登录

2. **关联项目**
   - 在Earth Engine界面中
   - 选择您创建的Google Cloud项目
   - 确认关联

### 步骤4: 更新代码配置

修改 `backend/services/satellite_service.py`:

```python
def __init__(self):
    """初始化GEE服务"""
    try:
        # 使用您的项目ID初始化GEE
        project_id = "your-project-id-here"  # 替换为您的项目ID
        ee.Initialize(project=project_id)
        print("Google Earth Engine 初始化成功")
        self.use_real_data = True
    except Exception as e:
        print(f"GEE初始化失败: {e}")
        print("请检查项目配置")
        self.use_real_data = False
```

### 步骤5: 测试真实数据

运行测试脚本验证配置:

```python
import ee

# 使用您的项目ID
project_id = "your-project-id-here"
ee.Initialize(project=project_id)

# 测试数据访问
point = ee.Geometry.Point([116.4074, 39.9042])  # 北京
collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
image = collection.filterBounds(point).first()
print("真实数据测试成功！")
print("图像ID:", image.getInfo()['id'])
```

## 🔧 快速配置脚本

创建一个自动配置脚本:

```python
# configure_gee.py
import ee
import os

def configure_gee():
    """配置GEE使用真实数据"""
    
    # 获取项目ID
    project_id = input("请输入您的Google Cloud项目ID: ")
    
    try:
        # 初始化GEE
        ee.Initialize(project=project_id)
        print("✅ GEE初始化成功！")
        
        # 测试数据访问
        point = ee.Geometry.Point([116.4074, 39.9042])
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        image = collection.filterBounds(point).first()
        
        if image:
            info = image.getInfo()
            print("✅ 真实数据访问成功！")
            print(f"   图像ID: {info.get('id')}")
            print(f"   获取日期: {info.get('properties', {}).get('DATE_ACQUIRED')}")
            
            # 保存项目ID到配置文件
            with open('.gee_project_id', 'w') as f:
                f.write(project_id)
            print("✅ 项目ID已保存到配置文件")
            
            return True
        else:
            print("❌ 无法获取数据")
            return False
            
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False

if __name__ == "__main__":
    configure_gee()
```

## 📝 详细操作步骤

### 1. Google Cloud项目创建

**访问**: https://console.cloud.google.com/

**操作**:
1. 点击顶部项目选择器
2. 点击"新建项目"
3. 输入项目名称: `data-center-location-analysis`
4. 点击"创建"
5. 等待项目创建完成
6. 记录项目ID（格式: `data-center-location-analysis-xxxxx`）

### 2. 启用Earth Engine API

**访问**: https://console.cloud.google.com/apis/library

**操作**:
1. 搜索"Earth Engine API"
2. 点击进入API页面
3. 点击"启用"按钮
4. 等待启用完成（通常2-3分钟）

### 3. Earth Engine项目关联

**访问**: https://earthengine.google.com/

**操作**:
1. 使用相同Google账号登录
2. 在项目选择器中选择您创建的Google Cloud项目
3. 确认关联

### 4. 更新代码

修改 `backend/services/satellite_service.py` 中的项目ID:

```python
# 将这一行
ee.Initialize()

# 改为
ee.Initialize(project="your-actual-project-id")
```

## 🧪 测试验证

创建测试脚本 `test_gee.py`:

```python
import ee

def test_gee_connection():
    """测试GEE连接"""
    try:
        # 使用您的项目ID
        project_id = "your-project-id-here"
        ee.Initialize(project=project_id)
        
        print("✅ GEE初始化成功")
        
        # 测试北京地区数据
        beijing = ee.Geometry.Point([116.4074, 39.9042])
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        image = collection.filterBounds(beijing).first()
        
        if image:
            info = image.getInfo()
            print("✅ 数据访问成功")
            print(f"图像ID: {info.get('id')}")
            print(f"获取日期: {info.get('properties', {}).get('DATE_ACQUIRED')}")
            print(f"云量: {info.get('properties', {}).get('CLOUD_COVER')}%")
            return True
        else:
            print("❌ 无法获取图像数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_gee_connection()
```

## 🚨 常见问题解决

### 问题1: 项目ID错误
**错误**: `Project not found`
**解决**: 检查项目ID是否正确，确保项目已创建

### 问题2: API未启用
**错误**: `API not enabled`
**解决**: 在Google Cloud Console中启用Earth Engine API

### 问题3: 权限不足
**错误**: `Permission denied`
**解决**: 确保账号有项目访问权限

### 问题4: 配额超限
**错误**: `Quota exceeded`
**解决**: 等待配额重置或升级账号
