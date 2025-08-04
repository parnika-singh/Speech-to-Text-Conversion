from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import whisper
import os
import uuid
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import asyncio

# Load the Whisper model
#use medium model for hindi
whisper_model = whisper.load_model("base")

# Deepgram API key
DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY', 'your_api_key_here')

def index(request):
    return render(request, 'comparator/index.html')

@csrf_exempt
def compare_audio(request):
    if request.method == 'POST':
        try:
            if 'audio' not in request.FILES:
                return JsonResponse({'error': 'No audio file provided'}, status=400)
                
            audio_file = request.FILES['audio']
            print(f"Audio file received: {audio_file.name}, size: {audio_file.size}")
            
            # Save with original extension
            file_ext = os.path.splitext(audio_file.name)[1]
            temp_filename = os.path.join(os.getcwd(), f"temp_audio_{uuid.uuid4()}{file_ext}")
            print(f"Temp filename: {temp_filename}")
            
            # Save audio file
            with open(temp_filename, "wb+") as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            print(f"File saved successfully: {os.path.exists(temp_filename)}")
            
            # Whisper Transcription
            try:
                print("Starting Whisper transcription...")
                import librosa
                import numpy as np
                import time
                
                # Load audio data directly
                audio_data, sr = librosa.load(temp_filename, sr=16000)
                
                whisper_start_time = time.time()
                #for hindi use
                #whisper_result = whisper_model.transcribe(audio_data, language='hi')
                #for auto detection but can confuse similar language
                whisper_result = whisper_model.transcribe(audio_data)
                whisper_end_time = time.time()
                
                whisper_text = whisper_result['text']
                whisper_total_time = whisper_end_time - whisper_start_time
                whisper_first_token_time = whisper_total_time  # For Whisper, first token = total time
                
                print(f"Whisper result: {whisper_text[:50]}...")
                print(f"Whisper timing: {whisper_total_time:.2f}s")
            except Exception as whisper_error:
                print(f"Whisper error: {whisper_error}")
                whisper_text = f"Whisper error: {str(whisper_error)}"
                whisper_total_time = 0
                whisper_first_token_time = 0
            
            # Deepgram Transcription
            try:
                print("Starting Deepgram transcription...")
                deepgram_client = DeepgramClient(DEEPGRAM_API_KEY)
                
                with open(temp_filename, "rb") as audio:
                    buffer_data = audio.read()

                payload: FileSource = {"buffer": buffer_data}
                #for hindi use
                #options = PrerecordedOptions(model="nova-3", language="hi", smart_format=True)
                #for auto detection 
                options = PrerecordedOptions(model="nova-3", smart_format=True)

                deepgram_start_time = time.time()
                response = deepgram_client.listen.prerecorded.v("1").transcribe_file(payload, options)
                deepgram_end_time = time.time()
                
                deepgram_text = response.results.channels[0].alternatives[0].transcript
                deepgram_total_time = deepgram_end_time - deepgram_start_time
                deepgram_first_token_time = deepgram_total_time  # For batch processing, first token = total time
                
                print(f"Deepgram result: {deepgram_text[:50]}...")
                print(f"Deepgram timing: {deepgram_total_time:.2f}s")
            except Exception as deepgram_error:
                print(f"Deepgram error: {deepgram_error}")
                deepgram_text = f"Deepgram error: {str(deepgram_error)}"
                deepgram_total_time = 0
                deepgram_first_token_time = 0
            
            # Clean up
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

            return JsonResponse({
                'whisper': {
                    'text': whisper_text,
                    'total_time': round(whisper_total_time, 2),
                    'first_token_time': round(whisper_first_token_time, 2),
                },
                'deepgram': {
                    'text': deepgram_text,
                    'total_time': round(deepgram_total_time, 2),
                    'first_token_time': round(deepgram_first_token_time, 2),
                }
            })
            
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': f'General error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)