import os
import requests
import json
from typing import List, Dict

def lookup_location_id(location: str):
    # 城市搜索
    print(location)
    url = "https://geoapi.qweather.com/v2/city/lookup"
    params = {
        'location': location,
        'key': '052117518d70409ba75dfbd38c615972'
    }
    params_json = json.dumps(params)
    response = requests.get(url, params=params_json)
    print("response")
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data["code"] == "200":
            # 如果有id，则返回id
            return data["location"][0]["id"]
        else:
            print(f"error: {data['code']}")
    else:
        print(f"failed: {response.status_code}")
    return None

def get_current_weather(location: str):
    # 获取城市ID
    location_id = lookup_location_id(location)
    # 如果有多个location_id，选取第一个
    if isinstance(location_id, list) and len(location_id) > 0:
        location_id = location_id[0]
    if not location_id:
        return "Sorry, I can't find the location"

    # 构建API请求URL
    base_url = "https://api.qweather.com/v7/weather/now"
    params = {
        "location": location_id,
        "key": "052117518d70409ba75dfbd38c615972",  # API密钥
        "lang": "zh"  
    }

    # 发送请求
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["code"] == "200":
            weather_info = data["now"]
            return f"当前天气：{weather_info['text']}，温度：{weather_info['temp']}°C，体感温度：{weather_info['feelsLike']}°C，风向：{weather_info['windDir']}，风速：{weather_info['windSpeed']}km/h"
        else:
            return f"unable to get weather info: {data['code']}"
    else:
        return f"failed: {response.status_code}"

def add_todo(todo: str):
    # 创建一个全局变量来存储所有的todo项
    global todo_list
    if 'todo_list' not in globals():
        todo_list = []
    todo_list.append(todo)
    return todo_list

def function_calling(messages: List[Dict]):
    # 检查消息内容是否包含天气查询
    if any("What's the weather like in " in message["content"] for message in messages):
        weather_query = next(message["content"] for message in reversed(messages) if "What's the weather like in " in message["content"])
        city = weather_query.split("What's the weather like in ", 1)[1].strip()
        # 如果城市名称以问号结尾，去除问号
        if city.endswith('?'):
            city = city[:-1]
        city_location_id = lookup_location_id(city)
        # weather_info = get_current_weather(city_location_id)
        return city_location_id
    # 检查消息内容是否包含添加待办事项
    elif any("Add a todo: " in message["content"] for message in messages):
        todo_content = next(message["content"].split("Add a todo: ", 1)[1].strip() for message in reversed(messages) if "Add a todo: " in message["content"])
        todo_list = add_todo(todo_content)
        return f"{todo_list}"
    else:
        return "No function calling"

if __name__ == "__main__":
    messages = [{"role": "user", "content": "What's the weather like in Beijing?"}]
    response = function_calling(messages)
    print(response)