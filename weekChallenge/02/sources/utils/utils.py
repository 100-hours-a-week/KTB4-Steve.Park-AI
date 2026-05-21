from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from utils.models import SECRET_KEY


def pad(text) -> str:
    return text + (16 - len(text) % 16) * chr(16 - len(text) % 16)

def unpad(text) -> str:
    return text[:-ord(text[-1])]

def encryptPwd(pwd: str) -> str:
    if not pwd:
        return pwd
    
    key = SECRET_KEY.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(pwd).encode('utf-8'))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')

    return iv + ct

def decryptPwd(pwd: str) -> str:
    if not pwd:
        return pwd
    
    key = SECRET_KEY.encode('utf-8')
    iv = b64decode(pwd[:24])
    ct = b64decode(pwd[24:])
    cipher = AES.new(key, AES.MODE_CBC, iv)

    return unpad(cipher.decrypt(ct).decode('utf-8'))
