"""The Python implementation of the GRPC users.Users server."""

import os
import logging
from concurrent import futures

import grpc
import users_pb2_grpc

from src.resources.users import Users


def serve():
    port = os.getenv("PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    # server.add_insecure_port("[::]:" + port)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
