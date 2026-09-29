"""Renderer faktycznego wyglądu strony firmy.

Renderuje bloki strony jako HTML/CSS w QWebEngineView lub QTextBrowser.
Używamy QTextBrowser (bez zależności QtWebEngine — lżejsze, bez dodatkowych
alertów AV). Renderujemy stylizowany HTML.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget


def render_website_html(blocks: list, company_name: str = "Moja Firma Hostingowa") -> str:
    """Renderuje HTML strony firmy z bloków."""
    css = """
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0;
               background: #0f172a; color: #e2e8f0; }
        .container { max-width: 720px; margin: 0 auto; padding: 16px; }
        .nav { background: #1e293b; padding: 14px 20px; border-bottom: 2px solid #2563eb; }
        .nav .logo { font-weight: bold; font-size: 18px; color: #60a5fa; }
        .block { margin: 12px 0; padding: 16px; border-radius: 8px; background: #1e293b;
                 border: 1px solid #334155; }
        .hero { text-align: center; padding: 40px 16px; background: linear-gradient(135deg, #1e3a5f, #2563eb);
                border: none; }
        .hero h1 { font-size: 28px; margin: 0 0 12px; color: #fff; }
        .hero p { font-size: 14px; color: #bfdbfe; margin: 0; }
        .pricing h2 { color: #60a5fa; margin-top: 0; }
        .plan { background: #0f172a; padding: 12px; margin: 8px 0; border-left: 3px solid #2563eb;
                border-radius: 4px; }
        .plan .price { color: #4ade80; font-weight: bold; float: right; }
        .reviews .quote { font-style: italic; color: #cbd5e1; padding: 8px 0; border-bottom: 1px solid #334155; }
        .reviews .author { color: #60a5fa; font-size: 12px; }
        .status .row { display: flex; justify-content: space-between; padding: 6px 0;
                       border-bottom: 1px solid #334155; }
        .status .ok { color: #4ade80; }
        .faq details { padding: 8px 0; border-bottom: 1px solid #334155; }
        .faq summary { cursor: pointer; color: #60a5fa; font-weight: bold; }
        .contact .line { padding: 4px 0; }
        .chat { text-align: center; }
        .chat .bubble { display: inline-block; background: #2563eb; color: #fff; padding: 8px 16px;
                        border-radius: 16px; }
        .blog .post { padding: 8px 0; border-bottom: 1px solid #334155; }
        .blog .post .title { color: #60a5fa; font-weight: bold; }
        .blog .post .meta { color: #64748b; font-size: 11px; }
        .footer { text-align: center; padding: 24px; color: #64748b; font-size: 12px; }
    </style>
    """

    parts = [f"<html><head><meta charset='utf-8'>{css}</head><body>"]
    parts.append(
        f"<div class='nav'><span class='logo'>🌐 {company_name}</span></div>"
    )
    parts.append("<div class='container'>")

    sorted_blocks = sorted(blocks, key=lambda b: b.order)
    for block in sorted_blocks:
        bt = block.block_type
        if bt == "hero":
            parts.append(
                "<div class='block hero'>"
                "<h1>Cloud hosting bez kompromisów</h1>"
                "<p>VPS • Hosting WWW • Dedyki • Domeny — od garażu do globalnego providera</p>"
                "</div>"
            )
        elif bt == "pricing":
            parts.append(
                "<div class='block pricing'>"
                "<h2>💰 Cennik</h2>"
                "<div class='plan'>Hosting WWW — 1 GB SSD<span class='price'>$4.99/mies</span></div>"
                "<div class='plan'>VPS 2vCPU / 4GB / 50GB<span class='price'>$9.99/mies</span></div>"
                "<div class='plan'>Serwer dedykowany<span class='price'>$89.00/mies</span></div>"
                "</div>"
            )
        elif bt == "reviews":
            parts.append(
                "<div class='block reviews'>"
                "<h2>⭐ Opinie klientów</h2>"
                "<div class='quote'>„Najlepszy support jaki miałem — odpowiedź w 5 minut!”"
                "<div class='author'>— Marek K.</div></div>"
                "<div class='quote'>„Uptime 99.99% przez rok. Polecam.”"
                "<div class='author'>— Anna W.</div></div>"
                "</div>"
            )
        elif bt == "status":
            parts.append(
                "<div class='block status'>"
                "<h2>📡 Status serwerów</h2>"
                "<div class='row'><span>Region EU-1</span><span class='ok'>● Operacyjny</span></div>"
                "<div class='row'><span>Region US-1</span><span class='ok'>● Operacyjny</span></div>"
                "<div class='row'><span>DNS</span><span class='ok'>● Operacyjny</span></div>"
                "</div>"
            )
        elif bt == "faq":
            parts.append(
                "<div class='block faq'>"
                "<h2>❓ FAQ</h2>"
                "<details><summary>Jak szybko aktywujecie VPS?</summary>"
                "Automatycznie w mniej niż 60 sekund.</details>"
                "<details><summary>Czy mam panel do zarządzania?</summary>"
                "Tak, pełny panel z metrykami i restartem.</details>"
                "</div>"
            )
        elif bt == "contact":
            parts.append(
                "<div class='block contact'>"
                "<h2>✉️ Kontakt</h2>"
                "<div class='line'>📧 support@example.com</div>"
                "<div class='line'>📞 +48 800 000 000</div>"
                "<div class='line'>💬 Live chat 24/7</div>"
                "</div>"
            )
        elif bt == "chat":
            parts.append(
                "<div class='block chat'>"
                "<h2>💬 Live chat</h2>"
                "<div class='bubble'>Napisz do nas — odpowiadamy w 5 minut!</div>"
                "</div>"
            )
        elif bt == "blog":
            parts.append(
                "<div class='block blog'>"
                "<h2>📝 Blog</h2>"
                "<div class='post'><div class='title'>Jak wybrać VPS w 2026</div>"
                "<div class='meta'>2 dni temu • Tech</div></div>"
                "<div class='post'><div class='title'>Backup: dlaczego warto</div>"
                "<div class='meta'>5 dni temu • Porady</div></div>"
                "</div>"
            )

    parts.append("</div>")
    parts.append(f"<div class='footer'>© 2026 {company_name} — Wszelkie prawa zastrzeżone</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


class WebsiteRenderer(QWidget):
    """Widget pokazujący faktyczny wygląd strony firmy."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Podgląd strony")
        title.setObjectName("section-title")
        layout.addWidget(title)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        layout.addWidget(self.browser, 1)

    def render(self, blocks: list, company_name: str = "Moja Firma Hostingowa") -> None:
        html = render_website_html(blocks, company_name)
        self.browser.setHtml(html)