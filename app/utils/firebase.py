
"""
Firebase integration utilities
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os


class FirebaseService:
    """Service để tương tác với Firestore"""
    
    def __init__(self):
        if not firebase_admin._apps:
            # Initialize Firebase
            service_account_path = os.path.join(os.path.dirname(__file__), '../../attached_assets/serviceAccountKey.json')
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
    
    def create_user(self, user_data: Dict) -> str:
        """Tạo user mới trong Firestore"""
        try:
            user_ref = self.db.collection('users').document()
            user_data.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'status': 'active'
            })
            user_ref.set(user_data)
            return user_ref.id
        except Exception as e:
            raise Exception(f"Error creating user: {e}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Lấy thông tin user"""
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            raise Exception(f"Error getting user: {e}")
    
    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """Cập nhật thông tin user"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            self.db.collection('users').document(user_id).update(update_data)
            return True
        except Exception as e:
            raise Exception(f"Error updating user: {e}")
    
    def authenticate_user(self, email: str, password_hash: str) -> Optional[Dict]:
        """Xác thực user qua email và password"""
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where('email', '==', email).where('password_hash', '==', password_hash).limit(1)
            docs = query.stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            raise Exception(f"Error authenticating user: {e}")
    
    def create_certificate(self, cert_data: Dict) -> str:
        """Tạo certificate record"""
        try:
            cert_ref = self.db.collection('certificates').document()
            cert_data.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'status': 'active'
            })
            cert_ref.set(cert_data)
            return cert_ref.id
        except Exception as e:
            raise Exception(f"Error creating certificate: {e}")
    
    def get_certificate(self, cert_id: str) -> Optional[Dict]:
        """Lấy thông tin certificate"""
        try:
            doc = self.db.collection('certificates').document(cert_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            raise Exception(f"Error getting certificate: {e}")
    
    def verify_certificate_by_id(self, cert_id: str) -> Optional[Dict]:
        """Xác thực certificate bằng ID"""
        return self.get_certificate(cert_id)
    
    def get_user_certificates(self, user_id: str) -> List[Dict]:
        """Lấy danh sách certificates của user"""
        try:
            certs_ref = self.db.collection('certificates')
            query = certs_ref.where('recipient_id', '==', user_id)
            docs = query.stream()
            
            certificates = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                certificates.append(data)
            return certificates
        except Exception as e:
            raise Exception(f"Error getting user certificates: {e}")
    
    def create_organization(self, org_data: Dict) -> str:
        """Tạo organization"""
        try:
            org_ref = self.db.collection('organizations').document()
            org_data.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'status': 'pending_approval'
            })
            org_ref.set(org_data)
            return org_ref.id
        except Exception as e:
            raise Exception(f"Error creating organization: {e}")
    
    def get_pending_organizations(self) -> List[Dict]:
        """Lấy danh sách organizations chờ phê duyệt"""
        try:
            orgs_ref = self.db.collection('organizations')
            query = orgs_ref.where('status', '==', 'pending_approval')
            docs = query.stream()
            
            organizations = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                organizations.append(data)
            return organizations
        except Exception as e:
            raise Exception(f"Error getting pending organizations: {e}")
    
    def approve_organization(self, org_id: str) -> bool:
        """Phê duyệt organization"""
        try:
            self.db.collection('organizations').document(org_id).update({
                'status': 'approved',
                'approved_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            return True
        except Exception as e:
            raise Exception(f"Error approving organization: {e}")
    
    def log_action(self, log_data: Dict) -> str:
        """Ghi log hành động"""
        try:
            log_ref = self.db.collection('audit_logs').document()
            log_data.update({
                'timestamp': datetime.utcnow()
            })
            log_ref.set(log_data)
            return log_ref.id
        except Exception as e:
            raise Exception(f"Error logging action: {e}")
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Lấy logs gần đây"""
        try:
            logs_ref = self.db.collection('audit_logs')
            query = logs_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            
            logs = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                logs.append(data)
            return logs
        except Exception as e:
            raise Exception(f"Error getting recent logs: {e}")
    
    def create_course(self, course_data: Dict) -> str:
        """Tạo khóa học"""
        try:
            course_ref = self.db.collection('courses').document()
            course_data.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'status': 'active'
            })
            course_ref.set(course_data)
            return course_ref.id
        except Exception as e:
            raise Exception(f"Error creating course: {e}")
    
    def get_marketplace_courses(self) -> List[Dict]:
        """Lấy danh sách khóa học trên marketplace"""
        try:
            courses_ref = self.db.collection('courses')
            query = courses_ref.where('status', '==', 'active').where('is_published', '==', True)
            docs = query.stream()
            
            courses = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                courses.append(data)
            return courses
        except Exception as e:
            raise Exception(f"Error getting marketplace courses: {e}")
    
    def create_reward(self, reward_data: Dict) -> str:
        """Tạo phần thưởng"""
        try:
            reward_ref = self.db.collection('rewards').document()
            reward_data.update({
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'status': 'active'
            })
            reward_ref.set(reward_data)
            return reward_ref.id
        except Exception as e:
            raise Exception(f"Error creating reward: {e}")
    
    def get_user_rewards(self, user_id: str) -> List[Dict]:
        """Lấy phần thưởng của user"""
        try:
            rewards_ref = self.db.collection('rewards')
            query = rewards_ref.where('user_id', '==', user_id)
            docs = query.stream()
            
            rewards = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                rewards.append(data)
            return rewards
        except Exception as e:
            raise Exception(f"Error getting user rewards: {e}")


# Singleton instance
firebase_service = FirebaseService()
