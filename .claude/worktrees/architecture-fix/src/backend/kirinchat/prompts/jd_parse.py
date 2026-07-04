JD_PARSE_PROMPT = """你是一位资深的 HR 技术专家，请分析以下职位描述（JD），提取关键信息。

{anti_injection}

{data_boundary}

## 分析要求
请以 JSON 格式返回分析结果：
{{
    "company": "公司名称",
    "position": "职位名称",
    "experience_required": "经验要求（如：3-5年）",
    "categories": [
        {{
            "key": "java",
            "label": "Java",
            "priority": "CORE",
            "keywords": ["Java", "JVM", "Spring"]
        }}
    ],
    "summary": "职位概要（50字内）"
}}

## 分类标准化
请将 JD 中的技术要求标准化为以下分类之一：
java, mysql, redis, spring, python, javascript, typescript, react, vue,
html-css, browser, algorithm, system-design, distributed, mq, network,
linux, docker, kubernetes, git, design-pattern, project

如果 JD 中的技术不完全匹配上述分类，选择最接近的。
请只返回 JSON，不要包含其他文字。"""
