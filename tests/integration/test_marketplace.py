
"""
Integration tests cho marketplace
"""

import pytest
from unittest.mock import patch, MagicMock
from app.backend import create_app
from app.utils.marketplace import marketplace_service, reward_service
import json


class TestMarketplaceIntegration:
    """Test tích hợp marketplace"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app('testing')
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_marketplace_page_loads(self, client):
        """Test marketplace page loads correctly"""
        response = client.get('/marketplace')
        assert response.status_code == 200
        assert b'Marketplace' in response.data
    
    @patch('app.utils.marketplace.firebase_service')
    def test_create_course_listing(self, mock_firebase):
        """Test creating course listing"""
        mock_firebase.create_course.return_value = 'course_123'
        
        course_data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'price': 100,
            'category': 'programming'
        }
        
        course_id = marketplace_service.create_course_listing(course_data, 'user_123')
        assert course_id == 'course_123'
        mock_firebase.create_course.assert_called_once()
    
    @patch('app.utils.marketplace.firebase_service')
    def test_reward_milestone_check(self, mock_firebase):
        """Test milestone reward checking"""
        # Mock user with 5 certificates
        mock_firebase.get_user_certificates.return_value = [
            {'id': f'cert_{i}'} for i in range(5)
        ]
        mock_firebase.get_user_rewards.return_value = []
        mock_firebase.create_reward.return_value = 'reward_123'
        
        rewards = reward_service.check_milestone_rewards('user_123')
        
        # Should create rewards for first certificate and five certificates
        assert len(rewards) == 2
        assert any(r['milestone_type'] == 'first_certificate' for r in rewards)
        assert any(r['milestone_type'] == 'five_certificates' for r in rewards)
