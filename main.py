class TokenQualityEvaluator:
    def __init__(self):
        # إعداد الأوزان والمعايير المطلوبة
        self.MIN_UNIQUE_WALLETS = 50

    def evaluate_token(self, token_data: dict) -> dict:
        """
        تقييم العملة وإعطاؤها تنقيط (Score) من 0 إلى 100
        مع تحديد واش مقبولة للشراء ولا مرفوضة.
        """
        score = 0
        reasons = []

        # 1. فلتر المحافظ الفريدة (Unique Wallets) - الوزن: 30 نقطة
        unique_wallets = token_data.get("unique_wallets", 0)
        if unique_wallets >= self.MIN_UNIQUE_WALLETS:
            score += 30
            reasons.append(f"✅ Unique wallets passed: {unique_wallets}")
        else:
            reasons.append(f"❌ Low unique wallets: {unique_wallets} (Min: {self.MIN_UNIQUE_WALLETS})")

        # 2. فلتر الباندلر (Bundler Detection) - الوزن: 25 نقطة
        # (إيلا كان الباندلر شاريني بالنسبة الأولى في نفس البلوك كينقص التنقيط)
        is_bundled = token_data.get("is_bundled", False)
        if not is_bundled:
            score += 25
            reasons.append("✅ No malicious bundler detected")
        else:
            reasons.append("⚠️ Warning: Bundler activity detected")
            score -= 10  # خصم نقاط في حالة وجود باندلر مشبوه

        # 3. محفظة المطور (Dev Holding %) - الوزن: 25 نقطة
        dev_holding_pct = token_data.get("dev_holding_pct", 100.0)
        # المثالي أن المطور يكون ما بينيدش بزاف أو محروق/مباع جزء كبير
        if dev_holding_pct <= 5.0:
            score += 25
            reasons.append(f"✅ Dev holding is safe: {dev_holding_pct}%")
        elif dev_holding_pct <= 10.0:
            score += 15
            reasons.append(f"⚠️ Dev holding is acceptable: {dev_holding_pct}%")
        else:
            reasons.append(f"❌ Dev holding too high: {dev_holding_pct}%")

        # 4. نسبة السنايبرز (Snipers Presence) - الوزن: 20 نقطة
        snipers_count = token_data.get("snipers_count", 0)
        if snipers_count <= 5: # عدد قليل كيعني بلي مكانش هجوم عنيف من بوتات التخريب
            score += 20
            reasons.append(f"✅ Snipers count is low: {snipers_count}")
        else:
            score += 5
            reasons.append(f"⚠️ High snipers count: {snipers_count}")

        # التأكد من أن التنقيط محصور بين 0 و 100
        final_score = max(0, min(100, score))

        # القرار النهائي (مثلاً الشرط يكون فوق 70 عاد يدوز الأوتوباي)
        is_approved = final_score >= 70

        return {
            "score": final_score,
            "approved": is_approved,
            "reasons": reasons
        }

# --- مثال على كيفية الاستخدام في البوت ديالك ---
if __name__ == "__main__":
    evaluator = TokenQualityEvaluator()

    # بيانات تجريبية لعملة جديدة وصلت في الـ WebSocket
    sample_token = {
        "unique_wallets": 65,
        "is_bundled": False,
        "dev_holding_pct": 3.5,
        "snipers_count": 2
    }

    result = evaluator.evaluate_token(sample_token)
    print(f"Token Final Score: {result['score']}/100")
    print(f"Approved for Auto-Buy: {result['approved']}")
    print("Details:")
    for r in result['reasons']:
        print(f"  - {r}")
