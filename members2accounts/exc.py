__author__ = 'marijn'

class CryptoException(RuntimeError):
    """I get raised when there is something wrong with the cryptography part."""
    pass

class DecryptionFailedException(CryptoException):
    """I get raised when the decryption failed. For example, the file was not encrypted."""
    pass

class UnknownSignatureException(CryptoException):
    """I get raised when the key signing the file was not in the keyring or the file was not signed."""
    pass

class KeyNotTrustedException(CryptoException):
    """I get raised when the key signing the file is not trusted in the keyring."""
    pass

class SignerIsNotAllowedException(CryptoException):
    """I get raised when the signed is not one of the allowed changers of the code."""
    pass