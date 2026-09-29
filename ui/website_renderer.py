"""Renderer faktycznego wyglądu strony firmy — inspirowany OVH.com.

Nowoczesny layout: gradient hero, grid produktów z cenami, sekcje z metrykami.
Renderowany jako HTML w QTextBrowser.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget


def render_website_html(blocks: list, company_name: str = "Moja Firma Hostingowa",
                        cash: float = 0, customers: int = 0, reputation: float = 50) -> str:
    """Renderuje HTML strony firmy z bloków."""
    css = """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            background: #0a0e1a; color: #e2e8f0; font-size: 14px; line-height: 1.6;
        }
        a { color: #3b82f6; text-decoration: none; }

        /* NAV — jak OVH: dark, gradient, logo + menu */
        .nav {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 16px 32px;
            border-bottom: 3px solid #3b82f6;
            display: flex; justify-content: space-between; align-items: center;
        }
        .nav .logo { font-size: 22px; font-weight: 800; color: #3b82f6; letter-spacing: -0.5px; }
        .nav .menu a { color: #cbd5e1; margin-left: 24px; font-size: 13px; font-weight: 500; }
        .nav .menu a:hover { color: #3b82f6; }
        .nav .badge { background: #3b82f6; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; }

        /* HERO — gradient, duży napis, CTA */
        .hero {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3730a3 100%);
            padding: 64px 32px; text-align: center; position: relative; overflow: hidden;
        }
        .hero::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 30% 50%, rgba(59,130,246,0.3) 0%, transparent 50%);
        }
        .hero h1 { font-size: 36px; color: white; font-weight: 800; margin-bottom: 16px; position: relative; }
        .hero p { font-size: 18px; color: #bfdbfe; max-width: 600px; margin: 0 auto 24px; position: relative; }
        .hero .cta {
            display: inline-block; background: #3b82f6; color: white; padding: 12px 32px;
            border-radius: 6px; font-weight: 700; font-size: 15px; position: relative;
        }
        .hero .stats { margin-top: 32px; display: flex; justify-content: center; gap: 48px; position: relative; }
        .hero .stat { text-align: center; }
        .hero .stat .num { font-size: 28px; font-weight: 800; color: white; }
        .hero .stat .lbl { font-size: 12px; color: #93c5fd; text-transform: uppercase; }

        /* SEKCJA — białe karty na ciemnym tle */
        section { padding: 48px 32px; }
        .section-title { font-size: 24px; font-weight: 800; color: white; margin-bottom: 8px; text-align: center; }
        .section-sub { color: #94a3b8; text-align: center; margin-bottom: 32px; font-size: 14px; }

        /* GRID PRODUKTÓW — karty jak OVH */
        .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; max-width: 900px; margin: 0 auto; }
        .product {
            background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 24px;
            text-align: center; transition: transform 0.2s;
        }
        .product:hover { border-color: #3b82f6; transform: translateY(-2px); }
        .product .icon { font-size: 32px; margin-bottom: 12px; }
        .product .name { font-size: 16px; font-weight: 700; color: white; margin-bottom: 8px; }
        .product .price { font-size: 28px; font-weight: 800; color: #4ade80; margin: 8px 0; }
        .product .price .per { font-size: 13px; color: #94a3b8; font-weight: 400; }
        .product .features { color: #cbd5e1; font-size: 12px; text-align: left; margin-top: 12px; }
        .product .features div { padding: 4px 0; border-bottom: 1px solid #334155; }
        .product .features div:last-child { border: none; }
        .product .btn {
            display: inline-block; margin-top: 16px; background: #3b82f6; color: white;
            padding: 8px 20px; border-radius: 6px; font-weight: 600; font-size: 13px;
        }

        /* OPINIE */
        .reviews-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; max-width: 700px; margin: 0 auto; }
        .review {
            background: #1e293b; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px;
        }
        .review .quote { font-style: italic; color: #e2e8f0; margin-bottom: 8px; }
        .review .author { color: #3b82f6; font-weight: 600; font-size: 12px; }
        .review .stars { color: #facc15; margin-bottom: 4px; }

        /* STATUS */
        .status-grid { max-width: 700px; margin: 0 auto; }
        .status-row {
            display: flex; justify-content: space-between; padding: 12px 0;
            border-bottom: 1px solid #334155; align-items: center;
        }
        .status-row .name { color: #cbd5e1; font-weight: 500; }
        .status-row .ok { color: #4ade80; font-weight: 600; }
        .status-row .ok::before { content: '● '; }

        /* FAQ */
        .faq-list { max-width: 700px; margin: 0 auto; }
        .faq-item { background: #1e293b; border-radius: 6px; margin-bottom: 8px; padding: 16px; }
        .faq-item .q { font-weight: 700; color: #3b82f6; margin-bottom: 8px; }
        .faq-item .a { color: #cbd5e1; font-size: 13px; }

        /* KONTAKT */
        .contact-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; max-width: 700px; margin: 0 auto; text-align: center; }
        .contact-card { background: #1e293b; border-radius: 8px; padding: 24px; }
        .contact-card .icon { font-size: 28px; margin-bottom: 8px; }
        .contact-card .label { color: #94a3b8; font-size: 11px; text-transform: uppercase; margin-bottom: 4px; }
        .contact-card .value { color: white; font-weight: 600; }

        /* LIVE CHAT */
        .chat-box {
            max-width: 500px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 24px; text-align: center;
        }
        .chat-bubble {
            display: inline-block; background: #3b82f6; color: white; padding: 10px 20px;
            border-radius: 16px; font-weight: 600;
        }

        /* BLOG */
        .blog-list { max-width: 700px; margin: 0 auto; }
        .blog-post {
            background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 12px;
            border-left: 3px solid #3b82f6;
        }
        .blog-post .title { color: white; font-weight: 700; font-size: 15px; margin-bottom: 4px; }
        .blog-post .meta { color: #64748b; font-size: 11px; margin-bottom: 8px; }
        .blog-post .excerpt { color: #94a3b8; font-size: 13px; }

        /* FOOTER */
        .footer {
            background: #0f172a; padding: 32px; text-align: center; color: #64748b; font-size: 12px;
            border-top: 1px solid #1e293b;
        }
        .footer a { color: #94a3b8; margin: 0 12px; }

        .empty { padding: 48px; text-align: center; color: #64748b; }
    </style>
    """

    parts = [f"<html><head><meta charset='utf-8'>{css}</head><body>"]

    # NAV
    parts.append(
        f"<div class='nav'>"
        f"<span class='logo'>🌐 {company_name}</span>"
        f"<div class='menu'>"
        f"<a href='#'>Hosting</a><a href='#'>VPS</a><a href='#'>Dedyki</a>"
        f"<a href='#'>Domeny</a><a href='#'>Status</a><a href='#'>Kontakt</a>"
        f"</div>"
        f"<span class='badge'>🔴 Online</span>"
        f"</div>"
    )

    sorted_blocks = sorted(blocks, key=lambda b: b.order)
    has_hero = any(b.block_type == "hero" for b in sorted_blocks)

    # HERO (zawsze obecny, ale jeśli dodany jako blok — z metrykami)
    if has_hero:
        parts.append(
            f"<div class='hero'>"
            f"<h1>Cloud hosting bez kompromisów</h1>"
            f"<p>VPS, hosting WWW, serwery dedykowane i domeny — "
            f"niezawodna infrastruktura dla Twojego biznesu.</p>"
            f"<a href='#' class='cta'>Zobacz ofertę →</a>"
            f"<div class='stats'>"
            f"<div class='stat'><div class='num'>{customers:,}</div><div class='lbl'>Klientów</div></div>"
            f"<div class='stat'><div class='num'>99.{min(99,int(reputation))}%</div><div class='lbl'>Uptime</div></div>"
            f"<div class='stat'><div class='num'>24/7</div><div class='lbl'>Support</div></div>"
            f"</div>"
            f"</div>"
        )

    for block in sorted_blocks:
        bt = block.block_type
        if bt == "pricing":
            parts.append(
                "<section>"
                "<div class='section-title'>Nasze produkty</div>"
                "<div class='section-sub'>Wybierz usługę dopasowaną do Twoich potrzeb</div>"
                "<div class='grid'>"
                "<div class='product'>"
                "<div class='icon'>🌐</div>"
                "<div class='name'>Hosting WWW</div>"
                "<div class='price'>$4.99<span class='per'>/mies</span></div>"
                "<div class='features'><div>✓ 10 GB SSD</div><div>✓ SSL gratis</div><div>✓ Panel</div></div>"
                "<a href='#' class='btn'>Wybierz</a>"
                "</div>"
                "<div class='product'>"
                "<div class='icon'>🖥️</div>"
                "<div class='name'>VPS</div>"
                "<div class='price'>$9.99<span class='per'>/mies</span></div>"
                "<div class='features'><div>✓ 2 vCPU</div><div>✓ 4 GB RAM</div><div>✓ 50 GB NVMe</div></div>"
                "<a href='#' class='btn'>Wybierz</a>"
                "</div>"
                "<div class='product'>"
                "<div class='icon'>🗄️</div>"
                "<div class='name'>Dedyk</div>"
                "<div class='price'>$89<span class='per'>/mies</span></div>"
                "<div class='features'><div>✓ 8 vCPU</div><div>✓ 32 GB RAM</div><div>✓ 1 TB SSD</div></div>"
                "<a href='#' class='btn'>Wybierz</a>"
                "</div>"
                "</div>"
                "</section>"
            )
        elif bt == "reviews":
            parts.append(
                "<section>"
                "<div class='section-title'>Co mówią klienci</div>"
                "<div class='section-sub'>Zaufały nam tysiące firm</div>"
                "<div class='reviews-grid'>"
                "<div class='review'>"
                "<div class='stars'>★★★★★</div>"
                "<div class='quote'>Najlepszy support jaki miałem — odpowiedź w 5 minut!</div>"
                "<div class='author'>— Marek K., startup</div>"
                "</div>"
                "<div class='review'>"
                "<div class='stars'>★★★★★</div>"
                "<div class='quote'>Uptime 99.99% przez rok. Polecam każdemu.</div>"
                "<div class='author'>— Anna W., agencja</div>"
                "</div>"
                "<div class='review'>"
                "<div class='stars'>★★★★☆</div>"
                "<div class='quote'>Dobre ceny, szybki VPS, panel intuicyjny.</div>"
                "<div class='author'>— Piotr Z., freelancer</div>"
                "</div>"
                "<div class='review'>"
                "<div class='stars'>★★★★★</div>"
                "<div class='quote'>Migracja za darmo, wszystko działa od pierwszego dnia.</div>"
                "<div class='author'>— Kasia L., e-commerce</div>"
                "</div>"
                "</div>"
                "</section>"
            )
        elif bt == "status":
            parts.append(
                "<section>"
                "<div class='section-title'>Status systemu</div>"
                "<div class='section-sub'>Wszystkie systemy operacyjne</div>"
                "<div class='status-grid'>"
                "<div class='status-row'><span class='name'>Region EU-1</span><span class='ok'>Operacyjny</span></div>"
                "<div class='status-row'><span class='name'>Region US-1</span><span class='ok'>Operacyjny</span></div>"
                "<div class='status-row'><span class='name'>DNS globalny</span><span class='ok'>Operacyjny</span></div>"
                "<div class='status-row'><span class='name'>Backup</span><span class='ok'>Operacyjny</span></div>"
                "<div class='status-row'><span class='name'>Panel</span><span class='ok'>Operacyjny</span></div>"
                "</div>"
                "</section>"
            )
        elif bt == "faq":
            parts.append(
                "<section>"
                "<div class='section-title'>Najczęstsze pytania</div>"
                "<div class='faq-list'>"
                "<div class='faq-item'><div class='q'>Jak szybko aktywujecie VPS?</div>"
                "<div class='a'>Automatycznie w mniej niż 60 sekund po płatności.</div></div>"
                "<div class='faq-item'><div class='q'>Czy mam panel do zarządzania?</div>"
                "<div class='a'>Tak, pełny panel z metrykami, restartem i snapshotami.</div></div>"
                "<div class='faq-item'><div class='q'>Czy oferujecie SLA?</div>"
                "<div class='a'>Tak, SLA 99.9% z karami umownymi w planach Business.</div></div>"
                "</div>"
                "</section>"
            )
        elif bt == "contact":
            parts.append(
                "<section>"
                "<div class='section-title'>Kontakt</div>"
                "<div class='section-sub'>Jesteśmy do dyspozycji 24/7</div>"
                "<div class='contact-grid'>"
                "<div class='contact-card'><div class='icon'>📧</div>"
                "<div class='label'>Email</div><div class='value'>support@example.com</div></div>"
                "<div class='contact-card'><div class='icon'>📞</div>"
                "<div class='label'>Telefon</div><div class='value'>+48 800 000 000</div></div>"
                "<div class='contact-card'><div class='icon'>💬</div>"
                "<div class='label'>Live chat</div><div class='value'>24/7 online</div></div>"
                "</div>"
                "</section>"
            )
        elif bt == "chat":
            parts.append(
                "<section>"
                "<div class='chat-box'>"
                "<div class='chat-bubble'>💬 Napisz do nas — odpowiadamy średnio w 5 minut!</div>"
                "</div>"
                "</section>"
            )
        elif bt == "blog":
            parts.append(
                "<section>"
                "<div class='section-title'>Blog techniczny</div>"
                "<div class='blog-list'>"
                "<div class='blog-post'><div class='title'>Jak wybrać VPS w 2026</div>"
                "<div class='meta'>2 dni temu • Tech • 5 min czytania</div>"
                "<div class='excerpt'>Porównanie vCPU, RAM i dysków — co naprawdę matters dla Twojej aplikacji.</div></div>"
                "<div class='blog-post'><div class='title'>Backup: dlaczego warto go mieć</div>"
                "<div class='meta'>5 dni temu • Porady • 3 min czytania</div>"
                "<div class='excerpt'>3 rodzaje backupu i kiedy używać każdego z nich w praktyce.</div></div>"
                "</div>"
                "</section>"
            )

    # FOOTER
    parts.append(
        f"<div class='footer'>"
        f"<div>© 2026 {company_name} — Wszelkie prawa zastrzeżone</div>"
        f"<div style='margin-top: 8px;'>"
        f"<a href='#'>Regulamin</a><a href='#'>Polityka prywatności</a>"
        f"<a href='#'>SLA</a><a href='#'>Status</a>"
        f"</div>"
        f"</div>"
    )

    parts.append("</body></html>")
    return "\n".join(parts)


class WebsiteRenderer(QWidget):
    """Widget pokazujący faktyczny wygląd strony firmy (inspirowany OVH)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Podgląd strony")
        title.setObjectName("section-title")
        layout.addWidget(title)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        # Szerokość jak browser (limitowana)
        self.browser.setMinimumWidth(400)
        layout.addWidget(self.browser, 1)

    def render(self, blocks: list, company_name: str = "Moja Firma Hostingowa",
               cash: float = 0, customers: int = 0, reputation: float = 50) -> None:
        html = render_website_html(blocks, company_name, cash, customers, reputation)
        self.browser.setHtml(html)