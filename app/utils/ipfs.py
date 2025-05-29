
"""
Utilities cho tương tác với IPFS/Pinata
"""
import requests
import json
from typing import Dict, Optional
from flask import current_app


class PinataClient:
    """Client cho Pinata IPFS service"""
    
    def __init__(self):
        self.api_key = current_app.config['PINATA_API_KEY']
        self.secret_key = current_app.config['PINATA_SECRET_KEY']
        self.base_url = "https://api.pinata.cloud"
        
        self.headers = {
            'pinata_api_key': self.api_key,
            'pinata_secret_api_key': self.secret_key
        }
    
    def pin_json_to_ipfs(self, json_data: Dict, name: str = None) -> Dict:
        """Pin JSON data lên IPFS"""
        url = f"{self.base_url}/pinning/pinJSONToIPFS"
        
        payload = {
            "pinataContent": json_data,
            "pinataMetadata": {
                "name": name or "achievo_metadata"
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error pinning JSON to IPFS: {e}")
            return {"error": str(e)}
    
    def pin_file_to_ipfs(self, file_data: bytes, filename: str) -> Dict:
        """Pin file lên IPFS"""
        url = f"{self.base_url}/pinning/pinFileToIPFS"
        
        files = {
            'file': (filename, file_data)
        }
        
        metadata = {
            'name': filename,
            'keyvalues': {
                'service': 'achievo',
                'type': 'certificate_image'
            }
        }
        
        data = {
            'pinataMetadata': json.dumps(metadata)
        }
        
        try:
            response = requests.post(url, files=files, data=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error pinning file to IPFS: {e}")
            return {"error": str(e)}
    
    def get_pinned_data(self, ipfs_hash: str) -> Optional[Dict]:
        """Lấy dữ liệu đã pin từ IPFS hash"""
        gateway_url = f"{current_app.config['IPFS_GATEWAY']}{ipfs_hash}"
        
        try:
            response = requests.get(gateway_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error getting IPFS data: {e}")
            return None
    
    def unpin_from_ipfs(self, ipfs_hash: str) -> bool:
        """Unpin dữ liệu từ IPFS"""
        url = f"{self.base_url}/pinning/unpin/{ipfs_hash}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            current_app.logger.error(f"Error unpinning from IPFS: {e}")
            return False
    
    def list_pinned_files(self, status: str = "pinned") -> List[Dict]:
        """Liệt kê các file đã pin"""
        url = f"{self.base_url}/data/pinList"
        params = {"status": status}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('rows', [])
        except requests.RequestException as e:
            current_app.logger.error(f"Error listing pinned files: {e}")
            return []


class IPFSUtils:
    """Utilities cho IPFS operations"""
    
    @staticmethod
    def create_certificate_metadata(certificate_data: Dict) -> Dict:
        """Tạo metadata cho certificate"""
        metadata = {
            "name": certificate_data["name"],
            "description": certificate_data.get("description", ""),
            "image": certificate_data.get("image_ipfs_url", ""),
            "external_url": certificate_data.get("external_url", ""),
            "attributes": [
                {
                    "trait_type": "Recipient",
                    "value": certificate_data["recipient_name"]
                },
                {
                    "trait_type": "Issuer",
                    "value": certificate_data["issuer_name"]
                },
                {
                    "trait_type": "Course",
                    "value": certificate_data.get("course_name", "")
                },
                {
                    "trait_type": "Issue Date",
                    "value": certificate_data["issue_date"]
                },
                {
                    "trait_type": "Certificate Type",
                    "value": certificate_data.get("type", "completion")
                },
                {
                    "trait_type": "Grade",
                    "value": certificate_data.get("grade", "")
                }
            ],
            "properties": {
                "achievo_version": "1.0",
                "certificate_id": certificate_data["certificate_id"],
                "verification_url": f"https://achievo.app/verify/{certificate_data['certificate_id']}"
            }
        }
        return metadata
    
    @staticmethod
    def validate_ipfs_hash(ipfs_hash: str) -> bool:
        """Kiểm tra tính hợp lệ của IPFS hash"""
        # Basic validation for IPFS hash
        return len(ipfs_hash) == 46 and ipfs_hash.startswith('Qm')
    
    @staticmethod
    def get_ipfs_url(ipfs_hash: str) -> str:
        """Tạo URL IPFS từ hash"""
        return f"{current_app.config['IPFS_GATEWAY']}{ipfs_hash}"


def get_pinata_client() -> PinataClient:
    """Factory function để tạo Pinata client"""
    return PinataClient()
