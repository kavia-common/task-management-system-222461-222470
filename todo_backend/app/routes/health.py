from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    def get(self):
        """
        Health check endpoint
        Returns a simple JSON to indicate the service is up.
        """
        return {"message": "Healthy"}
