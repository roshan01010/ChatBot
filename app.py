from flask import Flask, request, render_template, jsonify
import json
from difflib import get_close_matches
from typing import Optional, List

app = Flask(__name__)

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: List[str]) -> Optional[str]:
    matches: List[str] = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> Optional[str]:
    for q in knowledge_base["questions"]:
        if q["question"].strip().lower() == question.strip().lower():  # Compare ignoring case and whitespace
            return q["answer"]
    return None  # Return None if no match found

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            knowledge_base = load_knowledge_base('knowledge_base.json')
            best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

            if best_match:
                answer = get_answer_for_question(best_match, knowledge_base)
                if answer:
                    return jsonify({'response': answer})
                else:
                    return jsonify({'response': "I don’t know the answer. Can you teach me?", 'learn': True})
            else:
                return jsonify({'response': "I don’t know the answer. Can you teach me?", 'learn': True})
    return render_template('index.html')

@app.route('/learn', methods=['POST'])
def learn():
    user_question = request.form.get('question')
    user_answer = request.form.get('answer')
    if user_question and user_answer:
        knowledge_base = load_knowledge_base('knowledge_base.json')
        if not any(q["question"].strip().lower() == user_question.strip().lower() for q in knowledge_base["questions"]):
            knowledge_base["questions"].append({"question": user_question, "answer": user_answer})
            save_knowledge_base('knowledge_base.json', knowledge_base)
            return jsonify({'response': "Thank you! I learned a new response!"})
        return jsonify({'response': "I already know the answer to that question."})
    return jsonify({'response': "Failed to learn new response."})

if __name__ == '__main__':
    app.run(debug=True)
