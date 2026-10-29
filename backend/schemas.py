from pydantic import BaseModel, Field
from typing import Optional

class CommanderResponse(BaseModel):
    user_id: str
    username: str
    wallet_address: Optional[str] = None
    points: int
    ctm_balance: float
    sequencer_level: int
    paymaster_vault_level: int
    shield_active_until: float
    ads_watched_today: int
    nft_minted: bool
    clan_id: Optional[str] = None

    class Config:
        from_attributes = True

class NodeUpgradeRequest(BaseModel):
    user_id: str
    upgrade_type: str  # 'sequencer' veya 'paymaster'

class AdsgramRewardRequest(BaseModel):
    user_id: str
    reward_type: str  # 'shield', 'boost', 'gas_refill', 'faucet_ad'

class WalletRegisterRequest(BaseModel):
    user_id: str
    username: Optional[str] = "CyberCommander"
    wallet_address: str

class SendMessageRequest(BaseModel):
    user_id: str
    sender_name: str
    message: str
    channel: str = "global"

class PayoutClaimRequest(BaseModel):
    partner_username: str
    clan_id: str
    wallet_address: str
    amount: float

class CreateClanRequest(BaseModel):
    admin_username: str
    partner_username: str
    clan_name: str
    clan_id: str
