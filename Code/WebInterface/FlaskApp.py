import os
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
# from Code import GlobalEngineRegistry as gbl


app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
socketio = SocketIO(app)


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """API endpoint to get framework status"""
    return jsonify(
        {
            "framework_initialized": gbl.EngineContainer is not None,
            "loadflowcomplete": False,
            "visualsready": False
        }
    )
@app.route('/hello')
def hello():
    return "<h1>Hello World!</h1><p>Flask is running if you see this.</p>"
@app.route('/api/loadflow/run', methods=['POST'])
def run_loadflow():
    """API endpoint to run load flow analysis"""
    if gbl.EngineContainer and gbl.EngineLoadFlowContainer:
        try:
            # gbl.EngineLoadFlowContainer.runloadflow()
            # gbl.EngineLoadFlowContainer.getandupdatebusbarloadflowresults()
            return jsonify({"status": "success", "message": "Load flow analysis completed successfully."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Framework not initialized or Load Flow Container missing."}), 500
# @app.route('/api/visualization/generate', methods=['POST'])
# def generate_visualisation():
#     """API endpoint to generate vizualisation"""
#     if gbl.EngineContainer:
#         try:
#             # Placeholder for vizualisation generation logic
#             return jsonify({"status": "success", "message": "Visualisation generated successfully."})
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
#     else:
#         return jsonify({"error": "Framework not initialized."}), 500
@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    emit('response', {'message': 'Connected to PowerFactory Framework'})
    
def start_web_server(host='localhost', port=5000):
    print(f"Flask attempting to start on {host}:{port}")
    try:
        socketio.run(app, host=host, port=port, debug=False, use_reloader=False)
        print("Flask started successfully")  # This probably never prints
    except Exception as e:
        print(f"Flask failed to start: {e}")