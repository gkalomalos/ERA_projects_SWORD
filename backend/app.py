from flask import Flask, request, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configure CORS if needed
    CORS(app)

    # Setup your routes
    @app.route('/run-scenario', methods=['POST'])
    def run_scenario():
        data = request.json
        # Process data using Climada or other logic
        result = {'status': 'success', 'data': 'Processed data here'}
        return jsonify(result)

    return app

if __name__ == "__main__":
    # Only for running in local development
    app = create_app()
    app.run(debug=True)
