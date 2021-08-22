import base64
import hashlib
from Cryptodome import Random
from Cryptodome.Cipher import AES
from binascii import a2b_hex 

import os
os.getcwd() 

BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]


class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        print('넘어온 raw ', raw)
        iv = Random.new().read( AES.block_size )
        print('인크립트 iv', iv)
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        print('인크립트 cipher', cipher)
        return base64.b64encode( iv + cipher.encrypt( raw.encode('utf-8') ) )

    def decrypt( self, enc ):
        #enc = base64.b64decode(enc)
        #print(enc, '으다다다다')
        cryptor  = AES.new(self.key, AES.MODE_ECB  ) #MODE_CFB
        plain_text = cryptor.decrypt(a2b_hex(enc))
        print('플레인 텍스트', plain_text)
        result = bytes.decode(plain_text).strip()
        #result = bytes.decode(plain_text).rstrip('\0').strip()
        print('디크립션에대한 결과', result)
        return result
    




'''
import base64
import hashlib
from Cryptodome import Random
from Cryptodome.Cipher import AES


BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]


class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        print('넘어온 raw ', raw)
        iv = Random.new().read( AES.block_size )
        print('인크립트 iv', iv)
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        print('인크립트 cipher', cipher)
        return base64.b64encode( iv + cipher.encrypt( raw.encode('utf-8') ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        print(enc, '으다다다다')
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv ) #MODE_CFB
        return unpad(cipher.decrypt( enc[16:] ))
    
'''

'''

class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        print('넘어온 raw ', raw)
        iv = Random.new().read( AES.block_size )
        print('인크립트 iv', iv)
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        print('인크립트 cipher', cipher)
        return base64.b64encode( iv + cipher.encrypt( raw.encode('utf-8') ) )

    def decrypt( self, enc ):
        enc =  binascii.unhexlify(enc)
        #enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypt = cipher.decrypt(enc)
        print(decrypt, '이건또 뭔')
        decrypted_text = decrypt.decode('ANSI')
        print(decrypted_text, 'text')
        result = unpad(decrypt)
        return result


'''
'''


    data = "Iran has seized a foreign oil tanker in the Persian Gulf that was smuggling fuel to some Arab states, according to a state television report on Sunday. The report said that the tanker had been detained and the ship's foreign crew held by the country's elite Islamic Revolutionary Guards Corps."

    encrypted_data = aes_decrypt.AESCipher(bytes(key, encoding='utf8')).encrypt(data)  
    print(encrypted_data, '제발')

    decrypted_data = aes_decrypt.AESCipher(bytes(key, encoding='utf8')).decrypt(encrypted_data)
    abd = decrypted_data.decode('utf-8')
    print('이것이 abd', abd)
'''

'''
    from Cryptodome import Random
    from Cryptodome.Cipher import AES
    from accounts.utils import aes_decrypt
    import binascii
    import hashlib, base64
    

    #encrypt_key  = key.encode(encoding='utf-8', errors='strict')
    #print(encrypt_key , '키키키')
    BS = 32
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    unpad = lambda s : s[0:-s[-1]]

    def encrypt( raw ):
        mysecretpassword = 'wtfrudoinganpang'
        KEY = hashlib.sha256(key.encode('utf-8')).digest()
        raw = pad(raw)
        #iv = Random.new().read( AES.block_size )
        cipher = AES.new( KEY, AES.MODE_CBC) #iv )
        return base64.b64encode(cipher.encrypt(raw.encode('utf-8')))
    
    def decrypt(enc):
        mysecretpassword = 'wtfrudoinganpang'
        KEY = hashlib.sha256(mysecretpassword.encode('utf-8')).digest()  
        enc = base64.b64decode(enc)
        cipher = AES.new(KEY, AES.MODE_CBC )
        return unpad(cipher.decrypt( enc[16:] ))
    
    enc = encrypt('8039aa7975a3f91df8a54bff8bcdf107')
    dec = decrypt(enc).decode()
    print(dec, 'sss')
    #print(encrypt('8039aa7975a3f91df8a54bff8bcdf107'), '네?')

'''

