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

class SecretKeyNotInKeyringException(CryptoException):
    """I get called when trying to define a fingerprint as the key for this process, but there is no secret key available."""
    pass

class EncryptingFailedException(CryptoException):
    """I get called when the encryption failed."""
    pass

class LDAPException(RuntimeError):
    """I form the base for all LDAP related exceptions."""
    pass

class LDAPConnectionException(LDAPException):
    """I Get raised when there are issues connecting to the LDAP."""
    pass

class AccountDoesNotExistException(LDAPException): pass
class MultipleResultsException(LDAPException): pass
class OperationNotSupported(LDAPException): pass

class MemberizerException(RuntimeError):
    """I am the basis for exceptions that are specific for Memberizer"""
    pass

class MemberNotValidException(MemberizerException):
    """The member entry doesn't have the minimal necessary structure to be usable."""
    pass