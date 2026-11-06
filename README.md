# FigCraft to Bootstrap 5 + FontAwesome Exporter Engine (Native Rust / WASM v2.0)

[![FigCraft](https://img.shields.io/badge/FigCraft-Plugin%20(Native%20WASM)-blue?logo=rust&logoColor=white)](https://github.com/storytold/figcraft)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3+-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![FontAwesome 7](https://img.shields.io/badge/FontAwesome-7-339AF0?logo=fontawesome&logoColor=white)](https://fontawesome.com/)
[![Pure Rust](https://img.shields.io/badge/Language-Pure%20Rust%20%2F%20WASM-orange?logo=rust)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plugin **100% nativo em Rust compilado para WebAssembly (WASM)** para o **[FigCraft](https://github.com/storytold/figcraft)** (clone open-source em Rust do Figma).

Executado **diretamente de dentro do FigCraft** ao clicar no menu de Plugins: lê a hierarquia dos frames, extrai estilos reais, gera **todas as classes CSS de cada elemento** com Bootstrap 5.3+ e ícones FontAwesome, e aciona o diálogo nativo do sistema para salvar o `index.html` compilado.

---

## ⚡ Como Funciona a Execução Nativa por Dentro do FigCraft

Ao contrário de scripts externos que exigem terminal ou atalhos fora do programa, a versão **v2.0.0** foi totalmente reescrita em **Rust puro**:

1. **Acionamento no Menu**: Você clica em `Plugins ▸ Bootstrap 5 & FontAwesome Exporter ▸ Exportar para Bootstrap 5…`.
2. **Execução em Sandbox WASM**: O motor do FigCraft invoca a função `figcraft_run` do binário `plugin.wasm`.
3. **Leitura da Árvore de Camadas**: O plugin consulta os frames da seleção ou da página através de chamadas internas seguras (`node.find` e `node.get`).
4. **Compilação Semântica com Classes CSS Reais**:
   * Cada nó recebe sua própria classe CSS semântica (ex: `.fc-hero-title-12`, `.fc-station-card-16`, `.fc-btn-play-22`).
   * As regras CSS reais de cada elemento (posicionamento, dimensões, cores hex/rgba, gradientes lineares, sombras `box-shadow`, desfoques `backdrop-filter: blur()`, auto-layout flexbox e tipografia) são geradas na folha de estilo.
   * Integração de classes nativas do **Bootstrap 5.3** (`card`, `btn`, `badge`, `d-flex`, etc.) e ícones **FontAwesome**.
5. **Diálogo de Salvamento Nativo**: O plugin invoca a syscall oficial `save_file("index.html", "text/html", bytes)` do FigCraft, que abre a janela nativa do Windows/macOS/Linux para você salvar o arquivo HTML completo!
6. **Toast de Confirmação**: O FigCraft exibe uma notificação nativa confirmando a quantidade de nós e classes CSS geradas.

---

## 🚀 Instalação Rápida no FigCraft

1. No FigCraft, clique no logo (canto superior esquerdo) ▸ **Plugins ▸ Development ▸ Import plugin from manifest...**.
2. Selecione o arquivo **`figcraft-plugin.json`**.
3. Pronto! O comando aparecerá no menu **Plugins**.
4. Sempre que quiser exportar, basta clicar no comando e escolher onde salvar o seu `index.html`!

---

## 🛠️ Como Compilar a Partir do Código-Fonte Rust

Caso deseje compilar ou customizar o módulo WebAssembly:

```bash
# 1. Adicionar o target wasm32 (se ainda não tiver):
rustup target add wasm32-unknown-unknown

# 2. Compilar o plugin em modo release otimizado:
cargo build --target wasm32-unknown-unknown --release

# 3. O binário compilado será gerado em:
# target/wasm32-unknown-unknown/release/plugin.wasm
```

---

## 👤 Autor

Desenvolvido por **[Uziel](https://github.com/uzielweb)**  
Licença MIT.
