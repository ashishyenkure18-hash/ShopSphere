from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(role):
    """Decorator: require a valid JWT AND a specific role claim."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != role:
                return jsonify(error="Forbidden", message=f"{role} access required"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper