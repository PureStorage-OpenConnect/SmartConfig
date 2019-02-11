from Crypto.Cipher import AES
import hashlib

passphrase = 'pure-director-pass-word'
key = hashlib.sha256(passphrase.encode('utf-8')).digest()


def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)


def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    # return plaintext.rstrip(b"\0")
    return plaintext


def decrypt_file(file_name):
    with open(file_name, 'rb') as fo:
        ciphertext = fo.read()
    dec = decrypt(ciphertext, key)
    with open(file_name[:-4], 'wb') as fo:
        fo.write(dec)
    return file_name[:-4]
