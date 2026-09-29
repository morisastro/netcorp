"""Stałe balansu gry — wszystkie liczby do tuningu w jednym miejscu."""
from __future__ import annotations

# ---- Kapitał startowy (garaż) ----
START_CASH = 5000.0
START_REPUTATION = 50.0

# ---- Prawdopodobieństwo awarii ----
# Bazowe prawdopodobieństwo awarii per serwer per dzień (przed modyfikatorami)
FAILURE_BASE_DAILY = 0.02  # 2% szans na awarię na serwer dziennie (base)

# Modyfikatory stanu (mnożniki na bazowe prawdopodobieństwo)
FAILURE_MOD_OVERLOAD_CPU = 3.0   # CPU > 80% → 3× szansa
FAILURE_MOD_OVERLOAD_RAM = 2.0  # RAM > 90% → 2× szansa
FAILURE_MOD_HIGH_TEMP = 2.5     # przegrzanie (cooling_factor < obciążenie)
FAILURE_MOD_AGE = 1.5           # serwer > 365 dni → 1.5×
FAILURE_MOD_REDUNDANCY_NET = 0.5  # 2+ uplinki → 0.5× ryzyko sieci

# Progi
THRESHOLD_CPU_OVERLOAD = 0.80
THRESHOLD_RAM_OVERLOAD = 0.90
THRESHOLD_AGE_DAYS = 365

# ---- Typy awarii i ich wagi (prawdopodobieństwo względne) ----
FAILURE_TYPES = {
    "disk": 0.25,
    "cpu_overload": 0.20,
    "overheat": 0.15,
    "power": 0.15,
    "network": 0.15,
    "ddos": 0.10,
}

# ---- MTBF per tier (godziny) ----
TIER_MTBF = {
    "budget": 4000.0,
    "standard": 10000.0,
    "premium": 25000.0,
}

# Mnożnik awaryjności per tier (mnożnik na bazowe prawdopodobieństwo)
TIER_FAILURE_MULTIPLIER = {
    "budget": 2.0,
    "standard": 1.0,
    "premium": 0.5,
}

# ---- SLA kary ----
SLA_PENALTY_PER_HOUR_HOBBYIST = 5.0      # $/h downtime per klient
SLA_PENALTY_PER_HOUR_SMALL_BIZ = 20.0
SLA_PENALTY_PER_HOUR_ENTERPRISE = 100.0

# ---- Churn ----
CHURN_BASE_MONTHLY = 0.05  # 5% miesięcznie bazowo
CHURN_FROM_HIGH_PRICE = 0.02     # +2% jeśli cena > rynek
CHURN_FROM_LOW_UPTIME = 0.05      # +5% jeśli uptime < 99%
CHURN_FROM_SLOW_SUPPORT = 0.03    # +3% jeśli support wolny

# ---- Marketing ----
MARKETING_COST_PER_NEW_CUSTOMER = 10.0  # średnio $ wydan na marketing → 1 nowy klient (było $15)
MARKETING_BASELINE_NEW_CUSTOMERS = 3     # bazowo dziennie (bez marketingu, z reputacji)

# ---- Pracownicy ----
EMPLOYEE_SALARY_PER_LEVEL = 30.0   # pensja dzienna = level × $30 (było $50)
EMPLOYEE_CAPACITY_PER_LEVEL = 10    # pojemność (ticketów/awacji) = level × 10

# ---- Koszty stałe (dzienne) ----
# Prąd: $/kWh
POWER_PRICE_PER_KWH = 0.15
# Łącze: $/Mbps/dzień
NETWORK_PRICE_PER_MBPS_DAILY = 0.05
# Licencje (stałe dzienne)
LICENSE_DAILY = 2.0  # było $5

# ---- Rozbudowa serwerowni ----
# Cena zakupu slotu rośnie z liczbą slotów: base + (slots_total × step)
SLOT_BUY_BASE_PRICE = 500.0    # pierwszy slot od $500
SLOT_BUY_STEP = 100.0          # każdy kolejny slot +$100
# Pojemność prądu dodawana per slot (kW)
SLOT_POWER_KW = 1.5