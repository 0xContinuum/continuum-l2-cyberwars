from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class CommanderProfile(BaseModel):
    user_id: str
    username: str
    wallet_address: Optional[str] = None
    points: int = 150
    ctm_balance: float = 5.0  # Mainnet CTM başlangıç bakiyesi
    sequencer_level: int = 1       # Üs Sequencer Seviyesi
    paymaster_vault_level: int = 1 # Gaz Kasa Seviyesi
    shield_active_until: float = 0 # Siber Kalkan Bitiş Zamanı (Timestamp)
    last_farm_time: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    ads_watched_today: int = 0     # Günlük izlenen reklam sayısı
    nft_minted: bool = False       # OG Pioneer veya Cyber Commander NFT durumu
    clan_id: Optional[str] = None  # Bağlı olduğu Clan / İş Ortağı ID'si

class ChatMessage(BaseModel):
    sender_id: str
    sender_name: str
    message: str
    timestamp: float
    channel: str = "global"  # 'global' veya clan_id

class PayoutRequest(BaseModel):
    id: int
    partner_username: str
    clan_id: str
    requested_amount: float
    wallet_address: str
    status: str = "Pending"  # Pending, Approved, Rejected
    timestamp: float
