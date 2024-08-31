import openai

def chat(messages):
    openai.api_key = "your_api_key"
    openai.api_base = "http://localhost:8080/v1"
    
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
    
    # return response['choices'][0]['message']['content']