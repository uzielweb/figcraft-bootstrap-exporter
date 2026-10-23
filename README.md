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
├── exporter.py            # Motor CLI de exportação e ponte TCP
├── index.html             # Exemplo exportado: App Android de Rádio (SonicPulse FM)
└── README.md              # Documentação de uso e instalação
```

---

## 🛠️ Como Instalar no FigCraft

1. Abra o FigCraft.
2. Acesse o menu **Plugins ▸ Development ▸ Import plugin from manifest...**.
3. Selecione a pasta deste repositório ou o arquivo `figcraft-plugin.json`.
4. O comando **"Exportar para HTML Bootstrap 5 + FontAwesome 7"** estará disponível no menu **Plugins** e via atalho `Ctrl+Shift+B`.

---

## 💻 Uso via Linha de Comando (CLI)

Você também pode utilizar o motor de exportação standalone via Python:

```bash
# Exportar a tela atual do FigCraft aberto (porta 7987)
python exporter.py --host 127.0.0.1 --port 7987 --output meu-layout.html
```

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
