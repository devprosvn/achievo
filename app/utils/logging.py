
"""
Utilities cho logging và audit trail
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import current_app, session, request
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogAction(Enum):
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    
    # Certificate actions
    CERTIFICATE_ISSUE = "certificate_issue"
    CERTIFICATE_VERIFY = "certificate_verify"
    CERTIFICATE_REVOKE = "certificate_revoke"
    CERTIFICATE_UPDATE = "certificate_update"
    
    # Admin actions
    ADMIN_APPROVE_ORG = "admin_approve_organization"
    ADMIN_REJECT_ORG = "admin_reject_organization"
    ADMIN_EXPORT_DATA = "admin_export_data"
    
    # Marketplace actions
    MARKETPLACE_BUY = "marketplace_buy"
    MARKETPLACE_SELL = "marketplace_sell"
    
    # System actions
    SYSTEM_ERROR = "system_error"
    SYSTEM_STARTUP = "system_startup"


class AuditLogger:
    """Logger cho audit trail và security events"""
    
    @staticmethod
    def log_action(
        action: LogAction,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
        level: LogLevel = LogLevel.INFO
    ):
        """Log một action của người dùng hoặc hệ thống"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.value,
            "level": level.value,
            "user_id": user_id or session.get('user_id'),
            "user_type": session.get('user_type'),
            "ip_address": request.remote_addr if request else None,
            "user_agent": request.headers.get('User-Agent') if request else None,
            "details": details
        }
        
        # Log to application logger
        current_app.logger.info(f"AUDIT: {json.dumps(log_entry)}")
        
        # TODO: Ghi vào Firestore/database cho persistent storage
        # FirestoreUtils.add_audit_log(log_entry)
        
        return log_entry
    
    @staticmethod
    def log_security_event(
        event_type: str,
        description: str,
        severity: LogLevel = LogLevel.WARNING,
        additional_data: Dict = None
    ):
        """Log security events đặc biệt"""
        
        details = {
            "event_type": event_type,
            "description": description,
            "additional_data": additional_data or {}
        }
        
        AuditLogger.log_action(
            LogAction.SYSTEM_ERROR,
            details,
            level=severity
        )
    
    @staticmethod
    def log_certificate_action(
        action: LogAction,
        certificate_id: str,
        recipient_id: str = None,
        issuer_id: str = None,
        additional_details: Dict = None
    ):
        """Log các action liên quan đến certificate"""
        
        details = {
            "certificate_id": certificate_id,
            "recipient_id": recipient_id,
            "issuer_id": issuer_id
        }
        
        if additional_details:
            details.update(additional_details)
        
        AuditLogger.log_action(action, details)
    
    @staticmethod
    def log_admin_action(
        action: LogAction,
        target_id: str,
        target_type: str,
        admin_id: str = None,
        details: Dict = None
    ):
        """Log các action của admin"""
        
        log_details = {
            "target_id": target_id,
            "target_type": target_type,
            "admin_id": admin_id or session.get('user_id')
        }
        
        if details:
            log_details.update(details)
        
        AuditLogger.log_action(action, log_details, level=LogLevel.WARNING)


class PerformanceLogger:
    """Logger cho performance monitoring"""
    
    @staticmethod
    def log_slow_query(query: str, duration: float, threshold: float = 1.0):
        """Log slow database queries"""
        if duration > threshold:
            current_app.logger.warning(
                f"SLOW_QUERY: {query} took {duration:.2f}s"
            )
    
    @staticmethod
    def log_api_performance(endpoint: str, method: str, duration: float):
        """Log API response times"""
        current_app.logger.info(
            f"API_PERFORMANCE: {method} {endpoint} - {duration:.3f}s"
        )


def configure_logging(app):
    """Cấu hình logging cho ứng dụng"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Set log level
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    app.logger.setLevel(log_level)
    
    # File handler cho audit logs
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/achievo.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    # Console handler cho development
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    app.logger.info('Achievo application startup')
