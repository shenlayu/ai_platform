import gradio as gr
import os
import time
from chat import chat
from search import search
from fetch import fetch
from stt import audio2text
from pdf import generate_answer, generate_summary

messages = []
current_file_text = None
isTxt = False
isFile = False

def add_text(history, text):
    global messages, current_file_text, isFile
    if text.startswith("/search "):
        search_query = text[len("/search "):]
        search_result = search(search_query)
        messages.append({"role": "user", "content": search_result})
    elif text.startswith("/fetch"):
        fetch_url = text[len("/fetch "):]
        fetch_result = fetch(fetch_url)
        messages.append({"role": "user", "content": fetch_result})
    elif text.startswith("/file"):
        question = text[len("/file "):].strip()
        user_message = question
        isFile = True
        messages.append({"role": "user", "content": user_message})
    else:
        messages.append({"role": "user", "content": text})

    history = history + [(text, None)]
    
    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global messages, current_file_text, isTxt
    history = history + [((file.name,), None)]
    if file.name.endswith(".wav"):
        audio_text = audio2text(file.name)
        messages.append({"role": "user", "content": f"{audio_text}"})
    elif file.name.endswith(".txt"):
        current_file_text = open(file.name).read()
        messages.append({"role": "user", "content": f"{file.name}"})
        isTxt = True
    else:
        messages.append({"role": "user", "content": f"File uploaded: {file.name}"})
    
    return history

def bot(history):
    global messages, current_file_text, isTxt, isFile
    if isTxt:
        isTxt = False
        summary = generate_summary(current_file_text)
        messages.append({"role": "assistant", "content": f"{summary}"})
        history[-1][1] = summary
        yield history
    elif isFile:
        isFile = False
        if current_file_text:
            answer = generate_answer(current_file_text, messages[-1]['content'])
            assistant_message = answer
        else:
            assistant_message = "请先上传一个文件"
        messages.append({"role": "assistant", "content": assistant_message})
        history[-1][1] = assistant_message
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