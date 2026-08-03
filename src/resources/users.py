import grpc
import uuid
import users_pb2
import users_pb2_grpc

from pydantic import ValidationError
from src.schemas import LoginUserSchema, UserSchema
from src.utils.auth_utils import auth_required, generate_token
 

users:dict[str, UserSchema] = {}

def get_user_by_email(email:str) -> UserSchema|None:
    for details in users.values():
        if details.email == email:
            return details
    return None

class Users(users_pb2_grpc.UsersServicer):
    def LoginUser (self, request, context):
        try:
            payload = LoginUserSchema(email=request.email, password=request.password)
        except ValidationError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))

        # Get user
        user = get_user_by_email(payload.email)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, str('User not found'))
        if user.password != payload.password:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str('Invalid password'))


        # Return user
        return users_pb2.AuthUserReponse(
            user=users_pb2.User(
                id = user.id,
                name= user.name,
                email= payload.email,
                ),
            token= generate_token(user.id),
        )


    def CreateUser(self, request, context):
        uid = str(uuid.uuid4())

        try:
            payload = UserSchema(
                id = uid,
                name= request.name, 
                email=request.email, 
                password=request.password
            )

        except ValidationError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))

        # User exist
        for uid, details in users.items():
            if details.email == payload.email:
                    context.abort(grpc.StatusCode.ALREADY_EXISTS, str(f'User already exists.'))

        # Add to the in-memory database
        users[uid] = payload

        return users_pb2.AuthUserReponse(
            user=users_pb2.User(
                id = payload.id,
                name= payload.name,
                email= payload.email,
                ),
            token= generate_token(payload.id),
        )
    
    
    def GetUsers(self, request, context):
        users_list = []
        for user in users.values():
            users_list.append(
                users_pb2.User(
                    id = user.id,
                    name= user.name,
                    email= user.email,
                )
            )
        return users_pb2.GetUsersResponse(users=users_list)
    
    @auth_required
    def GetUserById(self, request, context):
        uid = context.user_id
        user = users.get(uid)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, str('User not found'))
        return users_pb2.User(
                    id = user.id,
                    name= user.name,
                    email= user.email,
                )