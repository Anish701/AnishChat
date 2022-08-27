from website import create_app

#automatically runs __init__.py from website folder

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)