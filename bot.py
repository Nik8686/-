import os
import requests
import time

# إعدادات بوت تيليجرام (يمكنك استبدالها بمتغيرات البيئة في Railway)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

def send_telegram_alert(message):
    """دالة لإرسال التنبيهات مباشرة إلى تطبيق تيليجرام"""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️ تنبيه: يرجى ضبط توكن بوت تيليجرام و Chat ID")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"فشل إرسال التيليجرام: {response.text}")
    except Exception as e:
        print(f"خطأ في الاتصال بتيليجرام: {e}")

class TokenQualityEvaluator:
    def __init__(self):
        # الشروط الأساسية المحددة
        self.MIN_UNIQUE_WALLETS = 50

    def evaluate_token(self, token_data: dict) -> dict:
        """
        تقييم العملة وإعطاؤها تنقيط (Score) من 0 إلى 100
        """
        score = 0
        reasons = []

        # 1. فلتر المحافظ الفريدة (Unique Wallets) - الوزن: 30 نقطة
        unique_wallets = token_data.get("unique_wallets", 0)
        if unique_wallets >= self.MIN_UNIQUE_WALLETS:
            score += 30
            reasons.append(f"✅ المحافظ الفريدة ممتازة: {unique_wallets}")
        else:
            reasons.append(f"❌ المحافظ الفريدة ضعيفة: {unique_wallets} (الحد الأدنى: {self.MIN_UNIQUE_WALLETS})")

        # 2. فلتر الباندلر (Bundler Detection) - الوزن: 25 نقطة
        is_bundled = token_data.get("is_bundled", False)
        if not is_bundled:
            score += 25
            reasons.append("✅ لا يوجد باندلر مشبوه")
        else:
            reasons.append("⚠️ تحذير: تم رصد نشاط باندلر")
            score -= 10

        # 3. محفظة المطور (Dev Holding %) - الوزن: 25 نقطة
        dev_holding_pct = token_data.get("dev_holding_pct", 100.0)
        if dev_holding_pct <= 5.0:
            score += 25
            reasons.append(f"✅ نسبة امتلاك المطور آمنة: {dev_holding_pct}%")
        elif dev_holding_pct <= 10.0:
            score += 15
            reasons.append(f"⚠️ نسبة امتلاك المطور مقبولة: {dev_holding_pct}%")
        else:
            reasons.append(f"❌ نسبة امتلاك المطور مرتفعة جداً: {dev_holding_pct}%")

        # 4. بوتات القنص والسنايبرز (Snipers Presence) - الوزن: 20 نقطة
        snipers_count = token_data.get("snipers_count", 0)
        if snipers_count <= 5:
            score += 20
            reasons.append(f"✅ عدد السنايبرز قليل ومستقر: {snipers_count}")
        else:
            score += 5
            reasons.append(f"⚠️ هجوم مكثف من السنايبرز: {snipers_count}")

        final_score = max(0, min(100, score))
        is_approved = final_score >= 70  # شرط القبول: 70 نقطة فما فوق

        return {
            "score": final_score,
            "approved": is_approved,
            "reasons": reasons
        }

def process_new_token(token_info: dict):
    """معالجة العملة الجديدة، تقييمها، وإرسال تنبيه في تيليجرام إذا كانت ممتازة"""
    evaluator = TokenQualityEvaluator()
    result = evaluator.evaluate_token(token_info)
    
    token_name = token_info.get("name", "Unknown")
    token_mint = token_info.get("mint", "N/A")
    
    print(f"🔍 فحص العملة: {token_name} | النقاط: {result['score']}/100")
    
    # إرسال تنبيه في تيليجرام فقط إذا نجحت العملة في الفلتر
    if result["approved"]:
        message = (
            f"🚀 **عملة جديدة ناجحة في الفلتر!**\n\n"
            f"📌 **الاسم:** {token_name}\n"
            f"💎 **التنقيط:** `{result['score']}/100`\n"
            f"🔑 **العقد (Mint):** `{token_mint}`\n\n"
            f"📋 **التفاصيل:**\n"
        )
        for r in result["reasons"]:
            message += f"• {r}\n"
            
        send_telegram_alert(message)
        print(f"✅ تم إرسال تنبيه العملة {token_name} إلى تيليجرام بنجاح.")

# --- محاكاة التشغيل للتجربة ---
if __name__ == "__main__":
    print("🤖 بوت الفلترة والتنبيهات يعمل الآن...")
    
    # مثال لبيانات عملة وهمية وصلت للنظام
    sample_token_data = {
        "name": "SuperMoon (MOON)",
        "mint": "So11111111111111111111111111111111111111112",
        "unique_wallets": 58,
        "is_bundled": False,
        "dev_holding_pct": 2.1,
        "snipers_count": 3
    }
    
    # تجربة معالجة العملة
    process_new_token(sample_token_data)
