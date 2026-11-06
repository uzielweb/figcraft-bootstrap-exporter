# FigCraft to Bootstrap 5 + FontAwesome 7 Exporter

[![FigCraft](https://img.shields.io/badge/FigCraft-Plugin-blue)](https://github.com/storytold/figcraft)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3+-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![FontAwesome 7](https://img.shields.io/badge/FontAwesome-7-339AF0?logo=fontawesome&logoColor=white)](https://fontawesome.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plugin e motor de exportação inteligente para o **[FigCraft](https://github.com/storytold/figcraft)** (ferramenta de design de interfaces Rust-native/Figma-alternative). Converte telas, componentes, auto-layouts e estilos criados no FigCraft diretamente em código HTML5 semântico, moderno e responsivo com **Bootstrap 5.3+** e ícones **FontAwesome 7**.

---

## 🚀 Funcionalidades

- **Exportação Semântica**: Converte frames e seções do FigCraft em containers responsivos (`container`, `row`, `col-*`, `card`, `glassmorphism`).
- **Suporte a FontAwesome 7**: Mapeia automaticamente símbolos e tags do layout para a biblioteca de ícones FontAwesome 7.
- **Design Tokens Customizados**: Preserva paletas de cores, gradientes e sombras convertendo-os em variáveis CSS nativas (`:root`).
- **Integração Nativa FigCraft (WASM)**: Manifest oficial `figcraft-plugin.json` compatível com o sistema de plugins WebAssembly do FigCraft.
- **Conexão em Tempo Real (Control Protocol)**: Capaz de se conectar via TCP loopback (`127.0.0.1:7987`) a uma instância ativa do FigCraft para extrair o design em tempo real.

---

## 📦 Estrutura do Repositório

```text
├── figcraft-plugin.json   # Manifesto do plugin FigCraft
├── plugin.wasm            # Módulo WebAssembly compilado para o FigCraft
├── exporter.py            # Motor de exportação e ponte TCP Control
├── exportar.bat           # Executável de 1 clique no Windows (abre seletor de pastas)
├── index.html             # Exemplo exportado: App Android de Rádio (SonicPulse FM)
└── README.md              # Documentação de uso e instalação
```

---

## 🛠️ Como Exportar seus Layouts

Você tem formas práticas de exportar qualquer tela aberta no FigCraft:

### Método 1: Duplo Clique com Navegador de Pastas do Windows (Mais Fácil)
1. Certifique-se de que o FigCraft está aberto com o seu projeto.
2. Dê um duplo clique no arquivo **`exportar.bat`**.
3. A janela nativa do **Explorador de Arquivos do Windows** abrirá na sua tela para você escolher onde quer salvar o site.
4. Selecione a pasta e o motor compilará o HTML semântico e todas as imagens em segundos!

### Método 2: Via Terminal / Python
Você pode abrir o navegador gráfico ou definir a pasta diretamente:

```bash
# 1. Abre o seletor nativo de pastas do sistema para escolher interativamente:
python exporter.py

# 2. Ou força a abertura do seletor gráfico de pastas:
python exporter.py --browse

# 3. Ou define o caminho de destino diretamente pelo terminal (modo silencioso / CI):
python exporter.py --dist "C:\MeusProjetos\NovoSite"
```

---

## 🧩 Menu Interno do FigCraft

1. No FigCraft, clique no logo (canto superior esquerdo) ▸ **Plugins ▸ Development ▸ Import plugin from manifest...**.
2. Selecione o arquivo `figcraft-plugin.json`.
3. O comando **"Exportar para Bootstrap 5 & FontAwesome…"** abrirá o formulário modal na tela.

---

## 🎨 Exemplo Incluído: App Android de Rádio

O repositório inclui a exportação completa de duas telas de um app de rádio online em Dark Mode:
- **Tela 1: Player Ao Vivo (On Air)**: Com arte de capa em vinil, visualizador de ondas sonoras animado, sintonizador FM 98.5 e controles hero.
- **Tela 2: Equalizador FX & Gêneros**: Com mesa de equalização de 5 bandas, Bass Boost, Áudio 3D e categorias musicais.

Visualize o resultado abrindo o arquivo `index.html` em qualquer navegador moderno.

---

## 👤 Autor

Desenvolvido por **[Uziel](https://github.com/uzielweb)**  
Licença MIT.
