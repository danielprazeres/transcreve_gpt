import os
import streamlit as st
from pydub import AudioSegment
from openai import OpenAI

st.title('Transcritor de Áudio para Texto')

api_key = st.text_input('Insira sua chave da OpenAI', type='password')

uploaded_file = st.file_uploader('Envie o arquivo de áudio (.opus, .mp3, .wav)', type=['opus', 'mp3', 'wav'])

language = st.selectbox('Selecione o idioma do áudio', ['Português', 'Espanhol', 'Inglês'])
lang_code = {'Português': 'pt', 'Espanhol': 'es', 'Inglês': 'en'}[language]

if st.button('Processar Áudio') and uploaded_file and api_key:
    openai = OpenAI(api_key=api_key)

    input_file = uploaded_file.name
    with open(input_file, 'wb') as f:
        f.write(uploaded_file.read())

    file_extension = os.path.splitext(input_file)[1].lower()
    if file_extension != '.wav':
        audio = AudioSegment.from_file(input_file)
        input_file = 'converted_audio.wav'
        audio.export(input_file, format='wav')

    audio = AudioSegment.from_file(input_file, format='wav')
    chunks = [audio[i:i + 30000] for i in range(0, len(audio), 30000)]
    chunk_files = []
    for idx, chunk in enumerate(chunks):
        chunk_file = f'chunk_{idx}.wav'
        chunk.export(chunk_file, format='wav')
        chunk_files.append(chunk_file)

    full_transcription = ''
    for chunk_file in chunk_files:
        with open(chunk_file, 'rb') as audio_file:
            transcription = openai.audio.transcriptions.create(
                model='whisper-1',
                file=audio_file,
                response_format='text',
                language=lang_code
            )
            full_transcription += transcription + ' '
        os.remove(chunk_file)

    output_file = f'transcripted_{os.path.splitext(uploaded_file.name)[0]}.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcription.strip())

    with open(output_file, 'rb') as f:
        st.download_button(
            label='Baixar Transcrição',
            data=f,
            file_name=output_file,
            mime='text/plain'
        )

    os.remove(input_file)
    os.remove(output_file)
