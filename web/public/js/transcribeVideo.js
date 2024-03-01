export function transcribeVideo(filePath) {
    const requestData = {
        path: filePath
    };

    fetch('http://127.0.0.1:5000/transcribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const transcriptModal = document.getElementById('transcriptModal');
            const transcriptText = data.text;

            const transcriptContent = transcriptModal.querySelector('#text-inside');
            transcriptContent.textContent = transcriptText;

            const containerText = document.getElementById('container-text');
            containerText.style.display = 'block';
            containerText.classList.add('fadeIn');

            setTimeout(() => {
                containerText.classList.remove('fadeIn');
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
