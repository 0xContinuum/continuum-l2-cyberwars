from pydantic import BaseModel, Field
from typing import Optional

class CommanderResponse(BaseModel):
    user_id: str
    username: str
    wallet_address: Optional[str] = None
    points: int
    sequencer_level: int
    paymaster_vault_level: int
    shield_active_until: float
    ads_watched_today: int
    nft_minted: bool

    class Config:
        from_attributes = True

class NodeUpgradeRequest(BaseModel):
    user_id: str
    upgrade_type: str  # 'sequencer' veya 'paymaster'

class AdsgramRewardRequest(BaseModel):
    user_id: str
    reward_type: str  # 'shield', 'boost', 'gas_refill'

class WalletRegisterRequest(BaseModel):
    user_id: str
    username: Optional[str] = "CyberCommander"
    wallet_address: str
