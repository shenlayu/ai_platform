import os
import re
import requests
import json
import openai

def generate_text(prompt):
    try: 
        # response = requests.post(
        #     "http://localhost:8080/v1/completions",
        #     json={
        #         "model": "gpt-3.5-turbo",
        #         "prompt": prompt,
        #         "temperature": 0.7,
        #     },
        #     stream=True # 以流的形式返回数据
        # )
        # # return response
        # # response = openai.ChatCompletion.create(
        # #     model="gpt-3.5-turbo",
        # #     messages=prompt,
        # #     temperature=0.7,
        # #     stream=True
        # # )

        # # for chunk in response:
        # #     if 'choices' in chunk:
        # #         if 'delta' in chunk['choices'][0]:
        # #             print(chunk['choices'][0]['delta'].get('content', ''))
        # #             yield chunk['choices'][0]['delta'].get('content', '')

        # # # 从response中获取数据
        # for line in response.iter_lines():
        #     if line:
        #         result = json.loads(line)
        #         output_text = result['choices'][0]['text']
        #         yield output_text
        # response = requests.post(
        #     "http://localhost:8080/v1/completions",
        #     json={
        #         "model": "gpt-3.5-turbo",
        #         "prompt": prompt,
        #         "temperature": 0.7,
        #     },
        #     stream=True  # 使用流式返回数据
        # )
        openai.api_key = "your_api_key"
        openai.api_base = "http://localhost:8080/v1"
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}  # Replace prompt with the user input
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            stream=True
        )

        for chunk in response:
            if 'choices' in chunk:
                if 'delta' in chunk['choices'][0]:
                    yield chunk['choices'][0]['delta'].get('content', '')
    except Exception as e:
        return str(e)


def generate_answer(current_file_text: str, content: str):
    answer_prompt = "About the following text: \n\n{}\n\nAnswer the following question: \n\n{}".format(current_file_text, content)
    for chunk in generate_text(answer_prompt):
        yield chunk


def generate_summary(current_file_text: str):
    summary_prompt = "Act as a summarizer. Please summarize the following text: \n\n{}".format(current_file_text)
    for chunk in generate_text(summary_prompt):
        yield chunk

def generate_question(current_file_text, content):
    question_prompt = "About the following text: \n\n{}\n\nAsk a question about the following text: \n\n{}".format(current_file_text, content)
    assistant_message = generate_text(question_prompt)
    return assistant_message

if __name__ == "__main__":
    prompt = generate_answer("Hello", "Who is Sun Wukong?")
    print(generate_text(prompt))
    