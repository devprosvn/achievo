"""Utilities cho tương tác với Cardano blockchain qua Koios API, with API token support."""
import requests
import json
import hashlib
import os
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from flask import current_app


class KoiosClient:
    """Client cho Koios API"""

    def __init__(self, base_url: str = None):
        if base_url:
            self.base_url = base_url
        else:
            try:
                self.base_url = current_app.config['KOIOS_API_URL']
            except RuntimeError:
                # Default URL when not in app context
                self.base_url = 'https://api.koios.rest/api/v1'

        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def get_address_info(self, address: str) -> Dict:
        """Lấy thông tin của một địa chỉ Cardano"""
        endpoint = f"{self.base_url}/address_info"
        payload = {"_addresses": [address]}

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error getting address info: {e}")
            return {}

    def get_address_utxos(self, address: str) -> List[Dict]:
        """Lấy danh sách UTXOs của một địa chỉ"""
        endpoint = f"{self.base_url}/address_utxos"
        payload = {"_addresses": [address]}

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error getting UTXOs: {e}")
            return []

    def submit_transaction(self, tx_cbor: str) -> Dict:
        """Submit transaction lên blockchain"""
        endpoint = f"{self.base_url}/submittx"
        payload = {"_tx_cbor": tx_cbor}

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error submitting transaction: {e}")
            return {"error": str(e)}

    def get_transaction_info(self, tx_hash: str) -> Dict:
        """Lấy thông tin chi tiết của transaction"""
        endpoint = f"{self.base_url}/tx_info"
        payload = {"_tx_hashes": [tx_hash]}

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            return result[0] if result else {}
        except requests.RequestException as e:
            current_app.logger.error(f"Error getting transaction info: {e}")
            return {}

    def get_asset_info(self, policy_id: str, asset_name: str) -> Dict:
        """Lấy thông tin của một asset (NFT)"""
        endpoint = f"{self.base_url}/asset_info"
        asset_id = f"{policy_id}{asset_name}"
        payload = {"_asset_list": [asset_id]}

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            return result[0] if result else {}
        except requests.RequestException as e:
            current_app.logger.error(f"Error getting asset info: {e}")
            return {}


class CardanoUtils:
    """Utilities cho Cardano operations"""

    @staticmethod
    def validate_address(address: str) -> bool:
        """Kiểm tra tính hợp lệ của địa chỉ Cardano"""
        # Basic validation - trong thực tế sẽ dùng PyCardano
        return len(address) > 50 and address.startswith(('addr1', 'addr_test1'))

    @staticmethod
    def generate_nft_metadata(certificate_data: Dict) -> Dict:
        """Tạo metadata cho NFT certificate"""
        metadata = {
            "721": {
                "policy_id_placeholder": {
                    certificate_data["token_name"]: {
                        "name": certificate_data["name"],
                        "description": certificate_data.get("description", ""),
                        "image": certificate_data.get("image_url", ""),
                        "mediaType": "image/png",
                        "attributes": {
                            "recipient": certificate_data["recipient_name"],
                            "issuer": certificate_data["issuer_name"],
                            "course": certificate_data.get("course_name", ""),
                            "issue_date": certificate_data["issue_date"],
                            "certificate_type": certificate_data.get("type", "completion")
                        }
                    }
                }
            }
        }
        return metadata

    @staticmethod
    def calculate_min_ada(utxo_size: int) -> int:
        """Tính toán min ADA cần thiết cho UTXO"""
        # Cardano min UTXO calculation
        base_min_ada = 1000000  # 1 ADA in lovelace
        return base_min_ada + (utxo_size * 1000)

    @staticmethod
    def build_certificate_datum(certificate_data: Dict) -> str:
        """Xây dựng datum cho certificate UTXO"""
        datum = {
            "constructor": 0,
            "fields": [
                {"bytes": certificate_data["recipient_name"].encode().hex()},
                {"bytes": certificate_data["issuer_name"].encode().hex()},
                {"bytes": certificate_data["course_name"].encode().hex()},
                {"int": certificate_data["issue_timestamp"]},
                {"bytes": certificate_data["certificate_hash"]}
            ]
        }
        return json.dumps(datum)

    @staticmethod
    def verify_signature(data: Dict) -> bool:
        """Xác thực chữ ký từ ví Cardano"""
        try:
            # Helper function để thêm padding cho Base64 nếu thiếu
            def add_padding(base64_str):
                return base64_str + '=' * (-len(base64_str) % 4)

            # Log dữ liệu nhận được để debug
            print(f"Received signature: {data['signature']}")
            print(f"Received key: {data['key']}")

            # Kiểm tra xem dữ liệu có phải hex hay Base64
            try:
                # Thử hex trước (cho các ví khác)
                signature = bytes.fromhex(data["signature"])
                key = bytes.fromhex(data["key"])
                print("Successfully decoded as hex format")
            except ValueError:
                # Nếu không phải hex, thử Base64 (cho Lace wallet)
                try:
                    signature = base64.b64decode(add_padding(data["signature"]))
                    key = base64.b64decode(add_padding(data["key"]))
                    print("Successfully decoded as Base64 format")
                except Exception as e:
                    print(f"Failed to decode as both hex and Base64: {e}")
                    return False

            message = data["message"].encode('utf-8')

            # Tạo VerifyKey từ public key
            verify_key = VerifyKey(key)

            # Xác thực chữ ký
            verify_key.verify(message, signature)
            print("Signature verification successful")
            return True

        except (ValueError, BadSignatureError) as e:
            print(f"Signature verification failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error in signature verification: {e}")
            return False


def get_koios_client() -> KoiosClient:
    """Factory function để tạo Koios client"""
    return KoiosClient()