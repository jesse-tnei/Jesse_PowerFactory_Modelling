import os
import sys
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

# Add the parent directory to Python path to import framework modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)

# Global framework instance
framework_instance = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loadflow')
def loadflow():
    return render_template('loadflow.html')

@app.route('/EDCM')
def start_edcm():
    return render_template('edcm-dashboard.html')

@app.route('/api/initialize-engine', methods=['POST'])
def initialize_engine():
    """Initialize the selected engine (PowerFactory or IPSA)"""
    global framework_instance
    
    try:
        data = request.get_json()
        engine = data.get('engine', '').lower()
        
        if engine not in ['powerfactory', 'ipsa']:
            return jsonify({
                'success': False, 
                'message': 'Invalid engine. Must be "powerfactory" or "ipsa"'
            }), 400
        
        # Import and initialize framework if not already done
        if framework_instance is None:
            from FrameworkInitialiser import FrameworkInitialiser
            framework_instance = FrameworkInitialiser()
            
            # Initialize web interface only first
            if not framework_instance.webinitialized:
                framework_instance.initializeproduct(webinterfaceonly=True)
        
        # Initialize the backend with selected engine
        if not framework_instance.backendinitialized:
            result = framework_instance.initialize_backend(engine)
            
            if result:
                return jsonify({
                    'success': True,
                    'message': f'{engine.upper()} engine initialized successfully',
                    'engine': engine,
                    'status': framework_instance.get_framework_status()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Failed to initialize {engine.upper()} engine'
                }), 500
        else:
            return jsonify({
                'success': True,
                'message': f'{engine.upper()} engine already initialized',
                'engine': engine,
                'status': framework_instance.get_framework_status()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error initializing engine: {str(e)}'
        }), 500

@app.route('/api/framework-status', methods=['GET'])
def get_framework_status():
    """Get current framework initialization status"""
    global framework_instance
    
    if framework_instance is None:
        return jsonify({
            'webinitialized': False,
            'backendinitialized': False,
            'selected_engine': None
        })
    
    return jsonify(framework_instance.get_framework_status())

@app.route('/api/load-ipsa-file', methods=['POST'])
def load_ipsa_file():
    """Load IPSA file for analysis"""
    global framework_instance
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        if not file_path:
            return jsonify({
                'success': False,
                'message': 'File path is required'
            }), 400
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': 'File does not exist'
            }), 404
        
        # TODO: Implement actual IPSA file loading logic
        # For now, just simulate success
        return jsonify({
            'success': True,
            'message': 'IPSA file loaded successfully',
            'file_path': file_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading IPSA file: {str(e)}'
        }), 500

@app.route('/api/run-loadflow', methods=['POST'])
def run_loadflow():
    """Execute load flow analysis"""
    global framework_instance
    
    try:
        if framework_instance is None or not framework_instance.backendinitialized:
            return jsonify({
                'success': False,
                'message': 'Engine not initialized'
            }), 400
        
        data = request.get_json()
        engine = framework_instance.selected_engine
        
        # TODO: Implement actual load flow execution logic
        # This would call the appropriate engine's load flow method
        
        return jsonify({
            'success': True,
            'message': f'Load flow analysis completed using {engine.upper()}',
            'engine': engine,
            'results': {
                'analysis_type': 'load_flow',
                'timestamp': '2025-10-29T10:30:00Z',
                'status': 'completed'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error running load flow: {str(e)}'
        }), 500
def start_web_server(host='localhost', port=5000):
    """Start the Flask web server"""
    app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
    print("Completed running Flask app.")
