import numpy as np
import pandas as pd


def generate_synthetic_data(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic B2C subscriber dataset (5,000 rows) aligned with
    TelkomGroup 2025 B2C operational benchmarks and the 5-entity ERD schema.
    """
    rng = np.random.default_rng(seed)

    # 1. Segment distribution reflecting 2025 B2C base:
    # ~75% Mobile (95% Prabayar, 5% Halo) & ~25% IndiHome (70% 1P, 30% 3P)
    segments = rng.choice(
        ["Telkomsel Prabayar", "Telkomsel Halo", "IndiHome 1P", "IndiHome 3P"],
        size=n,
        p=[0.7125, 0.0375, 0.1750, 0.0750],
    )

    cities = rng.choice(
        [
            "Jabodetabek",
            "Bandung",
            "Surabaya",
            "Medan",
            "Semarang",
            "Makassar",
            "Denpasar",
            "Balikpapan",
        ],
        size=n,
        p=[0.30, 0.14, 0.14, 0.10, 0.10, 0.08, 0.07, 0.07],
    )

    subscriber_ids = [f"SUB-{i+1:05d}" for i in range(n)]
    household_ids = [f"HH-{rng.integers(10000, 99999)}" for _ in range(n)]
    tenure_months = rng.integers(1, 120, size=n)
    account_status = rng.choice(["Active", "Grace Period"], size=n, p=[0.92, 0.08])

    # 2. Usage & ARPU simulation per segment
    data_usage_gb = np.zeros(n)
    data_growth_pct = np.zeros(n)
    voice_minutes = np.zeros(n, dtype=int)
    sms_count = np.zeros(n, dtype=int)
    monthly_arpu_idr = np.zeros(n)
    reload_drop_pct = np.zeros(n)
    remaining_active_days = np.zeros(n, dtype=int)
    iptv_usage_drop_pct = np.zeros(n)
    has_active_mobile_in_hh = np.zeros(n, dtype=bool)
    current_product_id = np.empty(n, dtype=object)
    product_name = np.empty(n, dtype=object)

    for i, seg in enumerate(segments):
        if seg == "Telkomsel Prabayar":
            data_usage_gb[i] = np.round(rng.lognormal(mean=2.6, sigma=0.65), 1)
            data_growth_pct[i] = np.round(rng.normal(loc=15.0, scale=12.0), 1)
            voice_minutes[i] = int(max(0, rng.normal(loc=25, scale=20)))
            sms_count[i] = int(max(0, rng.normal(loc=8, scale=10)))
            monthly_arpu_idr[i] = np.round(rng.uniform(25000, 110000), -2)
            reload_drop_pct[i] = np.round(rng.uniform(0, 55), 1)
            remaining_active_days[i] = int(rng.integers(1, 30))
            iptv_usage_drop_pct[i] = 0.0
            has_active_mobile_in_hh[i] = True
            current_product_id[i] = "PRD-PRE-01"
            product_name[i] = "Kartu Prabayar Data"

        elif seg == "Telkomsel Halo":
            data_usage_gb[i] = np.round(rng.lognormal(mean=3.2, sigma=0.5), 1)
            data_growth_pct[i] = np.round(rng.normal(loc=14.0, scale=10.0), 1)
            voice_minutes[i] = int(max(0, rng.normal(loc=90, scale=45)))
            sms_count[i] = int(max(0, rng.normal(loc=15, scale=12)))
            monthly_arpu_idr[i] = np.round(rng.uniform(120000, 350000), -3)
            reload_drop_pct[i] = 0.0
            remaining_active_days[i] = 30
            iptv_usage_drop_pct[i] = 0.0
            has_active_mobile_in_hh[i] = True
            current_product_id[i] = "PRD-HALO-01"
            product_name[i] = "Halo+ Postpaid"

        elif seg == "IndiHome 1P":
            data_usage_gb[i] = np.round(rng.uniform(120, 450), 1)
            data_growth_pct[i] = np.round(rng.normal(loc=16.0, scale=8.0), 1)
            voice_minutes[i] = 0
            sms_count[i] = 0
            monthly_arpu_idr[i] = np.round(rng.uniform(220000, 360000), -3)
            reload_drop_pct[i] = 0.0
            remaining_active_days[i] = 30
            iptv_usage_drop_pct[i] = 0.0
            has_active_mobile_in_hh[i] = bool(rng.choice([True, False], p=[0.68, 0.32]))
            current_product_id[i] = "PRD-IH-1P"
            product_name[i] = "IndiHome 1P Internet Only"

        else:  # IndiHome 3P
            data_usage_gb[i] = np.round(rng.uniform(150, 500), 1)
            data_growth_pct[i] = np.round(rng.normal(loc=12.0, scale=8.0), 1)
            voice_minutes[i] = int(max(0, rng.normal(loc=40, scale=30)))
            sms_count[i] = 0
            monthly_arpu_idr[i] = np.round(rng.uniform(380000, 580000), -3)
            reload_drop_pct[i] = 0.0
            remaining_active_days[i] = 30
            iptv_usage_drop_pct[i] = np.round(rng.uniform(5, 85), 1)
            has_active_mobile_in_hh[i] = bool(rng.choice([True, False], p=[0.60, 0.40]))
            current_product_id[i] = "PRD-IH-3P"
            product_name[i] = "IndiHome 3P Full Package"

    # 3. Deterministic Business Rules Engine (Decision Matrix)
    churn_risk_score = np.zeros(n, dtype=float)
    churn_risk_tier = np.empty(n, dtype=object)
    recommended_offer = np.empty(n, dtype=object)
    triggered_rule = np.empty(n, dtype=object)
    delivery_channel = np.empty(n, dtype=object)
    projected_arpu_uplift = np.zeros(n, dtype=float)
    projected_retention_gain = np.zeros(n, dtype=float)

    for i in range(n):
        seg = segments[i]

        # Base risk score calculation
        if seg == "Telkomsel Prabayar":
            score = 20.0 + (reload_drop_pct[i] * 0.9) + max(0, (10 - remaining_active_days[i]) * 2.5)
            if data_growth_pct[i] >= 15 and monthly_arpu_idr[i] < 65000:
                score += 12.0
        elif seg == "IndiHome 3P":
            score = 15.0 + (iptv_usage_drop_pct[i] * 0.85)
        elif seg == "IndiHome 1P":
            score = 25.0 + (15.0 if has_active_mobile_in_hh[i] else 5.0)
        else:  # Telkomsel Halo
            score = 15.0 + (10.0 if tenure_months[i] < 12 else 0.0)

        score = float(np.clip(np.round(score, 1), 5.0, 98.0))
        churn_risk_score[i] = score

        if score >= 65.0:
            churn_risk_tier[i] = "High"
        elif score >= 40.0:
            churn_risk_tier[i] = "Medium"
        else:
            churn_risk_tier[i] = "Low"

        # NBO Decision Matrix Rules
        # NOTE: projected_arpu_uplift & projected_retention_gain are simulation model assumptions
        if seg == "IndiHome 1P" and has_active_mobile_in_hh[i]:
            recommended_offer[i] = "Telkomsel One (Dynamic/Complete)"
            triggered_rule[i] = "IndiHome 1P + Active Mobile in Household"
            delivery_channel[i] = "WhatsApp Official & Outbound Telemarketing"
            projected_arpu_uplift[i] = 65000.0  # Assumed FMC migration uplift (IDR/month)
            projected_retention_gain[i] = monthly_arpu_idr[i] * 0.25

        elif seg == "IndiHome 3P" and iptv_usage_drop_pct[i] > 50.0:
            recommended_offer[i] = "Telkomsel One + Add-on MAXStream VIP"
            triggered_rule[i] = "IndiHome 3P IPTV/Voice Drop > 50%"
            delivery_channel[i] = "MyTelkomsel In-App Banner & Email Billing"
            projected_arpu_uplift[i] = 35000.0  # Assumed retention & OTT substitution uplift
            projected_retention_gain[i] = monthly_arpu_idr[i] * 0.35

        elif seg == "Telkomsel Prabayar" and reload_drop_pct[i] > 30.0 and remaining_active_days[i] < 7:
            recommended_offer[i] = "Win-back Combo Sakti + Voucher MAXStream"
            triggered_rule[i] = "Prepaid Reload Drop > 30% & Active Days < 7"
            delivery_channel[i] = "Targeted SMS & WhatsApp Interactive"
            projected_arpu_uplift[i] = 18000.0  # Assumed win-back top-up recovery
            projected_retention_gain[i] = monthly_arpu_idr[i] * 0.40

        elif seg == "Telkomsel Prabayar" and data_growth_pct[i] >= 15.0 and voice_minutes[i] < 30 and monthly_arpu_idr[i] < 65000:
            recommended_offer[i] = "Paket Data Utama + Bundling Digital (Dunia Games / Langit Musik)"
            triggered_rule[i] = "Prepaid High-Traffic (>=15%) & Low-Yield"
            delivery_channel[i] = "MyTelkomsel Push Notification & UMB (*363#)"
            projected_arpu_uplift[i] = 12000.0  # Assumed micro-upsell digital bundle
            projected_retention_gain[i] = monthly_arpu_idr[i] * 0.15

        else:
            recommended_offer[i] = "Retain / No Promo Needed"
            triggered_rule[i] = "Normal / Low Risk Profile"
            delivery_channel[i] = "No Campaign (Margin Protection)"
            projected_arpu_uplift[i] = 0.0
            projected_retention_gain[i] = 0.0

    df = pd.DataFrame(
        {
            "subscriber_id": subscriber_ids,
            "household_id": household_ids,
            "customer_segment": segments,
            "city_region": cities,
            "tenure_months": tenure_months,
            "account_status": account_status,
            "current_product_id": current_product_id,
            "product_name": product_name,
            "data_usage_gb": data_usage_gb,
            "data_growth_pct": data_growth_pct,
            "voice_minutes": voice_minutes,
            "sms_count": sms_count,
            "monthly_arpu_idr": monthly_arpu_idr,
            "reload_drop_pct": reload_drop_pct,
            "remaining_active_days": remaining_active_days,
            "iptv_usage_drop_pct": iptv_usage_drop_pct,
            "has_active_mobile_in_hh": has_active_mobile_in_hh,
            "churn_risk_score": churn_risk_score,
            "churn_risk_tier": churn_risk_tier,
            "recommended_offer": recommended_offer,
            "triggered_rule": triggered_rule,
            "delivery_channel": delivery_channel,
            "projected_arpu_uplift": projected_arpu_uplift,
            "projected_retention_gain": projected_retention_gain,
        }
    )

    return df
