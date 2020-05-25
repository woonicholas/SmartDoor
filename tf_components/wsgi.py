from app import app

if __name__ == "__main__":
    #app.run(debug=False, use_reloader=False)
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
