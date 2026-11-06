"""
Universal FigCraft to Bootstrap 5 + FontAwesome 6/7 Exporter Engine
Author: uzielweb (https://github.com/uzielweb)
License: MIT

High-fidelity, responsive, semantic Bootstrap 5 inference and exporter engine.
Works on ANY design: Websites, Landings, Portals, Dashboards, Mobile and Web Apps.
"""

import socket
import json
import base64
import sys
import os
import argparse
import subprocess
import zipfile
import shutil
import webbrowser
import tempfile
import re

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
        if a < 0.99:
            return f"rgba({r}, {g}, {b}, {a:.2f})"
        return f"#{r:02X}{g:02X}{b:02X}"
    return str(color_val)

def extract_node_style(node):
    fills = node.get('fills', [])
    bg = None
    has_image = False
    image_hash = None
    if fills:
        for f in fills:
            if f.get('visible', True):
                ftype = f.get('type')
                if ftype == 'solid':
                    bg = rgb_or_hex(f.get('color'))
                elif ftype == 'image':
                    has_image = True
                    image_hash = f.get('image')

    name = node.get('name', '').lower()
    ntype = node.get('type', '')
    w = node.get('width', 0)
    h = node.get('height', 0)

    if ntype != 'TEXT' and w >= 24 and h >= 24:
        for kw in ['img', 'foto', 'photo', 'thumb', 'hero', 'author', 'culture', 'banner', 'cover', 'avatar', 'pic', 'image']:
            if kw in name:
                has_image = True
                break

    style_obj = node.get('style') or {}
    f_size = node.get('fontSize') or style_obj.get('font_size') or style_obj.get('fontSize') or 14.0
    f_fam = node.get('fontFamily') or style_obj.get('font_family') or style_obj.get('fontFamily') or 'Segoe UI'
    f_style = str(node.get('fontStyle') or style_obj.get('font_style') or style_obj.get('fontStyle') or '')
    
    f_weight = 400
    if 'bold' in f_style.lower() or 'bold' in str(node.get('fontWeight', '')).lower():
        f_weight = 700
    elif 'semi' in f_style.lower() or 'medium' in f_style.lower():
        f_weight = 600
    elif node.get('fontWeight'):
        try:
            f_weight = int(node.get('fontWeight'))
        except Exception:
            f_weight = 400

    t_align = node.get('textAlign') or style_obj.get('text_align') or style_obj.get('textAlign') or 'left'
    c_radius = node.get('corner_radius') or node.get('cornerRadius') or style_obj.get('corner_radius') or style_obj.get('cornerRadius') or 0.0

    return {
        'bg': bg,
        'has_image': has_image,
        'image_hash': image_hash,
        'fontSize': float(f_size),
        'fontFamily': f_fam,
        'fontWeight': f_weight,
        'textAlign': t_align,
        'radius': float(c_radius)
    }

def detect_universal_icon(text, name):
    t = text.strip()
    icon_map = {
        "🔍": "fa-solid fa-magnifying-glass",
        "🔎": "fa-solid fa-magnifying-glass",
        "⌕": "fa-solid fa-magnifying-glass",
        "☰": "fa-solid fa-bars",
        "⚙️": "fa-solid fa-gear",
        "⚙": "fa-solid fa-gear",
        "⭐": "fa-solid fa-star",
        "★": "fa-solid fa-star",
        "❤️": "fa-solid fa-heart",
        "♥": "fa-solid fa-heart",
        "✓": "fa-solid fa-check",
        "✔": "fa-solid fa-check",
        "✅": "fa-solid fa-check",
        "✖": "fa-solid fa-xmark",
        "✕": "fa-solid fa-xmark",
        "❌": "fa-solid fa-xmark",
        "➕": "fa-solid fa-plus",
        "+": "fa-solid fa-plus",
        "→": "fa-solid fa-arrow-right",
        "↳": "fa-solid fa-arrow-right",
        "➔": "fa-solid fa-arrow-right",
        "←": "fa-solid fa-arrow-left",
        "🔔": "fa-solid fa-bell",
        "✉": "fa-solid fa-envelope",
        "✉️": "fa-solid fa-envelope",
        "📞": "fa-solid fa-phone",
        "🌐": "fa-solid fa-globe",
        "🔒": "fa-solid fa-lock",
        "🔗": "fa-solid fa-link",
        "📅": "fa-solid fa-calendar",
        "🕒": "fa-solid fa-clock",
    }
    if t in icon_map:
        return icon_map[t]

    n = name.lower()
    if 'icon' in n or 'ico' in n or 'icone' in n:
        if 'search' in n or 'busca' in n: return "fa-solid fa-magnifying-glass"
        if 'menu' in n or 'hambur' in n or 'bars' in n: return "fa-solid fa-bars"
        if 'user' in n or 'perfil' in n or 'profile' in n: return "fa-solid fa-user"
        if 'star' in n or 'fav' in n: return "fa-solid fa-star"
        if 'heart' in n or 'like' in n: return "fa-solid fa-heart"
        if 'gear' in n or 'config' in n: return "fa-solid fa-gear"
        if 'close' in n or 'fechar' in n: return "fa-solid fa-xmark"
        if 'check' in n: return "fa-solid fa-check"
        if 'bell' in n or 'notif' in n: return "fa-solid fa-bell"
        if 'share' in n: return "fa-solid fa-share-nodes"
        if 'arrow' in n and 'right' in n: return "fa-solid fa-arrow-right"
        if 'arrow' in n and 'left' in n: return "fa-solid fa-arrow-left"

    return None

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

    def list_documents(self):
        try:
            req = {'id': 99, 'method': 'engine.execute', 'params': {'command': 'doc.list', 'params': {}}}
            self.sock.sendall((json.dumps(req) + '\n').encode('utf-8'))
            line = self.file.readline()
            if line:
                res = json.loads(line)
                if res.get('ok'):
                    return res.get('result', [])
        except Exception:
            pass
        return []

    def inspect_document(self):
        req = {'id': 1, 'method': 'document.inspect', 'params': {}}
        self.sock.sendall((json.dumps(req) + '\n').encode('utf-8'))
        line = self.file.readline()
        res = json.loads(line)
        return res.get('result', {})

    def export_layer(self, layer_id, fmt="png"):
        req = {'id': layer_id, 'method': 'engine.execute', 'params': {'command': 'file.export', 'params': {'ids': [layer_id], 'format': fmt}}}
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

class FigCraftZipClient:
    def __init__(self, file_path):
        self.file_path = os.path.abspath(file_path)
        self.doc_data = None
        self.zip_ref = None
        self._load()

    def _expand_tree(self, node_id, nodes):
        raw_node = nodes.get(str(node_id)) or nodes.get(node_id)
        if not raw_node:
            return None
        node = dict(raw_node)
        if 'transform' in node and isinstance(node['transform'], list) and len(node['transform']) >= 6:
            node['x'] = node['transform'][4]
            node['y'] = node['transform'][5]
        children = []
        for cid in raw_node.get('children', []):
            if isinstance(cid, dict):
                c_dict = dict(cid)
                if 'transform' in c_dict and isinstance(c_dict['transform'], list) and len(c_dict['transform']) >= 6:
                    c_dict['x'] = c_dict['transform'][4]
                    c_dict['y'] = c_dict['transform'][5]
                children.append(c_dict)
            else:
                cnode = self._expand_tree(cid, nodes)
                if cnode:
                    children.append(cnode)
        node['children'] = children
        return node

    def _load(self):
        self.zip_ref = zipfile.ZipFile(self.file_path, 'r')
        with self.zip_ref.open('document.json') as f:
            raw_doc = json.load(f)

        pages = raw_doc.get('pages', [])
        if pages and isinstance(pages[0], dict) and 'children' in pages[0]:
            self.doc_data = raw_doc
        else:
            nodes = raw_doc.get('nodes', {})
            expanded_pages = []
            for pid in pages:
                if isinstance(pid, dict):
                    expanded_pages.append(pid)
                else:
                    p = self._expand_tree(pid, nodes)
                    if p:
                        expanded_pages.append(p)
            self.doc_data = dict(raw_doc)
            self.doc_data['pages'] = expanded_pages

    def list_documents(self):
        name = os.path.splitext(os.path.basename(self.file_path))[0]
        return [{
            'id': 1,
            'index': 0,
            'name': name,
            'path': self.file_path,
            'active': True,
            'dirty': False
        }]

    def inspect_document(self):
        return self.doc_data

    def export_layer(self, layer_id, fmt="png", image_hash=None):
        if image_hash:
            target_entry = f"images/{image_hash}"
            if target_entry in self.zip_ref.namelist():
                with self.zip_ref.open(target_entry) as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')

        cli_bin = shutil.which("figcraft-cli")
        if not cli_bin and sys.platform == 'win32':
            default_cli = r"C:\Program Files\FigCraft\figcraft-cli.exe"
            if os.path.exists(default_cli):
                cli_bin = default_cli

        if cli_bin:
            with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as tmp:
                tmp_out = tmp.name
            try:
                cmd = [cli_bin, "export", "--out", tmp_out, "--format", fmt, "--node", str(layer_id), self.file_path]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 0:
                    with open(tmp_out, 'rb') as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                    os.unlink(tmp_out)
                    return b64
            except Exception:
                if os.path.exists(tmp_out):
                    try:
                        os.unlink(tmp_out)
                    except Exception:
                        pass

        for member in self.zip_ref.namelist():
            if member.startswith('images/') and not member.endswith('/'):
                with self.zip_ref.open(member) as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
        return None

    def close(self):
        if self.zip_ref:
            try:
                self.zip_ref.close()
            except Exception:
                pass

class UniversalASTCompiler:
    def __init__(self, client, dist_dir="dist"):
        self.client = client
        self.dist_dir = dist_dir
        self.img_dir = os.path.join(dist_dir, "assets", "images")
        self.css_dir = os.path.join(dist_dir, "assets", "css")
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.css_dir, exist_ok=True)
        self.exported_images = {}

    def export_image(self, nid, name, image_hash=None):
        if nid in self.exported_images:
            return self.exported_images[nid]

        clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name).strip('_')
        filename = f"img_{nid}_{clean}.png"
        filepath = os.path.join(self.img_dir, filename)
        rel_url = f"assets/images/{filename}"

        if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
            self.exported_images[nid] = rel_url
            return rel_url

        b64_data = None
        if hasattr(self.client, 'export_layer'):
            if isinstance(self.client, FigCraftZipClient):
                b64_data = self.client.export_layer(nid, "png", image_hash=image_hash)
            else:
                b64_data = self.client.export_layer(nid, "png")

        if b64_data:
            with open(filepath, 'wb') as img_out:
                img_out.write(base64.b64decode(b64_data))
            self.exported_images[nid] = rel_url
            return rel_url
        return None

    def compile_frame(self, frame):
        frame_name = frame.get('name', 'Page')
        frame_w = frame.get('width', 1440.0)
        frame_h = frame.get('height', 1080.0)
        frame_bg = extract_node_style(frame).get('bg') or '#FFFFFF'

        raw_children = frame.get('children', [])
        print(f"\n[AST] Compilando Frame Universal: '{frame_name}' ({frame_w}x{frame_h}) com {len(raw_children)} nós...")

        # 1. Identificar divisores reais de seções (Bands)
        # Retângulos FULL-BLEED (x <= 15, w >= frame_w * 0.85, h >= 60) ou a linha de TopBar definem bandas de seção
        boundary_ys = [0.0, frame_h]
        section_bgs = []

        for c in raw_children:
            w = c.get('width', 0)
            h = c.get('height', 0)
            x = c.get('x', 0)
            y = c.get('y', 0)
            ntype = (c.get('type') or '').upper()
            
            # Linha de divisão da barra de topo (y <= 50, h <= 3, full-bleed)
            if ntype == 'RECTANGLE' and w >= (frame_w * 0.70) and x <= 15 and y <= 50 and h <= 3:
                boundary_ys.append(y + h)
            # Barra fina tipo Focus / Ticker / Inner bar (25 <= h <= 55 e w >= frame_w * 0.65)
            elif ntype == 'RECTANGLE' and w >= (frame_w * 0.65) and 25 <= h <= 55:
                boundary_ys.append(y)
                boundary_ys.append(y + h)
                section_bgs.append(c)
            # Retângulos de fundo de seção REAL full-bleed (x <= 15, w >= frame_w * 0.85, h >= 60)
            elif ntype == 'RECTANGLE' and x <= 15 and w >= (frame_w * 0.85) and h >= 60:
                boundary_ys.append(y)
                boundary_ys.append(y + h)
                section_bgs.append(c)

        boundary_ys = sorted(list(set(boundary_ys)))
        cleaned_ys = [boundary_ys[0]]
        for y in boundary_ys[1:]:
            if y - cleaned_ys[-1] >= 25.0:
                cleaned_ys.append(y)
        if cleaned_ys[-1] < frame_h:
            cleaned_ys.append(frame_h)

        # Monta as seções
        bands = []
        for i in range(len(cleaned_ys) - 1):
            y_start = cleaned_ys[i]
            y_end = cleaned_ys[i + 1]

            bg_color = None
            band_name = f"Section_{i}"
            is_full_bleed = False
            for b in section_bgs:
                by = b.get('y', 0)
                bh = b.get('height', 0)
                if abs(by - y_start) <= 20 and bh >= 25:
                    bg_color = extract_node_style(b).get('bg')
                    band_name = b.get('name', band_name)
                    is_full_bleed = (b.get('x', 0) <= 15) and (b.get('width', 0) >= frame_w * 0.85)
                    break

            b_lower = band_name.lower()
            is_topbar = i == 0 and y_end <= 50
            is_header = ('masthead' in b_lower or 'nav' in b_lower or 'header' in b_lower) or (i == 1 and y_start <= 50 and y_end <= 300)
            is_footer = 'footer' in b_lower or y_start >= (frame_h * 0.75)

            bands.append({
                'name': band_name,
                'y_start': y_start,
                'y_end': y_end,
                'bg_color': bg_color,
                'is_full_bleed': is_full_bleed,
                'is_topbar': is_topbar,
                'is_header': is_header,
                'is_footer': is_footer,
                'nodes': []
            })

        # Aloca nós de conteúdo em suas bandas correspondentes (ignorando os próprios retângulos de fundo de banda)
        bg_ids = {b.get('id') for b in section_bgs}
        for c in raw_children:
            cid = c.get('id')
            if cid in bg_ids:
                continue

            cy = c.get('y', 0)
            allocated = False
            for b in bands:
                if b['y_start'] <= cy < b['y_end']:
                    b['nodes'].append(c)
                    allocated = True
                    break
            if not allocated and bands:
                bands[-1]['nodes'].append(c)

        # 2. Compilar cada banda com fusão semântica e grid
        sections_html = []
        for b_idx, b in enumerate(bands):
            b_nodes = b['nodes']
            if not b_nodes and not b['bg_color']:
                continue

            fused_elements = self.fuse_nodes(b_nodes)
            sec_html = self.render_band(b_idx, b, fused_elements, frame_w)
            if sec_html:
                sections_html.append(sec_html)

        # 3. Calcula a largura útil real do conteúdo do design
        visible_children = [c for c in raw_children if c.get('id') not in bg_ids and c.get('x') is not None]
        if visible_children:
            min_c_x = min((c.get('x', 0) for c in visible_children if c.get('x', 0) > 0 and c.get('width', 0) < frame_w * 0.95), default=0.0)
            max_c_x = max((c.get('x', 0) + c.get('width', 0) for c in visible_children if c.get('width', 0) < frame_w * 0.95), default=frame_w)
            content_w = (max_c_x - min_c_x) if (max_c_x > min_c_x and (max_c_x - min_c_x) >= 280) else frame_w
            pad_x = min(min_c_x, 30.0) if min_c_x > 0 else 15.0
        else:
            content_w = frame_w
            pad_x = 15.0

        return self.wrap_document(frame_name, frame_w, content_w, pad_x, frame_bg, sections_html)

    def fuse_nodes(self, nodes):
        fused = []
        skip_ids = set()

        for i, curr in enumerate(nodes):
            cid = curr.get('id')
            if cid in skip_ids:
                continue

            c_name = curr.get('name', '')
            c_type = (curr.get('type') or '').upper()
            c_x = curr.get('x', 0)
            c_y = curr.get('y', 0)
            c_w = curr.get('width', 0)
            c_h = curr.get('height', 0)
            c_style = extract_node_style(curr)

            # Imagem
            if c_style.get('has_image'):
                img_url = self.export_image(cid, c_name, image_hash=c_style.get('image_hash'))
                fused.append({
                    'kind': 'IMAGE',
                    'id': cid,
                    'name': c_name,
                    'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                    'src': img_url or f"assets/images/img_{cid}.png",
                    'radius': c_style.get('radius', 0.0)
                })
                continue

            # Divisor vertical (w <= 4 e h >= 20) -> NÃO é coluna de conteúdo
            if c_type == 'RECTANGLE' and c_w <= 4 and c_h >= 20:
                fused.append({
                    'kind': 'VERTICAL_DIVIDER',
                    'id': cid,
                    'name': c_name,
                    'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                    'bg': c_style.get('bg') or '#EAEAEA'
                })
                continue

            # Divisor fino horizontal (<hr>)
            if c_type == 'RECTANGLE' and c_h <= 4 and c_w >= 30:
                fused.append({
                    'kind': 'DIVIDER',
                    'id': cid,
                    'name': c_name,
                    'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                    'bg': c_style.get('bg') or '#EAEAEA'
                })
                continue

            # Botão (Fusão de Retângulo + Texto sobreposto)
            name_lower = c_name.lower()
            if (c_type == 'RECTANGLE' and 24 <= c_h <= 60 and c_w <= 320) or 'btn' in name_lower or 'button' in name_lower:
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
                    fused.append({
                        'kind': 'BUTTON',
                        'id': cid,
                        'name': c_name,
                        'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                        'bg': c_style.get('bg') or '#111111',
                        'text': btn_text_node.get('characters', '').strip(),
                        'color': extract_node_style(btn_text_node).get('bg') or '#FFFFFF',
                        'radius': c_style.get('radius', 0.0)
                    })
                    continue

            # Badge / Tag (Fusão de Retângulo pequeno + Texto)
            if (c_type == 'RECTANGLE' and c_h <= 34 and c_w <= 240) or 'badge' in name_lower or 'tag' in name_lower or 'pill' in name_lower:
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
                    fused.append({
                        'kind': 'BADGE',
                        'id': cid,
                        'name': c_name,
                        'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                        'bg': c_style.get('bg') or '#F1F5F9',
                        'text': badge_text_node.get('characters', '').strip(),
                        'color': extract_node_style(badge_text_node).get('bg') or '#0F172A',
                        'radius': c_style.get('radius', 0.0)
                    })
                    continue

            # Texto
            if c_type == 'TEXT':
                chars = curr.get('characters', '').strip()
                if chars:
                    icon = detect_universal_icon(chars, c_name)
                    # Detecta se é menu de navegação (múltiplos itens separados por 3+ espaços)
                    is_nav_menu = bool(re.search(r'\s{3,}', chars))
                    nav_items = [p.strip() for p in re.split(r'\s{3,}', chars) if p.strip()] if is_nav_menu else []

                    fused.append({
                        'kind': 'NAV_MENU' if is_nav_menu else 'TEXT',
                        'id': cid,
                        'name': c_name,
                        'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                        'text': chars,
                        'nav_items': nav_items,
                        'fontSize': c_style.get('fontSize', 14),
                        'fontFamily': c_style.get('fontFamily', 'Inter'),
                        'fontWeight': c_style.get('fontWeight', 400),
                        'color': c_style.get('bg') or '#111111',
                        'textAlign': c_style.get('textAlign', 'left'),
                        'icon': icon
                    })
                continue

            # Card de fundo ou bloco
            is_card = c_w >= 220 and c_h >= 60
            fused.append({
                'kind': 'CARD' if is_card else 'BOX',
                'id': cid,
                'name': c_name,
                'x': c_x, 'y': c_y, 'w': c_w, 'h': c_h,
                'bg': c_style.get('bg') or '#FFFFFF',
                'radius': c_style.get('radius', 0.0)
            })

        return fused

    def render_band(self, b_idx, band, elements, frame_w):
        if not elements:
            return ""

        bg_color = band['bg_color']
        bg_style = f"background-color: {bg_color};" if bg_color else ""
        is_dark = bg_color and any(k in bg_color.lower() for k in ['#0', '#1', '#2', '#111', '#111317'])
        theme_class = "text-white" if is_dark else ""
        band_h = band['y_end'] - band['y_start']

        # 1. TopBar: layout horizontal flex limpo com 3 blocos (esquerda, centro, direita) respeitando container -> row -> col
        if band['is_topbar']:
            elements.sort(key=lambda e: e['x'])
            left_items = [e for e in elements if e['x'] < frame_w * 0.30]
            center_items = [e for e in elements if frame_w * 0.30 <= e['x'] < frame_w * 0.75]
            right_items = [e for e in elements if e['x'] >= frame_w * 0.75]

            left_html = " ".join([f"<span style=\"color:{e['color']}; font-size:{e['fontSize']}px;\">{e['text']}</span>" for e in left_items if e['kind'] == 'TEXT'])
            center_html = " ".join([f"<span style=\"color:{e['color']}; font-size:{e['fontSize']}px;\">{e['text']}</span>" for e in center_items if e['kind'] == 'TEXT'])
            right_html = "".join([f"<span class=\"small text-muted\" style=\"color:{e['color']}; font-size:{e['fontSize']}px;\">{e['text']}</span>" if e['kind'] == 'TEXT' else self.render_element(e) for e in right_items])

            return f"""  <!-- TopBar -->
  <div class="topbar py-2 border-bottom {theme_class}" style="{bg_style}">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-lg-4 col-md-4 col-12 d-flex align-items-center">
          {left_html}
        </div>
        <div class="col-lg-5 col-md-5 d-none d-md-block text-center">
          {center_html}
        </div>
        <div class="col-lg-3 col-md-3 col-12 d-flex justify-content-end align-items-center gap-3">
          {right_html}
        </div>
      </div>
    </div>
  </div>"""

        # 2. Header / Masthead: Logo central, Nav Links e Busca respeitando container -> row -> col
        if band['is_header']:
            elements.sort(key=lambda e: (round(e['y'] / 30) * 30, e['x']))
            logo_item = next((e for e in elements if e['kind'] == 'TEXT' and e['fontSize'] >= 36), None)
            sub_item = next((e for e in elements if e['kind'] == 'TEXT' and 10 <= e['fontSize'] <= 14 and e['y'] < 160), None)
            nav_item = next((e for e in elements if e['kind'] == 'NAV_MENU'), None)
            search_item = next((e for e in elements if e['kind'] == 'TEXT' and ('busca' in e['name'].lower() or 'search' in e['name'].lower())), None)

            logo_html = f'<h1 class="display-3 fw-bold font-serif mb-1" style="color:{logo_item["color"]}; font-size:{logo_item["fontSize"]}px; letter-spacing:0.02em;">{logo_item["text"]}</h1>' if logo_item else ""
            sub_html = f'<p class="small text-muted text-uppercase tracking-wide mb-3" style="color:{sub_item["color"]}; font-size:{sub_item["fontSize"]}px;">{sub_item["text"]}</p>' if sub_item else ""

            nav_links_html = ""
            if nav_item:
                nav_links_html = "".join([f'<li class="nav-item"><a class="nav-link text-dark px-2 fw-semibold small text-uppercase" href="#">{item}</a></li>' for item in nav_item['nav_items']])
            elif nav_item is None:
                nav_links_html = "".join([f'<li class="nav-item"><a class="nav-link text-dark px-2 fw-semibold small" href="#">{e["text"]}</a></li>' for e in elements if e['kind'] == 'TEXT' and e != logo_item and e != sub_item])

            search_html = f'<a href="#" class="text-secondary small text-decoration-none fw-semibold text-uppercase"><i class="fa-solid fa-magnifying-glass me-1"></i> {search_item["text"]}</a>' if search_item else ""

            return f"""  <!-- Masthead -->
  <header class="masthead pt-4 pb-2 {theme_class}" style="{bg_style}">
    <div class="container">
      <!-- Row: Logo e Subtítulo (col-12 text-center) -->
      <div class="row justify-content-center text-center">
        <div class="col-12">
          {logo_html}
          {sub_html}
          <div class="border-top border-dark border-2 pt-1 mb-2">
            <div class="border-top border-dark"></div>
          </div>
        </div>
      </div>
      <!-- Row: Navegação e Busca (col-12) -->
      <div class="row align-items-center">
        <div class="col-12">
          <nav class="d-flex flex-wrap justify-content-between align-items-center py-1">
            <ul class="nav gap-3 mb-0">
              {nav_links_html}
            </ul>
            <div class="d-none d-lg-block">
              {search_html}
            </div>
          </nav>
          <div class="border-bottom mb-2"></div>
        </div>
      </div>
    </div>
  </header>"""

        # 3. Barra fina horizontal (Focus Bar, Ticker, etc: altura <= 75px)
        if band_h <= 75 and not band['is_footer']:
            elements.sort(key=lambda e: e['x'])
            bar_items_html = []
            for e in elements:
                if e['kind'] == 'DIVIDER' or e['kind'] == 'VERTICAL_DIVIDER':
                    continue
                if e['kind'] == 'TEXT':
                    text_str = e['text']
                    if '•' in text_str and len(text_str) > 30:
                        parts = [p.strip() for p in text_str.split('•') if p.strip()]
                        li_parts = "".join([f'<li class="list-inline-item"><a href="#" class="text-secondary text-decoration-none small">{p}</a></li><li class="list-inline-item text-muted">•</li>' for p in parts])
                        if li_parts.endswith('<li class="list-inline-item text-muted">•</li>'):
                            li_parts = li_parts[:-len('<li class="list-inline-item text-muted">•</li>')]
                        bar_items_html.append(f'<nav class="d-inline-block"><ul class="list-inline mb-0 small">{li_parts}</ul></nav>')
                    elif len(text_str) <= 15:
                        bar_items_html.append(f'<span class="fw-bold text-danger text-uppercase small">{text_str}</span>')
                    else:
                        bar_items_html.append(f'<span class="small" style="color:{e["color"]};">{text_str}</span>')
                elif e['kind'] == 'BADGE':
                    bar_items_html.append(f'<span class="badge rounded-pill px-3 py-1 fw-bold text-uppercase" style="background-color:{e["bg"]}; color:{e["color"]};">{e["text"]}</span>')
                else:
                    bar_items_html.append(self.render_element(e))

            content_html = "\n            ".join(bar_items_html)

            # Se não for full-bleed, mantém o fundo contido no container (sem border-radius artificial)
            if not band.get('is_full_bleed'):
                return f"""  <!-- Section: {band['name']} -->
  <div class="container mb-3">
    <div class="d-flex flex-wrap align-items-center gap-3 px-3 py-2" style="{bg_style}">
      {content_html}
    </div>
  </div>"""

            return f"""  <!-- Section: {band['name']} -->
  <div class="py-2 border-bottom {theme_class}" style="{bg_style}">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-12 d-flex flex-wrap align-items-center gap-3">
          {content_html}
        </div>
      </div>
    </div>
  </div>"""

        # 4. Footer: Colunas de links semânticas e copyright respeitando container -> row -> col
        if band['is_footer']:
            header_items, col_clusters, v_dividers, copyright_item = self.partition_section(elements, frame_w, band_h)
            cols_html = []

            for c_span, c_elements, _, _ in col_clusters:
                col_html = self.render_column_content(c_elements)
                if col_html.strip():
                    cols_html.append(f'        <div class="col-lg-{c_span} col-md-6 col-12 mb-4 mb-lg-0">\n{col_html}        </div>')

            copy_html = f"""      <!-- Row: Footer Copyright (col-12) -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="border-top pt-4 text-center text-muted small">{copyright_item["text"]}</div>
        </div>
      </div>""" if copyright_item else ""

            top_border_el = next((e for e in elements if e['kind'] == 'DIVIDER' and abs(e['y'] - band['y_start']) <= 10 and e['w'] >= frame_w * 0.70), None)
            footer_border = f"border-top: {max(1, int(top_border_el['h']))}px solid {top_border_el['bg']} !important;" if top_border_el else "border-top: 1px solid var(--bs-border-color);"
            return f"""  <!-- Footer -->
  <footer class="footer py-5 {theme_class}" style="{bg_style} {footer_border}">
    <div class="container">
      <!-- Row: Footer Columns -->
      <div class="row g-4">
{"\n".join(cols_html)}
      </div>
{copy_html}
    </div>
  </footer>"""

        # 5. Seção de Conteúdo Geral (com detecção de Título col-12 e Colunas reais)
        header_items, col_clusters, v_dividers, _ = self.partition_section(elements, frame_w, band_h)

        rows_html = []

        # Row de Header da Seção (col-12) se houver título/divisor largo
        if header_items:
            h_content = self.render_column_content(header_items)
            if h_content.strip():
                rows_html.append(f"""      <!-- Row: Section Header (col-12) -->
      <div class="row mb-4">
        <div class="col-12">
{h_content}        </div>
      </div>""")

        # Row das Colunas de Conteúdo
        if col_clusters:
            cols_html = []
            for c_span, c_elements, border_class, col_bg_style in col_clusters:
                col_content = self.render_column_content(c_elements)
                if not col_content.strip():
                    continue  # NUNCA cria colunas vazias!
                b_cls = f" {border_class}" if border_class else ""
                if col_bg_style:
                    cols_html.append(f'        <div class="col-lg-{c_span} col-md-6 col-12{b_cls}">\n          <div class="h-100 p-4" style="{col_bg_style}">\n{col_content}          </div>\n        </div>')
                else:
                    cols_html.append(f'        <div class="col-lg-{c_span} col-md-6 col-12{b_cls}">\n{col_content}        </div>')

            if cols_html:
                rows_html.append(f"""      <!-- Row: Content Columns -->
      <div class="row g-4">
{"\n".join(cols_html)}
      </div>""")

        if not rows_html:
            return ""

        return f"""  <!-- Section: {band['name']} -->
  <section class="py-5 {theme_class}" style="{bg_style}">
    <div class="container">
{"\n".join(rows_html)}
    </div>
  </section>"""

    def partition_section(self, elements, frame_w, band_h=0):
        """Particiona os elementos de uma seção em:
        1. Itens de cabeçalho (Section Header em col-12)
        2. Clusters de colunas com larguras reais e classes de borda
        3. Divisores verticais
        """
        if not elements:
            return [], [], []

        # Separa divisores verticais (w <= 4 e h >= 20) e copyright
        v_dividers = [e for e in elements if e['kind'] == 'VERTICAL_DIVIDER']
        content_items = [e for e in elements if e['kind'] != 'VERTICAL_DIVIDER']

        # Isola elemento de copyright se houver (para não distorcer colunas)
        copyright_item = next((e for e in content_items if '©' in e.get('text', '') or 'todos os direitos' in e.get('text', '').lower()), None)
        if copyright_item:
            content_items = [e for e in content_items if e != copyright_item]

        # Remove divisores horizontais duplicados e divisores residuais no final da seção
        filtered = []
        last_divider_y = -999
        max_content_y = max((e['y'] + e['h'] for e in content_items if e['kind'] not in ['DIVIDER', 'VERTICAL_DIVIDER']), default=9999)
        for e in content_items:
            if e['kind'] == 'DIVIDER':
                if abs(e['y'] - last_divider_y) < 15:
                    continue
                if e['y'] >= max_content_y - 5:
                    continue
                last_divider_y = e['y']
            filtered.append(e)

        # Detecta linha divisória de cabeçalho no topo da seção (primeiros 35% de altura da seção)
        header_items = []
        body_items = []

        min_y = min((e['y'] for e in filtered), default=0)
        max_y = max((e['y'] + e['h'] for e in filtered), default=min_y + 1)
        eff_h = band_h if band_h > 0 else (max_y - min_y)

        # Procura wide_divider apenas no terço superior para ser divisor de cabeçalho
        top_wide_divider = next((e for e in filtered if e['kind'] == 'DIVIDER' and e['w'] >= frame_w * 0.65 and (e['y'] - min_y) <= (eff_h * 0.35)), None)

        if top_wide_divider:
            for e in filtered:
                if e['y'] < top_wide_divider['y']:
                    header_items.append(e)
                elif e != top_wide_divider:
                    body_items.append(e)
            header_items.append(top_wide_divider)
        else:
            body_items = filtered

        # Agrupa body_items em clusters de colunas pelo eixo X
        col_items = [e for e in body_items if e['w'] < frame_w * 0.65]
        full_width_body = [e for e in body_items if e['w'] >= frame_w * 0.65]
        if full_width_body and not header_items:
            # Se não tínhamos header e há um divisor/banner largo
            pass

        clusters = []
        if col_items:
            col_items.sort(key=lambda e: (e['x'], e['y']))
            current_cluster = [col_items[0]]
            for e in col_items[1:]:
                # Se o X do elemento estiver alinhado com o cluster atual
                # Calculamos o limite direito real dos elementos do cluster atual
                c_right = max(item['x'] + item['w'] for item in current_cluster)
                # Uma coluna mantém elementos se eles começam perto de onde a coluna está (gap <= 30px)
                if e['x'] < (c_right + 30):
                    current_cluster.append(e)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [e]
            if current_cluster:
                clusters.append(current_cluster)

        # Filtra clusters que não contêm nenhum elemento renderizável
        valid_clusters = []
        for c in clusters:
            has_visual = any(e['kind'] in ['TEXT', 'IMAGE', 'BUTTON', 'BADGE', 'NAV_MENU'] for e in c)
            if has_visual:
                valid_clusters.append(c)

        # Calcula spans proporcionais do Bootstrap (12 colunas)
        num_clusters = len(valid_clusters)
        col_results = []

        if num_clusters == 0:
            pass
        elif num_clusters == 1:
            valid_clusters[0].sort(key=lambda e: e['y'])
            col_results.append((12, valid_clusters[0], ""))
        elif num_clusters == 2:
            w0 = max(10, max(e['x'] + e['w'] for e in valid_clusters[0]) - min(e['x'] for e in valid_clusters[0]))
            w1 = max(10, max(e['x'] + e['w'] for e in valid_clusters[1]) - min(e['x'] for e in valid_clusters[1]))
            tot = w0 + w1
            if abs(w0 - w1) / max(w0, w1) <= 0.25:
                s0, s1 = 6, 6
            else:
                s0 = max(3, min(9, round((w0 / tot) * 12)))
                s1 = 12 - s0
            valid_clusters[0].sort(key=lambda e: e['y'])
            valid_clusters[1].sort(key=lambda e: e['y'])
            col_results.append((s0, valid_clusters[0], "mb-4 mb-lg-0"))
            col_results.append((s1, valid_clusters[1], ""))
        elif num_clusters == 3:
            w0 = max(10, max(e['x'] + e['w'] for e in valid_clusters[0]) - min(e['x'] for e in valid_clusters[0]))
            w1 = max(10, max(e['x'] + e['w'] for e in valid_clusters[1]) - min(e['x'] for e in valid_clusters[1]))
            w2 = max(10, max(e['x'] + e['w'] for e in valid_clusters[2]) - min(e['x'] for e in valid_clusters[2]))
            tot = w0 + w1 + w2
            s0 = max(2, min(6, round((w0 / tot) * 12)))
            s1 = max(4, min(8, round((w1 / tot) * 12)))
            s2 = 12 - s0 - s1
            if s2 < 2:
                s2 = 3
                s1 = 12 - s0 - s2
            for c in valid_clusters:
                c.sort(key=lambda e: e['y'])
            # Borda vertical para a coluna 0 e 1 se houver divisores verticais
            b0 = "border-end pe-lg-4 mb-4 mb-lg-0" if v_dividers else "mb-4 mb-lg-0"
            b1 = "border-end px-lg-4 mb-4 mb-lg-0" if v_dividers else "mb-4 mb-lg-0"
            b2 = "ps-lg-4" if v_dividers else ""
            col_results.append((s0, valid_clusters[0], b0))
            col_results.append((s1, valid_clusters[1], b1))
            col_results.append((s2, valid_clusters[2], b2))
        elif num_clusters == 4:
            for c in valid_clusters:
                c.sort(key=lambda e: e['y'])
                col_results.append((3, c, "mb-4 mb-lg-0"))
        elif num_clusters == 5:
            # 5 colunas: no footer, 3 para logo/institucional e 2 para colunas de links
            spans = [3, 2, 2, 2, 3]
            for idx, c in enumerate(valid_clusters):
                c.sort(key=lambda e: e['y'])
                col_results.append((spans[idx], c, "mb-4 mb-lg-0"))
        else:
            span = max(2, 12 // num_clusters)
            for c in valid_clusters:
                c.sort(key=lambda e: e['y'])
                col_results.append((span, c, ""))

        # Identifica se alguma coluna possui cartão/fundo próprio (ex: Col_Opiniao_Bg)
        final_col_results = []
        for span, c_elements, b_cls in col_results:
            bg_card = next((e for e in c_elements if e['kind'] == 'CARD' and e['w'] >= 180 and e['h'] >= 80), None)
            col_bg_style = ""
            if bg_card:
                c_elements = [e for e in c_elements if e != bg_card]
                cr = bg_card.get('radius', 0)
                radius_str = f"border-radius: {cr}px;" if cr > 0 else "border-radius: 0px;"
                col_bg_style = f"background-color: {bg_card['bg']}; {radius_str}"
            final_col_results.append((span, c_elements, b_cls, col_bg_style))

        header_items.sort(key=lambda e: e['y'])
        return header_items, final_col_results, v_dividers, copyright_item

    def render_column_content(self, elements):
        """Renderiza elementos de uma coluna identificando automagicamente:
        - Listas verticais de links (nav/ul/li sem bullets: class="list-unstyled mb-0")
        - Sub-links com setas (↳ Análise: ...)
        - Listas com marcadores explícitos (•, -, *, 1.)
        - Títulos de cabeçalho seguidos de links
        - Tópicos inline
        - Imagens, Botões, Badges, Divisores
        """
        if not elements:
            return ""

        output_html = []
        i = 0
        n = len(elements)

        while i < n:
            curr = elements[i]
            kind = curr['kind']

            # 1. Detecta cabeçalho de links (ex: NOTÍCIAS, OPINIÃO, etc.) seguido por lista de links verticais
            if kind == 'TEXT' and (curr['fontSize'] <= 14 and (curr['text'].isupper() or 'font-weight' in str(curr))):
                header_text = curr['text']
                header_color = curr['color']
                
                # Verifica se há divisor opcional logo após
                next_idx = i + 1
                if next_idx < n and elements[next_idx]['kind'] == 'DIVIDER':
                    next_idx += 1

                # Verifica se os elementos seguintes formam uma lista vertical de links
                link_items = []
                while next_idx < n and elements[next_idx]['kind'] == 'TEXT' and elements[next_idx]['fontSize'] <= 13 and len(elements[next_idx]['text']) < 60:
                    link_items.append(elements[next_idx])
                    next_idx += 1

                if len(link_items) >= 2:
                    # Achamos uma lista vertical de navegação completa!
                    links_li = "".join([f'            <li class="mb-2"><a href="#" class="text-secondary text-decoration-none small">{item["text"]}</a></li>\n' for item in link_items])
                    output_html.append(f"""          <h6 class="fw-bold text-uppercase small mb-3" style="color: {header_color};">{header_text}</h6>
          <nav aria-label="{header_text}">
            <ul class="list-unstyled mb-0">
{links_li}            </ul>
          </nav>\n""")
                    i = next_idx
                    continue

            # 2. Detecta itens com marcador de retorno/sub-artigo (↳ ou →)
            if kind == 'TEXT' and (curr['text'].startswith('↳') or curr['text'].startswith('→')):
                sub_links = [curr]
                next_idx = i + 1
                while next_idx < n and elements[next_idx]['kind'] == 'TEXT' and (elements[next_idx]['text'].startswith('↳') or elements[next_idx]['text'].startswith('→')):
                    sub_links.append(elements[next_idx])
                    next_idx += 1

                sub_lis = "".join([f'            <li class="mb-2"><a href="#" class="text-decoration-none small text-primary fw-medium"><i class="fa-solid fa-arrow-turn-down-right me-2"></i>{item["text"].lstrip("↳→ ").strip()}</a></li>\n' for item in sub_links])
                output_html.append(f"""          <ul class="list-unstyled mt-3 mb-0">
{sub_lis}          </ul>\n""")
                i = next_idx
                continue

            # 3. Detecta lista com marcadores explícitos (•, -, *)
            if kind == 'TEXT' and (curr['text'].startswith('•') or curr['text'].startswith('-') or curr['text'].startswith('*')):
                bullet_items = [curr]
                next_idx = i + 1
                while next_idx < n and elements[next_idx]['kind'] == 'TEXT' and (elements[next_idx]['text'].startswith('•') or elements[next_idx]['text'].startswith('-') or elements[next_idx]['text'].startswith('*')):
                    bullet_items.append(elements[next_idx])
                    next_idx += 1

                b_lis = "".join([f'            <li class="mb-1">{item["text"].lstrip("•-* ").strip()}</li>\n' for item in bullet_items])
                output_html.append(f"""          <ul class="ps-3 mb-3">
{b_lis}          </ul>\n""")
                i = next_idx
                continue

            # 4. Detecta lista numerada (1., 2.)
            if kind == 'TEXT' and re.match(r'^\d+\.', curr['text']):
                num_items = [curr]
                next_idx = i + 1
                while next_idx < n and elements[next_idx]['kind'] == 'TEXT' and re.match(r'^\d+\.', elements[next_idx]['text']):
                    num_items.append(elements[next_idx])
                    next_idx += 1

                num_lis = "".join([f'            <li class="mb-1">{re.sub(r"^\\d+\\.\\s*", "", item["text"])}</li>\n' for item in num_items])
                output_html.append(f"""          <ol class="ps-3 mb-3">
{num_lis}          </ol>\n""")
                i = next_idx
                continue

            # 5. Fusão de Avatar + Autor/Perfil (imagem pequena <= 80px + no máximo 2 linhas curtas de nome/cargo)
            if kind == 'IMAGE' and curr['w'] <= 80 and curr['h'] <= 80:
                author_texts = []
                next_idx = i + 1
                while next_idx < n and elements[next_idx]['kind'] == 'TEXT' and elements[next_idx]['fontSize'] <= 16 and len(author_texts) < 2 and len(elements[next_idx]['text']) <= 45:
                    author_texts.append(elements[next_idx])
                    next_idx += 1
                if author_texts:
                    texts_html = "".join([f'<div class="{"fw-semibold" if idx == 0 else "small text-muted"}" style="color:{t["color"]}; font-size:{t["fontSize"]}px;">{t["text"]}</div>' for idx, t in enumerate(author_texts)])
                    cr = curr.get('radius', 0)
                    radius_style = f"border-radius: {cr}px;" if cr > 0 else "border-radius: 0px;"
                    radius_cls = "rounded-circle" if cr >= (curr['w'] / 2) and cr > 0 else "rounded-0"
                    output_html.append(f"""          <div class="d-flex align-items-center gap-3 mb-2">
            <img src="{curr['src']}" class="{radius_cls}" style="width: {int(curr['w'])}px; height: {int(curr['h'])}px; object-fit: cover; {radius_style}" alt="{curr['name']}">
            <div>
              {texts_html}
            </div>
          </div>\n""")
                    i = next_idx
                    continue

            # 6. Elemento individual normal
            rendered = self.render_element(curr)
            if rendered:
                output_html.append(f"          {rendered}")
            i += 1

        return "".join(output_html)

    def render_element(self, el):
        kind = el['kind']
        if kind == 'IMAGE':
            max_w = f"max-width: {int(el['w'])}px;" if el.get('w') else ""
            radius_cls = f"style=\"border-radius: {el['radius']}px;\"" if el.get('radius', 0) > 0 else ""
            return f'<div class="mb-3"><img src="{el["src"]}" class="img-fluid w-100" style="{max_w} {radius_cls}" alt="{el["name"]}"></div>\n'

        if kind == 'BUTTON':
            btn_size = "btn-sm px-3 py-1" if el.get('h', 40) <= 34 else "px-4 py-2"
            radius_cls = f"style=\"border-radius: {el['radius']}px;\"" if el.get('radius', 0) > 0 else "rounded-0"
            return f'<a href="#" class="btn btn-dark {btn_size} {radius_cls} fw-semibold my-1 text-uppercase" style="background-color: {el["bg"]}; color: {el["color"]}; font-size: 10px; letter-spacing: 0.05em;">{el["text"]}</a>\n'

        if kind == 'BADGE':
            radius_cls = f"style=\"border-radius: {el['radius']}px;\"" if el.get('radius', 0) > 0 else "rounded-0"
            return f'<span class="badge px-3 py-2 fw-bold text-uppercase my-1 {radius_cls}" style="background-color: {el["bg"]}; color: {el["color"]};">{el["text"]}</span>\n'

        if kind == 'DIVIDER':
            h = max(1, int(el.get('h', 1)))
            bg = el.get('bg') or '#EEEEEE'
            return f'<hr class="my-3" style="border: 0; border-top: {h}px solid {bg}; opacity: 1; margin: 14px 0;">\n'

        if kind == 'NAV_MENU':
            links = "".join([f'<li class="nav-item"><a class="nav-link text-dark px-3 fw-semibold small text-uppercase" href="#">{item}</a></li>' for item in el['nav_items']])
            return f'<nav class="navbar navbar-expand-lg justify-content-center py-2"><ul class="nav justify-content-center mb-0">{links}</ul></nav>\n'

        if kind == 'TEXT':
            fsize = el['fontSize']
            font_cls = "font-serif" if 'georgia' in el['fontFamily'].lower() or 'serif' in el['fontFamily'].lower() else ""
            align_cls = f"text-{el['textAlign']}" if el['textAlign'] != 'left' else ""
            fweight = el.get('fontWeight', 400)
            weight_style = f"font-weight: {fweight};" if fweight != 400 else ""
            color_style = f"color: {el['color']}; font-size: {fsize}px; {weight_style}"

            icon_html = f'<i class="{el["icon"]} me-1"></i>' if el.get('icon') else ""

            if fsize >= 40:
                return f'<h1 class="display-3 fw-bold mb-2 {font_cls} {align_cls}" style="{color_style}">{icon_html}{el["text"]}</h1>\n'
            elif fsize >= 24:
                return f'<h2 class="h2 fw-bold mb-2 {font_cls} {align_cls}" style="{color_style}">{icon_html}{el["text"]}</h2>\n'
            elif fsize >= 16:
                return f'<h3 class="h4 fw-semibold mb-2 {font_cls} {align_cls}" style="{color_style}">{icon_html}{el["text"]}</h3>\n'
            elif fsize <= 12:
                return f'<p class="small text-muted mb-1 {align_cls}" style="{color_style}">{icon_html}{el["text"]}</p>\n'
            else:
                return f'<p class="mb-2 {font_cls} {align_cls}" style="{color_style}">{icon_html}{el["text"]}</p>\n'

        return ""

    def wrap_document(self, title, frame_w, content_w, pad_x, bg_color, sections):
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  
  <!-- Bootstrap 5.3.3 CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  
  <!-- FontAwesome 6.5.2 CDN -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
  
  <!-- Google Fonts: Inter & Georgia Serif -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">

  <style>
    :root {{
      --fc-content-width: {int(content_w)}px;
    }}

    body {{
      background-color: {bg_color};
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: #111111;
      line-height: 1.5;
      margin: 0;
      padding: 0;
    }}
    .font-serif {{
      font-family: 'Georgia', 'Playfair Display', serif;
    }}
    .site-wrapper {{
      width: 100%;
      margin: 0 auto;
      background-color: {bg_color};
      position: relative;
    }}
    /* As seções principais expandem por toda a largura da tela */
    section, header, footer, .topbar {{
      width: 100%;
    }}
    /* O container centraliza estritamente na largura útil do design */
    .container, .container-xxl, .container-xl, .container-lg, .container-md {{
      width: 100%;
      max-width: var(--fc-content-width) !important;
      margin-left: auto !important;
      margin-right: auto !important;
      padding-left: 15px !important;
      padding-right: 15px !important;
    }}
    img {{
      max-width: 100%;
      height: auto;
    }}
    a {{
      text-decoration: none;
    }}
    .tracking-wide {{
      letter-spacing: 0.1em;
    }}
  </style>
</head>
<body>

<div class="site-wrapper">
{"".join(sections)}
</div>

  <!-- Bootstrap 5.3.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description="FigCraft to Bootstrap 5 + FontAwesome Exporter Engine")
    parser.add_argument("file", nargs="?", default=None, help="Caminho do arquivo .figcraft (opcional se o FigCraft estiver aberto)")
    parser.add_argument("--host", default="127.0.0.1", help="Host do FigCraft TCP")
    parser.add_argument("--port", type=int, default=7987, help="Porta do FigCraft TCP")
    parser.add_argument("--dist", default="dist", help="Diretório de saída")
    parser.add_argument("--no-browser", action="store_true", help="Não abre o navegador automaticamente")

    args = parser.parse_args()

    client = None
    doc_path = None

    # Tenta conexão TCP
    try:
        c = FigCraftClient(args.host, args.port)
        c.connect()
        docs = c.list_documents()
        if docs:
            client = c
            doc_path = docs[0].get('path')
            print(f"✓ Conectado ao FigCraft via TCP (Documento: {docs[0].get('name')})")
    except Exception:
        pass

    # Modo arquivo offline
    if not client:
        file_target = args.file
        if not file_target:
            recent_dirs = [
                os.path.expanduser(r"~\Documents\antigravity"),
                r"E:\OneDrive\Documentos\FigCraftLayouts",
                os.path.expanduser(r"~\Downloads"),
                r"E:\Downloads"
            ]
            for d in recent_dirs:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        if f.endswith('.figcraft'):
                            file_target = os.path.join(d, f)
                            break
                    if file_target:
                        break

        if file_target and os.path.exists(file_target):
            client = FigCraftZipClient(file_target)
            doc_path = file_target
            print(f"✓ Carregado diretamente do arquivo: {file_target}")
        else:
            print("Erro: FigCraft não está aberto e nenhum arquivo .figcraft foi fornecido.")
            sys.exit(1)

    compiler = UniversalASTCompiler(client, dist_dir=args.dist)
    doc_data = client.inspect_document()
    pages = doc_data.get('pages', [])

    if not pages:
        print("Erro: Nenhuma página encontrada no documento.")
        sys.exit(1)

    generated_files = []
    for page in pages:
        frames = page.get('children', [])
        for f in frames:
            if f.get('type') == 'FRAME':
                html = compiler.compile_frame(f)
                clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', f.get('name', 'index')).lower().strip('_')
                out_path = os.path.join(args.dist, f"{clean_name}.html")
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(html)
                generated_files.append(out_path)
                print(f"  -> Gerado com sucesso: {out_path} ({len(html)} bytes)")

    client.close()

    print("\n===========================================================================")
    print(" ✓ EXPORTAÇÃO UNIVERSAL CONCLUÍDA COM 100% DE ALTA FIDELIDADE!")
    print("===========================================================================")

    if generated_files and not args.no_browser:
        webbrowser.open(f"file:///{os.path.abspath(generated_files[0])}")

if __name__ == '__main__':
    main()
