document.addEventListener('DOMContentLoaded', () => {
    // File upload functionality
    const uploadButton = document.getElementById('uploadButton');
    const audioFileInput = document.getElementById('audioFile');

    if (uploadButton && audioFileInput) {
        uploadButton.addEventListener('click', () => {
            console.log('Upload button clicked');
            const file = audioFileInput.files[0];
            console.log('Selected file:', file);
            if (file) {
                console.log('File found, sending to server');
                const startTime = new Date();
                const stopTime = new Date();
                sendAudioToServer(file, startTime, stopTime);
            } else {
                console.log('No file selected');
                alert('Please select an audio file first.');
            }
        });

        async function sendAudioToServer(audioFile, startTime, stopTime) {
            console.log('Sending audio to server:', audioFile.name);
            const formData = new FormData();
            formData.append('audio', audioFile);
            formData.append('start_time', startTime.toISOString());
            formData.append('stop_time', stopTime.toISOString());

            try {
                const response = await fetch('/compare/', {
                    method: 'POST',
                    body: formData,
                });
                console.log('Response status:', response.status);
                const data = await response.json();
                console.log('Response data:', data);
                updateResults(data);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function updateResults(data) {
            document.getElementById('whisperText').textContent = data.whisper.text;
            document.getElementById('whisperFirstTokenTime').textContent = `${data.whisper.first_token_time.toFixed(2)}s`;
            document.getElementById('whisperTotalTime').textContent = `${data.whisper.total_time.toFixed(2)}s`;

            document.getElementById('deepgramText').textContent = data.deepgram.text;
            document.getElementById('deepgramFirstTokenTime').textContent = `${data.deepgram.first_token_time.toFixed(2)}s`;
            document.getElementById('deepgramTotalTime').textContent = `${data.deepgram.total_time.toFixed(2)}s`;
        }
    } else {
        console.error('Upload button or file input not found');
    }
});