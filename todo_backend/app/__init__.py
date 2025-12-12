from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

# Import blueprints after Flask app is created to avoid circular imports
from .routes.health import blp as health_blp
from .routes.tasks import blp as tasks_blp


def create_app() -> Flask:
    """
    Create and configure the Flask application with CORS and OpenAPI docs.

    - Enables CORS for http://localhost:3000
    - Registers health and tasks blueprints
    - Configures flask-smorest OpenAPI UI under /docs
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # CORS: restrict to frontend origin per acceptance criteria
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:3000"]}},
        supports_credentials=False,
    )

    # OpenAPI / Swagger configuration
    app.config["API_TITLE"] = "Todo API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    api = Api(app)

    # Tags for grouping
    api.spec.components.security_scheme(
        "NoAuth", {"type": "http", "scheme": "none"}  # doc purpose only
    )
    openapi_tags = [
        {"name": "Health", "description": "Health check routes"},
        {"name": "Tasks", "description": "Task CRUD operations"},
    ]
    for tag in openapi_tags:
        api.spec.tag(tag)

    # Register blueprints
    api.register_blueprint(health_blp)
    api.register_blueprint(tasks_blp)

    return app


# Provide app and api compatibility for existing imports and openapi generation script
app = create_app()
api = Api(app)
