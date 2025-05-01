from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Flask Server!',
        'status': 'success'
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy'
    })

@app.route('/start_simulation', methods=['GET'])
def start_simulation():
    """
    Implement the logic to start the simulation
    """
    return jsonify({
        'status': 'simulation started'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)