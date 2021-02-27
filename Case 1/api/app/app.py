import os
from pathlib import Path
import numpy as np
from flask import Flask, request, jsonify, render_template
from joblib import load

PROJECT_ROOT = Path(os.path.abspath('')).resolve()

app = Flask(__name__)  # Initialize the flask App
model = load(os.path.join(PROJECT_ROOT, 'analysis', 'best_decision_tree22.joblib'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = list(request.form.values())[0].split(',')
    final_features = np.array(int_features).reshape(1, -1)
    prediction = model.predict(final_features)[0]

    return render_template('index.html', prediction_text='The customer is belonged to cluster {}.'.format(prediction))

if __name__ == "__main__":
    app.run(debug=True)