
"""
Marketplace service for courses and rewards
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .firebase import firebase_service
from .cardano import CardanoUtils, get_koios_client
from .logging import AuditLogger, LogAction


class MarketplaceService:
    """Service quản lý marketplace"""
    
    def __init__(self):
        self.firebase = firebase_service
        self.cardano = get_koios_client()
    
    def create_course_listing(self, course_data: Dict, creator_id: str) -> str:
        """Tạo listing khóa học trên marketplace"""
        try:
            course_data.update({
                'creator_id': creator_id,
                'is_published': True,
                'listing_type': 'course',
                'created_at': datetime.utcnow(),
                'sales_count': 0,
                'rating': 0.0,
                'reviews_count': 0
            })
            
            course_id = self.firebase.create_course(course_data)
            
            AuditLogger.log_action(
                LogAction.MARKETPLACE_CREATE,
                {"course_id": course_id, "title": course_data.get('title')},
                user_id=creator_id
            )
            
            return course_id
            
        except Exception as e:
            raise Exception(f"Error creating course listing: {e}")
    
    def get_marketplace_listings(self, category: Optional[str] = None, 
                               search: Optional[str] = None) -> List[Dict]:
        """Lấy danh sách courses trên marketplace"""
        try:
            courses = self.firebase.get_marketplace_courses()
            
            # Filter by category
            if category:
                courses = [c for c in courses if c.get('category') == category]
            
            # Filter by search term
            if search:
                search_lower = search.lower()
                courses = [c for c in courses 
                          if search_lower in c.get('title', '').lower() or 
                             search_lower in c.get('description', '').lower()]
            
            return courses
            
        except Exception as e:
            raise Exception(f"Error getting marketplace listings: {e}")
    
    def purchase_course(self, course_id: str, buyer_id: str, 
                       payment_tx_hash: str) -> Dict:
        """Mua khóa học với Cardano"""
        try:
            # Verify transaction on Cardano
            tx_info = self.cardano.get_transaction_info(payment_tx_hash)
            if not tx_info:
                raise Exception("Transaction not found on blockchain")
            
            # Get course info
            course = self.firebase.db.collection('courses').document(course_id).get()
            if not course.exists:
                raise Exception("Course not found")
            
            course_data = course.to_dict()
            
            # Create purchase record
            purchase_data = {
                'course_id': course_id,
                'buyer_id': buyer_id,
                'seller_id': course_data['creator_id'],
                'amount': course_data['price'],
                'currency': 'ADA',
                'tx_hash': payment_tx_hash,
                'status': 'completed',
                'purchased_at': datetime.utcnow()
            }
            
            purchase_ref = self.firebase.db.collection('purchases').document()
            purchase_ref.set(purchase_data)
            
            # Update course sales count
            self.firebase.db.collection('courses').document(course_id).update({
                'sales_count': firestore.Increment(1)
            })
            
            # Grant access to buyer
            access_data = {
                'user_id': buyer_id,
                'course_id': course_id,
                'access_type': 'full',
                'granted_at': datetime.utcnow(),
                'expires_at': None  # Lifetime access
            }
            
            self.firebase.db.collection('course_access').document().set(access_data)
            
            AuditLogger.log_action(
                LogAction.MARKETPLACE_PURCHASE,
                {
                    "course_id": course_id,
                    "amount": course_data['price'],
                    "tx_hash": payment_tx_hash
                },
                user_id=buyer_id
            )
            
            return {
                'purchase_id': purchase_ref.id,
                'status': 'success',
                'access_granted': True
            }
            
        except Exception as e:
            raise Exception(f"Error processing course purchase: {e}")
    
    def check_course_access(self, user_id: str, course_id: str) -> bool:
        """Kiểm tra quyền truy cập khóa học"""
        try:
            access_ref = self.firebase.db.collection('course_access')
            query = access_ref.where('user_id', '==', user_id).where('course_id', '==', course_id)
            docs = list(query.stream())
            
            if not docs:
                return False
            
            access_data = docs[0].to_dict()
            
            # Check if access expired
            if access_data.get('expires_at'):
                if datetime.utcnow() > access_data['expires_at']:
                    return False
            
            return True
            
        except Exception as e:
            return False


class RewardService:
    """Service quản lý phần thưởng tự động"""
    
    def __init__(self):
        self.firebase = firebase_service
        self.cardano = get_koios_client()
    
    def check_milestone_rewards(self, user_id: str) -> List[Dict]:
        """Kiểm tra và tự động cấp phần thưởng milestone"""
        try:
            # Get user progress
            user_certs = self.firebase.get_user_certificates(user_id)
            user_rewards = self.firebase.get_user_rewards(user_id)
            
            new_rewards = []
            
            # Milestone: First certificate
            if len(user_certs) >= 1 and not self._has_reward(user_rewards, 'first_certificate'):
                reward = self._create_milestone_reward(
                    user_id, 
                    'first_certificate',
                    'First Certificate Achievement',
                    'Congratulations on earning your first certificate!'
                )
                new_rewards.append(reward)
            
            # Milestone: 5 certificates
            if len(user_certs) >= 5 and not self._has_reward(user_rewards, 'five_certificates'):
                reward = self._create_milestone_reward(
                    user_id,
                    'five_certificates', 
                    'Certificate Collector',
                    'Excellent! You have earned 5 certificates!'
                )
                new_rewards.append(reward)
            
            # Milestone: 10 certificates
            if len(user_certs) >= 10 and not self._has_reward(user_rewards, 'ten_certificates'):
                reward = self._create_milestone_reward(
                    user_id,
                    'ten_certificates',
                    'Certificate Master',
                    'Outstanding! You are a true learning champion!'
                )
                new_rewards.append(reward)
            
            return new_rewards
            
        except Exception as e:
            raise Exception(f"Error checking milestone rewards: {e}")
    
    def _has_reward(self, rewards: List[Dict], milestone_type: str) -> bool:
        """Kiểm tra user đã có reward này chưa"""
        return any(r.get('milestone_type') == milestone_type for r in rewards)
    
    def _create_milestone_reward(self, user_id: str, milestone_type: str, 
                                title: str, description: str) -> Dict:
        """Tạo NFT reward cho milestone"""
        try:
            # Generate NFT metadata
            nft_metadata = {
                'name': title,
                'description': description,
                'image': f'https://achievo.com/rewards/{milestone_type}.png',
                'attributes': {
                    'milestone_type': milestone_type,
                    'earned_date': datetime.utcnow().isoformat(),
                    'recipient': user_id
                }
            }
            
            # Create reward record
            reward_data = {
                'user_id': user_id,
                'milestone_type': milestone_type,
                'title': title,
                'description': description,
                'reward_type': 'nft',
                'nft_metadata': nft_metadata,
                'status': 'pending_mint',
                'earned_at': datetime.utcnow()
            }
            
            reward_id = self.firebase.create_reward(reward_data)
            
            # TODO: Mint NFT on Cardano blockchain
            # This would involve creating transaction with OpShin contract
            
            AuditLogger.log_action(
                LogAction.REWARD_EARNED,
                {
                    "reward_id": reward_id,
                    "milestone_type": milestone_type,
                    "title": title
                },
                user_id=user_id
            )
            
            reward_data['id'] = reward_id
            return reward_data
            
        except Exception as e:
            raise Exception(f"Error creating milestone reward: {e}")
    
    def process_pending_rewards(self):
        """Xử lý các rewards đang chờ mint NFT"""
        try:
            # Get pending rewards
            rewards_ref = self.firebase.db.collection('rewards')
            query = rewards_ref.where('status', '==', 'pending_mint')
            pending_rewards = query.stream()
            
            for reward_doc in pending_rewards:
                reward_data = reward_doc.to_dict()
                reward_id = reward_doc.id
                
                try:
                    # TODO: Implement NFT minting logic with OpShin
                    # For now, mark as completed
                    self.firebase.db.collection('rewards').document(reward_id).update({
                        'status': 'completed',
                        'tx_hash': f'mock_reward_tx_{reward_id}',
                        'minted_at': datetime.utcnow()
                    })
                    
                    AuditLogger.log_action(
                        LogAction.REWARD_MINTED,
                        {
                            "reward_id": reward_id,
                            "tx_hash": f'mock_reward_tx_{reward_id}'
                        },
                        user_id=reward_data['user_id']
                    )
                    
                except Exception as mint_error:
                    # Mark as failed
                    self.firebase.db.collection('rewards').document(reward_id).update({
                        'status': 'failed',
                        'error_message': str(mint_error),
                        'failed_at': datetime.utcnow()
                    })
                    
        except Exception as e:
            raise Exception(f"Error processing pending rewards: {e}")


# Service instances
marketplace_service = MarketplaceService()
reward_service = RewardService()
