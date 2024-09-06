from flask import jsonify, current_app as app

def error_logger(status_code):
    app.logger.error(f'HTTP ERROR RESPONSE CODE {status_code} SENT')

def handle_401_error(error):
    error_logger(403)
    return jsonify({"message": "Unauthorized"}), 401

def handle_403_error(error):
    error_logger(403)
    return jsonify({"message": "Forbidden"}), 403

def handle_404_error(error):
    error_logger(404)
    return jsonify({"message": "Resource not found"}), 404

def handle_500_error(error):
    error_logger(500)
    return jsonify({"message": "Internal server error"}), 500

def handle_400_error(error):
    error_logger(400)
    return jsonify({"message": "Bad request"}), 400

