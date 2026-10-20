"""
Módulo Centralizado de Versionamento Semântico
SPECTRUM-LAB PRO (Fluent Edition)
"""

__version__ = "4.16.4"
__build__ = "1265"
__release_date__ = "20/10/2026"
__app_name__ = "SPECTRUM-LAB PRO"
__authors__ = ("Davi Baracat", "Kauê Alencar", "Mateus Ferreira")
__credits__ = "Protótipo desenvolvido por Davi Baracat, Kauê Alencar e Mateus Ferreira"
# Perfis no GitHub (só quem tem perfil informado vira link).
__author_links__ = {
    "Davi Baracat": "https://github.com/DaviBaracat",
    "Kauê Alencar": "https://github.com/indiolibanes",
    "Mateus Ferreira": "https://github.com/yosemate",
}


def credits_html(link_color=None):
    """Assinatura em HTML simples para QLabel, com o nome de cada autor ligado ao seu GitHub.

    Sem link_color, o link usa a cor de link da paleta do tema (QPalette.Link = destaque)."""
    parts = []
    for name in __authors__:
        url = __author_links__.get(name)
        color = f"color:{link_color};" if link_color else ""
        parts.append(f'<a href="{url}" style="{color}text-decoration:none;font-weight:bold">{name}</a>' if url else name)
    names = ", ".join(parts[:-1]) + " e " + parts[-1] if len(parts) > 1 else parts[0]
    return f"Protótipo desenvolvido por {names}"
__app_title__ = f"{__app_name__} v{__version__} (Build {__build__})"
__app_full_title__ = f"{__app_name__} v{__version__} (Build {__build__}) | Sistema Supervisório Espectrométrico NIR (GY-AS7263)"
