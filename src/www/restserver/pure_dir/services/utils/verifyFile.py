from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


def verifyFile(public_key, filePath, signature):
    pub_key = RSA.importKey(public_key)

    signer = PKCS1_v1_5.new(pub_key)
    verifier = SHA256.new()
    verifier.update(filePath)
    if signer.verify(verifier, signature):
        print("Verified")
    else:
        print("Unverified")


private_key = open('mypubkey.asc', "r").read()
#filePath = open('my_json.json', "r").read()
filePath = open('sampleTest/pure.tar.gz.enc', "r").read()
signature = open('mysignature.asc', "r").read()

verifyFile(private_key, filePath, signature)
