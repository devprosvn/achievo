
"""
Unit tests cho Cardano utilities
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from app.utils.cardano import KoiosClient, CardanoUtils


class TestKoiosClient:
    """Test Koios API client"""
    
    @patch('app.utils.cardano.current_app')
    def test_koios_client_initialization(self, mock_app):
        """Test KoiosClient initialization"""
        mock_app.config = {'KOIOS_API_URL': 'https://test.koios.rest/api/v1'}
        
        client = KoiosClient()
        assert client.base_url == 'https://test.koios.rest/api/v1'
        assert 'Content-Type' in client.session.headers
    
    @patch('requests.Session.post')
    @patch('app.utils.cardano.current_app')
    def test_get_address_info_success(self, mock_app, mock_post):
        """Test successful address info retrieval"""
        mock_app.config = {'KOIOS_API_URL': 'https://test.koios.rest/api/v1'}
        
        mock_response = MagicMock()
        mock_response.json.return_value = [{"address": "test_address", "balance": "1000000"}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = KoiosClient()
        result = client.get_address_info("test_address")
        
        assert isinstance(result, list)
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    @patch('app.utils.cardano.current_app')
    def test_get_address_info_error(self, mock_app, mock_post):
        """Test error handling in address info retrieval"""
        mock_app.config = {'KOIOS_API_URL': 'https://test.koios.rest/api/v1'}
        mock_app.logger = MagicMock()
        
        mock_post.side_effect = requests.RequestException("Network error")
        
        client = KoiosClient()
        result = client.get_address_info("test_address")
        
        assert result == {}
        mock_app.logger.error.assert_called_once()


class TestCardanoUtils:
    """Test Cardano utilities"""
    
    def test_validate_address_valid(self):
        """Test valid Cardano address validation"""
        valid_address = "addr1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwq2ytjqp"
        assert CardanoUtils.validate_address(valid_address) is True
        
        valid_testnet = "addr_test1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwq123456"
        assert CardanoUtils.validate_address(valid_testnet) is True
    
    def test_validate_address_invalid(self):
        """Test invalid Cardano address validation"""
        invalid_addresses = [
            "short_address",
            "invalid_prefix_123456789012345678901234567890",
            "",
            "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"  # Bitcoin address
        ]
        
        for address in invalid_addresses:
            assert CardanoUtils.validate_address(address) is False
    
    def test_generate_nft_metadata(self):
        """Test NFT metadata generation"""
        certificate_data = {
            "token_name": "CERT001",
            "name": "Test Certificate",
            "description": "Test certificate description",
            "image_url": "https://example.com/image.png",
            "recipient_name": "John Doe",
            "issuer_name": "Test University",
            "course_name": "Python Programming",
            "issue_date": "2024-01-01",
            "type": "completion"
        }
        
        metadata = CardanoUtils.generate_nft_metadata(certificate_data)
        
        assert "721" in metadata
        assert "policy_id_placeholder" in metadata["721"]
        assert certificate_data["token_name"] in metadata["721"]["policy_id_placeholder"]
        
        token_metadata = metadata["721"]["policy_id_placeholder"][certificate_data["token_name"]]
        assert token_metadata["name"] == certificate_data["name"]
        assert token_metadata["attributes"]["recipient"] == certificate_data["recipient_name"]
    
    def test_calculate_min_ada(self):
        """Test min ADA calculation"""
        utxo_size = 1000
        min_ada = CardanoUtils.calculate_min_ada(utxo_size)
        
        assert min_ada >= 1000000  # At least 1 ADA
        assert isinstance(min_ada, int)


if __name__ == "__main__":
    pytest.main([__file__])
