from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"message": "Test working"})

@app.route('/test-post', methods=['POST'])
def test_post():
    return jsonify({"message": "POST working", "data": request.json})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)