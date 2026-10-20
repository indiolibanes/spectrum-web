# Interface ISA-101, tema noturno e correções — 4.16.2

Versão 4.16.2 · Build 1263 · 20/10/2026.

## O que mudou

**Interface**

- Estilo minimalista: gráficos com cor por banda; **botões neutros e iguais** (sem cor por função); cantos de 12 px; sem degradê, reflexo nem textura nos controles.
- **Painéis translúcidos** sobre brilhos suaves do fundo, nos dois temas, para que a profundidade venha da transparência. Veja a exceção registrada em [docs/ISA-101.md](docs/ISA-101.md).
- Tema **Noturno** com roxo profundo, **ouro** como destaque e roxo lilás como secundária. Tema **Claro** com quatro verdes distintos. Preferências antigas (`dark`, `gold`, `umber`) migram sozinhas.
- Botões com estilo iOS: véu translúcido, mola curta ao pressionar, sem onda nem anel de luz.
- Fonte principal trocada para **Inter** (sans-serif neutra, SIL OFL). Títulos em Dropline, marca em Arena, valores em IBM Plex Mono.
- Logo do projeto ao lado do nome no cabeçalho.
- Indicadores (KPIs) e logos do rodapé menores; cartões **ESP32 · Comunicação** e **Sensor espectral** com mais destaque.
- Link do GitHub de Davi Baracat (@DaviBaracat) e nome **Kauê Alencar** na assinatura.

**Teclado na tela**

- Não abre mais sozinho ao iniciar um teste. Reconhece se o aparelho tem tela de toque (ou é móvel) e só então abre; modos **Automático**, **Sempre** e **Nunca**.
- Menor e no canto superior esquerdo (desloca-se só se cobrir o campo).

**Conexão com o ESP32**

- Tempo-limite de 4 s na conexão TCP, botão "Conectando…" durante a tentativa e janela **Falha na conexão** com o motivo.
- O indicador abaixo do gráfico mostra "ESP32 desconectado" em vez de "Pronto" quando não há conexão.
- **Causa raiz não confirmada.** O defeito relatado ("pronto" mas "desconectado") não foi reproduzido: o transporte funcionou em teste sem interface. As mudanças acima tornam a falha visível e explicável; o teste N1–N5 de [docs/TUTORIAL_CODESPACE.md](docs/TUTORIAL_CODESPACE.md) (seção F) deve fechar o caso, de preferência também com o ESP32 real.

## Limites desta versão

- A interface gráfica real (PyQt5) não pôde ser executada no ambiente de desenvolvimento do assistente. Os testes sem interface passam; os testes de interface (`tests/test_gui_smoke.py`) e a conferência visual dependem do Codespace.
- A ISA-101 foi aplicada a partir de fontes secundárias; a norma não foi lida na íntegra.
- As fontes Arena e Dropline (e as decorativas Evershore e Heritage, não usadas) vieram sem licença legível: confirme os direitos antes de distribuir.
- Android e web continuam para a última fase do roteiro.
