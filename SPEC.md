# NetCorp Tycoon — Specyfikacja gry

> Dokument wywiadu projektowego. Wszystkie decyzje poniżej są ustalone i zatwierdzone przez gracza (zleceniodawcę).

---

## 1. Pełny opis gry

**NetCorp Tycoon** to web-desktopowa gra management/tycoon o budowaniu własnej firmy hostingowej / cloud providera — od garażowego home labu do międzynarodowego operatora infrastruktury.

Gracz zaczyna z minimalnym kapitałem (3-5k$), jednym starym serwerem i jednym routerem. Sam jest supportem, sysadminem i sprzedażą. Stopniowo zdobywa klientów, zarabia, kupuje lepszy sprzęt, wynajmuje serwerownie, otwiera kolejne regiony, zatrudnia pracowników i rozwija firmę w multi-region providera.

Gra jest **open-ended sandbox** bez sztucznego warunku wygranej — jedynym fail state jest bankructwo. Skupia się na satysfakcjonującym procesie wzrostu firmy przez 30h+ rozgrywki.

**Klimat:** poważny, pro-operator UI (dark, monospace, metryki, czyste tabele) + lekki flavor (memowe nazwy serwerów, zabawne tickety, komentarze klientów). Hybryda poważnego panelu z odrobiną humoru.

**Platforma:** desktop (Windows/macOS/Linux), aplikacja instalowana, działa offline, brak DB i serwera — stan w pliku lokalnym. Licencja komercyjna (płatna). Auto-update: sprawdza najnowszą wersję na GitHub releases przy starcie i powiadamia gracza.

---

## 2. Core gameplay loop

Gra działa w **turach dziennych** (1 klik „Następny dzień" = symulacja 24h).

**W jednej turze gracz:**

1. **Faza planowania (swobodna, bez limitu czasu):**
   - Buduje/kupuje infrastrukturę (modele serwerów, sloty w serwerowni).
   - Ustawia produkty, plany i ceny (custom, ręczne ceny per plan).
   - Projektuje stronę firmy (drag & drop builder) — wpływa na konwersję klientów.
   - Wydaje na marketing (budżet $ → przyrost klientów).
   - Zatrudnia/zwalnia pracowników.
   - Reaguje na aktywne awarie (wybór akcji per awaria).
   - Ustawia polityki (auto-priorytety ticketów, autokonfiguracje).

2. **Faza symulacji (klik „Następny dzień"):**
   - System losuje awarie wg prawdopodobieństwa = baza × modyfikatory stanu (jakość sprzętu, temperatura, obciążenie, wiek, chłodzenie, redundancja sieci).
   - Tickety supportu są rozwiązywane automatycznie przez pracowników (liczba + poziom = pojemność).
   - Klienci przychodzą/odchodzą wg: marketing $, jakości strony, ceny vs rynek, reputacji.
   - Subskrypcje są pobierane, koszty stałe są płatne.
   - Kary SLA są naliczane automatycznie za awarie.
   - Reputacja się aktualizuje.

3. **Faza podsumowania (raport dzienny):**
   - Przychód, koszty, churn, awarie, nowe tickety.
   - Nowe możliwości (kamienie milowe) jeśli osiągnięte.

Pętla powtarza się. W późnym etapie (wiele regionów, tysiące klientów) gracz przechodzi na wyższy poziom abstrakcji — mniej mikrozarządzania, więcej strategii (regiony, kontrakty enterprise), detale wykonuje automatyzacja/polityki.

---

## 3. Lista głównych systemów

1. **Symulacja czasu** — tury dzienne, tick wydarzeń.
2. **Infrastruktura** — modele serwerów, sloty w serwerowni, zasoby DC (prąd, sieć, cooling), oversubscription.
3. **Produkty** — WWW, VPS, dedyk, domena. Custom plany z ręcznymi cenami.
4. **Klienci** — agregaty per produkt, churn %, SLA kary.
5. **Awarie** — 6 typów (dysk, CPU, przegrzanie, zasilanie, sieć, DDoS), RNG z modyfikatorami stanu, wybór akcji per awaria.
6. **Pracownicy** — 5 ról (Support, Sysadmin, NetEng, Sales, Marketing), indywidualni (imię, poziom, pensja), automatyczne wykonanie ról.
7. **Finanse** — prosta gotówka, koszty stałe (DC, prąd, łącza, pensje, licencje), przychody z subskrypcji.
8. **Marketing i strona** — wydatek $ na marketing + drag & drop website builder (bonus do konwersji).
9. **Domeny i DNS** — cennik per TLD, cykl życia domeny u klienta, DNS jako abstrakcja (działa z hostingiem).
10. **Regiony / datacentry** — zaczynamy od 1, docelowo multi-region z osobnymi kosztami i awariami.
11. **Reputacja** — wpływa na przyrost klientów i churn.
12. **Save/load** — stan w pliku lokalnym (JSON).
13. **Update checker** — sprawdzanie GitHub releases przy starcie.
14. **UI** — dark pro-operator panel, monospace, metryki, tabele, wykresy, proste SVG (racki jako sloty).

---

## 4. Zakres gry (pełna wersja, z podziałem na fazy)

Gra budowana jest jako pełna wersja, ale implementowana **fazowo** (patrz kolejność implementacji i roadmapa). Nie ma „MVP cut" — wszystko poniżej jest docelowo w grze, ale faza 1 jest pierwszą grywalną wersją.

### Faza 1 — Pierwsza grywalna wersja (core)
- Tury dzienne + symulacja.
- 1 region / 1 serwerownia.
- 4 produkty (WWW, VPS, dedyk, domena) z custom planami.
- Infrastruktura: modele serwerów + tier jakości, sloty, zasoby DC (prąd, sieć, cooling).
- 6 typów awarii z wyborem akcji.
- 5 ról pracowników, automatyczne wykonanie.
- Klienci jako agregaty per produkt, churn + SLA kary.
- Marketing (wydatek $) + prosty website builder (drag & drop, kilka bloków).
- Domeny per TLD, DNS abstrakcja.
- Finanse: prosta gotówka, koszty stałe.
- Reputacja.
- Save/load.
- UI: dashboard, infrastruktura (sloty SVG), produkty, klienci, pracownicy, finanse, awarie, strona.
- Update checker.

### Faza 2 — Rozszerzenie
- Wiele regionów / datacentrów (multi-DC).
- Kontrakty enterprise (indywidualni duzi klienci z kontraktami).
- Upgrade DDoS protection.
- Skok abstrakcji na późnym etapie (polityki automatyzacji).
- Więcej typów awarii (błąd pracownika, backup fail, storage fail).
- Backup jako produkt.

### Faza 3 — Polish i multiplayer
- Pełny multiplayer (ranking, marketplace, handel domenami, kontrakty między graczami, globalny rynek cen, globalne wydarzenia).
- Więcej produktów (Minecraft, serwer aplikacyjny, storage, backup jako usługa zarządzana).
- Modowanie / workshop.
- Localization.

---

## 5. Rzeczy odłożone na później

- Pełny multiplayer (marketplace, handel, kontrakty między graczami).
- Produkty: Minecraft, serwer aplikacyjny, managed storage, managed backup (poza core 4).
- Pełna księgowość (P&L, bilans, cashflow, depreciacja).
- BGP/IP, realne distro, realne ceny sprzętu.
- Rack-level z fizycznymi U-slots (zostajemy przy slotach).
- Skill tree / poziomy firmy.
- Modding API.
- Localization (na start EN + PL).

---

## 6. Struktura ekranów UI

Główne menu aplikacji (sidebar + główny panel). Dark pro-operator styl.

1. **Dashboard** — KPI: gotówka, klienci (per produkt), uptime %, reputacja, aktywne awarie, tickety, wykres przychodu 30d, alerty.
2. **Infrastruktura**
   - Serwerownia (siatka slotów SVG z serwerami).
   - Lista serwerów (tabela: model, CPU/RAM/dysk, tier jakości, MTBF, wiek, status).
   - Zasoby DC (prąd kW, sieć Gbps + redundancja, cooling factor) z paskami obciążenia.
   - Kup sprzęt (katalog modeli z tierami).
3. **Produkty** — 4 produkty, każdy z listą custom planów (dodaj/edytuj/usuń), ceny, parametry.
4. **Klienci** — agregaty per produkt (sprzedane, churn, NPS, SLA status), brak indywidualnych klientów.
5. **Awarie** — lista aktywnych awarii z wyborem akcji (restart / wymiana / failover / ignore) + historia.
6. **Pracownicy** — lista per rola (imię, poziom, pensja, wydajność), zatrudnij/zwolnij.
7. **Marketing** — wydatek $ na marketing, ROI, wykres przyrostu klientów.
8. **Strona firmy** — drag & drop builder (sekcje: hero, cennik, opinie, status serwerów, FAQ, kontakt, live chat, blog). Render podglądu na żywo. Bonus do konwersji zależy od jakości strony.
9. **Finanse** — prosta gotówka, przychody/koszty dzienne, wykres.
10. **Ustawienia** — save/load, prędkość symulacji, licencja, sprawdź aktualizacje, about.
11. **Raport dzienny** — modal po kliknięciu „Następny dzień".

---

## 7. Model ekonomii

**Przychody:**
- Subskrypcje miesięczne od klientów (WWW, VPS, dedyk, domena). Pobierane daily (subskrypcja/30).
- Domeny: jednorazowa opłata rejestracji + roczna odnowa.

**Koszty stałe (dzienne):**
- Wynajem serwerowni / DC.
- Prąd (proporcjonalnie do obciążenia sprzętu).
- łącza (uplinki).
- Pensje pracowników.
- Licencje (software).
- Marketing (ustawiony budżet dzienny).

**Koszty zmienne:**
- Zakup sprzętu (jednorazowo).
- Naprawy awarii (komponenty, failover).
- Kary SLA (automatyczne przy awarii — zależą od kontraktu klienta i długości downtime).

**Konsekwencje decyzji (kluczowe mechaniki):**
- Tani sprzęt (tier budget) = niższy MTBF = wyższa szansa awarii = kary SLA + churn.
- Oversubscription VPS (wiele VPS na jednym serwerze) = wyższa marża, ale wyższa szansa CPU overload.
- Mało pracowników = niższe koszty, ale wolniejszy support = wyższy churn.
- Słabe chłodzenie (cooling factor) = tańsza infra, ale wyższa szansa przegrzania.
- Dobre SLA (wysoki target) = więcej klientów, ale większe kary za awarie.
- Dobra strona (drag & drop) = wyższa konwersja z marketingu.

**Reputacja:** liczba 0-100, wpływa na przyrost klientów i churn. Spada przy awariach i karach, rośnie przy stabilnym uptime.

---

## 8. Progression gracza

**Start:** garaż / home lab. 1 stary serwer (budget tier), 1 router, 3-5k$ kapitału, 0 klientów, 0 pracowników (gracz jest wszystkim).

**Kamienie milowe (unlock możliwości, bez zmiany UI):**
- **0 klientów** → garaż (1-3 sloty, ograniczone zasoby).
- **~50 klientów + X$** → unlock: wynajem małej serwerowni (więcej slotów, lepsze zasoby DC).
- **~500 klientów** → unlock: pełne DC (dużo slotów, redundancja zasilania/sieci).
- **~2000 klientów** → unlock: drugi region (multi-DC).
- **~10000 klientów** → unlock: enterprise kontrakty (indywidualni duzi klienci).
- **~50000 klientów** → unlock: globalny provider (multi-region, skok abstrakcji).

**Skok abstrakcji na późnym etapie:** przy >10k klientów gracz zarządza strategicznie (regiony, kontrakty, polityki automatyzacji), detale (pojedyncze serwery, ticket) robi automatyka. UI się nie zmienia drastycznie, ale pojawiają się widoki wysokiego poziomu.

---

## 9. System klientów

**Reprezentacja:** agregaty per produkt („180 VPS-ów sprzedanych"). Brak indywidualnych encji klientów w faza 1. W faza 2 pojawiają się enterprise jako indywidualni.

**Segmenty (wewnętrzne, per produkt):**
- Hobbyist (niska cena, niskie SLA, wysoki churn).
- Small biz (średnia cena, średnie SLA).
- Enterprise (wysoka cena, wysokie SLA, kary, długi kontrakt) — faza 2.

**Źródło klientów:**
- Marketing $ → przyrost proporcjonalny.
- Strona drag & drop → bonus do konwersji (lepsza strona = więcej klientów z tego samego budżetu).
- Reputacja → organiczny przyrost (niezależny od marketingu).
- Cena vs rynek → jeśli tańsze niż rynek, więcej klientów; jeśli droższe, mniej.

**Churn (miesięczny %):**
- Liczony z: cena vs rynek, uptime %, czas reakcji supportu, reputacja.
- Awarie zwiększają churn w kolejnych dniach.

**SLA kary:** automatyczne $ z konta przy awarii, zależne od długości downtime i kontraktu segmentu.

---

## 10. System awarii

**6 typów (faza 1):**
1. Dysk fail — wymiana dysku / failover na backup.
2. CPU overload — restart / upgrade / migrate VPS.
3. Przegrzanie — wzmocnij cooling / shutdown serwera.
4. Awareria zasilania — UPS / restart DC section.
5. Awareria sieci — failover uplink / restart switch.
6. DDoS — ochrona DDoS (upgrade DC) / mit manually.

**Prawdopodobieństwo awarii:**
```
P(awaria) = baza_typu ×
  × modifier_jakości_sprzętu (budget ×2.0, standard ×1.0, premium ×0.5)
  × modifier_temperatury (>threshold → rośnie)
  × modifier_obciążenia (CPU >80% → rośnie)
  × modifier_wieku (starszy → rośnie)
  × modifier_cooling_factor (słabe chłodzenie → rośnie)
  × modifier_redundancji_sieci (1 uplink → wyższe ryzyko sieci)
```

**Wybór akcji per awaria:** restart / wymiana komponentu / failover na backup / ignore. Każda akcja: czas trwania, koszt $, skutki (downtime, wpływ na klientów, SLA kary).

**DDoS jako upgrade:** gracz może kupić DDoS protection (firewall/scrubbing) jako upgrade DC — zmniejsza szansę/poczas skutecznego DDoS.

---

## 11. System pracowników

**5 ról (faza 1):**
- **Support** — zamyka tickety (poziom = szybkość/pojemność).
- **Sysadmin** — naprawia awarie sprzętowe (poziom = czas naprawy).
- **Network engineer** — naprawia awarie sieciowe / DDoS.
- **Sales** — zwiększa konwersję leadów (bonus do przyrostu klientów).
- **Marketing** — zwiększa efektywność wydatków marketingowych (ROI).

**Model:** indywidualni pracownicy — imię (losowane), poziom (1-5), pensja dzienna, wydajność (pochodna poziomu). Gracz zatrudnia z rynku (lista kandydatów odświeżana cyklicznie) i zwalnia.

**Wpływ:** automatyczne wykonanie ról — liczba pracowników + średni poziom w roli = pojemność/szybkość danej funkcji. Gracz nie mikrozarządza przypisaniami. Brak pracownika w roli = funkcja nie działa (np. 0 sysadminów = awarie się przedłużają).

---

## 12. Proponowany stack technologiczny

- **Język:** Python 3.11+.
- **UI framework:** PySide6 (Qt for Python) — dojrzały, desktopowy, dobre widgety do tabel/wykresów/drag&drop.
- **Stan gry:** plik lokalny (JSON) — brak DB, brak serwera. Save/load do `~/.netcorp-tycoon/saves/`.
- **Wykresy:** QtCharts lub matplotlib (.QtCharts bliżej natywnego looku).
- **Bundling:** PyInstaller → .exe (Windows), .app (macOS), bin (Linux).
- **Auto-update:** sprawdzanie GitHub releases API (GET /repos/.../releases/latest) przy starcie, porównanie wersji, powiadomienie gracza (nie auto-pobieranie — gracz sam pobiera z linku).
- **Licencja:** gra darmowa (free). Kod na **CC BY-ND 4.0** (No Derivatives) — można kopiować, dystrybuować i używać oryginalnej gry pod warunkiem oznaczenia autora, ale **nie wolno redystrybuować zmodyfikowanej wersji kodu gry**. **Modyfikacje (mody) dozwolone** jako osobne pliki/dodatki ładowane przez system modów gry (nie są derivative work oryginału, tylko dodatkami). Plik LICENSE + ekran akceptacji przy pierwszym uruchomieniu.
- **VCS:** Git, repo na GitHub (prywatne na development, public releases).
- **CI:** GitHub Actions → automatyczny build na tag (PyInstaller) + upload release.

---

## 13. Struktura backendu (aplikacji)

Brak backendu serwerowego — cała logika po stronie klienta (desktop).

**Warstwy aplikacji:**

```
netcorp_tycoon/
├── main.py                  # entrypoint, inicjalizacja Qt, okno główne
├── app/
│   ├── __init__.py
│   ├── app.py               # QApplication, routing okien
│   ├── settings.py          # konfiguracja, licencja, paths
│   └── update_checker.py    # GitHub releases API check
├── core/                    # logika gry (framework-agnostic, testowalna)
│   ├── __init__.py
│   ├── game.py              # Game state + tick (next_day)
│   ├── simulation.py        # symulacja tury (awarie, finanse, churn)
│   ├── models.py            # dataclasses: Server, Customer, Product, Employee, Region, ...
│   ├── economy.py           # przychody, koszty, SLA kary
│   ├── failures.py          # generowanie awarii (RNG + modyfikatory), akcje
│   ├── employees.py         # zatrudnianie, automatyczne role
│   ├── customers.py         # agregaty, churn, przyrost, segmenty
│   ├── marketing.py         # marketing $ + website bonus
│   ├── domains.py           # domeny per TLD, cykl życia, DNS abstrakcja
│   ├── reputation.py        # reputacja 0-100
│   ├── progression.py       # kamienie milowe, unlocki
│   ├── events.py            # raport dzienny, alerty
│   └── rng.py               # deterministyczny RNG (seed w save)
├── data/                    # dane statyczne (JSON/Python dicts)
│   ├── server_models.py     # katalog modeli serwerów + tier jakości
│   ├── products.py          # szablony produktów
│   ├── names.py             # generator imion pracowników, nazw serwerów
│   ├── tlds.py               # TLD + ceny bazowe
│   └── balance.py           # stałe balansu (MTBF, modyfikatory, koszty)
├── persistence/
│   ├── save_load.py         # serializacja stanu do JSON
│   └── schemas.py           # wersjonowanie save
├── ui/                      # PySide6 widgety
│   ├── main_window.py
│   ├── dashboard.py
│   ├── infrastructure.py    # serwerownia (SVG sloty), lista serwerów, katalog
│   ├── products.py
│   ├── customers.py
│   ├── failures.py
│   ├── employees.py
│   ├── marketing.py
│   ├── website_builder.py   # drag & drop
│   ├── finances.py
│   ├── settings.py
│   ├── daily_report.py
│   └── widgets/              # współdzielone widgety (metryki, wykresy, ikony)
└── tests/
    └── test_*.py            # testy logiki (pytest)
```

**Zasada:** `core/` jest całkowicie odseparowane od `ui/` — logika gry nie zna Qt. Pozwala to testować symulację bez UI i ewentualnie podmienić UI w przyszłości.

---

## 14. Wstępny model danych (zamiast DB — struktura stanu JSON)

Stan gry zapisany do pojedynczego pliku JSON. Brak relacyjnej bazy.

```python
# core/models.py (dataclasses, serializowane do JSON)

@dataclass
class Server:
    id: str
    model_id: str           # referencja do server_models
    quality_tier: str       # "budget" | "standard" | "premium"
    cpu_cores: int
    ram_gb: int
    disk_gb: int
    disk_type: str          # "hdd" | "ssd" | "nvme"
    slot_id: str            # pozycja w serwerowni
    region_id: str
    age_days: int
    mtbf_base: float
    load_cpu: float         # 0.0-1.0
    load_ram: float
    status: str             # "ok" | "down" | "maintenance"
    host_of: list[str]      # lista plan_id które na nim żyją (VPS/WWW)

@dataclass
class ProductPlan:
    id: str
    product_type: str       # "www" | "vps" | "dedicated" | "domain"
    name: str
    cpu_cores: int          # dla VPS/dedyk
    ram_gb: int
    disk_gb: int
    bandwidth_mbps: int
    price_monthly: float
    sla_target: float       # np. 99.9
    setup_fee: float

@dataclass
class CustomerAggregate:
    product_type: str
    segment: str            # "hobbyist" | "small_biz" | "enterprise"
    count: int
    churn_monthly: float
    nps: int
    sla_breaches_this_month: int

@dataclass
class Employee:
    id: str
    name: str
    role: str               # support | sysadmin | neteng | sales | marketing
    level: int              # 1-5
    salary_daily: float
    hired_day: int

@dataclass
class Failure:
    id: str
    type: str               # disk | cpu_overload | overheat | power | network | ddos
    server_id: str | None
    region_id: str
    started_day: int
    duration_hours: int
    status: str             # "active" | "resolved" | "ignored"
    actions_taken: list[str]

@dataclass
class Region:
    id: str
    name: str
    slots_total: int
    slots_used: int
    power_kw_total: float
    power_kw_used: float
    network_gbps: float
    uplinks: int            # redundancja 1/2/3
    cooling_factor: float
    ddos_protection: bool
    rent_daily: float

@dataclass
class Website:
    blocks: list[dict]      # sekcje drag&drop (typ, kolejność, treść)
    conversion_bonus: float # liczony z jakości bloków

@dataclass
class GameState:
    day: int
    cash: float
    reputation: float       # 0-100
    regions: list[Region]
    servers: list[Server]
    products: list[ProductPlan]
    customers: list[CustomerAggregate]
    employees: list[Employee]
    failures_active: list[Failure]
    failures_history: list[Failure]
    marketing_budget_daily: float
    website: Website
    tickets_open: int
    tickets_resolved_today: int
    unlocked_milestones: list[str]
    rng_seed: int
    version: str            # wersja save
```

---

## 15. Podział pracy dla 2 osób

**Osoba A — Core / logika symulacji:**
- `core/` w całości: game.py, simulation.py, economy.py, failures.py, employees.py, customers.py, marketing.py, domains.py, reputation.py, progression.py.
- `data/` (balance, katalogi, generatory).
- `persistence/` (save/load).
- Testy logiki (pytest).

**Osoba B — UI / aplikacja desktop:**
- `ui/` w całości (PySide6): wszystkie ekrany, widgety, SVG racki, wykresy, drag & drop builder.
- `main.py`, `app/` (aplikacja, routing okien).
- Update checker (GitHub API).
- Bundling (PyInstaller), CI (GitHub Actions), releases.
- Ikony, styl dark, monospace, theme.

**Wspólne:**
- Definicja modeli danych (`core/models.py`) — wspólnie, bo to kontrakt między A i B.
- Balans gry — wspólnie (test play).
- Specyfikacja API między UI a core (game expose methods: `game.next_day()`, `game.buy_server(...)`, itd.).

**Zasada integracji:** UI woła metody na obiekcie `Game`, nigdy nie modyfikuje stanu bezpośrednio. `Game` jest jedynym źródłem prawdy. Po każdej akcji UI odświeża się z `Game.get_state()`.

---

## 16. Kolejność implementacji

1. **Scaffold projektu:** struktura katalogów, Git, venv, PySide6 hello world, PyInstaller config, GitHub Actions build. (Osoba B)
2. **Modele danych + Game stub:** `core/models.py`, `core/game.py` z pustym `next_day()`, save/load JSON. (Osoba A)
3. **Main window + Dashboard:** sidebar + prosty dashboard z KPI z `Game`. (Osoba B)
4. **Infrastruktura core:** katalog serwerów, kupowanie, sloty, zasoby DC. (Osoba A logika) + (Osoba B UI slotów SVG).
5. **Produkty + plany:** tworzenie planów, ceny. (A + B)
6. **Klienci (agregaty) + churn + przyrost:** podstawowy loop przyrostu. (A) + (B tabela).
7. **Finanse (przychód/koszty dzienne) + raport dzienny:** pierwsza grywalna pętla „kup serwer → ustaw produkt → next_day → widzisz przychód". (A + B)
8. **Awarie (6 typów + wybór akcji):** (A generowanie + akcje) + (B ekran awarii).
9. **Pracownicy (5 ról, zatrudnianie, automatyczne role):** (A + B).
10. **Marketing + website builder drag&drop:** (A konwersja/bonus) + (B builder).
11. **Domeny per TLD + DNS abstrakcja:** (A + B).
12. **Reputacja + kamienie milowe + progression:** (A + B).
13. **Update checker + licencja + about:** (B).
14. **Balans i polish fazy 1:** wspólne test play, balans MTBF/cen/churn.
15. **Release faza 1 (tag v0.1).**

Po fazie 1 → faza 2 (regiony, enterprise, DDoS upgrade, backup) → faza 3 (multiplayer, więcej produktów, polish).

---

## 17. Roadmapa kolejnych wersji

| Wersja | Zakres | Status |
|--------|--------|--------|
| **v0.1** | Faza 1: core loop, 1 region, 4 produkty, 6 awarii, 5 ról pracowników, marketing, website builder, domeny/DNS, reputacja, save/load, update checker. Pierwsza grywalna wersja. | Cel pierwszy. |
| **v0.2** | Balans, polish, więcej danych serwerów/produktów, ulepszenia UI (filtry, sortowanie, skróty klawiszowe). | |
| **v0.3** | Backup jako mechanika + backup fail awaria. Więcej typów awarii (błąd pracownika, storage fail). | |
| **v0.4** | Wiele regionów / multi-DC. | |
| **v0.5** | Kontrakty enterprise (indywidualni duzi klienci z kontraktami i karami SLA). | |
| **v0.6** | DDoS protection upgrade DC + zaawansowana obrona. | |
| **v0.7** | Skok abstrakcji na późnym etapie (polityki automatyzacji, widoki strategiczne). | |
| **v0.8** | Nowe produkty: Minecraft, serwer aplikacyjny, managed storage. | |
| **v0.9** | Multiplayer faza 1: globalny ranking firm. | |
| **v1.0** | Multiplayer pełny: marketplace, handel domenami, kontrakty między graczami, globalny rynek cen, globalne wydarzenia. Pełne wydanie. | |

---

## Podsumowanie decyzji z wywiadu

| Temat | Decyzja |
|-------|---------|
| Platforma | Desktop (Python + PySide6), brak DB/serwera, stan JSON, licencja komercyjna |
| Tempo | Tury dzienne (1 klik = 1 dzień) |
| Aktywność gracza | Strategia + operacje + reaktywne (miks) |
| Długość sesji | Open-ended 30h+ sandbox |
| Koniec gry | Tylko bankructwo = fail |
| Realizm techniczny | Średni (parametry, bez BGP/IP/OS) |
| Klimat | Hybryda: pro UI dark + lekki flavor |
| Klienci | Agregaty per produkt (brak indywidualnych w faza 1) |
| Losowość awarii | RNG z modyfikatorami stanu (jakość, temp, obciążenie, wiek, cooling, redundancja) |
| Start | Garaż / home lab, 3-5k$ |
| Progression | Kamienie milowe (unlock możliwości), UI płynne |
| Późny etap | Skok abstrakcji (strategia, polityki) |
| Sprzęt | Gotowe modele + tier jakości (budget/standard/premium) |
| Lokacja | Sloty w serwerowni (SVG, bez U) |
| Zasoby DC | Prąd + sieć (Gbps + redundancja) + cooling factor |
| Produkty MVP | Core 4: WWW, VPS, dedyk, domena |
| Ceny/plany | Ręczne ceny, własne plany custom |
| Źródło klientów | Marketing $ + strona drag&drop bonus + organicznie od reputacji |
| Churn | % miesięczny + automatyczne SLA kary |
| Awarie MVP | 6 typów (dysk, CPU, przegrzanie, zasilanie, sieć, DDoS) |
| Reakcja na awarię | Wybór akcji per awaria (restart/wymiana/failover/ignore) |
| DDoS | Specyficzna awaria + ochrona jako upgrade DC |
| Pracownicy | 5 ról, indywidualni (imię, poziom, pensja), automatyczne role |
| Koszty | Standard: DC + prąd + łącza + pensje + licencje |
| Przychód | Subskrypcje miesięczne |
| Finanse UI | Prosta gotówka |
| Domeny | Cennik per TLD, cykl życia |
| DNS | Abstrakcja (działa z hostingiem) |
| Regiony MVP | 1 region (multi-DC w faza 2) |
| UI styl | Dark pro-operator (terminal/panel), monospace, metryki |
| Multiplayer | Singleplayer (multiplayer w faza 3) |
| Stack | Python 3.11+ / PySide6 / JSON / PyInstaller / GitHub Actions |
| Update | Sprawdzanie GitHub releases przy starcie, powiadomienie gracza |
| Website builder | Drag & drop sekcji, bonus do konwersji |
| Licencja | Gra darmowa. CC BY-ND 4.0 (no derivatives na kod). Mody dozwolone przez system modów. |