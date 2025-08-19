from django.shortcuts import render
import os

# Create your views here.
def home(request):
    #home page for navigation of old and new comparison
    return render(request, 'realtime_comparator/home.html')

def realtime_view(request):
    #realtime processing of audio 
    context = {'DEEPGRAM_API_KEY': os.getenv('DEEPGRAM_API_KEY')}
    return render(request, 'realtime_comparator/realtime.html', context)

def future_view(request):
    #renders for future functionality of faster-whisper/whisperx
    return render(request, 'realtime_comparator/future.html')