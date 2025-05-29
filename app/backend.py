"""
Achievo Flask Backend Application
Nền tảng chứng chỉ NFT trên Cardano với Python stack
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import os
import json
import time
from typing import Dict, List, Optional

from app.config import config
from app.utils.auth import *
from app.utils.cardano import get_koios_client, CardanoUtils
from app.utils.ipfs import get_pinata_client, IPFSUtils
from app.utils.logging import AuditLogger, LogAction, LogLevel, configure_logging
from app.utils.firebase import firebase_service
from app.utils.marketplace import marketplace_service, reward_service


def create_app(config_name='default'):
    """Factory function để tạo Flask app"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=app.config['RATE_LIMIT_STORAGE_URL']
    )
    limiter.init_app(app)

    # Configure logging
    configure_logging(app)

    # Initialize components
    cardano_client = get_koios_client()
    # IPFS client will be lazy-loaded when needed

    # Routes
    @app.route('/')
    def index():
        """Trang chủ"""
        return render_template('index.html')

    # Authentication routes
    @app.route('/auth/get_nonce', methods=['POST'])
    def get_nonce():
        """Generate nonce for Cardano wallet authentication"""
        try:
            data = request.get_json()
            wallet_name = data.get('wallet_name')

            # Generate secure nonce
            import secrets
            nonce = secrets.token_hex(16)

            # Store nonce temporarily (in production, use Redis or database)
            if not hasattr(app, 'auth_nonces'):
                app.auth_nonces = {}

            # Clean old nonces (older than 5 minutes)
            current_time = time.time()
            app.auth_nonces = {k: v for k, v in app.auth_nonces.items() 
                              if current_time - v['timestamp'] < 300}

            # Store new nonce
            app.auth_nonces[nonce] = {
                'wallet_name': wallet_name,
                'timestamp': current_time
            }

            current_app.logger.info(f"Generated nonce for wallet: {wallet_name}")
            return jsonify({'success': True, 'nonce': nonce})

        except Exception as e:
            current_app.logger.error(f"Error generating nonce: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit("10 per minute")
    def login():
        """Đăng nhập người dùng"""
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            if email and password:
                try:
                    # Hash password for authentication
                    password_hash = hash_password(password)
                    user = firebase_service.authenticate_user(email, password_hash)

                    if user:
                        session['user_id'] = user['id']
                        session['user_name'] = user.get('full_name', 'User')
                        session['user_type'] = user.get('user_type', 'learner')
                        session['email'] = email

                        AuditLogger.log_action(
                            LogAction.USER_LOGIN,
                            {"email": email, "login_method": "email"}
                        )

                        flash('Đăng nhập thành công!', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Email hoặc mật khẩu không đúng', 'error')

                except Exception as e:
                    flash('Lỗi đăng nhập. Vui lòng thử lại.', 'error')
                    app.logger.error(f"Login error: {e}")
            else:
                flash('Vui lòng điền đầy đủ thông tin', 'error')

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    @limiter.limit("5 per minute")
    def register():
        """Đăng ký tài khoản mới"""
        if request.method == 'POST':
            user_type = request.form.get('user_type')
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password')

            if all([user_type, full_name, email, password]):
                try:
                    # Hash password
                    password_hash = hash_password(password)

                    user_data = {
                        'user_type': user_type,
                        'full_name': full_name,
                        'email': email,
                        'phone': phone,
                        'password_hash': password_hash
                    }

                    user_id = firebase_service.create_user(user_data)

                    AuditLogger.log_action(
                        LogAction.USER_REGISTER,
                        {
                            "user_type": user_type,
                            "email": email,
                            "registration_method": "email"
                        },
                        user_id=user_id
                    )

                    flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
                    return redirect(url_for('login'))

                except Exception as e:
                    flash('Lỗi đăng ký. Vui lòng thử lại.', 'error')
                    app.logger.error(f"Registration error: {e}")
            else:
                flash('Vui lòng điền đầy đủ thông tin', 'error')

        return render_template('register.html')

    @app.route('/logout')
    def logout():
        """Đăng xuất"""
        user_id = session.get('user_id')
        if user_id:
            AuditLogger.log_action(
                LogAction.USER_LOGOUT,
                {"logout_method": "manual"},
                user_id=user_id
            )

        session.clear()
        flash('Đã đăng xuất thành công', 'success')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard người dùng"""
        user_type = session.get('user_type')

        # Mock data based on user type
        if user_type == 'learner':
            context = {
                'progress': 75,
                'certificates_count': 5,
                'rewards_count': 3,
                'recent_activities': [
                    {
                        'type': 'Hoàn thành khóa học',
                        'description': 'Python Fundamentals',
                        'created_at': datetime.utcnow() - timedelta(days=1)
                    },
                    {
                        'type': 'Nhận chứng chỉ',
                        'description': 'Data Science Certificate',
                        'created_at': datetime.utcnow() - timedelta(days=3)
                    }
                ]
            }
        elif user_type == 'educator':
            context = {
                'students_count': 150,
                'courses_count': 8,
                'issued_certificates': 45
            }
        elif user_type == 'admin':
            context = {
                'total_users': 1250,
                'pending_organizations': 5,
                'total_certificates': 2890
            }
        else:
            context = {}

        return render_template('dashboard.html', **context)

    @app.route('/admin')
    @admin_required
    def admin():
        """Dashboard quản trị"""
        # Mock admin data
        stats = {
            'total_users': 1250,
            'learners': 1100,
            'educators': 145,
            'certificates': 2890,
            'transactions': 1560,
            'rewards': 890
        }

        pending_organizations = [
            {
                'id': 'org_1',
                'name': 'Trường Đại học ABC',
                'organization_type': 'university',
                'email': 'admin@abc.edu.vn'
            },
            {
                'id': 'org_2', 
                'name': 'Trung tâm XYZ',
                'organization_type': 'training_center',
                'email': 'contact@xyz.vn'
            }
        ]

        recent_logs = [
            {
                'timestamp': datetime.utcnow() - timedelta(minutes=5),
                'level': 'INFO',
                'message': 'Certificate issued successfully for user_123'
            },
            {
                'timestamp': datetime.utcnow() - timedelta(minutes=15),
                'level': 'WARNING',
                'message': 'Failed login attempt for email test@example.com'
            }
        ]

        return render_template('admin.html', 
                             stats=stats,
                             pending_organizations=pending_organizations,
                             recent_logs=recent_logs)

    @app.route('/verify', methods=['GET', 'POST'])
    @app.route('/verify/<certificate_id>')
    @limiter.limit("30 per minute")
    def verify_certificate(certificate_id=None):
        """Xác thực chứng chỉ công khai"""
        certificate = None
        error = None

        if request.method == 'POST':
            certificate_id = request.form.get('certificate_id')

        if certificate_id:
            # TODO: Thực hiện xác thực từ blockchain/database
            # certificate = CertificateService.verify(certificate_id)

            # Mock certificate verification
            if len(certificate_id) > 10:
                certificate = {
                    'name': 'Data Science Professional Certificate',
                    'recipient_name': 'Nguyễn Văn A',
                    'issuer_name': 'Trường Đại học ABC',
                    'issued_date': datetime.utcnow() - timedelta(days=30),
                    'status': 'active',
                    'status_display': 'Có hiệu lực',
                    'description': 'Chứng chỉ hoàn thành khóa học Data Science cơ bản',
                    'tx_hash': 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
                    'ipfs_hash': 'QmXyZ123abc456def789ghi012jkl345mno678pqr901stu234vwx567yza890',
                    'verification_history': [
                        {
                            'timestamp': datetime.utcnow(),
                            'action': 'Xác thực qua web portal'
                        },
                        {
                            'timestamp': datetime.utcnow() - timedelta(days=5),
                            'action': 'Xác thực qua API'
                        }
                    ]
                }

                AuditLogger.log_certificate_action(
                    LogAction.CERTIFICATE_VERIFY,
                    certificate_id,
                    additional_details={"verification_method": "web"}
                )
            else:
                error = "Không tìm thấy chứng chỉ với mã này"

        return render_template('certificate.html', 
                             certificate=certificate, 
                             error=error)

    @app.route('/api/certificate/issue', methods=['POST'])
    @educator_required
    @limiter.limit("10 per hour")
    def api_issue_certificate():
        """API phát hành chứng chỉ NFT"""
        try:
            data = request.get_json()

            # Validate input
            required_fields = ['recipient_id', 'course_name', 'certificate_type']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400

            # TODO: Implement certificate issuance logic
            # 1. Tạo metadata IPFS
            # 2. Build transaction OpShin contract
            # 3. Submit transaction lên Cardano
            # 4. Lưu thông tin vào database

            # Mock certificate issuance
            certificate_id = f"cert_{datetime.utcnow().timestamp()}"
            tx_hash = "mock_tx_hash_" + certificate_id

            AuditLogger.log_certificate_action(
                LogAction.CERTIFICATE_ISSUE,
                certificate_id,
                recipient_id=data['recipient_id'],
                issuer_id=session.get('user_id'),
                additional_details=data
            )

            return jsonify({
                'success': True,
                'certificate_id': certificate_id,
                'tx_hash': tx_hash,
                'message': 'Certificate issued successfully'
            })

        except Exception as e:
            app.logger.error(f"Error issuing certificate: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/certificate/verify/<certificate_id>')
    @limiter.limit("60 per minute")
    def api_verify_certificate(certificate_id):
        """API xác thực chứng chỉ"""
        try:
            # TODO: Implement verification logic
            # verification_result = CertificateService.verify_by_id(certificate_id)

            # Mock verification
            if len(certificate_id) > 10:
                result = {
                    'valid': True,
                    'certificate': {
                        'id': certificate_id,
                        'name': 'Mock Certificate',
                        'status': 'active',
                        'issued_date': datetime.utcnow().isoformat(),
                        'issuer': 'Mock Issuer',
                        'recipient': 'Mock Recipient'
                    }
                }

                AuditLogger.log_certificate_action(
                    LogAction.CERTIFICATE_VERIFY,
                    certificate_id,
                    additional_details={"verification_method": "api"}
                )
            else:
                result = {
                    'valid': False,
                    'error': 'Certificate not found'
                }

            return jsonify(result)

        except Exception as e:
            app.logger.error(f"Error verifying certificate: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/auth/wallet', methods=['POST'])
    @limiter.limit("10 per minute")
    def auth_wallet():
        """Xác thực qua Cardano wallet"""
        try:
            data = request.get_json()
            wallet_address = data.get('address')

            if not wallet_address or not CardanoUtils.validate_address(wallet_address):
                return jsonify({'error': 'Invalid wallet address'}), 400

            # TODO: Implement wallet authentication logic
            # 1. Verify wallet signature
            # 2. Check if wallet is registered
            # 3. Create session

            # Mock wallet authentication
            session['user_id'] = f"wallet_{wallet_address[:8]}"
            session['user_name'] = f"Wallet User"
            session['user_type'] = 'learner'
            session['wallet_address'] = wallet_address

            AuditLogger.log_action(
                LogAction.USER_LOGIN,
                {
                    "wallet_address": wallet_address,
                    "login_method": "cardano_wallet"
                }
            )

            return jsonify({'success': True, 'message': 'Wallet authenticated'})

        except Exception as e:
            app.logger.error(f"Error authenticating wallet: {e}")
            return jsonify({'error': 'Authentication failed'}), 500

    @app.route('/marketplace')
    def marketplace():
        """Marketplace page"""
        try:
            category = request.args.get('category')
            search = request.args.get('search')

            courses = marketplace_service.get_marketplace_listings(category, search)

            categories = ['programming', 'data-science', 'blockchain', 'design', 'business']

            return render_template('marketplace.html', 
                                 courses=courses, 
                                 categories=categories,
                                 selected_category=category,
                                 search_term=search)
        except Exception as e:
            app.logger.error(f"Error loading marketplace: {e}")
            flash('Lỗi tải marketplace', 'error')
            return redirect(url_for('index'))

    @app.route('/my-certificates')
    @login_required
    def my_certificates():
        return "<h1>My Certificates</h1><p>Coming soon...</p>"

    @app.route('/my-rewards')
    @login_required
    def my_rewards():
        return "<h1>My Rewards</h1><p>Coming soon...</p>"

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    return app


# Create application instance
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)