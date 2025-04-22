let recognition;
let isRecording = false;
let finalTranscript = "";

function startRecording() {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Speech recognition not supported.');
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (event) {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interim += transcript;
            }
        }
        document.getElementById('transcription').innerHTML = finalTranscript + '<i>' + interim + '</i>';
    };

    recognition.onaudiostart = () => {
        console.log("Microphone is picking up sound");
        document.getElementById('micStatus').innerText = "🎙️ Microphone is picking up sound";
    };

    recognition.onaudioend = () => {
        console.log("Microphone stopped");
        document.getElementById('micStatus').innerText = "⛔ Microphone is not hearing sound";
    };

    recognition.onerror = (e) => {
        console.error("Error:", e.error);
    };

    recognition.onend = () => {
        console.log("Recording stopped");
        analyzeTranscript(finalTranscript); // Call backend
    };

    finalTranscript = "";  // reset on new start
    recognition.start();
    isRecording = true;
    console.log("Recording started...");
}

function stopRecording() {
    if (recognition && isRecording) {
        recognition.stop();
        isRecording = false;
    }
}

function analyzeTranscript(text) {
    fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript: text })
    })
    .then(response => response.json())
    .then(data => {
        const feedback = `
            <strong>Original:</strong> ${data.original_transcript}<br>
            <strong>Total Filler Words:</strong> ${data.total_fillers}<br>
            <strong>Details:</strong> ${JSON.stringify(data.filler_counts)}<br>
            <strong>Feedback:</strong> ${data.feedback}
        `;
        document.getElementById('feedback').innerHTML = feedback;
    })
    .catch(err => console.error("Error:", err));
}
