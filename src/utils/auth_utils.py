import jwt
import datetime
import grpc
from functools import wraps

SECRET_KEY = "your-secret-key"


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token):
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=["HS256"],
    )
    return payload["user_id"]


def auth_required(f):
    @wraps(f)
    def decorated(self, request, context):
        metadata = {
            k.lower(): v
            for k, v in context.invocation_metadata()
        }

        auth_header: str|None = metadata.get("authorization")

        if not auth_header:
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Authorization token is missing",
            )

        token = auth_header.replace("Bearer ", "")

        try:
            user_id = verify_token(token)

        except jwt.ExpiredSignatureError:
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Token expired",
            )

        except jwt.InvalidTokenError:
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Invalid token",
            )

        context.user_id = user_id

        return f(self, request, context)

    return decorated