
"""
Achievo NFT Certificate Contract - OpShin Implementation
Quản lý phát hành, xác thực và thu hồi chứng chỉ NFT trên Cardano
"""

from opshin.prelude import *


@dataclass
class CertificateMetadata(PlutusData):
    """Metadata của chứng chỉ NFT"""
    recipient_name: bytes
    issuer_name: bytes
    course_name: bytes
    issue_date: int
    certificate_hash: bytes


@dataclass
class CertificateAction(PlutusData):
    """Các hành động có thể thực hiện với chứng chỉ"""
    MINT = 0
    BURN = 1
    UPDATE = 2


@dataclass
class CertificateDatum(PlutusData):
    """Datum lưu trữ trạng thái chứng chỉ"""
    metadata: CertificateMetadata
    status: int  # 0: active, 1: revoked, 2: expired
    issuer_pubkey: bytes
    recipient_address: bytes


@dataclass
class CertificateRedeemer(PlutusData):
    """Redeemer cho các thao tác với chứng chỉ"""
    action: CertificateAction
    signature: bytes


def validator(
    datum: CertificateDatum,
    redeemer: CertificateRedeemer,
    context: ScriptContext
) -> bool:
    """
    Validator chính cho NFT Certificate contract
    """
    purpose = context.purpose
    
    # Chỉ cho phép spending
    if not isinstance(purpose, Spending):
        return False
        
    tx_info = context.tx_info
    
    # Kiểm tra action trong redeemer
    if redeemer.action == CertificateAction.MINT:
        return validate_mint(datum, redeemer, tx_info)
    elif redeemer.action == CertificateAction.BURN:
        return validate_burn(datum, redeemer, tx_info)
    elif redeemer.action == CertificateAction.UPDATE:
        return validate_update(datum, redeemer, tx_info)
    
    return False


def validate_mint(
    datum: CertificateDatum,
    redeemer: CertificateRedeemer,
    tx_info: TxInfo
) -> bool:
    """Xác thực việc mint chứng chỉ NFT mới"""
    
    # Kiểm tra chữ ký của issuer
    if not verify_signature(datum.issuer_pubkey, redeemer.signature, tx_info):
        return False
    
    # Kiểm tra chỉ mint 1 NFT
    minted_tokens = get_minted_tokens(tx_info)
    if len(minted_tokens) != 1:
        return False
    
    # Kiểm tra NFT được gửi đến đúng địa chỉ recipient
    outputs_to_recipient = [
        output for output in tx_info.outputs
        if output.address == datum.recipient_address
    ]
    
    if len(outputs_to_recipient) != 1:
        return False
    
    # Kiểm tra output chứa NFT và datum
    recipient_output = outputs_to_recipient[0]
    if not contains_nft_token(recipient_output, minted_tokens[0]):
        return False
    
    return True


def validate_burn(
    datum: CertificateDatum,
    redeemer: CertificateRedeemer,
    tx_info: TxInfo
) -> bool:
    """Xác thực việc burn (thu hồi) chứng chỉ NFT"""
    
    # Kiểm tra chữ ký của issuer (chỉ issuer mới có thể burn)
    if not verify_signature(datum.issuer_pubkey, redeemer.signature, tx_info):
        return False
    
    # Kiểm tra NFT bị burn
    burned_tokens = get_burned_tokens(tx_info)
    if len(burned_tokens) != 1:
        return False
    
    return True


def validate_update(
    datum: CertificateDatum,
    redeemer: CertificateRedeemer,
    tx_info: TxInfo
) -> bool:
    """Xác thực việc cập nhật trạng thái chứng chỉ"""
    
    # Kiểm tra chữ ký của issuer
    if not verify_signature(datum.issuer_pubkey, redeemer.signature, tx_info):
        return False
    
    # Kiểm tra có output trả về script với datum mới
    script_outputs = [
        output for output in tx_info.outputs
        if output.address == get_script_address(tx_info)
    ]
    
    if len(script_outputs) != 1:
        return False
    
    return True


def verify_signature(pubkey: bytes, signature: bytes, tx_info: TxInfo) -> bool:
    """Xác thực chữ ký số"""
    # Implementation sẽ sử dụng built-in crypto functions của Plutus
    # Placeholder cho signature verification
    return len(signature) > 0 and len(pubkey) > 0


def get_minted_tokens(tx_info: TxInfo) -> List[bytes]:
    """Lấy danh sách tokens được mint trong transaction"""
    minted = []
    for mint_entry in tx_info.mint:
        if mint_entry.amount > 0:
            minted.append(mint_entry.token_name)
    return minted


def get_burned_tokens(tx_info: TxInfo) -> List[bytes]:
    """Lấy danh sách tokens bị burn trong transaction"""
    burned = []
    for mint_entry in tx_info.mint:
        if mint_entry.amount < 0:
            burned.append(mint_entry.token_name)
    return burned


def contains_nft_token(output: TxOut, token_name: bytes) -> bool:
    """Kiểm tra output có chứa NFT token cụ thể"""
    for value_entry in output.value:
        if value_entry.token_name == token_name and value_entry.amount == 1:
            return True
    return False


def get_script_address(tx_info: TxInfo) -> bytes:
    """Lấy địa chỉ của script hiện tại"""
    # Implementation cụ thể sẽ trả về script hash
    return b"script_address_placeholder"


# Compile contract to Plutus Core
def compile_contract():
    """Biên dịch contract thành Plutus Core"""
    return validator
