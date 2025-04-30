from flask import Flask, render_template, request, jsonify
import language_tool_python
import re

app = Flask(__name__)
tool = language_tool_python.LanguageTool('en-US')

# List of common filler words
filler_words_list = [
    "uh", "um","ss", "like", "you know", "I mean", "actually", "basically", "so", "well", "literally",
    "right", "kinda", "sorta", "I guess", "anyway", "to be honest", "just", "honestly", "seriously",
    "in a way", "you see", "in fact", "the thing is", "well, you know", "let me think", "hold on",
    "I don't know", "let's see", "whatever", "as I was saying", "you know what I mean", "you know what I'm saying",
    "I'm like", "I was like", "actually, like", "basically, like", "so, um", "I don't know, like", "I mean, like",
    "well, like", "I guess so", "to be fair", "well, actually", "I mean, seriously", "just saying", "no offense",
    "if that makes sense", "like I said", "I'm not sure", "it's like", "maybe", "it’s just", "pretty much",
    "I would say", "I'm thinking", "if you think about it"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    transcript = data.get('transcript', '')

    # Count pauses marked as [pause_3s] in transcript
    pause_count = transcript.lower().count('[pause_3s]')

    # Detect filler words used in the transcript
    filler_used = []
    filler_counts = {}
    lower_transcript = transcript.lower()
    for word in set(filler_words_list):
        count = len(re.findall(r'\b' + re.escape(word) + r'\b', lower_transcript))
        if count > 0:
            filler_used.append(word)
            filler_counts[word] = count

    total_fillers = sum(filler_counts.values())

    # LanguageTool: filter grammar-only mistakes (exclude spelling mistakes)
    matches = tool.check(transcript)
    grammar_issues = []
    for match in matches:
        if "Spelling mistake" not in match.message and match.ruleId != "MORFOLOGIK_RULE_EN_US":
            grammar_issues.append({
                "message": match.message,
                "sentence": match.context
            })

    # Confidence score calculation
    confidence = round(1 - (len(grammar_issues) + total_fillers + pause_count) / max(len(transcript.split()), 1), 2)

    # Sentence structure
    sentence_count = transcript.count('.') + transcript.count('!') + transcript.count('?')
    avg_sentence_length = len(transcript.split()) / (sentence_count or 1)
    structure = "Well-structured" if avg_sentence_length <= 20 else "Too long; consider shorter sentences."

    # Fluency classification
    if len(grammar_issues) <= 2 and total_fillers <= 2:
        fluency = "Excellent"
    elif len(grammar_issues) <= 5 and total_fillers <= 5:
        fluency = "Moderate"
    else:
        fluency = "Needs Improvement"

    result = {
        "transcript": transcript,
        "filler_words_found": filler_used,
        "filler_counts": filler_counts,
        "total_fillers": total_fillers,
        "grammar_issues": grammar_issues,
        "pause_count": pause_count,
        "structure_feedback": structure,
        "fluency": fluency,
        "confidence": f"{confidence * 100}%"
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
