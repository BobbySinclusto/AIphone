from flask import Flask, request

app = Flask(__name__)

@app.route("/get_prompt")
def get_prompt():
    initial_prompt = request.args.get('prompt', '')
    return {'prompt': 'this is definitely random'}

