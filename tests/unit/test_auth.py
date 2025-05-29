
"""
Unit tests cho authentication utilities
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.utils.auth import (
    hash_password, verify_password, generate_jwt_token, 
    verify_jwt_token, verify_cardano_wallet_signature
)


class TestAuthUtils:
    """Test authentication utilities"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    @patch('app.utils.auth.current_app')
    def test_jwt_token_generation(self, mock_app):
        """Test JWT token generation"""
        mock_app.config = {
            'JWT_SECRET_KEY': 'test_secret',
            'JWT_ACCESS_TOKEN_EXPIRES': 3600
        }
        
        user_id = "user_123"
        user_type = "learner"
        
        token = generate_jwt_token(user_id, user_type)
        assert isinstance(token, str)
        assert len(token) > 0
    
    @patch('app.utils.auth.current_app')
    def test_jwt_token_verification(self, mock_app):
        """Test JWT token verification"""
        mock_app.config = {
            'JWT_SECRET_KEY': 'test_secret',
            'JWT_ACCESS_TOKEN_EXPIRES': 3600
        }
        
        user_id = "user_123"
        user_type = "learner"
        
        token = generate_jwt_token(user_id, user_type)
        payload = verify_jwt_token(token)
        
        assert payload is not None
        assert payload['user_id'] == user_id
        assert payload['user_type'] == user_type
    
    @patch('app.utils.auth.current_app')
    def test_expired_jwt_token(self, mock_app):
        """Test expired JWT token handling"""
        mock_app.config = {
            'JWT_SECRET_KEY': 'test_secret'
        }
        
        # Create expired token
        payload = {
            'user_id': 'user_123',
            'user_type': 'learner',
            'exp': datetime.utcnow() - timedelta(hours=1),
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        
        expired_token = jwt.encode(payload, 'test_secret', algorithm='HS256')
        result = verify_jwt_token(expired_token)
        
        assert result is None
    
    def test_cardano_wallet_signature_verification(self):
        """Test Cardano wallet signature verification"""
        address = "addr1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwq2ytjqp"
        signature = "test_signature"
        message = "test_message"
        
        # Mock implementation returns True for non-empty inputs
        result = verify_cardano_wallet_signature(address, signature, message)
        assert result is True
        
        # Test with empty inputs
        result = verify_cardano_wallet_signature("", signature, message)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
