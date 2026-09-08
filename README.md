# Agent AI do publikacji wpisów na blogu (E-fix Olsztyn)

Co tydzień bierze kolejny temat z `topics.csv`, pisze wpis (Claude API)
i zapisuje go na Twoim WordPressie. Domyślnie jako **szkic** — Ty klikasz
"Publikuj" po przejrzeniu. Całość działa na GitHub Actions, więc nie
potrzebujesz żadnego serwera.

## Koszt

- GitHub Actions, harmonogram, WordPress REST API — **0 zł**.
- Jedyny koszt to wywołania Claude API: przy modelu Haiku 4.5 to grosze
  za wpis (ok. kilku groszy), czyli pojedyncze złote rocznie przy
  publikacji raz w tygodniu. Aktualny cennik: https://claude.com/pricing

## Konfiguracja krok po kroku

### 1. Wrzuć ten folder na GitHub
Załóż darmowe konto na github.com (jeśli nie masz), utwórz nowe repozytorium
(może być prywatne) i wgraj do niego zawartość tego folderu.

### 2. Wygeneruj hasło aplikacji w WordPressie
W panelu WP: **Użytkownicy → Profil** → sekcja "Hasła aplikacji" na dole
strony → wpisz nazwę np. `blog-agent` → **Dodaj nowe hasło aplikacji**.
Skopiuj wygenerowany ciąg znaków (pokazany tylko raz) — to jest
`WP_APP_PASSWORD`, nie hasło do Twojego konta.

Wymaga WordPress 5.6+ i strony po HTTPS — Twoja strona spełnia oba warunki.
Jeśli nie widzisz tej sekcji, zapytaj hostingodawcę, czy REST API i
Application Passwords są włączone.

### 3. Zdobądź klucz Anthropic API
Wejdź na console.anthropic.com → **API Keys** → **Create Key**. To osobne
konto od Claude.ai/aplikacji Claude — działa na płatności za zużycie
(patrz sekcja Koszt wyżej).

### 4. Dodaj sekrety w repozytorium GitHub
**Settings → Secrets and variables → Actions → New repository secret**,
dodaj cztery:
- `ANTHROPIC_API_KEY`
- `WP_URL` — np. `https://serwis-telefonow-olsztyn.pl`
- `WP_USER` — Twój login administratora WP
- `WP_APP_PASSWORD` — hasło z kroku 2

### 5. (opcjonalnie) włącz automatyczną publikację
Domyślnie wpisy trafiają jako szkic. Jeśli po kilku tygodniach uznasz,
że jakość jest stabilna i chcesz publikować bez ręcznego zatwierdzania:
**Settings → Secrets and variables → Actions → zakładka Variables →
New repository variable** → `AUTO_PUBLISH` = `true`.

### 6. Przetestuj ręcznie
Zakładka **Actions** → "Publikacja wpisu na blogu" → **Run workflow**.
Sprawdź w panelu WP, czy szkic się pojawił.

## Dodawanie kolejnych tematów

Edytuj `topics.csv`, dodaj wiersz: `fraza kluczowa,pending`. Skąd brać
tematy za darmo:
- Google Search Console (frazy, na które już się pojawiasz)
- Google Keyword Planner (wolumeny wyszukiwań)
- pytania, które faktycznie zadają klienci w serwisie

## Ważne

Zawsze przeglądaj szkice przed publikacją — regularna, ale nadzorowana
publikacja z realną wartością dla czytelnika jest bezpieczna; masowa,
bezobsługowa publikacja ryzykuje wpadnięciem w politykę Google dot.
"scaled content abuse", o czym rozmawialiśmy wcześniej.

## Harmonogram

Domyślnie: poniedziałki 8:00 UTC. Zmień w
`.github/workflows/publish-blog.yml`, linia z `cron`.
