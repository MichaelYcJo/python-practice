import base64
from Cryptodome.Cipher import AES

BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]


class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        cipher = AES.new(self.key, AES.MODE_ECB )
        return base64.b64encode( cipher.encrypt( raw.encode('utf-8') ) )

    
    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return unpad(cipher.decrypt(enc)).decode('utf8')



plain_text = "Secret Information"

key = 'keymustbe16bytes'
print('키값', bytes(key, encoding='utf8'))

encrypted_data = AESCipher(bytes(key, encoding='utf8')).encrypt(plain_text)  
print('인크립트데이터', encrypted_data)


decrypted_data = AESCipher(bytes(key, encoding='utf8')).decrypt(encrypted_data)
print('이것은 결론', decrypted_data)