import requests
import os

def text2audio(content: str):
    url = "http://localhost:8080/tts"
    payload = {
        "model": "en-us-blizzard_lessac-medium.onnx",
        "input": content
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        # 定义保存路径并保存
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "output.wav")
        with open(file_path, "wb") as audio_file:
            audio_file.write(response.content)

        return file_path
    else:
        # 错误输出
        raise Exception(f"Failed to generate audio: {response.status_code} {response.text}")

if __name__ == "__main__":
    text2audio(
        "Sun Wukong (also known as the Great Sage of Qi Tian, Sun Xing Shi, and Dou Sheng Fu) is one of the main characters in the classical Chinese novel Journey to the West")
