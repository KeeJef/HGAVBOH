from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from os import path

def signHashes(selfobj, dataToSign):

    dataToSign = str.encode(dataToSign)
    signature = selfobj.private_key.sign(dataToSign)  

    public_key = selfobj.private_key.public_key()      
    public_key.verify(signature, dataToSign)

    signeddata = signature

    return signeddata


def generateOrLoadKeypair(selfobj):

        encoding = 'utf-8'

        if not path.exists("privkey.txt"):
            
            private_key = Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            textualPublicKey = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
            textualPrivateKey = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())

            textualPublicKey = textualPublicKey.decode(encoding)
            textualPrivateKey = textualPrivateKey.decode(encoding)

            f = open("pubkey.txt", "a")
            f.write(textualPublicKey)
            f.close()

            f = open("privkey.txt", "a")
            f.write(textualPrivateKey)
            f.close()

            selfobj.private_key = private_key

            return

        f=open("privkey.txt", "r")
        if f.mode == 'r':
            contents =f.read()
            pass

        textualPrivateKey = contents.encode(encoding)
        selfobj.private_key  = serialization.load_pem_private_key(data=textualPrivateKey,password=None,backend=default_backend())
        
        