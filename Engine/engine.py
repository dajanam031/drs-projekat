from flask import Flask
from blueprints.users import user_blueprint, transaction_process, transaction_queue
from database.models import Base, engine
from multiprocessing import Process

app = Flask(__name__)

# podesavanje baze 
Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.register_blueprint(user_blueprint, url_prefix = '/engine')
    p = Process(target=transaction_process, args=(transaction_queue, ))
    p.start()
    app.run(port=5001, debug=True, host='0.0.0.0')