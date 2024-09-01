import os
import re
import requests
import json
def generate_text(prompt):
    try: 
        response = requests.post(
            "http://localhost:8080/v1/completions",
            json={
                "model": "gpt-3.5-turbo",
                "prompt": prompt,
                "temperature": 0.7,
            },
            stream=True # 以流的形式返回数据
        )

        # 从response中获取数据
        for line in response.iter_lines():
            if line:
                result = json.loads(line)
                output_text = result['choices'][0]['text']
                return output_text
    except Exception as e:
        return str(e)


def generate_answer(current_file_text: str, content: str):
    answer_prompt = "About the following text: \n\n{}\n\nAnswer the following question: \n\n{}".format(current_file_text, content)
    print("answer_prompt", answer_prompt)
    assistant_message = generate_text(answer_prompt)
    print("assistant_message", assistant_message)
    return "Answer: " + assistant_message


def generate_summary(current_file_text: str):
    summary_prompt = "Act as a summarizer. Please summarize the following text: \n\n{}".format(current_file_text)
    assistant_message = generate_text(summary_prompt)
    return assistant_message

def generate_question(current_file_text, content):
    question_prompt = "About the following text: \n\n{}\n\nAsk a question about the following text: \n\n{}".format(current_file_text, content)
    assistant_message = generate_text(question_prompt)
    return assistant_message

if __name__ == "__main__":
    prompt = generate_answer("Hello", "Who is Sun Wukong?")
    print(generate_text(prompt))
    