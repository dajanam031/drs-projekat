from flask import Flask
from blueprints.users import user_blueprint

app = Flask(__name__)

# registracija ruta
app.register_blueprint(user_blueprint, url_prefix = '/engine')
app.run(port=5001, debug=True)