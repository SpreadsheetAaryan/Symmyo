from flask import Flask, render_template
import matplotlib.pyplot as plt
import asyncio

app = Flask(__name__)

@app.route('/')
def index(methods=['GET']):
    return render_template('../templates/index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)