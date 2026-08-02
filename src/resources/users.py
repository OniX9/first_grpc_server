import users_pb2
import users_pb2_grpc

class Users(users_pb2_grpc.UsersServicer):
    def GetUsers(self, request, context):
        users = [
            users_pb2.User(
                id = "1", 
                name= "Onis Emem",
                email= "onisemem9@gmail.com",
                password= "securepswd",
            )
        ]
        return users_pb2.GetUsersResponse(users=users)