import os
import json
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from models import CommanderProfile, NodeUpgradeRequest, AdsgramRewardRequest

app = FastAPI(title="Continuum: L2 Cyber Wars API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "cyberwars_database.json"
BASE_SEPOLIA_RPC = "https://sepolia.base.org"
w3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"commanders": {}, "alliances": {}}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Veritabanı kayıt hatası: {e}")

@app.get("/")
def read_root():
    return {"status": "online", "game": "Continuum: L2 Cyber Wars API Active!"}

@app.get("/api/commander-info")
def get_commander(user_id: str):
    db = load_db()
    commanders = db.setdefault("commanders", {})
    
    if user_id not in commanders:
        # Yeni Komutan Profili Oluştur
        new_commander = CommanderProfile(
            user_id=user_id,
            username=f"Commander_{user_id[-4:]}",
            points=150,
            sequencer_level=1,
            paymaster_vault_level=1
        ).dict()
        commanders[user_id] = new_commander
        save_db(db)
    
    return {"success": True, "commander": commanders[user_id]}

@app.post("/api/upgrade-node")
def upgrade_node(req: NodeUpgradeRequest):
    db = load_db()
    commanders = db.get("commanders", {})
    
    if req.user_id not in commanders:
        raise HTTPException(status_code=404, detail="Komutan bulunamadı.")
    
    cmd = commanders[req.user_id]
    upgrade_cost = 500 * (cmd["sequencer_level"] if req.upgrade_type == 'sequencer' else cmd["paymaster_vault_level"])
    
    if cmd["points"] < upgrade_cost:
        raise HTTPException(status_code=400, detail=f"Yetersiz puan! Gerekli: {upgrade_cost} PTS")
    
    cmd["points"] -= upgrade_cost
    if req.upgrade_type == 'sequencer':
        cmd["sequencer_level"] += 1
    elif req.upgrade_type == 'paymaster':
        cmd["paymaster_vault_level"] += 1
    
    save_db(db)
    return {"success": True, "message": "Üs başarıyla yükseltildi!", "commander": cmd}

@app.post("/api/adsgram-reward")
def claim_adsgram_reward(req: AdsgramRewardRequest):
    """Adsgram reklamı izlendiğinde çağrılan stratejik hızlandırma kancası (Kumar/Şans yok, tamamen buff/hızlandırma)."""
    db = load_db()
    commanders = db.get("commanders", {})
    
    if req.user_id not in commanders:
        raise HTTPException(status_code=404, detail="Komutan bulunamadı.")
    
    cmd = commanders[req.user_id]
    now = datetime.utcnow().timestamp()
    
    if req.reward_type == 'shield':
        # 2 Saatlik Siber Kalkan Aktifleştirme
        cmd["shield_active_until"] = now + 7200
        msg = "🛡️ 2 Saatlik Siber Kalkan Aktif Edildi!"
    elif req.reward_type == 'boost':
        # Anında +250 Puan Stratejik Kaynak
        cmd["points"] += 250
        msg = "⚡ Stratejik Kaynak Takviyesi: +250 PTS!"
    elif req.reward_type == 'gas_refill':
        cmd["paymaster_vault_level"] += 0.5
        msg = "⛽ Paymaster Gaz Kapasitesi Artırıldı!"
    else:
        raise HTTPException(status_code=400, detail="Geçersiz ödül türü.")
    
    cmd["ads_watched_today"] += 1
    save_db(db)
    return {"success": True, "message": msg, "commander": cmd}

@app.post("/api/register-wallet")
def register_wallet(data: dict):
    user_id = str(data.get("user_id"))
    wallet_address = data.get("wallet_address")
    username = data.get("username", "CyberCommander")
    
    if not wallet_address or not Web3.is_address(wallet_address):
        raise HTTPException(status_code=400, detail="Geçersiz cüzdan adresi.")
    
    db = load_db()
    commanders = db.setdefault("commanders", {})
    
    if user_id not in commanders:
        commanders[user_id] = CommanderProfile(user_id=user_id, username=username).dict()
    
    commanders[user_id]["wallet_address"] = Web3.to_checksum_address(wallet_address)
    commanders[user_id]["username"] = username
    save_db(db)
    
    return {"success": True, "message": "Cüzdan başarıyla eşlendi."}
