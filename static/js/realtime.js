document.addEventListener('DOMContentLoaded', () => {
    const micButton = document.getElementById('micButton');
    const statusDiv = document.getElementById('status');
    const openaiTextElem = document.getElementById('openaiText');
    const deepgramTextElem = document.getElementById('deepgramText');

    let mediaRecorder;
    let deepgramSocket;

    micButton.addEventListener('click', toggleMic);

    async function toggleMic() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            //stop recording
            mediaRecorder.stop();
            micButton.textContent = 'Start Mic';
            micButton.classList.remove('recording');
            statusDiv.textContent = 'Mic stopped. Click to start again.';
        } else {
            //start recording
            try {
                if (!DEEPGRAM_API_KEY || DEEPGRAM_API_KEY === '') {
                    statusDiv.textContent = 'Error: Deepgram API key not configured';
                    return;
                }
                
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        sampleRate: 16000,
                        channelCount: 1,
                        echoCancellation: true
                    } 
                });
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

                // --- setting up WebSocket for Deepgram ---
                console.log('Connecting to Deepgram with API key:', DEEPGRAM_API_KEY.substring(0, 10) + '...');
                const deepgramUrl = `wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&smart_format=true`;
                deepgramSocket = new WebSocket(deepgramUrl, ['token', DEEPGRAM_API_KEY]);

                deepgramSocket.onopen = () => {
                    console.log('Deepgram WebSocket connected successfully');
                    
                    //send keepalive message as websocket connection is closing abruptly
                    const keepAlive = JSON.stringify({"type": "KeepAlive"});
                    deepgramSocket.send(keepAlive);
                    
                    mediaRecorder.addEventListener('dataavailable', event => {
                        console.log('Sending audio chunk to Deepgram, size:', event.data.size);
                        if (event.data.size > 0 && deepgramSocket.readyState === WebSocket.OPEN) {
                            deepgramSocket.send(event.data);
                        }
                    });
                };

                deepgramSocket.onmessage = (event) => {
                    console.log('Deepgram response:', event.data);
                    const data = JSON.parse(event.data);
                    console.log('Parsed data:', data);
                    if (data.channel && data.channel.alternatives[0].transcript) {
                        const transcript = data.channel.alternatives[0].transcript;
                        console.log('Transcript:', transcript, 'Is final:', data.is_final);
                        if (transcript && data.is_final) {
                             deepgramTextElem.textContent += transcript + ' ';
                        }
                    }
                };

                deepgramSocket.onerror = (error) => {
                    console.error('Deepgram WebSocket Error:', error);
                    statusDiv.textContent = 'Deepgram connection failed. Check API key.';
                };
                
                deepgramSocket.onclose = (event) => {
                    console.log('Deepgram connection closed. Code:', event.code, 'Reason:', event.reason);
                };

                // --- OpenAI disabled for debugging ---
                openaiTextElem.textContent = 'OpenAI disabled for debugging';

                //start the recording process
                mediaRecorder.start(500); //sending data every 500ms
                micButton.textContent = 'Stop Mic';
                micButton.classList.add('recording');
                statusDiv.textContent = 'Recording... (Deepgram only)'; //for now in testing

                mediaRecorder.onstop = () => {
                    if (deepgramSocket) deepgramSocket.close();
                };

            } catch (error) {
                console.error('Error accessing microphone:', error);
                statusDiv.textContent = 'Error: Could not access microphone.';
            }
        }
    }
});