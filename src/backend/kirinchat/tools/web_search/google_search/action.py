from langchain.tools import tool
from langchain_community.utilities import SerpAPIWrapper
from kirinchat.settings import app_settings

_search = None

def _get_search():
    global _search
    if _search is None:
        api_key = app_settings.tools.google.get('api_key') if app_settings.tools else ''
        if not api_key:
            raise RuntimeError("GOOGLE_SEARCH_API_KEY 未配置，无法使用 Google 搜索")
        _search = SerpAPIWrapper(serpapi_api_key=api_key)
    return _search

@tool("web_search", parse_docstring=True)
def google_search(query: str):
    """
    根据用户的问题进行网上搜索信息。

    Args:
        query (str): 用户的问题。

    Returns:
        str: 搜索到的信息。
    """
    return _google_search(query)

def _google_search(query: str):
    """使用搜索工具给用户进行搜索"""
    result = _get_search().run(query)
    return result
