from flask import Flask, render_template, request, jsonify
import language_tool_python
import re

app = Flask(__name__)
tool = language_tool_python.LanguageTool('en-US')

filler_words = [
    "uh", "um", "like", "you know", "I mean", "actually", "basically",
    "so", "well", "literally", "right", "kinda", "maybe", "just",
    "hmm", "let me see", "in fact", "to be honest", "sort of",
    "kind of", "I guess", "you see", "I suppose", "perhaps",
    "honestly", "to be frank", "not only that", "eventually", "to sum up",
    "as far as I know", "absolutely", "definitely", "the point is", "in the end",
    "what's more", "besides that", "moreover", "in addition", "so yeah"
]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    transcript = data.get('transcript', '')
    lower_transcript = transcript.lower()

    pause_count = lower_transcript.count('[pause_2s]')

    used_fillers = []
    filler_counts = {}
    for word in filler_words:
        count = len(re.findall(r'\b' + re.escape(word) + r'\b', lower_transcript))
        if count > 0:
            used_fillers.append(word)
            filler_counts[word] = count

    total_fillers = sum(filler_counts.values())

    matches = tool.check(transcript)
    grammar_issues = []
    for match in matches:
        if match.ruleId != "MORFOLOGIK_RULE_EN_US":
            grammar_issues.append({
                "message": match.message,
                "sentence": match.context
            })

    structure = "Well-structured" if len(transcript.split()) / (transcript.count('.') + 1) <= 20 else "Too long"
    fluency = "Excellent" if len(grammar_issues) <= 2 and total_fillers <= 2 else "Needs Improvement"
    confidence = round(1 - (len(grammar_issues) + total_fillers + pause_count) / max(len(transcript.split()), 1), 2)

    return jsonify({
        "transcript": transcript,
        "filler_words_found": used_fillers,
        "total_fillers": total_fillers,
        "pause_count": pause_count,
        "grammar_issues": grammar_issues,
        "structure_feedback": structure,
        "fluency": fluency,
        "confidence": f"{confidence * 100}%"
    })

if __name__ == '__main__':
    app.run(debug=True)
