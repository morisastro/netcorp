# Changelog

## [0.3.1] - 2026-09-29

### Dodane
- Awansowanie pracowników (XP system)
  - Pracownicy zdobywają XP za rozwiązanee tickety/awarie
  - Awans na kolejny level przy odpowiedniej liczbie XP (max Lv 5)
  - Pensja rośnie z awansem (level × $30/dzień)
  - Pasek XP pokazywany w karcie pracownika
- Błędy pracowników (rzadkie, z konsekwencjami)
  - Każda rola techniczna ma konkretne typy błędów:
    - Sysadmin: dysk, zasilanie, ogólny
    - Network engineer: sieć, DDoS, ogólny
    - Support: tylko ogólny (mało ryzykowne)
  - Błąd = serwer pada na 1 dzień, pracownik traci level, reputacja spada
  - Szansa błędu maleje z poziomem (Lv1: 2%, Lv5: 0.8%)
- Checkbox "Auto-naprawa" per pracownik
  - Gracz wybiera czy pracownik może automatycznie naprawiać
  - Wyłączenie = brak błędów ale też brak auto-napraw
- Nowe opcje modowania dla pracowników:
  - mistake_chance_base, mistake_rep_loss, mistake_level_loss
  - xp_per_ticket, xp_per_level, max_level
- Typ awarii "employee_mistake" w UI
- Liczba błędów pokazywana w karcie pracownika
