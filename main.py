import sys
from threading import Thread
from flask import Flask, jsonify

from Machine import MixingMachine
import Factory
import Slurry

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
    slurry = Slurry(200)
    factory = Factory()
    anode_mixing_machine = MixingMachine(slurry)
    factory.add_machine(anode_mixing_machine) # the mixing machine should already be in the factory
    simulation_thread = Thread(target=anode_mixing_machine.start_simulation)
    simulation_thread.start()
    return jsonify({
        'status': 'simulation started'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)