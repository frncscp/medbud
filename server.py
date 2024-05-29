import streamlit as st
from audiorecorder import audiorecorder
from src.model.speech_to_text import *
import os
from datetime import datetime
import tempfile

st.set_page_config(
    page_title = 'Doctor Buddy',
    page_icon = "👨‍⚕️"
)

st.title("Doctor Buddy")
st.caption("Transcriptor de citas médicas")
st.divider()

format_ = ".mp3"
file_path = f'/app/temp.{format}'
file_path_fixed = r"/app/test-files/consulta_artificial.wav"
modelo = "google/gemma-1.1-7b-it"
groq_model = "llama3-8b-8192"
prompt = "Resume esta cita médica: "
use_groq = True

#prompt = """Genera un resumen cronológico detallado de la última cita médica, 
#incluyendo los detalles de la consulta, el diagnóstico y las recomendaciones
#de tratamiento proporcionadas por el médico: """

formato_medico = '''
1. Datos de identificación como número de historia clínica, nombre, nacionalidad, fecha de nacimiento, teléfono, ocupación, estado civil, etc:
2. Motivo de la consulta, citando textualmente al paciente entre comillas (siempre y cuando exista un motivo, de lo contrario, coloca "No Aplica."):
3. Antecedentes de enfermedad actual:
4. Antecedentes de interés como hábitos tóxicos, fisiológicos, enfermedades de infancia, heredofamiliares, etc:
5. Anamnesis y exploración física:
6. Diagnóstico:
7. Órdenes médicas:
8. Tratamiento farmacológico:
9. Plan médico y planificación de cuidados:'''

#groq_instruct = 'Genera un resumen de una cita médica en un solo pá como aparecería en la historia clínica de un paciente.'

summary_instruct = f''''
Genera un formato detallado de la conversación teniendo en cuenta las siguientes condiciones:

- Todo lo que aparezca en el formato debe estar en el prompt dado por el usuario.
- Si no hay información sobre uno de los puntos, coloca "No Aplica.", incluido en el motivo de la consulta.
- Si el audio que se entrega no es una conversación con los puntos incluidos, devuelve el formato co todos los puntos solo con la respuesta "No Aplica."

Este es el formato con los puntos:
{formato_medico}'''

answer_instruct = '''
Responde a la pregunta del usuario en base al historial de conversación, 
coloca entre comillas la parte de la conversación que estás usando para responder, de esta forma:

<respuesta>
<"cita de la conversación entre comillas">

No puedes generar nada que no esté en el historial de conversación. 
Las preguntas del usuario solo podran ser respondidas con el historial de conversación. 
No te dirijas en primera persona.'''

def main():
    init_chat_history()
    # Specify the length of the key, it will be randomnized and stored in the session state
    key_lenght = 10 #it'll be useful to know if a given audio has already been processed 

    if not st.session_state.get('key'):
        st.session_state['key'] = None #instantiate
    
    mic = audiorecorder(start_prompt="Empezar Grabación", 
    stop_prompt="Parar Grabación", pause_prompt="Pausar Grabación", key=None)
    
    if st.button("Transcribir"):
        st.session_state['key'] = generate_random_string(key_lenght) #create new key

    if len(mic) > 0:
        conv = audio_intake(mic, format_) 
        with st.spinner("Transcribiendo el audio..."):
            raw_text = transcribe_audio(
                conv, st.session_state['key'], 'transcribe', False)
            print(raw_text)
            #False is for not showing timestamps on the transcription
            st.session_state.messages.append({"role": "system", "content": f'La fecha de hoy es {datetime.now()}'})          
            st.session_state.messages.append({"role": "system", "content": 'Usa esta conversación para responder las preguntas que se te van a hacer: ' + raw_text})

        with st.spinner("Generando texto..."):
            if use_groq:
                with st.chat_message("assistant", avatar = "👨‍⚕️"): 
                    generate(summary_instruct, raw_text, groq_model, st.session_state["key"], groq = True, history = False)
                prompt = st.chat_input("Pregunta algo sobre la cita: ")
                if prompt:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    with st.chat_message("assistant", avatar = "👨‍⚕️"):
                        answer = generate(answer_instruct, prompt, groq_model, st.session_state['key'], groq = True)
            else:
                summary_text = generate(prompt, raw_text, modelo, st.session_state["key"])
                st.markdown(summary_text)

if __name__ == "__main__":
    main()
