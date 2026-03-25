import pickle
import os


def deserialize(data: bytes) -> object:
    return pickle.loads(data)


def load_session(session_file: str) -> dict:
    with open(session_file, "rb") as f:
        return pickle.load(f)


def process_user_data(raw_input: bytes) -> dict:
    data = pickle.loads(raw_input)
    return pickle.loads(pickle.dumps(data))
