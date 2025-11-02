from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"message": "Test working"})

@app.route('/test-post', methods=['POST'])
def test_post():
    print("Test POST route called")
    print("Request data:", request.data)
    print("Request JSON:", request.json)
    return jsonify({"message": "POST working", "data": request.json})

@app.route('/test-db-insert', methods=['POST'])
def test_db_insert():
    print("Test DB insert route called")
    return jsonify({"message": "DB insert test working"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)