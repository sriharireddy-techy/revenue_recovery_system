import uuid


def generate_case_id():
    return "REC_" + uuid.uuid4().hex[:8].upper()