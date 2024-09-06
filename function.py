import re

import os
import requests
import json
from typing import List, Dict
import openai

def lookup_location_id(location: str):
    try:
        # 城市搜索
        print(location)
        url = "https://geoapi.qweather.com/v2/city/lookup"
        params = {
            'location': location,
            'key': 'e6c15b192e8540dfb2dc5c17857580ff'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == "200":
                # 如果有id，则返回id
                return data["location"][0]["id"]
            else:
                print(f"error: {data['code']}")
                return '101010100'
        return None
    except:
        return '101010100'

def get_current_weather(id: str):
    # 获取城市ID
    location_id = id
    print(location_id)
    # 如果有多个location_id，选取第一个
    if isinstance(location_id, list) and len(location_id) > 0:
        location_id = location_id[0]
    if not location_id:
        return "Sorry, I can't find the location"

    # 构建API请求URL
    base_url = "https://api.qweather.com/v7/weather/now"
    params = {
        "location": location_id,
        "key": "0631f557d4bd4c19994cdae83bdc39bc",  # API密钥
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
    # print(todo_list)
    return todo_list

def function_calling(messages: List[Dict]):
    response = []
    result = []
    id = 0
    function_content = ""
    functions = [
        {
            "name": "get_current_weather",
            "description": "TODO",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "TODO",
                    },
                },
                "required": ["location"],
            },
        },
        {
            "name": "add_todo",
            "description": "TODO",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo": {
                        "type": "string",
                        "description": "TODO",
                    }
                },
                "required": ["todo"],
            },
        }
    ]

    openai.api_base = "http://localhost:8080/v1"
    openai.api_key = 'hahahaha'

    answer = openai.ChatCompletion.create(model="ggml-openllama.bin", messages=messages, functions=functions,
                                       function_call="auto",)

    print(answer)
    function_to_call = answer['choices'][0]['message']['function_call']['function']
    if function_to_call == 'get_current_weather':

        print(answer['choices'][0]['message']['function_call']['arguments'])
        p = re.findall('.*\"location\":\"(.*)\".*',answer['choices'][0]['message']['function_call']['arguments'])

        city_location_id = lookup_location_id(p[0])
        weather_info = get_current_weather(city_location_id)
        result.append(weather_info)
        id = 1

    elif function_to_call == 'add_todo':
        # todo_content = messages[0]["content"].split("Add a todo: ", 1)[1].strip()
        print(answer['choices'][0]['message']['function_call']['arguments'])
        p = re.findall('.*\"todo\":\"(.*)\".*', answer['choices'][0]['message']['function_call']['arguments'])
        print(p)
        todo_list = add_todo(p[0])
        result = todo_list
        id = 2

    if (len(result) > 0):
        if id == 2:
            for i in range(len(result)):
                function_content += f"-{result[i]}\n"
        elif id == 1:
            function_content += result[0]
        else:
            function_content = "Sorry, I didn't get that."
    return function_content


    # # 检查消息内容是否包含天气查询
    # for message in messages:
    #     if "What's the weather like in " in message["content"]:
    #         weather_query = next(message["content"] for message in reversed(messages) if "What's the weather like in " in message["content"])
    #         city = weather_query.split("What's the weather like in ", 1)[1].strip()
    #         # 如果城市名称以问号结尾，去除问号
    #         if city.endswith('?'):
    #             city = city[:-1]
    #         city_location_id = lookup_location_id(city)
    #         weather_info = get_current_weather(city_location_id)
    #         result.append(weather_info)
    #         id = 1
    #     elif "Add a todo: " in message["content"]:
    #         todo_content = message["content"].split("Add a todo: ", 1)[1].strip()
    #         todo_list = add_todo(todo_content)
    #         result = todo_list
    #         id = 2
    #
    # if (len(result) > 0):
    #     if id == 2:
    #         for i in range(len(result)):
    #             function_content += f"-{result[i]}\n"
    #     elif id == 1:
    #         function_content += result[0]
    #     else:
    #         function_content = "Sorry, I didn't get that."
    # return function_content

if __name__ == "__main__":
    messages = [{"role": "user", "content": "What's the weather like in Beijing?"},{"role": "user", "content": "Add a todo: swim"}]
    response = function_calling(messages)
    print(response)