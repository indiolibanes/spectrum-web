"""
Módulo Centralizado de Versionamento Semântico
SPECTRUM-LAB PRO (Fluent Edition)
"""

__version__ = "4.16.1"
__build__ = "1262"
__release_date__ = "17/10/2026"
__app_name__ = "SPECTRUM-LAB PRO"
__authors__ = ("Davi Baracat", "Kauê Carvalho", "Mateus Ferreira")
__credits__ = "Protótipo desenvolvido por Davi Baracat, Kauê Carvalho e Mateus Ferreira"
# Perfis no GitHub (só quem tem perfil informado vira link).
__author_links__ = {
    "Kauê Carvalho": "https://github.com/indiolibanes",
    "Mateus Ferreira": "https://github.com/yosemate",
}


def credits_html(link_color="#E8C96A"):
    """Assinatura em HTML simples para QLabel, com o nome de cada autor ligado ao seu GitHub."""
    parts = []
    for name in __authors__:
        url = __author_links__.get(name)
        parts.append(f'<a href="{url}" style="color:{link_color};text-decoration:none;font-weight:bold">{name}</a>' if url else name)
    names = ", ".join(parts[:-1]) + " e " + parts[-1] if len(parts) > 1 else parts[0]
    return f"Protótipo desenvolvido por {names}"
__app_title__ = f"{__app_name__} v{__version__} (Build {__build__})"
__app_full_title__ = f"{__app_name__} v{__version__} (Build {__build__}) | Sistema Supervisório Espectrométrico NIR (GY-AS7263)"
