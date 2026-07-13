import os
from flask import Flask
from config import Config
from extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Pastikan folder instance ada (untuk SQLite)
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    # Init ekstensi
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Import model supaya dikenali sebelum create_all
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrasi blueprint
    from routes.auth import auth_bp
    from routes.expenses import expenses_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(dashboard_bp)

    # Context processor: sediakan tahun sekarang untuk footer, dll.
    @app.context_processor
    def inject_globals():
        from datetime import date
        return {"current_year": date.today().year}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
