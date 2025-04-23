from flask import Flask, render_template, request, jsonify
import language_tool_python
import re

app = Flask(__name__)
tool = language_tool_python.LanguageTool('en-US')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    transcript = data.get('transcript', '')

    # LanguageTool for grammar feedback
    matches = tool.check(transcript)
    grammar_feedback = [{"message": m.message, "sentence": m.context} for m in matches]

    # Filler word detection
    filler_words_list = ['um', 'uh', 'like', 'you know', 'so']
    filler_counts = {word: transcript.lower().count(word) for word in filler_words_list}
    total_fillers = sum(filler_counts.values())

    # Simulated confidence score (could be enhanced with ML later)
    confidence = round(1 - (len(matches) + total_fillers) / max(len(transcript.split()), 1), 2)

    # Structure feedback (simple rules for example)
    sentence_count = transcript.count('.') + transcript.count('!')
    avg_sentence_length = len(transcript.split()) / (sentence_count or 1)
    structure = "Well-structured" if avg_sentence_length <= 20 else "Too long; consider shorter sentences."

    # Fluency (based on errors + fillers)
    if len(matches) <= 2 and total_fillers <= 2:
        fluency = "Excellent"
    elif len(matches) <= 5 and total_fillers <= 5:
        fluency = "Moderate"
    else:
        fluency = "Needs Improvement"

    # Simulated pause count (you can improve this with audio timestamps later)
    simulated_pauses = transcript.count('...')  # optional in UI

    result = {
        "transcript": transcript,
        "grammar_feedback": grammar_feedback,
        "filler_counts": filler_counts,
        "total_fillers": total_fillers,
        "structure_feedback": structure,
        "fluency": fluency,
        "confidence": f"{confidence * 100}%",
        "pauses": simulated_pauses
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
