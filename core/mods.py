"""System modów — ładuje pliki JSON z folderu mods/ obok gry.

Mody to pliki .json w folderze mods/. Każdy mod może nadpisywać/dodawać:
  - balance (stałe balansu)
  - server_models (katalog serwerów)
  - tlds (domeny)
  - names (imiona, nazwy serwerów)
  - products (dodatkowe produkty/plany)
  - regions (startowe regiony)
  - failure_types (typy awarii)
  - start (kapitał startowy, reputacja)
  - marketing (koszty, bonusy)
  - employee (pensje, pojemność)

Mody są opcjonalne — brak folderu/modów = gra domyślna.
Zgodne z licencją CC BY-ND 4.0 (mody to osobne pakiety, nie derivative work).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def mods_dir() -> Path:
    """Folder mods/ — obok exe (PyInstaller) lub w katalogu projektu (dev)."""
    import sys
    if hasattr(sys, '_MEIPASS') or getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent / "mods"
    else:
        base = Path(__file__).resolve().parent.parent / "mods"
    base.mkdir(parents=True, exist_ok=True)
    return base


def list_mods() -> list[dict[str, Any]]:
    """Zwraca listę zainstalowanych modów z folderu mods/."""
    mods: list[dict[str, Any]] = []
    for path in sorted(mods_dir().glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            mods.append({
                "name": data.get("name", path.stem),
                "version": data.get("version", "1.0"),
                "author": data.get("author", "nieznany"),
                "file": path.name,
                "enabled": data.get("enabled", True),
                "description": data.get("description", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return mods


def load_mods() -> dict[str, Any]:
    """Ładuje wszystkie włączone mody i zwraca scalone dane."""
    merged: dict[str, Any] = {
        "balance": {},
        "server_models": [],
        "tlds": [],
        "names": {},
        "products": [],
        "regions": [],
        "failure_types": {},
        "start": {},
        "marketing": {},
        "employee": {},
    }
    for mod_info in list_mods():
        if not mod_info.get("enabled", True):
            continue
        path = mods_dir() / mod_info["file"]
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if "balance" in data:
                merged["balance"].update(data["balance"])
            if "server_models" in data:
                merged["server_models"].extend(data["server_models"])
            if "tlds" in data:
                merged["tlds"].extend(data["tlds"])
            if "names" in data:
                merged["names"].update(data["names"])
            if "products" in data:
                merged["products"].extend(data["products"])
            if "regions" in data:
                merged["regions"].extend(data["regions"])
            if "failure_types" in data:
                merged["failure_types"].update(data["failure_types"])
            if "start" in data:
                merged["start"].update(data["start"])
            if "marketing" in data:
                merged["marketing"].update(data["marketing"])
            if "employee" in data:
                merged["employee"].update(data["employee"])
        except (json.JSONDecodeError, OSError):
            continue
    return merged


def apply_mods(state: Any) -> dict[str, Any]:
    """Aplikuje mody na stan gry. Wywoływane przy tworzeniu nowej gry.

    Zwraca dict z informacją co zostało zmodyfikowane (do logów/debug).
    """
    mods = load_mods()
    applied: dict[str, Any] = {"balance_keys": 0, "servers_added": 0, "products_added": 0,
                                "tlds_added": 0, "start_modified": False}

    # 1. Balance — nadpisz wartości w data.balance
    if mods["balance"]:
        from data import balance as balance_mod
        for key, value in mods["balance"].items():
            if hasattr(balance_mod, key):
                setattr(balance_mod, key, value)
                applied["balance_keys"] += 1

    # 2. Start — kapitał startowy, reputacja
    if mods["start"]:
        if "cash" in mods["start"]:
            state.cash = mods["start"]["cash"]
            applied["start_modified"] = True
        if "reputation" in mods["start"]:
            state.reputation = mods["start"]["reputation"]
            applied["start_modified"] = True

    # 3. Server models — dodaj do katalogu
    if mods["server_models"]:
        from data.server_models import SERVER_CATALOG
        existing_ids = {m["id"] for m in SERVER_CATALOG}
        for model in mods["server_models"]:
            if model.get("id") not in existing_ids:
                SERVER_CATALOG.append(model)
                applied["servers_added"] += 1

    # 4. TLDs — dodaj do listy
    if mods["tlds"]:
        from data.tlds import TLDS
        existing_ids = {t["id"] for t in TLDS}
        for tld in mods["tlds"]:
            if tld.get("id") not in existing_ids:
                TLDS.append(tld)
                applied["tlds_added"] += 1

    # 5. Products/plany — dodaj do stanu gry
    if mods["products"]:
        from core.models import ProductPlan
        for p in mods["products"]:
            plan = ProductPlan(
                id=p.get("id", f"mod_plan_{len(state.products)}"),
                product_type=p.get("product_type", "vps"),
                name=p.get("name", "Mod plan"),
                cpu_cores=p.get("cpu_cores", 0),
                ram_gb=p.get("ram_gb", 0),
                disk_gb=p.get("disk_gb", 0),
                bandwidth_mbps=p.get("bandwidth_mbps", 0),
                price_monthly=p.get("price_monthly", 10.0),
                sla_target=p.get("sla_target", 99.9),
                setup_fee=p.get("setup_fee", 0.0),
            )
            state.products.append(plan)
            applied["products_added"] += 1

    # 6. Failure types — dodaj/doładnij wagi
    if mods["failure_types"]:
        from data import balance as balance_mod
        for ftype, weight in mods["failure_types"].items():
            balance_mod.FAILURE_TYPES[ftype] = weight

    # 7. Marketing — nadpisz stałe
    if mods["marketing"]:
        from data import balance as balance_mod
        if "cost_per_customer" in mods["marketing"]:
            balance_mod.MARKETING_COST_PER_NEW_CUSTOMER = mods["marketing"]["cost_per_customer"]
        if "baseline_new" in mods["marketing"]:
            balance_mod.MARKETING_BASELINE_NEW_CUSTOMERS = mods["marketing"]["baseline_new"]

    # 8. Employee — nadpisz stałe
    if mods["employee"]:
        from data import balance as balance_mod
        if "salary_per_level" in mods["employee"]:
            balance_mod.EMPLOYEE_SALARY_PER_LEVEL = mods["employee"]["salary_per_level"]
        if "capacity_per_level" in mods["employee"]:
            balance_mod.EMPLOYEE_CAPACITY_PER_LEVEL = mods["employee"]["capacity_per_level"]

    # 9. Names — nadpisz listy
    if mods["names"]:
        from data import names
        if "first_names" in mods["names"]:
            names.FIRST_NAMES = mods["names"]["first_names"]
        if "last_names" in mods["names"]:
            names.LAST_NAMES = mods["names"]["last_names"]
        if "server_names" in mods["names"]:
            names.SERVER_NAME_POOL = mods["names"]["server_names"]

    return applied