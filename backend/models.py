from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class CommanderProfile(BaseModel):
    user_id: str
    username: str
    wallet_address: Optional[str] = None
    points: int = 100
    sequencer_level: int = 1       # Üs Sequencer Seviyesi (1 - 10)
    paymaster_vault_level: int = 1 # Gaz Kasa Seviyesi
    shield_active_until: float = 0 # Siber Kalkan Bitiş Zamanı (Timestamp)
    last_farm_time: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    ads_watched_today: int = 0     # Günlük izlenen reklam sayısı
    nft_minted: bool = False       # OG Pioneer veya Cyber Commander NFT durumu

class NodeUpgradeRequest(BaseModel):
    user_id: str
    upgrade_type: str  # 'sequencer' veya 'paymaster'

class AdsgramRewardRequest(BaseModel):
    user_id: str
    reward_type: str  # 'boost', 'shield', 'gas_refill'
