"""
Flask Application Factory for ERP System
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://erp_user:erp_password@localhost:5432/erp_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    from app.routes.procurement import procurement_bp
    from app.routes.goods_receiving import goods_receiving_bp
    from app.routes.production import production_bp
    from app.routes.packaging import packaging_bp
    from app.routes.sales import sales_bp
    from app.routes.financial import financial_bp
    from app.routes.reporting import reporting_bp

    app.register_blueprint(procurement_bp, url_prefix='/api/procurement')
    app.register_blueprint(goods_receiving_bp, url_prefix='/api/goods-receiving')
    app.register_blueprint(production_bp, url_prefix='/api/production')
    app.register_blueprint(packaging_bp, url_prefix='/api/packaging')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(financial_bp, url_prefix='/api/financial')
    app.register_blueprint(reporting_bp, url_prefix='/api/reporting')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'ERP System'}

    return app