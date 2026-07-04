import pytest
from kirinchat.utils.llm_parser import parse_llm_json


class TestParseLlmJson:
    def test_parse_plain_json(self):
        content = '{"key": "value", "num": 42}'
        result = parse_llm_json(content)
        assert result == {"key": "value", "num": 42}

    def test_parse_json_in_codeblock(self):
        content = '这是分析结果：\n```json\n{"score": 85}\n```\n以上。'
        result = parse_llm_json(content)
        assert result == {"score": 85}

    def test_parse_json_without_json_tag(self):
        content = '```\n{"score": 85}\n```'
        result = parse_llm_json(content)
        assert result == {"score": 85}

    def test_parse_invalid_json_raises(self):
        content = "这不是JSON"
        with pytest.raises((ValueError, Exception)):
            parse_llm_json(content)

    def test_parse_json_with_prefix_text(self):
        content = '好的，结果如下：\n```json\n{"company": "阿里巴巴"}\n```'
        result = parse_llm_json(content)
        assert result == {"company": "阿里巴巴"}
