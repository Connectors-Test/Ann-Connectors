from flask import Flask, render_template
from routes.servicenow_routes import servicenow_bp

app = Flask(__name__)
app.register_blueprint(servicenow_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)