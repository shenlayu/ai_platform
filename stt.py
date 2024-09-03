import requests

def audio2text(file_path):
    url = "http://localhost:8080/v1/audio/transcriptions"  # LocalAI endpoint

    files = {
        'file': (file_path, open(file_path, 'rb'), 'audio/wav'),  # Ensure the file is opened correctly
        'model': (None, 'whisper-1')  # Model name should be sent as a string, not a file
    }
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        # Parse the JSON response to get the transcribed text
        return response.json().get('text')
    else:
        print(f"Failed to transcribe. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    content = audio2text('sun-wukong.wav')
    

# curl http://localhost:8080/v1/audio/transcriptions -H "Content-Type: multipart/form-data" -F file="@sun-wukong.wav" -F model="whisper-1"