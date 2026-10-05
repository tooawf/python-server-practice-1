from .model import DataModel
from .rpc import RPCServer

if __name__ == "__main__":
    RPCServer(DataModel()).serve_forever()
