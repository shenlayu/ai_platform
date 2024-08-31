import gradio as gr
import os
import time
from chat import chat

messages = []
current_file_text = None

def add_text(history, text):
    global messages
    history = history + [(text, None)]
    messages.append({"role": "user", "content": text})
    
    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global messages
    history = history + [((file.name,), None)]
    messages.append({"role": "user", "content": f"File uploaded: {file.name}"})
    
    return history

def bot(history):
    global messages
    
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
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear_btn.click(lambda: messages.clear(), None, chatbot, queue=False)

demo.queue()
demo.launch()
