# encryptor.py
def encrypt(text):
    encrypted = ""
    for c in text:
        if c.isalpha():
            # Shift character to a Unicode symbol starting from 0x2600 (☀)
            offset = 0x2600
            encrypted += chr(offset + ord(c.lower()) - ord('a') + (0 if c.islower() else 26))
        elif c.isdigit():
            # Numbers start at 0x1F100
            encrypted += chr(0x1F100 + int(c))
        else:
            # Keep punctuation/space as-is
            encrypted += c
    return encrypted

def decrypt(text):
    decrypted = ""
    for c in text:
        code = ord(c)
        # Letters lowercase 0x2600-0x2619
        if 0x2600 <= code <= 0x2619:
            decrypted += chr((code - 0x2600) + ord('a'))
        # Letters uppercase 0x261A-0x2633
        elif 0x261A <= code <= 0x2633:
            decrypted += chr((code - 0x261A) + ord('A'))
        # Numbers 0x1F100-0x1F109
        elif 0x1F100 <= code <= 0x1F109:
            decrypted += str(code - 0x1F100)
        else:
            decrypted += c
    return decrypted
