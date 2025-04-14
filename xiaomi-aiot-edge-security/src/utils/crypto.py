# src/utils/crypto.py
import os
import hashlib
import base64
import hmac
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from .logger import get_logger

def encrypt_data(data, key):
    """加密数据
    
    Args:
        data: 待加密数据
        key: 加密密钥
        
    Returns:
        bytes: 加密后的数据
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data

def decrypt_data(encrypted_data, key):
    """解密数据
    
    Args:
        encrypted_data: 加密数据
        key: 解密密钥
        
    Returns:
        bytes: 解密后的数据
    """
    iv = encrypted_data[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_padded = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    return decrypted

def generate_key_pair():
    """生成密钥对
    
    Returns:
        tuple: (公钥, 私钥)
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return public_key, private_key

def sign_data(data, private_key):
    """签名数据
    
    Args:
        data: 待签名数据
        private_key: 私钥
        
    Returns:
        bytes: 签名
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
    if isinstance(data, str):
        data = data.encode('utf-8')
    signature = private_key.sign(
        data,
        asymmetric_padding.PSS(
            mgf=asymmetric_padding.MGF1(hashes.SHA256()),
            salt_length=asymmetric_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(data, signature, public_key):
    """验证签名
    
    Args:
        data: 原始数据
        signature: 签名
        public_key: 公钥
        
    Returns:
        bool: 验证结果
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
    if isinstance(data, str):
        data = data.encode('utf-8')
    try:
        public_key.verify(
            signature,
            data,
            asymmetric_padding.PSS(
                mgf=asymmetric_padding.MGF1(hashes.SHA256()),
                salt_length=asymmetric_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False

class CryptoUtils:
    """加密工具：提供加密、解密、哈希、签名等功能"""
    
    def __init__(self):
        self.logger = get_logger("CryptoUtils")
        self.logger.info("加密工具初始化完成")
    
    @staticmethod
    def generate_key(length=32):
        """生成随机密钥
        
        Args:
            length: 密钥长度（字节）
            
        Returns:
            bytes: 随机密钥
        """
        return os.urandom(length)
    
    @staticmethod
    def hash_sha256(data):
        """SHA-256哈希
        
        Args:
            data: 待哈希数据
            
        Returns:
            bytes: 哈希值
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).digest()
    
    @staticmethod
    def hmac_sha256(key, data):
        """HMAC-SHA256签名
        
        Args:
            key: 密钥
            data: 待签名数据
            
        Returns:
            bytes: 签名
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hmac.new(key, data, hashlib.sha256).digest()
    
    @staticmethod
    def encrypt_aes_cbc(key, plaintext):
        """AES-CBC加密
        
        Args:
            key: 密钥（16、24或32字节）
            plaintext: 明文
            
        Returns:
            dict: {"iv": 初始向量, "ciphertext": 密文}
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # 确保密钥长度
        if len(key) not in (16, 24, 32):
            raise ValueError("密钥长度必须为16、24或32字节")
        
        # 生成随机IV
        iv = os.urandom(16)
        
        # 填充
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        # 加密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            "iv": base64.b64encode(iv).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
        }
    
    @staticmethod
    def decrypt_aes_cbc(key, iv, ciphertext):
        """AES-CBC解密
        
        Args:
            key: 密钥（16、24或32字节）
            iv: 初始向量
            ciphertext: 密文
            
        Returns:
            bytes: 明文
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        # 解码Base64
        if isinstance(iv, str):
            iv = base64.b64decode(iv)
        if isinstance(ciphertext, str):
            ciphertext = base64.b64decode(ciphertext)
        
        # 确保密钥长度
        if len(key) not in (16, 24, 32):
            raise ValueError("密钥长度必须为16、24或32字节")
        
        # 解密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 去除填充
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext
    
    @staticmethod
    def generate_token(key, data, expire_seconds=3600):
        """生成认证令牌
        
        Args:
            key: 密钥
            data: 数据字典
            expire_seconds: 有效期（秒）
            
        Returns:
            str: 认证令牌
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        # 添加时间戳和过期时间
        payload = {
            **data,
            "timestamp": int(time.time()),
            "expire": int(time.time()) + expire_seconds
        }
        
        # 序列化为JSON
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        
        # 计算签名
        signature = hmac.new(key, payload_str.encode('utf-8'), hashlib.sha256).digest()
        
        # 组合令牌
        token = {
            "payload": base64.b64encode(payload_str.encode('utf-8')).decode('utf-8'),
            "signature": base64.b64encode(signature).decode('utf-8')
        }
        
        return base64.b64encode(json.dumps(token).encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def verify_token(key, token):
        """验证认证令牌
        
        Args:
            key: 密钥
            token: 认证令牌
            
        Returns:
            dict or None: 数据字典或None（验证失败）
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        try:
            # 解码令牌
            import json
            token_str = base64.b64decode(token).decode('utf-8')
            token_obj = json.loads(token_str)
            
            # 提取载荷和签名
            payload_str = base64.b64decode(token_obj["payload"]).decode('utf-8')
            signature = base64.b64decode(token_obj["signature"])
            
            # 验证签名
            expected_signature = hmac.new(key, payload_str.encode('utf-8'), hashlib.sha256).digest()
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # 解析载荷
            payload = json.loads(payload_str)
            
            # 检查是否过期
            current_time = int(time.time())
            if payload.get("expire", 0) < current_time:
                return None
            
            return payload
        except Exception:
            return None