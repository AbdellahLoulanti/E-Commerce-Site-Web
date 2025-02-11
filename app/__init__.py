from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from prometheus_flask_exporter import PrometheusMetrics
from flask_migrate import Migrate


app = Flask(__name__)
metrics = PrometheusMetrics(app)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from app import routes
