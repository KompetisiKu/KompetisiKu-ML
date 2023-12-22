from flask import Flask, request, jsonify
from model.vectorization import vector_rec
import os

app = Flask(__name__)

# To make converted dictionary to JSON not automatically ordered based on keys
app.json.sort_keys = False


@app.route('/', methods=['POST'])
def vector_recommendation():
    user_id = request.form['user_id']
    rec = vector_rec(user_id)
    if isinstance(rec, dict):
        return jsonify(rec)
    else:
        return rec


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5008)))