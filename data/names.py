"""Generator imion pracowników i nazw serwerów (flavor)."""
from __future__ import annotations

import random as _r

FIRST_NAMES = [
    "Anna", "Marek", "Kasia", "Piotr", "Łukasz", "Magda", "Tomek", "Ola",
    "Krzysiek", "Beata", "Michał", "Natalia", "Paweł", "Justyna", "Adam",
    "Sylwia", "Rafał", "Dominika", "Grzegorz", "Ewa", "Jacek", "Monika",
    "Bartek", "Agnieszka", "Marcin", "Karolina", "Filip", "Wiola", "Damian",
]

LAST_NAMES = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamińska",
    "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Dąbrowski", "Kozłowska",
    "Mazur", "Krawczyk", "Piotrowski", "Grabowski", "Pawlak", "Michalska",
]


def random_employee_name(rng: _r.Random | None = None) -> str:
    r = rng or _r
    return f"{r.choice(FIRST_NAMES)} {r.choice(LAST_NAMES)}"


# Memowe nazwy serwerów (flavor)
SERVER_NAME_POOL = [
    "BRZUCHOMÓW", "ŻÓŁW", "KRAKÓW-EXPRESS", "PĄCZEK-7", "KOX-KLIENT",
    "SŁOŃCE", "HIPER-KURA", "BIGOS", "PIEROG-9000", "STARY-BUT",
    "KUTAS-2", "OHYDA", "KRZACZEK", "CHMURA-CHMUREK", "SERWOREX",
    "MŁOT-BOŻY", "PIŁA", "CEGŁA", "DYNIA-3", "GROCHÓW",
]


def random_server_label(rng: _r.Random | None = None) -> str:
    r = rng or _r
    return f"{r.choice(SERVER_NAME_POOL)}-{r.randint(1, 99)}"