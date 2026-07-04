import pytest
from kirinchat.api.services.jd import JdService
from kirinchat.schemas.jd import JdParseResp, JdCategoryResp


class TestJdService:
    def test_build_persona(self):
        parse_result = JdParseResp(
            company="阿里巴巴",
            position="Java 高级工程师",
            experience_required="3-5年",
            categories=[
                JdCategoryResp(key="java", label="Java", priority="CORE", keywords=["Java"]),
                JdCategoryResp(key="mysql", label="MySQL", priority="CORE", keywords=["MySQL"]),
            ],
            summary="负责核心业务系统开发",
        )
        persona = JdService._build_persona(parse_result)
        assert "阿里巴巴" in persona
        assert "Java 高级工程师" in persona
        assert "3-5年" in persona
        assert "Java" in persona

    def test_find_reference_file_known(self):
        content = JdService._find_reference_file("java")
        assert content is not None
        assert len(content) > 100  # 参考资料内容应该足够长
        assert "Java" in content

    def test_find_reference_file_unknown(self):
        path = JdService._find_reference_file("nonexistent_xyz")
        assert path is None
