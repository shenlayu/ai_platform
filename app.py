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
from function import function_calling
from image_generate import image_generate

messages = []
current_file_text = None
isTxt = False
isFile = False
isImage = False
isImageGenerate = False
isAudio = False
isFunction = False
image = ''

def add_text(history, text):
    global messages, current_file_text, isFile, isAudio, isImageGenerate, isFunction
    if text.startswith("/search "):
        search_query = text[len("/search "):]
        search_result = search(search_query)
        messages.append({"role": "user", "content": search_result})
    elif text.startswith("/audio "):
        isAudio = True
        messages.append({"role": "user", "content": text})
    elif text.startswith("/image "):
        isImageGenerate = True
        messages.append({"role": "user", "content": text})
    elif text.startswith("/fetch"): # 检验是否是fetch命令
        fetch_url = text[len("/fetch "):]
        fetch_result = fetch(fetch_url)
        messages.append({"role": "user", "content": fetch_result})
    elif text.startswith("/function "): # 检验是否是function命令
        isFunction = True
        function_url = text[len("/function "):]
        messages.append({"role": "user", "content": function_url})
    elif text.startswith("/file"): # 检验是否是file命令, 如果是，设置isFile为True，用于bot中后续处理
        isFile = True
        question = text[len("/file "):].strip()
        user_message = question
        messages.append({"role": "user", "content": user_message})
    #elif text.startswith("/image"):
    #    content = text[len("/image "):]
    #    messages.append({"role": "user", "content": f'http://localhost:8080/generated-images/b644107623023.png'})
    #    # image_url = image_generate(content)
    #    messages.append({"role": "assistant", "content": f'http://localhost:8080/generated-images/b644107623023.png'})
    else:
        messages.append({"role": "user", "content": text})
    history = history + [(text, None)]
    
    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global messages, current_file_text, isTxt, isImage, image
    history = history + [((file.name,), None)]
    if file.name.endswith(".wav"): # 检验是否是音频文件
        audio_text = audio2text(file.name)
        messages.append({"role": "user", "content": f"{audio_text}"})
    elif file.name.endswith(".png"):
        isImage = True
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
    try:
        global messages, current_file_text, isTxt, isFile, isImage, image, isAudio, isImageGenerate, isFunction
        response_text = ""

        if isTxt: # 如果是txt文件，生成summary
            isTxt = False
            response_text = ""
            for chunk in generate_summary(current_file_text):
                response_text += chunk
                history[-1][1] = response_text
                yield history
            messages.append({"role": "assistant", "content": f"{response_text}"})
        elif isFile: # 如果是file命令，生成answer
            isFile = False
            if current_file_text:
                response_text = ""

                for chunk in generate_answer(current_file_text, messages[-1]['content']):
                    response_text += chunk
                    history[-1][1] = response_text
                    yield history
            else:
                response_text = "请先上传一个文件"
            messages.append({"role": "assistant", "content": response_text})
        elif isAudio: # 检验是否是音频文件
            isAudio = False
            for chunk in chat(messages):
                response_text += chunk
            audio_path = text2audio(response_text)
            if audio_path:
                history[-1][1] = (audio_path, )
                yield history
        elif isImageGenerate:
            isImageGenerate = False
            text = messages[-1]["content"]
            content = text[len("/image "):]
            image_url = image_generate(content)
            if image_url:
                history[-1][1] = (image_url, )
                messages.append({"role": "assistant", "content": f"{image_url}"})
                yield history
        elif isFunction:
            isFunction = False
            messages_function = []
            messages_function.append(messages[-1])
            function_url = function_calling(messages_function)
            if function_url:
                history[-1][1] = function_url
                messages.append({"role": "assistant", "content": f"{function_url}"})
                yield history
        # 检查是否是图像识别
        elif isImage:
            isImage = False
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
    except:
        messages, current_file_text, isTxt, isFile, isImage, image, isAudio, isImageGenerate = messages, False, False, False, False, False, False, False


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