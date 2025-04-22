from disfluency_detector import detect_disfluencies

text = "I I think we should um go to the store you know"
results = detect_disfluencies(text)

print("Token\t\tLabel")
for token, label in results:
    print(f"{token}\t\t{label}")
