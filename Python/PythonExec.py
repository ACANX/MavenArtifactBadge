import os
import pathlib
import json
import requests
from typing import Dict, Any, List


def create_maven_artifact_badge_svg_file(data: dict):
    """创建包含详细构件信息的 Maven 徽章 SVG 文件（垂直布局）"""
    # 安全提取构件数据
    group_id = data.get("group_id", "")
    artifact_id = data.get("artifact_id", "")
    latest_version = data.get("latest_version", "N/A")
    dependency_count = data.get("dependency_count", 0)
    ref_count = data.get("ref_count", 0)
    
    # 安全处理分类数据
    categories = data.get("categories", [])
    if not isinstance(categories, list):
        categories = []
    # 限制显示的分类数量
    displayed_categories = categories[:3]  # 最多显示3个分类
    categories_text = ", ".join(displayed_categories)
    if len(categories) > 3:
        categories_text += ", ..."
    
    # 获取当前 Python 文件的绝对路径
    current_file = pathlib.Path(__file__).resolve()
    
    # 构建目标路径: ../Maven/Badge/groupId/artifactId.svg
    target_dir = (
        current_file.parent              # PythonExec.py 所在目录
        .parent                          # 上一级目录 (../)
        / "Maven"                        # 进入 Maven 目录
        / "Badge"                        # 进入 Badge 目录
        / group_id.replace(".", "/")     # 将 groupId 的点替换为路径分隔符
    )
    target_file = target_dir / f"{artifact_id}.svg"
    
    # 创建目录（如果不存在）
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建 SVG 文件内容 - 垂直布局
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="240" viewBox="0 0 800 240">
  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#4a90e2"/>
    <stop offset="100%" stop-color="#9013fe"/>
  </linearGradient>
  <rect width="100%" height="100%" rx="5" ry="5" fill="url(#grad)"/>
  <g transform="translate(15, 15)">
    <text x="0" y="10" font-family="Arial" font-size="18" fill="white" font-weight="bold" width="260">GroupID:</text>
    <text x="110" y="10" font-family="Arial" font-size="18" fill="white" font-weight="bold" width="460">{group_id}</text>
    <text x="0" y="40" font-family="Arial" font-size="18" fill="white" font-weight="bold" width="260">ArtifactID:</text>
    <text x="110" y="40" font-family="Arial" font-size="18" fill="white" font-weight="bold" width="460">{artifact_id}</text>    
    <text x="0" y="70" font-family="Arial" font-size="18" fill="white" font-weight="bold">最新版本:</text>
    <text x="110" y="70" font-family="Arial" font-size="18" fill="white" font-weight="bold"><tspan font-weight="bold">{latest_version}</tspan></text>
    <text x="0" y="100" font-family="Arial" font-size="18" fill="white" font-weight="bold">依赖数: </text>
    <text x="110" y="100" font-family="Arial" font-size="18" fill="white"><tspan font-weight="bold">{dependency_count}</tspan></text>
    <text x="0" y="130" font-family="Arial" font-size="18" fill="white" font-weight="bold">引用量: </text>  
    <text x="110" y="130" font-family="Arial" font-size="18" fill="white"><tspan font-weight="bold">{ref_count}</tspan></text>  
    <text x="0" y="160" font-family="Arial" font-size="18" fill="white" font-weight="bold">分类:</text>
    <text x="10" y="190" font-family="Arial" font-size="10" fill="white"><tspan font-weight="bold">{categories_text}</tspan></text>
    <ellipse  cx="600" cy="120" rx="140" ry="60"  fill="#ff4081"/>
    <text x="600" y="120" text-anchor="middle" font-family="Arial" font-size="24" fill="white" font-weight="bold">MavenArtifactBadge</text>
  </g>
  <text x="720" y="225" font-family="Arial" font-size="3" fill="#d0d0d0">由MavenArtifactBadgeGenerator生成</text>
</svg>"""
    
    # 写入文件
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"✅ 徽章文件已创建: {target_file}")
    return target_file


def fetch_maven_components() -> List[Dict[str, Any]]:
    """从 Sonatype Central 获取 Maven 构件数据"""
    url = "https://central.sonatype.com/api/internal/browse/components"
    headers = {
        "User-Agent": "MavenBadgeGenerator/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "page": 0,
        "size": 20,
        "searchTerm": "",
        "sortField": "publishedDate",
        "sortDirection": "desc",
        "filter": []
    }
    
    print("⏳ 正在从 Sonatype Central 获取最新 Maven 构件数据...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # 检查 HTTP 错误
        
        data = response.json()
        return data.get("components", [])
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return []
    except json.JSONDecodeError:
        print("❌ 响应解析失败: 无效的 JSON 格式")
        return []

def parse_component_data(component: Dict[str, Any]) -> Dict[str, Any]:
    """解析单个构件元数据"""
    return {
        "group_id": component.get("namespace", ""),
        "artifact_id": component.get("name", ""),
        "latest_version": component.get("latestVersionInfo", {}).get("version", "N/A"),
        "dependency_count": component.get("dependencyOfCount", 0),
        "ref_count": component.get("dependentOnCount", 0),
        "categories": component.get("categories", [])
    }

def generate_badges_for_components():
    """为所有获取到的构件生成徽章"""
    components = fetch_maven_components()
    if not components:
        print("⚠️ 未获取到任何构件数据")
        return
    print(f"📦 获取到 {len(components)} 个 Maven 构件")
    
    for idx, component in enumerate(components, 1):
        data = parse_component_data(component)
        print(f"\n🔍 处理构件 #{idx}:")
        print(f"   Group ID: {data['group_id']}")
        print(f"   Artifact ID: {data['artifact_id']}")
        print(f"   最新版本: {data['latest_version']}")
        print(f"   依赖数量: {data['dependency_count']}")
        print(f"   被引用量: {data['ref_count']}")
        # 安全处理 categories 字段
        if data['categories']:
            categories_str = ", ".join(data['categories'])
            print(f"   分类: {categories_str}")
        else:
            print("   分类: 无")
        # 只为有效的 group_id 和 artifact_id 创建徽章
        if data['group_id'] and data['artifact_id']:
            # 创建徽章文件
            create_maven_artifact_badge_svg_file(data)
            # create_badge_file(data['group_id'], data['artifact_id'])
        else:
            print("⚠️ 跳过无效的构件: 缺少 group_id 或 artifact_id")


# 使用示例
if __name__ == "__main__":
    generate_badges_for_components()
    print("\n🎉 所有徽章生成完成！")
