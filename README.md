# Speech-to-Text-Conversion
Django application with javascript to show speech to text conversion using whisper and deepgram models
- comparator  app for comparison between whisper (base) model and deepgram (nova-3 model)
 1. observation: for english deepgram performs better but for hindi whisper (medium) model performs better
 2. Test asr 1, Test asr 2, Test asr 3 (hindi) audio used for comparison

- realtime_comparator app for comparison using realtime processing of audio using 
  1. OpenAI Realtime API using whisper-1 model instead of gpt-4o as it is complicated to use.
  2. Deepgram realtime capabilities