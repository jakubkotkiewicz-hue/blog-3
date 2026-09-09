#!/usr/bin/env python3
"""
Agent AI do automatycznego generowania i publikowania wpisów blogowych
pod SEO na WordPressie (E-fix - serwis telefonów Olsztyn).
 
Wymagane zmienne środowiskowe:
  ANTHROPIC_API_KEY   - klucz API Anthropic (console.anthropic.com)
  WP_URL              - adres strony, np. https://serwis-telefonow-olsztyn.pl
  WP_USER             - login administratora WordPress
  WP_APP_PASSWORD     - hasło APLIKACJI WordPress (nie zwykłe hasło do konta!)
  AUTO_PUBLISH        - "true" = publikuj od razu, inaczej zapisuje jako szkic
"""
 
import os
import csv
import json
import sys
import base64
import requests
import anthropic
 
TOPICS_FILE = "topics.csv"
MODEL = "claude-haiku-4-5-20251001"  # tani i wystarczająco dobry do tego zadania
 
SITE_CONTEXT = """
Jesteś copywriterem SEO dla E-fix - serwisu naprawy telefonów, tabletów,
smartwatchy i laptopów w Olsztynie. Firma naprawia telefony marek Apple,
Samsung, Xiaomi, Huawei, Oppo, Vivo, Motorola. Oferuje wymianę wyświetlaczy,
szybek, baterii, gniazd ładowania, czyszczenie po zalaniu oraz odzyskiwanie
danych. Ton: rzeczowy, pomocny, budujący zaufanie lokalnego eksperta.
Zawsze pisz po polsku, konkretnie i bez lania wody.
"""
 
 
def env(name):
    """Czyta zmienną środowiskową i usuwa białe znaki (spacje, nowe linie),
    które czasem wkradają się przy kopiowaniu sekretów do GitHuba."""
    return os.environ[name].strip()
 
 
def load_next_topic(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if row["status"].strip().lower() != "done":
            return row, rows
    return None, rows
 
 
def save_topics(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["keyword", "status"])
        writer.writeheader()
        writer.writerows(rows)
 
 
def generate_post(topic):
    client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY"))
    prompt = f"""{SITE_CONTEXT}
 
Napisz wpis na bloga pod SEO na temat: "{topic}"
 
Wymagania:
- 700-1000 słów
- Tytuł jako H1, kilka śródtytułów H2/H3 w treści
- Naturalnie wpleć frazę kluczową i frazy pokrewne (bez keyword-stuffingu)
- Konkretne, praktyczne informacje, nie ogólniki
- Zakończ krótkim CTA zachęcającym do kontaktu z serwisem
- Odpowiedz WYŁĄCZNIE poprawnym JSON, bez markdown i bez komentarzy, dokładnie w tym formacie:
{{"title": "...", "meta_description": "maks. 155 znaków", "html_body": "treść w HTML, tagi <h2>, <p> itd."}}
"""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    for fence in ("```json", "```"):
        if text.startswith(fence):
            text = text[len(fence):]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text.strip())
 
 
def publish_to_wordpress(post, status):
    wp_url = env("WP_URL").rstrip("/")
    user = env("WP_USER")
    app_password = env("WP_APP_PASSWORD")
    token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
 
    resp = requests.post(
        f"{wp_url}/wp-json/wp/v2/posts",
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        },
        json={
            "title": post["title"],
            "content": post["html_body"],
            "excerpt": post["meta_description"],
            "status": status,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
 
 
def main():
    topic_row, all_rows = load_next_topic(TOPICS_FILE)
    if topic_row is None:
        print("Brak nowych tematów w topics.csv - dodaj kolejne wiersze i uruchom ponownie.")
        sys.exit(0)
 
    print(f"Generuję wpis na temat: {topic_row['keyword']}")
    post = generate_post(topic_row["keyword"])
 
    status = "publish" if os.environ.get("AUTO_PUBLISH", "").strip().lower() == "true" else "draft"
    result = publish_to_wordpress(post, status)
    print(f"Zapisano na WordPressie ({status}): {result.get('link')}")
 
    topic_row["status"] = "done"
    save_topics(TOPICS_FILE, all_rows)
 
 
if __name__ == "__main__":
    main()
