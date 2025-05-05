from fastapi import FastAPI
from supabase import create_client, Client
import speech_recognition as sr
import tempfile
import os
import requests
import time
import threading
# from gtts import gTTS
from schema import chatbot
from langchain.schema import HumanMessage, AIMessage
from get_chathistory import save_chat_to_redis, load_chat_from_redis, clear_chat_from_redis
from tts_func import run_tts_pipeline

app = FastAPI()

SUPABASE_URL = "https://gyqzrdottcgybgpefzuc.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXpyZG90dGNneWJncGVmenVjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczOTE3NzIwOCwiZXhwIjoyMDU0NzUzMjA4fQ.WHodxbuOLZgRc6GAkWHREpzDsQAkgmg-uT-ZJT2ZOaU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def poll_changes():
    while True:
        try:
            response = supabase.table('meisan').select('*').execute()
            if response.data:
                new_audio = response.data[0]['new_audio']
                clear_chat = response.data[0]['clear_chat']
                if new_audio == "yes":
                    print(f"Change detected! Triggering `/run`")
                    supabase.table('meisan').update({"new_audio": "no"}).eq("id", 1).execute()
                    requests.get("http://localhost:8000/run")
                if clear_chat == "yes":
                    print(f"Clearing Chat History! Triggering `/clear`")
                    supabase.table('meisan').update({"clear_chat": "no"}).eq("id", 1).execute()
                    requests.get("http://localhost:8000/clear")
        except Exception as e:
            print("Polling error:", e)
        time.sleep(6)

@app.on_event("startup")
def start_background_polling():
    thread = threading.Thread(target=poll_changes, daemon=True)
    thread.start()

@app.get("/")
def home():
    return {"message": "Polling service is running."}

@app.get("/clear")
def clear_chat():
    clear_chat_from_redis()
    return {"message": "Cleared chat history"}

@app.get("/run")
def run_audio_processing_pipeline():
    audio_url = supabase.storage.from_('audio-input').get_public_url('audio_input.wav')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        r = requests.get(audio_url)
        tmp_file.write(r.content)
        tmp_file_path = tmp_file.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(tmp_file_path) as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data, language="my-MM")
    except Exception as e:
        os.remove(tmp_file_path)
        recognized_text = "I don't understand the audio"
        return {"error": f"Transcription failed: {e}"}

    os.remove(tmp_file_path)

    chat_history = load_chat_from_redis()
    result = chatbot.invoke({'question': recognized_text, 'chat_history': chat_history})

    if result:
        chat_history.append(HumanMessage(content=recognized_text))
        chat_history.append(AIMessage(content=result['response']['answer']))
        save_chat_to_redis(chat_history)
    
    output_filename = "response_output.wav"
    # tts = gTTS(text=result['response']['answer'], lang='my', slow=False)
    run_tts_pipeline(text = result['response']['answer'])
    # output_filename = "response_output.wav"
    # tts.save(output_filename)

    try:
        with open(output_filename, 'rb') as f:
            upload_response = supabase.storage.from_("audio-input").update(
                file=f,
                path="test_output.wav",
                file_options={"cache-control": "3600", "upsert": "true"},
            )
        os.remove(output_filename)
        supabase.table('meisan').update({"response":"yes", "command": result['command']}).eq("id", 1).execute()
    except Exception as e:
        return {"error": f"Upload failed: {e}"}

    return {
        "status": "completed",
        "recognized_text": recognized_text,
        "response_text": result['response']['answer'],
        "command": result['command'],
        "supabase_upload": upload_response
    }
