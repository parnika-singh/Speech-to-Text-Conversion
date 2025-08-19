
import json
import asyncio
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import os

class RealtimeConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_buffer = b''
        self.chunk_count = 0

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, bytes_data):
        if not bytes_data:
            return
            
        self.audio_buffer += bytes_data
        self.chunk_count += 1
        
        # Process every 6 chunks (about 3 seconds of audio)
        if self.chunk_count >= 6:
            await self.process_audio_chunk()
            self.audio_buffer = b''
            self.chunk_count = 0
    
    async def process_audio_chunk(self):
        if len(self.audio_buffer) < 1024:  # Skip very small chunks
            return
            
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            await self.send(text_data=json.dumps({
                'source': 'openai',
                'error': 'OpenAI API key not configured'
            }))
            return
            
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {'Authorization': f'Bearer {api_key}'}

        data = aiohttp.FormData()
        data.add_field('file', self.audio_buffer, filename='audio.webm', content_type='audio/webm')
        data.add_field('model', 'whisper-1')
        data.add_field('response_format', 'json')

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        text = response_json.get('text', '').strip()
                        if text:
                            await self.send(text_data=json.dumps({
                                'source': 'openai',
                                'text': text
                            }))
                    else:
                        error_text = await response.text()
                        await self.send(text_data=json.dumps({
                            'source': 'openai',
                            'error': f"API Error: {response.status}"
                        }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'source': 'openai',
                'error': f"Connection error: {str(e)}"
            }))

