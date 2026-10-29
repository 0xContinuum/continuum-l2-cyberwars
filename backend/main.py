import os
import json
import time
import threading
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from backend.models import CommanderProfile
from backend.schemas import (
    NodeUpgradeRequest, AdsgramRewardRequest, WalletRegisterRequest,
    SendMessageRequest, PayoutClaimRequest
)

app = FastAPI(title="Continuum: L2 Cyber Wars API", version="2.0.0")

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

# --- KEEP-ALIVE PING MEKANİZMASI (Render Uyumasın) ---
def self_ping():
    while True:
        try:
            url = os.getenv("RENDER_EXTERNAL_URL", "https://continuum-l2-cyberwars.onrender.com")
            requests.get(url, timeout=10)
        except Exception:
            pass
        time.sleep(840)  # Her 14 dakikada bir ping atar

threading.Thread(target=self_ping, daemon=True).start()

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "commanders": {}, 
        "clans": {
            "clan_teknohaber": {"name": "TeknoHaber Elite", "partner_username": "teknohaber", "total_ads": 0, "revenue_pool": 0.0}
        }, 
        "chats": [],
        "payout_requests": []
    }

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Veritabanı kayıt hatası: {e}")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    possible_paths = [
        os.path.join("frontend", "index.html"),
        os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"),
        "index.html"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>Cyberpunk UI index.html bulunamadı!</h1>"

@app.get("/api/commander-info")
def get_commander(user_id: str, clan_code: Optional[str] = None):
    db = load_db()
    commanders = db.setdefault("commanders", {})
    clans = db.get("clans", {})
    
    if user_id not in commanders:
        new_commander = CommanderProfile(
            user_id=user_id,
            username=f"Commander_{user_id[-4:]}",
            points=150,
            ctm_balance=5.0,
            sequencer_level=1,
            paymaster_vault_level=1,
            clan_id=clan_code if clan_code in clans else None
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
    db = load_db()
    commanders = db.get("commanders", {})
    clans = db.get("clans", {})
    
    if req.user_id not in commanders:
        raise HTTPException(status_code=404, detail="Komutan bulunamadı.")
    
    cmd = commanders[req.user_id]
    now = datetime.utcnow().timestamp()
    
    if req.reward_type == 'shield':
        cmd["shield_active_until"] = now + 7200
        msg = "🛡️ 2 Saatlik Siber Kalkan Aktif Edildi!"
    elif req.reward_type == 'boost':
        cmd["points"] += 250
        msg = "⚡ Stratejik Kaynak Takviyesi: +250 PTS!"
    elif req.reward_type == 'gas_refill':
        cmd["paymaster_vault_level"] += 0.5
        msg = "⛽ Paymaster Gaz Kapasitesi Artırıldı!"
    elif req.reward_type == 'faucet_ad':
        cmd["ctm_balance"] += 2.5
        msg = "💎 Reklam Onaylı +2.5 $CTM Faucet Yüklendi!"
    else:
        raise HTTPException(status_code=400, detail="Geçersiz ödül türü.")
    
    cmd["ads_watched_today"] += 1
    
    # Clan / Partner Gelir Havuzuna Katkı
    c_id = cmd.get("clan_id")
    if c_id and c_id in clans:
        clans[c_id]["total_ads"] += 1
        clans[c_id]["revenue_pool"] += 0.12  # Her reklam başına tahmini gelir (USDT)
        
    save_db(db)
    return {"success": True, "message": msg, "commander": cmd}

@app.post("/api/register-wallet")
def register_wallet(data: WalletRegisterRequest):
    if not data.wallet_address or not Web3.is_address(data.wallet_address):
        raise HTTPException(status_code=400, detail="Geçersiz cüzdan adresi.")
    
    db = load_db()
    commanders = db.setdefault("commanders", {})
    
    user_id = str(data.user_id)
    if user_id not in commanders:
        commanders[user_id] = CommanderProfile(user_id=user_id, username=data.username).dict()
    
    commanders[user_id]["wallet_address"] = Web3.to_checksum_address(data.wallet_address)
    commanders[user_id]["username"] = data.username
    save_db(db)
    
    return {"success": True, "message": "Cüzdan başarıyla eşlendi."}

# --- CHAT SİSTEMİ ENDPOINTLERİ ---
@app.get("/api/get-chats")
def get_chats(channel: str = "global"):
    db = load_db()
    chats = db.get("chats", [])
    filtered = [c for c in chats if c["channel"] == channel]
    return {"success": True, "chats": filtered[-50:]}

@app.post("/api/send-message")
def send_message(req: SendMessageRequest):
    db = load_db()
    new_msg = {
        "sender_id": req.user_id,
        "sender_name": req.sender_name,
        "message": req.message,
        "timestamp": datetime.utcnow().timestamp(),
        "channel": req.channel
    }
    db.setdefault("chats", []).append(new_msg)
    if len(db["chats"]) > 200:
        db["chats"] = db["chats"][-200:]
    save_db(db)
    return {"success": True}

# --- PARTNER DASHBOARD VE 100 USDT LİMİTLİ PAYOUT ---
@app.get("/api/partner-stats")
def get_partner_stats(partner_username: str):
    db = load_db()
    clans = db.get("clans", {})
    
    target_clan = None
    target_clan_id = None
    for c_id, c_data in clans.items():
        if c_data["partner_username"] == partner_username:
            target_clan = c_data
            target_clan_id = c_id
            break
            
    if not target_clan:
        raise HTTPException(status_code=403, detail="Yetkisiz partner hesabı.")
        
    total_revenue = target_clan["revenue_pool"]
    partner_share = total_revenue * 0.25  # %25 Ortaklık Payı
    member_count = sum(1 for cmd in db.get("commanders", {}).values() if cmd.get("clan_id") == target_clan_id)
    
    return {
        "success": True,
        "clan_name": target_clan["name"],
        "clan_id": target_clan_id,
        "member_count": member_count,
        "total_ads": target_clan["total_ads"],
        "total_revenue": round(total_revenue, 2),
        "partner_share": round(partner_share, 2),
        "payout_eligible": partner_share >= 100.0  # 100 USDT minimum sınır kuralı
    }

@app.post("/api/request-payout")
def request_payout(req: PayoutClaimRequest):
    db = load_db()
    clans = db.get("clans", {})
    clan = clans.get(req.clan_id)
    
    if not clan or clan["partner_username"] != req.partner_username:
        raise HTTPException(status_code=400, detail="Geçersiz clan veya partner.")
        
    share = clan["revenue_pool"] * 0.25
    if share < 100.0:
        raise HTTPException(status_code=400, detail="Minimum 100 USDT barajı henüz aşılmadı!")
        
    payout_req = {
        "id": len(db.get("payout_requests", [])) + 1,
        "partner_username": req.partner_username,
        "clan_id": req.clan_id,
        "requested_amount": round(share, 2),
        "wallet_address": req.wallet_address,
        "status": "Pending",
        "timestamp": datetime.utcnow().timestamp()
    }
    db.setdefault("payout_requests", []).append(payout_req)
    save_db(db)
    return {"success": True, "message": "Ödeme talebiniz admin onayına iletildi."}
