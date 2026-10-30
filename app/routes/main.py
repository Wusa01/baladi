from flask import Blueprint, jsonify, render_template


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "application": "Baladi",
        "message": "Baladi API is running"
    }), 200
