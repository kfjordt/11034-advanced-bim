# NOT FINISHED

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.transports.server import ServerTransport
from specklepy.api import operations

client = SpeckleClient()
account = get_default_account()
client.authenticate_with_account(account)

def create_stream(name: str):
    # initialise the client
    exisiting_streams = client.stream.search(name)

    if exisiting_streams:
        print(f"Stream(s) with name '{name}' already found. Enter number to proceed.")
        overwrite = input("1: Create new stream with same name.\n2: Delete stream(s) and create new one.\n3: Cancel.\n")
        if overwrite == "1":
            new_stream_id = client.stream.create(name=name)

        if overwrite == "2":
            [client.stream.delete(id=exisiting_stream.id) for exisiting_stream in exisiting_streams]
            new_stream_id = client.stream.create(name=name)

        if overwrite == "3":
            return None
            
    else:
        new_stream_id = client.stream.create(name=name)

    print(f"\nStream with id '{new_stream_id}' will be used from this point on.")
    return new_stream_id

def send_data_to_stream(stream_id, data_to_send):
    transport = ServerTransport(client=client, stream_id=stream_id)

    hash = operations.send(base=data_to_send, transports=[transport])

    commid_id = client.commit.create(
        stream_id=stream_id, 
        object_id=hash
        )