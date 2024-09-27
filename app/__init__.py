from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Registrar los blueprints (rutas)
    from .routes import main_routes
    app.register_blueprint(main_routes)
    
    return app
