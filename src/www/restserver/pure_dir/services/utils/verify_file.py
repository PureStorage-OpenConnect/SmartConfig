from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import os


def verifyFile(signPath, filepath, pubkeyPath):
    print " file path in verify ", filepath
    print " sign path in verify ", signPath
    print " key path in verify ", pubkeyPath
    try:
        mfile = open(filepath, "r").read()
        #signPath = signedPath+'pure_signature.asc'
        #pubkeyPath = signedPath+'pure_publickey.asc'
        if not os.path.exists(signPath):
            return "Signature file doesn't exist"
        if not os.path.exists(pubkeyPath):
            return "public_key file doesn't exist"

        public_key = open(pubkeyPath, "r").read()
        pub_key = RSA.importKey(public_key)
        signature = open(signPath, "r").read()

        signer = PKCS1_v1_5.new(pub_key)
        verifier = SHA256.new()
        verifier.update(mfile)
        if signer.verify(verifier, signature):
            return "Verified"
        else:
            return "Unverified file"
    except Exception as e:
        msg = "Error occurs while verifying the file"
        print("Error occurs while verifying the file ", e)
        return msg
