from flask import Flask
from blueprints.users import user_blueprint
from database.models import User, Base, engine

app = Flask(__name__)

# podesavanje baze 
Base.metadata.create_all(engine)

# registracija ruta
app.register_blueprint(user_blueprint, url_prefix = '/engine')
app.run(port=5001, debug=True, host='0.0.0.0')