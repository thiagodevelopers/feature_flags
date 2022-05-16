from flask import Flask, request

app = Flask(__name__)
app.config['FLASK_ENV'] = "development"

@app.before_request
def register_gatekeeper():
    # Put imports here to avoid circular import issues.
    from flask import request

    import gatekeeper

    request.gk = gatekeeper.initialize_gatekeeper(app=app)


@app.route("/teste")
def index():
    if request.gk.ff('ROTA_TESTE', 'NOT_VISIBLE'): 
        return 'Olá Mundo!'
    else:
        return 'teste'

if __name__ == "__main__":
	app.run()