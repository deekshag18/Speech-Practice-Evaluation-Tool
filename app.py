from flask import Flask, request, jsonify, render_template
from transformers import pipeline

app = Flask(__name__)

# Example route to render the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Filler words example API
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    transcript = data.get("transcript", "")
    
    filler_words = ["um", "like", "uh", "you know", "actually", "literally"]
    detected_fillers = [word for word in filler_words if word in transcript.lower()]

    return jsonify({
        "transcript": transcript,
        "filler_words_detected": detected_fillers,
        "filler_count": len(detected_fillers),
        "feedback": f"You used {len(detected_fillers)} filler word(s): {', '.join(detected_fillers)}"
    })

if __name__ == '__main__':
    app.run(debug=True)
