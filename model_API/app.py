from flask import Flask, request, jsonify
from model.vectorization import vector_rec
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# To make converted dictionary to JSON not automatically ordered based on keys
app.json.sort_keys = False

@app.route('/', methods=['POST'])
def vector_recommendation():
    # Ini diubah jadi integer dulu karena di db lokal ID nya di-set integer, bukan string
    user_id = int(request.form['user_id'])
    rec = vector_rec(user_id)
    return jsonify(rec)

if __name__ == '__main__':
    app.run()
