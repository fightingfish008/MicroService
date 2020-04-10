from main import app

if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=5001)
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
    # gunicorn -w 2 -b '127.0.0.1:5001' run:app
