import os
import streamlit as st
from pydub import AudioSegment
from openai import OpenAI

# Configurar o layout do Streamlit
st.title('Transcritor de Áudio para Texto')

# Entrada para a chave da API da OpenAI
api_key = st.text_input('Insira sua chave da OpenAI', type='password')

# Upload do arquivo de áudio
uploaded_file = st.file_uploader('Envie o arquivo de áudio (.opus, .mp3, .wav)', type=['opus', 'mp3', 'wav'])

# Seleção do idioma
language = st.selectbox('Selecione o idioma do áudio', ['Português', 'Espanhol', 'Inglês'])
lang_code = {'Português': 'pt', 'Espanhol': 'es', 'Inglês': 'en'}[language]

# Botão para processar o áudio
if st.button('Processar Áudio') and uploaded_file and api_key:
    # Configurar a API da OpenAI
    openai = OpenAI(api_key=api_key)

    # Salvar o arquivo enviado localmente de forma segura
    input_file = f'temp_{uploaded_file.name}'
    with open(input_file, 'wb') as f:
        f.write(uploaded_file.read())

    # Converter para .wav, se necessário
    file_extension = os.path.splitext(input_file)[1].lower()
    if file_extension != '.wav':
        audio = AudioSegment.from_file(input_file)
        input_file = 'converted_audio.wav'
        audio.export(input_file, format='wav')

    # Dividir o áudio em pedaços menores (30 segundos)
    audio = AudioSegment.from_file(input_file, format='wav')
    chunks = [audio[i:i + 30000] for i in range(0, len(audio), 30000)]
    chunk_files = []
    for idx, chunk in enumerate(chunks):
        chunk_file = f'chunk_{idx}.wav'
        chunk.export(chunk_file, format='wav')
        chunk_files.append(chunk_file)

    # Transcrever cada pedaço e concatenar o resultado
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

    # Nome do arquivo de saída
    output_file = f'transcripted_{os.path.splitext(uploaded_file.name)[0]}.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcription.strip())

    # Exibir a opção para download
    with open(output_file, 'rb') as f:
        st.download_button(
            label='Baixar Transcrição',
            data=f,
            file_name=output_file,
            mime='text/plain'
        )

    # Limpeza dos arquivos temporários
    os.remove(input_file)
    os.remove(output_file)
