
"""
Utilities cho xác thực và phân quyền
"""
import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, session, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Hash mật khẩu người dùng"""
    return generate_password_hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Xác thực mật khẩu"""
    return check_password_hash(hashed, password)


def generate_jwt_token(user_id: str, user_type: str) -> str:
    """Tạo JWT token cho người dùng"""
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def verify_jwt_token(token: str) -> dict:
    """Xác thực JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """Decorator yêu cầu đăng nhập"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator yêu cầu quyền admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session.get('user_type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def educator_required(f):
    """Decorator yêu cầu quyền educator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session.get('user_type') not in ['educator', 'admin']:
            return jsonify({'error': 'Educator access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def verify_cardano_wallet_signature(address: str, signature: str, message: str) -> bool:
    """Xác thực chữ ký Cardano wallet"""
    # Placeholder implementation
    # Trong thực tế sẽ sử dụng PyCardano hoặc tương đương
    return len(address) > 0 and len(signature) > 0


def generate_session_token() -> str:
    """Tạo session token ngẫu nhiên"""
    import secrets
    return secrets.token_urlsafe(32)


def hash_data(data: str) -> str:
    """Hash dữ liệu sử dụng SHA256"""
    return hashlib.sha256(data.encode()).hexdigest()
