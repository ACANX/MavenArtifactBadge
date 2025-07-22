import os
import pathlib

def create_badge_file(group_id, artifact_id):
    # 获取当前 Python 文件 (py3.py) 的绝对路径
    current_file = pathlib.Path(__file__).resolve()
    
    # 构建目标路径: ../Maven/Badge/groupId/artifactId.svg
    target_dir = (
        current_file.parent              # py3.py 所在目录
        .parent                          # 上一级目录 (../)
        / "Maven"                        # 进入 Maven 目录
        / "Badge"                        # 进入 Badge 目录
        / group_id.replace(".", "/")     # 将 groupId 的点替换为路径分隔符
    )
    target_file = target_dir / f"{artifact_id}.svg"
    
    # 创建目录（如果不存在）
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建 SVG 文件（示例内容）
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="128" height="20">
<rect width="100%" height="100%" fill="#555"/>
<text x="10" y="14" font-family="monospace" font-size="11" fill="#fff">
{group_id}:{artifact_id}
</text>
</svg>"""
    
    # 写入文件
    with open(target_file, "w") as f:
        f.write(svg_content)
    
    print(f"文件已创建: {target_file}")
    return target_file

# 使用示例
if __name__ == "__main__":
    # 替换为实际的 groupId 和 artifactId
    create_badge_file(group_id="org.mybatis", artifact_id="mybatis")
