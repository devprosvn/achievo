
"""
Unit tests cho Firebase service
"""

import pytest
from unittest.mock import patch, MagicMock
from app.utils.firebase import FirebaseService


class TestFirebaseService:
    """Test Firebase service"""
    
    @patch('app.utils.firebase.firebase_admin')
    @patch('app.utils.firebase.firestore')
    def test_create_user(self, mock_firestore, mock_firebase_admin):
        """Test user creation"""
        mock_db = MagicMock()
        mock_firestore.client.return_value = mock_db
        
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = 'user_123'
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        service = FirebaseService()
        
        user_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'user_type': 'learner'
        }
        
        user_id = service.create_user(user_data)
        assert user_id == 'user_123'
    
    @patch('app.utils.firebase.firebase_admin')
    @patch('app.utils.firebase.firestore')
    def test_authenticate_user(self, mock_firestore, mock_firebase_admin):
        """Test user authentication"""
        mock_db = MagicMock()
        mock_firestore.client.return_value = mock_db
        
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            'email': 'test@example.com',
            'password_hash': 'hashed_password'
        }
        mock_doc.id = 'user_123'
        
        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_doc]
        mock_db.collection.return_value.where.return_value.where.return_value.limit.return_value = mock_query
        
        service = FirebaseService()
        
        user = service.authenticate_user('test@example.com', 'hashed_password')
        assert user is not None
        assert user['id'] == 'user_123'
        assert user['email'] == 'test@example.com'
