from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
#######################ADDED###############################
from flask_socketio import SocketIO, send
#######################ADDED###############################


db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    #Initialize all outside components, like sockets, and migrate, and database
    app = Flask(__name__)
    #######################ADDED###############################
    global socketio
    socketio = SocketIO(app, cors_allowed_origins='*')
    #######################ADDED###############################
    app.config['SECRET_KEY'] = 'bhangre'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    migrate = Migrate(app, db)

    #register the blueprints views and auth
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    #create the database
    create_database(app)

    #register outside login components
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))    

    return app

#create the database
def create_database(app):
    if not path.exists('/website' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')