import gradio as gr
import os
import time
from chat import chat
from mnist import image_classification
from search import search
from fetch import fetch
from stt import audio2text
from pdf import generate_answer, generate_summary
from tts import text2audio
from image_generate import image_generate

messages = []
current_file_text = None
isTxt = False
isFile = False
image = ''

def add_text(history, text):
    global messages, current_file_text, isFile
    if text.startswith("/search "):
        search_query = text[len("/search "):]
        search_result = search(search_query)
        messages.append({"role": "user", "content": search_result})
    elif text.startswith("/fetch"): # 检验是否是fetch命令
        fetch_url = text[len("/fetch "):]
        fetch_result = fetch(fetch_url)
        messages.append({"role": "user", "content": fetch_result})
    elif text.startswith("/file"): # 检验是否是file命令, 如果是，设置isFile为True，用于bot中后续处理
        isFile = True
        question = text[len("/file "):].strip()
        user_message = question
        messages.append({"role": "user", "content": user_message})
    elif text.startswith("/image"):
        content = text[len("/image "):]
        image_url = image_generate(content)
        messages.append({"role": "user", "content": image_url})
    else:
        messages.append({"role": "user", "content": text})

    history = history + [(text, None)]
    
    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global messages, current_file_text, isTxt, image
    history = history + [((file.name,), None)]
    if file.name.endswith(".wav"): # 检验是否是音频文件
        audio_text = audio2text(file.name)
        messages.append({"role": "user", "content": f"{audio_text}"})
    elif file.name.endswith(".png"):
        messages.append({"role": "user", "content": f"Please classify {file.name}"})
        image = file
    elif file.name.endswith(".txt"): # 检验是否是txt文件，如果是，设置isTxt为True，用于bot中后续处理
        isTxt = True
        current_file_text = open(file.name).read()
        messages.append({"role": "user", "content": f"{file.name}"})
    else:
        messages.append({"role": "user", "content": f"File uploaded: {file.name}"})
    
    return history

def bot(history):
    global messages, current_file_text, isTxt, isFile, image
    response_text = ""
    
    if isTxt: # 如果是txt文件，生成summary
        isTxt = False
        summary = generate_summary(current_file_text)
        messages.append({"role": "assistant", "content": f"{summary}"})
        history[-1][1] = summary
        yield history
    elif isFile: # 如果是file命令，生成answer
        isFile = False
        if current_file_text:
            answer = generate_answer(current_file_text, messages[-1]['content'])
            assistant_message = answer
        else:
            assistant_message = "请先上传一个文件"
        messages.append({"role": "assistant", "content": assistant_message})
        history[-1][1] = assistant_message
        yield history
    elif messages[-1]["role"] == "user" and messages[-1]["content"].startswith("/audio "): # 检验是否是音频文件

        for chunk in chat(messages):
            response_text += chunk
        audio_path = text2audio(response_text)
        if audio_path:
            history[-1][1] = (audio_path, )
            yield history
    # 检查是否是图像识别
    if messages[-1]["role"] == "user" and messages[-1]["content"].startswith("Please classify "):
        result = image_classification(file=image)
        image = ''
        history[-1][1] = result
        yield history
    else:
        response_text = ""

        for chunk in chat(messages):
            response_text += chunk
            history[-1][1] = response_text
            yield history

        messages.append({"role": "assistant", "content": response_text})

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    # TODO 这个地方需要保证处理的时候不能再输入，而且需要生成的时候不能再输入，
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    
    clear_btn.click(lambda: messages.clear(), None, chatbot, queue=False)

demo.queue()
demo.launch()