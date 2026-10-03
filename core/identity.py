import os
import hashlib
import shutil


IDENTITY_FILE = ".ultron_identity"
BACKUP_FILE = ".ultron_identity.backup"
HASH_FILE = ".ultron_identity.hash"



def calculate_hash():

    if not os.path.exists(IDENTITY_FILE):

        return None


    with open(
        IDENTITY_FILE,
        "rb"
    ) as f:

        data = f.read()


    return hashlib.sha256(
        data
    ).hexdigest()



def verify_hash():

    if not os.path.exists(HASH_FILE):

        return False


    with open(
        HASH_FILE,
        "r"
    ) as f:

        saved_hash = f.read().split()[0]


    current_hash = calculate_hash()


    return saved_hash == current_hash



def verify_identity():

    if not os.path.exists(
        IDENTITY_FILE
    ):

        return False


    if not verify_hash():

        return False


    with open(
        IDENTITY_FILE,
        "r"
    ) as f:

        data = f.read()


    required = [
        "CREATOR=nath-dev",
        "PROJECT=ULTRON Panel",
        "STATUS=ACTIVE"
    ]


    for item in required:

        if item not in data:

            return False


    return True



def recover_identity():

    if not os.path.exists(
        BACKUP_FILE
    ):

        return False


    shutil.copy(
        BACKUP_FILE,
        IDENTITY_FILE
    )


    return True
