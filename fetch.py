import requests
from bs4 import BeautifulSoup

def fetch_content(url: str):
    """
    从指定的URL中获取内容
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # 寻找包含特定文本的<p>标签
    p_tag = soup.select_one("body > main > div > section > div.border-r10 > p:nth-of-type(1)")

    if p_tag:
        return p_tag.text
    else:
        return ""

def format_content(processed_text: str, url: str):
    """
    格式化内容
    """
    question = f"Act as a summarizer. Please summarize {url}. The following is the content:\n\n{processed_text}"
    return question

def fetch(url: str):
    """
    从指定的URL中提取内容并生成问题
    """
    content = fetch_content(url)
    question = format_content(content, url)
    return question


if __name__ == "__main__":
    fetch("https://dev.qweather.com/en/help")