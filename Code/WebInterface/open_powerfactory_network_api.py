from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/open-powerfactory-network', methods=['POST'])
def open_powerfactory_network():
    data = request.get_json()
    projectname = data.get('projectname')
    studycasename = data.get('studycasename')
    # TODO: Add your backend logic here to open the network
    # For now, just return success
    return jsonify({'success': True, 'message': 'Network opened successfully'})

if __name__ == '__main__':
    app.run(debug=True)
