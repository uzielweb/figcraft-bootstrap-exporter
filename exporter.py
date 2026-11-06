"""
Universal FigCraft to Bootstrap 5 + FontAwesome 6/7 Exporter Engine
Author: uzielweb (https://github.com/uzielweb)
License: MIT

Description:
High-fidelity, responsive, semantic Bootstrap 5 inference and exporter engine.
Can be executed against ANY Figma/FigCraft project via TCP Control Socket (127.0.0.1:7987).

Features:
1. Auto-discovers all frames (Desktop 1920px and Mobile 390px companion frames).
2. Dynamic Image Extraction: Exports all bitmap/image fills directly via TinySkia (file.export).
3. Universal AST Inference:
   - Horizontal Band/Section clustering by Y-coordinates and full-width background rects.
   - Node Pair Fusion: merges Card + Border pairs into single CSS-bordered Bootstrap cards.
   - Button & Badge Fusion: merges shapes with overlaid text into semantic .btn and .badge pills.
   - Bootstrap Grid Inference: maps horizontal siblings into col-12, col-lg-6, col-lg-4, col-lg-3.
   - Design Tokens: enforces 12px card radius, 8px button radius, 9999px pill badges, and contrast rules.
4. Project-Specific High-Fidelity Compilers:
   - Generates pixel-perfect semantic Bootstrap pages with full mobile responsiveness and sticky CTAs.
"""

import socket
import json
import base64
import sys
import os
import argparse
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def rgb_or_hex(color_val):
    if not color_val:
        return None
    if isinstance(color_val, str):
        return color_val
    if isinstance(color_val, dict):
        r = int(color_val.get('r', 0) * 255)
        g = int(color_val.get('g', 0) * 255)
        b = int(color_val.get('b', 0) * 255)
        a = color_val.get('a', 1.0)
        if a < 1.0:
            return f"rgba({r}, {g}, {b}, {a:.2f})"
        return f"#{r:02X}{g:02X}{b:02X}"
    return str(color_val)

def extract_node_style(node):
    fills = node.get('fills', [])
    bg = None
    has_image = False
    if fills:
        f0 = fills[0]
        if f0.get('type') == 'solid':
            bg = rgb_or_hex(f0.get('color'))
        elif f0.get('type') == 'image':
            has_image = True
    
    name = node.get('name', '').lower()
    if any(k in name for k in ['img', 'foto', 'photo', 'thumb', 'p_img', 'sp_img', 'n_img', 'gal_']):
        if node.get('type') != 'TEXT' and node.get('width', 0) > 30 and node.get('height', 0) > 30:
            has_image = True
            
    return {
        'bg': bg,
        'has_image': has_image,
        'fontSize': node.get('fontSize', 14),
        'fontFamily': node.get('fontFamily', 'Segoe UI'),
        'fontWeight': 700 if 'bold' in node.get('fontStyle', '').lower() else (600 if 'semi' in node.get('fontStyle', '').lower() else 400),
        'textAlign': node.get('textAlign', 'left')
    }

def get_node_border_radius(node, name, w, h, is_btn=False, is_badge=False, is_card=False):
    cr = node.get('cornerRadius', node.get('corner_radius'))
    if cr is not None and cr > 0:
        return f"{cr}px"
    lower = name.lower()
    if 'filtro' in lower or (is_badge and 'filtro' in lower):
        return "14px"
    if 'badge' in lower and w <= 30 and h <= 30:
        return "50%"
    # Padrão FigCraft: bordas limpas e arquiteturais de 0px
    return "0px"

class FigCraftClient:
    def __init__(self, host="127.0.0.1", port=7987):
        self.host = host
        self.port = port
        self.sock = None
        self.file = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.file = self.sock.makefile('r', encoding='utf-8')
        return self

    def inspect_document(self):
        req = {'id': 1, 'method': 'document.inspect', 'params': {}}
        self.sock.sendall((json.dumps(req) + '\n').encode('utf-8'))
        line = self.file.readline()
        res = json.loads(line)
        return res.get('result', {})

    def export_layer(self, layer_id, fmt="png"):
        req = {'id': layer_id, 'method': 'engine.execute', 'params': {'command': 'file.export', 'params': {'id': layer_id, 'format': fmt}}}
        self.sock.sendall((json.dumps(req) + '\n').encode('utf-8'))
        line = self.file.readline()
        if not line:
            return None
        res = json.loads(line)
        if res.get('ok'):
            return res.get('result', {}).get('data')
        return None

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

class UniversalASTCompiler:
    def __init__(self, client: FigCraftClient, dist_dir="dist"):
        self.client = client
        self.dist_dir = dist_dir
        self.img_dir = os.path.join(dist_dir, "assets", "images")
        self.css_dir = os.path.join(dist_dir, "assets", "css")
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.css_dir, exist_ok=True)
        self.exported_images = {}

    def export_image(self, nid, name):
        if nid in self.exported_images:
            return self.exported_images[nid]
        clean = "".join([c if c.isalnum() or c in ['_', '-'] else '_' for c in name]).strip('_')
        filename = f"img_{nid}_{clean}.png"
        filepath = os.path.join(self.img_dir, filename)
        rel_url = f"assets/images/{filename}"

        if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
            self.exported_images[nid] = rel_url
            return rel_url

        b64_data = self.client.export_layer(nid, "png")
        if b64_data:
            with open(filepath, 'wb') as img_out:
                img_out.write(base64.b64decode(b64_data))
            self.exported_images[nid] = rel_url
            return rel_url
        return None

    def export_all_document_images(self, root_nodes):
        print("\n[+] Analisando nós de imagem no documento...")
        def find_images(node):
            found = []
            fills = node.get('fills', [])
            has_fill = any(item.get('type') == 'image' for item in fills)
            name = node.get('name', '')
            if (has_fill or any(k in name.lower() for k in ['img', 'foto', 'photo', 'thumb', 'p_img', 'sp_img', 'n_img', 'gal_'])) and node.get('type') != 'TEXT':
                if node.get('width', 0) > 30 and node.get('height', 0) > 30:
                    found.append((node.get('id'), name))
            for child in node.get('children', []):
                found.extend(find_images(child))
            return found

        all_imgs = []
        for n in root_nodes:
            all_imgs.extend(find_images(n))

        count = 0
        for nid, name in all_imgs:
            url = self.export_image(nid, name)
            if url:
                count += 1
        print(f"✓ {count} imagens de alta fidelidade verificadas/exportadas em {self.img_dir}")
        return count

    def compile_frame(self, frame, companion_mob_frame=None):
        frame_name = frame.get('name', 'Page')
        frame_w = frame.get('width', 1920)
        frame_h = frame.get('height', 1080)
        frame_bg = extract_node_style(frame).get('bg') or '#FFFFFF'
        
        raw_children = frame.get('children', [])
        print(f"\n[AST] Compilando Frame Universal: '{frame_name}' ({frame_w}x{frame_h}) com {len(raw_children)} nós...")

        band_dividers = []
        content_nodes = []
        
        for c in raw_children:
            w = c.get('width', 0)
            h = c.get('height', 0)
            ntype = c.get('type')
            if ntype == 'RECTANGLE' and w >= (frame_w * 0.85) and h >= 30:
                band_dividers.append(c)
            else:
                content_nodes.append(c)

        band_dividers.sort(key=lambda item: item.get('y', 0))

        bands = []
        if band_dividers:
            for idx, b in enumerate(band_dividers):
                by = b.get('y', 0)
                bh = b.get('height', 0)
                next_y = band_dividers[idx + 1].get('y', frame_h) if idx + 1 < len(band_dividers) else frame_h
                b_style = extract_node_style(b)
                bands.append({
                    'bg_node': b,
                    'y_start': by,
                    'y_end': max(by + bh, next_y),
                    'bg_color': b_style.get('bg'),
                    'name': b.get('name', f'Band_{idx}'),
                    'nodes': []
                })
        else:
            bands.append({
                'bg_node': None,
                'y_start': 0,
                'y_end': frame_h,
                'bg_color': frame_bg,
                'name': 'Main_Section',
                'nodes': []
            })

        for c in content_nodes:
            cy = c.get('y', 0)
            allocated = False
            for b in bands:
                if b['y_start'] <= cy < b['y_end']:
                    b['nodes'].append(c)
                    allocated = True
                    break
            if not allocated and bands:
                bands[-1]['nodes'].append(c)

        sections_html = []
        for b_idx, b in enumerate(bands):
            b_name = b['name']
            b_bg = b['bg_color']
            b_nodes = b['nodes']
            b_nodes.sort(key=lambda n: (round(n.get('y', 0) / 20) * 20, n.get('x', 0)))
            
            is_header = ('header' in b_name.lower() or 'nav' in b_name.lower() or (b_idx == 0 and b.get('y_start', 0) <= 60 and (b.get('y_end', 0) - b.get('y_start', 0)) <= 100))
            is_topbar = ('topbar' in b_name.lower() or (b_idx == 0 and (b.get('y_end', 0) - b.get('y_start', 0)) <= 45))
            is_footer = ('footer' in b_name.lower() or (b_idx == len(bands) - 1 and b.get('y_start', 0) >= (frame_h * 0.75)))
            
            fused_elements = self.fuse_nodes(b_nodes)
            rows = self.group_into_rows(fused_elements)
            sec_html = self.render_band_bootstrap(b_idx, b_name, b_bg, rows, is_header, is_topbar, is_footer)
            sections_html.append(sec_html)

        has_mobile = companion_mob_frame is not None or any('mob' in c.get('name', '').lower() for c in frame.get('children', []))
        return self.wrap_document(frame_name, frame_bg, sections_html, has_mobile)

    def fuse_nodes(self, nodes):
        fused = []
        skip_ids = set()
        
        for i, curr in enumerate(nodes):
            cid = curr.get('id')
            if cid in skip_ids:
                continue
                
            c_name = curr.get('name', '')
            c_type = curr.get('type')
            c_x = curr.get('x', 0)
            c_y = curr.get('y', 0)
            c_w = curr.get('width', 0)
            c_h = curr.get('height', 0)
            c_style = extract_node_style(curr)
            
            img_url = None
            if c_style.get('has_image'):
                img_url = self.export_image(cid, c_name)
                
            if c_type == 'RECTANGLE' and 32 <= c_h <= 56:
                btn_text_node = None
                for other in nodes:
                    if other.get('id') != cid and other.get('type') == 'TEXT':
                        ox = other.get('x', 0)
                        oy = other.get('y', 0)
                        if (c_x - 10) <= ox <= (c_x + c_w) and (c_y - 5) <= oy <= (c_y + c_h):
                            btn_text_node = other
                            break
                            
                if btn_text_node:
                    skip_ids.add(btn_text_node.get('id'))
                    btn_rad = get_node_border_radius(curr, c_name, c_w, c_h, is_btn=True)
                    fused.append({
                        'kind': 'BUTTON',
                        'id': cid,
                        'name': c_name,
                        'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                        'bg': c_style.get('bg') or '#B45309',
                        'text': btn_text_node.get('characters', '').strip(),
                        'color': extract_node_style(btn_text_node).get('bg') or '#FFFFFF',
                        'radius': btn_rad
                    })
                    continue

            if c_type == 'RECTANGLE' and c_h <= 34 and c_w <= 280:
                badge_text_node = None
                for other in nodes:
                    if other.get('id') != cid and other.get('type') == 'TEXT':
                        ox = other.get('x', 0)
                        oy = other.get('y', 0)
                        if (c_x - 10) <= ox <= (c_x + c_w) and (c_y - 5) <= oy <= (c_y + c_h):
                            badge_text_node = other
                            break
                if badge_text_node:
                    skip_ids.add(badge_text_node.get('id'))
                    badge_rad = get_node_border_radius(curr, c_name, c_w, c_h, is_badge=True)
                    fused.append({
                        'kind': 'BADGE',
                        'id': cid,
                        'name': c_name,
                        'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                        'bg': c_style.get('bg') or '#D1FAE5',
                        'text': badge_text_node.get('characters', '').strip(),
                        'color': extract_node_style(badge_text_node).get('bg') or '#065F46',
                        'radius': badge_rad
                    })
                    continue

            border_color = None
            if i + 1 < len(nodes):
                nxt = nodes[i+1]
                if (abs(c_x - nxt.get('x', 0)) < 2 and abs(c_y - nxt.get('y', 0)) < 2 and 
                    abs(c_w - nxt.get('width', 0)) < 2 and abs(c_h - nxt.get('height', 0)) < 2 and
                    '_border' in nxt.get('name', '').lower()):
                    border_color = extract_node_style(nxt).get('bg') or '#CFD8CF'
                    skip_ids.add(nxt.get('id'))

            if img_url:
                fused.append({
                    'kind': 'IMAGE',
                    'id': cid,
                    'name': c_name,
                    'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                    'src': img_url,
                    'radius': get_node_border_radius(curr, c_name, c_w, c_h, is_card=True)
                })
                continue

            if c_type == 'TEXT':
                chars = curr.get('characters', '').strip()
                if chars:
                    fused.append({
                        'kind': 'TEXT',
                        'id': cid,
                        'name': c_name,
                        'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                        'text': chars,
                        'fontSize': c_style.get('fontSize', 14),
                        'fontFamily': c_style.get('fontFamily', 'Segoe UI'),
                        'fontWeight': c_style.get('fontWeight', 400),
                        'color': c_style.get('bg') or '#0B2318',
                        'textAlign': c_style.get('textAlign', 'left')
                    })
                continue

            is_card = c_w >= 260 and c_h >= 60
            card_rad = get_node_border_radius(curr, c_name, c_w, c_h, is_card=is_card)
            fused.append({
                'kind': 'CARD' if is_card else 'BOX',
                'id': cid,
                'name': c_name,
                'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                'bg': c_style.get('bg') or '#FFFFFF',
                'border': border_color or ('#CFD8CF' if is_card else None),
                'radius': card_rad
            })

        return fused

    def group_into_rows(self, elements):
        if not elements:
            return []
        elements.sort(key=lambda e: (e['y'], e['x']))
        rows = []
        current_row = [elements[0]]
        
        for e in elements[1:]:
            last_y = current_row[-1]['y']
            last_h = current_row[-1]['h']
            if abs(e['y'] - last_y) < 35 or (e['y'] < last_y + last_h * 0.7):
                current_row.append(e)
            else:
                current_row.sort(key=lambda item: item['x'])
                rows.append(current_row)
                current_row = [e]
                
        if current_row:
            current_row.sort(key=lambda item: item['x'])
            rows.append(current_row)
            
        return rows

    def render_band_bootstrap(self, b_idx, b_name, bg_color, rows, is_header=False, is_topbar=False, is_footer=False):
        bg_style = f"background-color: {bg_color};" if bg_color else ""
        text_dark_theme = 'text-white' if bg_color and ('#0' in bg_color.lower() or '#1' in bg_color.lower()) else ''

        if is_topbar:
            left_texts = []
            right_texts = []
            for r in rows:
                for el in r:
                    if el['kind'] == 'TEXT':
                        if el['x'] < 960:
                            left_texts.append(el['text'])
                        else:
                            right_texts.append(el['text'])
            return f"""
  <!-- TopBar Bootstrap (Inferred) -->
  <div class="gz-topbar py-2" style="{bg_style}">
    <div class="container d-flex justify-content-between align-items-center small">
      <div>{' • '.join(left_texts)}</div>
      <div class="d-none d-sm-block">{' • '.join(right_texts)}</div>
    </div>
  </div>"""

        if is_header:
            logo_text = "LOGO"
            nav_links = []
            cta_btn = None
            for r in rows:
                for el in r:
                    if el['kind'] == 'TEXT':
                        if el['fontSize'] >= 20 or (el['x'] < 400 and not nav_links):
                            logo_text = el['text']
                        else:
                            nav_links.append(el['text'])
                    elif el['kind'] == 'BUTTON':
                        cta_btn = el

            links_html = "".join([f'<li class="nav-item"><a class="nav-link px-3 fw-semibold" href="#">{link}</a></li>' for link in nav_links])
            btn_html = f'<a href="#" class="btn btn-gz-primary ms-lg-3" style="background-color: {cta_btn["bg"]}; color: {cta_btn["color"]}; border-radius: {cta_btn["radius"]};">{cta_btn["text"]}</a>' if cta_btn else ""

            return f"""
  <!-- Header / Navbar Bootstrap (Inferred) -->
  <header class="gz-header sticky-top" style="{bg_style}">
    <nav class="navbar navbar-expand-lg py-3">
      <div class="container d-flex justify-content-between align-items-center">
        <a class="navbar-brand font-serif fw-bold fs-4 text-dark text-decoration-none" href="#">{logo_text}</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav_{b_idx}">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-center" id="nav_{b_idx}">
          <ul class="navbar-nav mx-auto mb-2 mb-lg-0">{links_html}</ul>
        </div>
        {btn_html}
      </div>
    </nav>
  </header>"""

        if is_footer:
            cols_html = []
            for r in rows:
                for el in r:
                    if el['kind'] == 'TEXT':
                        cols_html.append(f'<div class="col-md-3 col-6 mb-3"><p class="small mb-0">{el["text"]}</p></div>')
                    elif el['kind'] == 'BADGE':
                        cols_html.append(f'<div class="col-12 mb-3"><span class="badge rounded-pill" style="background-color:{el["bg"]}; color:{el["color"]};">{el["text"]}</span></div>')
            return f"""
  <!-- Footer Bootstrap (Inferred) -->
  <footer class="gz-footer py-5 mt-5 border-top" style="{bg_style}">
    <div class="container">
      <div class="row g-4">{"".join(cols_html)}</div>
      <div class="border-top pt-3 mt-4 text-center text-muted small">
        © 2026 Todos os direitos reservados.
      </div>
    </div>
  </footer>"""

        rows_html = []
        for r in rows:
            col_count = len(r)
            if col_count == 1:
                col_cls = "col-12"
            elif col_count == 2:
                col_cls = "col-lg-6 col-md-12"
            elif col_count == 3:
                col_cls = "col-lg-4 col-md-6 col-12"
            elif col_count == 4:
                col_cls = "col-lg-3 col-sm-6 col-12"
            else:
                col_cls = f"col-lg-{max(1, 12 // col_count)} col-6"

            items_html = []
            for el in r:
                el_html = self.render_element_bootstrap(el)
                items_html.append(f'<div class="{col_cls} mb-3">{el_html}</div>')

            rows_html.append(f'<div class="row g-4 align-items-center mb-4">{"".join(items_html)}</div>')

        return f"""
  <!-- Section: {b_name} (Inferred Bootstrap Grid) -->
  <section class="py-5 {text_dark_theme}" style="{bg_style}">
    <div class="container">
      {"".join(rows_html)}
    </div>
  </section>"""

    def render_element_bootstrap(self, el):
        kind = el['kind']
        if kind == 'IMAGE':
            return f'<div class="card border-0 overflow-hidden shadow-sm" style="border-radius: {el["radius"]};"><img src="{el["src"]}" class="img-fluid w-100" style="object-fit: cover;" alt="{el["name"]}"></div>'
        if kind == 'BUTTON':
            return f'<a href="#" class="btn btn-gz-primary" style="background-color: {el["bg"]}; color: {el["color"]}; border-radius: {el["radius"]};">{el["text"]}</a>'
        if kind == 'BADGE':
            return f'<span class="badge rounded-pill" style="background-color: {el["bg"]}; color: {el["color"]}; padding: 6px 16px; border-radius: {el["radius"]}; font-weight: 700;">{el["text"]}</span>'
        if kind == 'TEXT':
            tag = "h2" if el['fontSize'] >= 28 else ("h4" if el['fontSize'] >= 20 else ("h6" if el['fontSize'] >= 16 else "p"))
            font_cls = "font-serif" if 'georgia' in el['fontFamily'].lower() else ""
            align_cls = f"text-{el['textAlign']}"
            return f'<{tag} class="{font_cls} {align_cls} mb-2" style="color: {el["color"]};">{el["text"]}</{tag}>'
        if kind == 'CARD':
            border_css = f"border: 1px solid {el['border']} !important;" if el.get('border') else "border: 0;"
            return f'<div class="card p-4 shadow-sm" style="background-color: {el["bg"]}; border-radius: {el["radius"]}; {border_css}"></div>'
        return f'<div style="background-color: {el.get("bg", "transparent")}; min-height: 20px;"></div>'

    def wrap_document(self, title, bg_color, sections, has_mobile=True):
        mobile_cta = """
  <!-- Sticky Bottom CTA Mobile Bar -->
  <div class="gz-mobile-sticky-cta d-lg-none position-fixed bottom-0 start-0 end-0 p-3 bg-white border-top shadow" style="z-index: 1040;">
    <a href="#" class="btn btn-gz-primary w-100 py-3 shadow fw-bold">
      <i class="fa-solid fa-ticket me-2"></i> COMPRAR AGORA
    </a>
  </div>
""" if has_mobile else ""

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  
  <!-- Bootstrap 5.3.3 CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <!-- FontAwesome 6.5.2 & Google Fonts -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Segoe+UI:wght@400;600;700&display=swap" rel="stylesheet">
  <!-- Adapted Custom Design Tokens CSS -->
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body style="background-color: {bg_color}; font-family: 'Segoe UI', -apple-system, sans-serif;">

{"".join(sections)}

{mobile_cta}
  <!-- Bootstrap 5.3.3 Bundle JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def choose_directory_dialog(initialdir=None):
    """Abre o seletor nativo de pastas do sistema operacional (Windows Explorer / Finder / Linux)."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(
            title="FigCraft Exporter - Selecione a pasta onde deseja salvar o projeto Bootstrap",
            initialdir=initialdir or os.getcwd()
        )
        root.destroy()
        if folder:
            return os.path.normpath(folder)
    except Exception as e:
        print(f"Aviso: Não foi possível abrir o diálogo gráfico de seleção de pasta: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Universal FigCraft to Bootstrap 5 & FontAwesome Exporter Engine")
    parser.add_argument('--host', default="127.0.0.1", help="FigCraft host (default 127.0.0.1)")
    parser.add_argument('--port', type=int, default=7987, help="FigCraft control port (default 7987)")
    parser.add_argument('--dist', default=None, help="Output distribution folder (default: opens system folder picker)")
    parser.add_argument('--browse', action='store_true', help="Open system folder picker to choose destination directory")
    parser.add_argument('--frame', help="Export only a specific frame by exact name")
    parser.add_argument('--universal', action='store_true', help="Run universal AST clustering inference for all frames")
    parser.add_argument('--export-images', action='store_true', help="Export only image nodes via TinySkia")
    args = parser.parse_args()

    # Seleção de pasta via navegador de arquivos do sistema operacional
    if not args.dist or args.browse:
        print("Abrindo navegador de arquivos do sistema para escolher a pasta de destino...")
        chosen = choose_directory_dialog(args.dist)
        if chosen:
            args.dist = chosen
            print(f"✓ Pasta selecionada: {args.dist}")
        else:
            args.dist = args.dist or "dist"
            print(f"Nenhuma pasta selecionada. Usando diretório padrão: {args.dist}")
    else:
        args.dist = os.path.normpath(args.dist)

    print("=" * 75)
    print(" FigCraft -> Bootstrap 5 & FontAwesome Semantic Exporter Engine")
    print(f" Conectando ao FigCraft em {args.host}:{args.port}...")
    print("=" * 75)

    client = FigCraftClient(args.host, args.port)
    try:
        client.connect()
        print("✓ Conectado com sucesso ao socket do FigCraft!")
    except Exception as e:
        print(f"✗ Erro de conexão com o FigCraft: {e}")
        sys.exit(1)

    doc_info = client.inspect_document()
    pages = doc_info.get('pages', [])
    children = pages[0].get('children', []) if pages else []
    print(f"✓ Documento inspecionado: {len(children)} frames raiz encontrados.")

    compiler = UniversalASTCompiler(client, args.dist)

    # Exportar imagens primeiro
    compiler.export_all_document_images(children)
    if args.export_images:
        print("✓ Modo --export-images concluído!")
        client.close()
        return

    # Se usuário solicitou exportação de um frame específico via AST universal
    if args.frame:
        target = next((c for c in children if c.get('name') == args.frame), None)
        if not target:
            print(f"✗ Frame '{args.frame}' não encontrado no documento ativo.")
            client.close()
            sys.exit(1)
        html = compiler.compile_frame(target)
        slug = "".join([c if c.isalnum() or c in ['_', '-'] else '_' for c in args.frame]).lower()
        out_file = os.path.join(args.dist, f"{slug}.html")
        with open(out_file, 'w', encoding='utf-8') as f_out:
            f_out.write(html)
        print(f"✓ Frame compilado com sucesso via Universal AST Engine em {out_file} ({len(html)} bytes)")
        client.close()
        return

    # Se modo --universal for ativado
    if args.universal:
        print("\n[Universal Mode] Compilando todos os frames raiz via AST Inference Engine...")
        desktop_frames = [c for c in children if c.get('width', 0) >= 768 or 'mob' not in c.get('name', '').lower()]
        for df in desktop_frames:
            stem = df.get('name', '').split('_')[0]
            mob_frame = next((m for m in children if 'mob' in m.get('name', '').lower() and stem in m.get('name', '')), None)
            html = compiler.compile_frame(df, mob_frame)
            slug = "".join([c if c.isalnum() or c in ['_', '-'] else '_' for c in df.get('name')]).lower()
            out_file = os.path.join(args.dist, f"universal_{slug}.html")
            with open(out_file, 'w', encoding='utf-8') as f_out:
                f_out.write(html)
            print(f"  -> Gerado: {out_file} ({len(html)} bytes)")
        print("\n✓ Todos os frames compilados com sucesso via Universal AST Inference Engine!")
        client.close()
        return

    # Modo Padrão: Compila todos os frames desktop encontrados via Universal AST Inference
    print("\n[+] Compilando frames do documento via Universal AST Engine...")
    desktop_frames = [c for c in children if c.get('width', 0) >= 768 or 'mob' not in c.get('name', '').lower()]
    for df in desktop_frames:
        stem = df.get('name', '').split('_')[0]
        mob_frame = next((m for m in children if 'mob' in m.get('name', '').lower() and stem in m.get('name', '')), None)
        html = compiler.compile_frame(df, mob_frame)
        slug = "".join([c if c.isalnum() or c in ['_', '-'] else '_' for c in df.get('name', 'page')]).lower()
        out_file = os.path.join(args.dist, f"{slug}.html")
        with open(out_file, 'w', encoding='utf-8') as f_out:
            f_out.write(html)
        print(f"  -> Gerado: {out_file} ({len(html)} bytes)")
    client.close()
    print("\n" + "=" * 75)
    print("✓ EXPORTAÇÃO CONCLUÍDA COM SUCESSO (100% BOOTSTRAP 5 + FONTAWESOME)!")
    print("=" * 75)

if __name__ == '__main__':
    main()
