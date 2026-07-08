from kirinchat.tools.send_email.action import send_email
from kirinchat.tools.web_search.tavily_search.action import tavily_search
from kirinchat.tools.web_search.bocha_search.action import bocha_search
from kirinchat.tools.arxiv.action import get_arxiv
from kirinchat.tools.get_weather.action import get_weather
from kirinchat.tools.delivery.action import get_delivery_info
from kirinchat.tools.text2image.action import text_to_image
from kirinchat.tools.docx_to_pdf.action import convert_to_pdf
from kirinchat.tools.pdf_to_docx.action import convert_to_docx
from kirinchat.tools.image2text.action import image_to_text


AgentTools = [
    send_email,
    tavily_search,
    bocha_search,
    get_weather,
    get_arxiv,
    get_delivery_info,
    text_to_image,
    image_to_text,
    convert_to_pdf,
    convert_to_docx
]


AgentToolsWithName = {
    "send_email": send_email,
    "tavily_search": tavily_search,
    "web_search": tavily_search,
    "get_arxiv": get_arxiv,
    "get_weather": get_weather,
    "get_delivery_info": get_delivery_info,
    "text_to_image": text_to_image,
    "image_to_text": image_to_text,
    "docx_to_pdf": convert_to_pdf,
    "pdf_to_docx": convert_to_docx,
    "bocha_search": bocha_search,
}

WorkSpacePlugins = AgentToolsWithName

LingSeekPlugins = AgentToolsWithName

WeChatTools = {
    "tavily_search": tavily_search,
    "get_arxiv": get_arxiv,
    "get_weather": get_weather,
    "text_to_image": text_to_image,
    "bocha_search": bocha_search,
}