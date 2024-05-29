from gradio_client import Client, file
from transformers import pipeline
import streamlit as st
import random
import string
import requests
import os
import io
from dotenv import load_dotenv
from groq import Groq
import tempfile

load_dotenv()
groq_api = os.getenv('GROQ_API')
hf_token = os.getenv('HF_TOKEN')

groq_client = Groq(
    api_key=groq_api,
)

headers = {"Authorization": f"Bearer {hf_token}"}
limit_of_tokens = round(240*4.26)
#maximum of tokens (minus the prompt) times the approximate char value of each token
high_demand_warning = "Los servidores tienen alta demanda, espere un poco e intente de nuevo."

@st.cache_resource(show_spinner = False)
def load_whisper_client():
    return Client("https://sanchit-gandhi-whisper-jax.hf.space/")

#whisper_client = load_whisper_client()

def reduce(text): #removes a lot of unnecesary spaces
    return text.replace("\n", "").replace("  ", " ")

#if the key is the same, it'll return the cached value
#at most it saves values for 1 hour (3600s) and 100 at a time
@st.cache_resource(ttl = 3600, max_entries = 100, show_spinner = False)
def transcribe_audio(audio_path, key, task="transcribe", return_timestamps=False):
    #try:
    #    #call API (works on demand, sometimes it doesn't transcribe)
    #    api = whisper_client.submit(
    #        audio_path,
    #        task,
    #        return_timestamps,
    #        api_name="/predict_1",
    #    )
    #
    #    transcription, _ = api.result()
    #    return reduce(transcription)
    #
    #except Exception as e:
    #    return high_demand_warning

    pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
    return pipe(audio_path)['text']
    
def audio_intake(mic, format):
    rec = mic.export().read()
    st.audio(rec)
    with tempfile.NamedTemporaryFile(suffix=format, delete=False) as temp_audio:
        temp_audio.write(rec)
        temp_audio.seek(0)
    return temp_audio.name

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    # Includes uppercase letters, lowercase letters, and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def query(payload, API_URL, headers):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def to_chat_template(text): #a template from google devs to make questions to gemma
    return f"""<bos><start_of_turn>user
{text}<end_of_turn>
<start_of_turn>model"""

def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

def init_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def groq_request(instruct, prompt, model, history = True):
    if history:
        stream = groq_client.chat.completions.create(
        messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
                ],
        model = model,
        temperature = .35,
        max_tokens = 1024,
        top_p = .75,
        stream=True,)
        response = st.write_stream(parse_groq_stream(stream))
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:
        stream = groq_client.chat.completions.create(
        messages = [
        {
                "role": "system",
                "content": instruct,
            },
        {
                "role": "user",
                "content": prompt,
            }
        ],
        model = model,
        temperature = .3,
        max_tokens = 1024,
        top_p = .7,
        stream=True,)
        response = st.write_stream(parse_groq_stream(stream))


@st.cache_resource(show_spinner = False)
def generate(prompt, text, model, key, groq = False, history = True):
    if groq:
        response = groq_request(prompt, text, model, history)
        return response
    else:
        if text == high_demand_warning:
            return st.error(high_demand_warning)
        
        if len(text) > limit_of_tokens:
            limit_index = text.find(" ", limit_of_tokens)
            #finds the nearest space to the limit of tokens, so it doesn't break a word while slicing
            text = text[limit_index + 1:] 
            #get the last biggest possible fragment, we'll supose that the last parts 
            # of the conversation are the most imporant
        full_query = to_chat_template(prompt + text)
        print(full_query)

        API_URL_summarize = f"https://api-inference.huggingface.co/models/{model}"

        data = query({
        "inputs": full_query,

        "parameters" : {
        "return_full_text" : False}, #returns the generated text without the input

        "options" : {
        "wait_for_model" : True} #if on queue due to high demand or slowdown
        }, 
        API_URL_summarize, headers)
        
        print(data)
        result = data[0]['generated_text']
        return result
