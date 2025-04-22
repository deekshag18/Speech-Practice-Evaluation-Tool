from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

def detect_disfluencies(text):
    model_name = "pszemraj/bertkilo-disfluency-detection"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=2)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    labels = predictions[0].tolist()

    result = []
    for token, label in zip(tokens, labels):
        if token not in tokenizer.all_special_tokens:
            result.append((token, 'Disfluent' if label == 1 else 'Fluent'))

    return result
