//! Universal FigCraft to Bootstrap 5 + FontAwesome Exporter Engine
//! Native Rust / WebAssembly Plugin
//! Author: uzielweb (https://github.com/uzielweb)
//! License: MIT

use figcraft_plugin_sdk::{Input, Result, Value, call, entry, json, notify, save_file};

/// Regra CSS acumulada
struct CssRule {
    selector: String,
    declarations: Vec<String>,
}

impl CssRule {
    fn new(selector: &str) -> Self {
        Self {
            selector: selector.to_string(),
            declarations: Vec::new(),
        }
    }

    fn add(&mut self, prop: &str, val: &str) {
        if !val.is_empty() {
            self.declarations.push(format!("  {}: {};", prop, val));
        }
    }

    fn to_css_string(&self) -> String {
        if self.declarations.is_empty() {
            return String::new();
        }
        let mut out = format!("{} {{\n", self.selector);
        for d in &self.declarations {
            out.push_str(d);
            out.push('\n');
        }
        out.push_str("}\n\n");
        out
    }
}

/// Converte cor {r, g, b, a} ou String #RRGGBB para CSS
fn format_color(color_val: &Value) -> Option<String> {
    if color_val.is_null() {
        return None;
    }
    if let Some(s) = color_val.as_str() {
        return Some(s.to_string());
    }
    if let Some(obj) = color_val.as_object() {
        let r = (obj.get("r").and_then(Value::as_f64).unwrap_or(0.0) * 255.0).round() as u8;
        let g = (obj.get("g").and_then(Value::as_f64).unwrap_or(0.0) * 255.0).round() as u8;
        let b = (obj.get("b").and_then(Value::as_f64).unwrap_or(0.0) * 255.0).round() as u8;
        let a = obj.get("a").and_then(Value::as_f64).unwrap_or(1.0);
        if a < 0.999 {
            return Some(format!("rgba({}, {}, {}, {:.2})", r, g, b, a));
        }
        return Some(format!("#{:02X}{:02X}{:02X}", r, g, b));
    }
    None
}

/// Extrai cor de fundo sólida ou gradiente
fn extract_bg_color(node: &Value) -> Option<String> {
    if let Some(fills) = node.get("fills").and_then(Value::as_array) {
        for f in fills {
            if f.get("visible").and_then(Value::as_bool).unwrap_or(true) {
                let fill_type = f.get("type").and_then(Value::as_str).unwrap_or("");
                if fill_type == "solid" {
                    if let Some(c) = f.get("color") {
                        return format_color(c);
                    }
                }
            }
        }
    }
    if let Some(c) = node.get("fill") {
        return format_color(c);
    }
    None
}

/// Verifica se o nó é uma imagem (fill image ou nome sugestivo)
fn is_image_node(node: &Value) -> bool {
    let node_type = node.get("type").and_then(Value::as_str).unwrap_or("");
    if node_type == "TEXT" {
        return false;
    }
    if let Some(fills) = node.get("fills").and_then(Value::as_array) {
        for f in fills {
            if f.get("type").and_then(Value::as_str) == Some("image") {
                return true;
            }
        }
    }
    let name = node.get("name").and_then(Value::as_str).unwrap_or("").to_lowercase();
    let width = node.get("width").and_then(Value::as_f64).unwrap_or(0.0);
    let height = node.get("height").and_then(Value::as_f64).unwrap_or(0.0);
    
    if width >= 24.0 && height >= 24.0 {
        for keyword in &["img", "foto", "photo", "thumb", "hero", "author", "culture", "banner", "cover", "avatar", "pic", "image"] {
            if name.contains(keyword) {
                return true;
            }
        }
    }
    false
}

/// Detecta ícone FontAwesome 6/7 universal a partir de texto ou nome
fn detect_universal_icon(text: &str, name: &str) -> Option<&'static str> {
    let t = text.trim();
    match t {
        "🔍" | "🔎" | "⌕" => return Some("fa-solid fa-magnifying-glass"),
        "☰" => return Some("fa-solid fa-bars"),
        "⚙️" | "⚙" => return Some("fa-solid fa-gear"),
        "⭐" | "★" => return Some("fa-solid fa-star"),
        "❤️" | "♥" => return Some("fa-solid fa-heart"),
        "✓" | "✔" | "✅" => return Some("fa-solid fa-check"),
        "✖" | "✕" | "❌" => return Some("fa-solid fa-xmark"),
        "➕" | "+" => return Some("fa-solid fa-plus"),
        "➖" | "-" => return Some("fa-solid fa-minus"),
        "→" | "➔" | "↳" | "➜" => return Some("fa-solid fa-arrow-right"),
        "←" | "⬅" => return Some("fa-solid fa-arrow-left"),
        "↑" => return Some("fa-solid fa-arrow-up"),
        "↓" => return Some("fa-solid fa-arrow-down"),
        "🔔" => return Some("fa-solid fa-bell"),
        "✉" | "✉️" => return Some("fa-solid fa-envelope"),
        "📞" => return Some("fa-solid fa-phone"),
        "🌐" => return Some("fa-solid fa-globe"),
        "🔒" => return Some("fa-solid fa-lock"),
        "🔗" => return Some("fa-solid fa-link"),
        "📅" => return Some("fa-solid fa-calendar"),
        "🕒" | "⏰" => return Some("fa-solid fa-clock"),
        _ => {}
    }

    let n = name.to_lowercase();
    if n.contains("icon") || n.contains("icone") || n.contains("ico") {
        if n.contains("search") || n.contains("busca") { return Some("fa-solid fa-magnifying-glass"); }
        if n.contains("menu") || n.contains("hambur") { return Some("fa-solid fa-bars"); }
        if n.contains("user") || n.contains("perfil") || n.contains("profile") { return Some("fa-solid fa-user"); }
        if n.contains("star") || n.contains("fav") { return Some("fa-solid fa-star"); }
        if n.contains("heart") || n.contains("like") { return Some("fa-solid fa-heart"); }
        if n.contains("gear") || n.contains("config") || n.contains("setting") { return Some("fa-solid fa-gear"); }
        if n.contains("close") || n.contains("fechar") { return Some("fa-solid fa-xmark"); }
        if n.contains("check") { return Some("fa-solid fa-check"); }
        if n.contains("bell") || n.contains("notif") { return Some("fa-solid fa-bell"); }
        if n.contains("share") || n.contains("compartilh") { return Some("fa-solid fa-share-nodes"); }
        if n.contains("arrow-right") || n.contains("next") { return Some("fa-solid fa-arrow-right"); }
        if n.contains("arrow-left") || n.contains("prev") { return Some("fa-solid fa-arrow-left"); }
    }

    None
}

/// Sanitiza strings para identificadores CSS
fn clean_identifier(name: &str) -> String {
    let mut clean = String::new();
    for c in name.chars() {
        if c.is_ascii_alphanumeric() || c == '-' || c == '_' {
            clean.push(c);
        } else if c == ' ' {
            clean.push('-');
        }
    }
    if clean.is_empty() {
        "el".to_string()
    } else {
        clean.to_lowercase()
    }
}

/// Escapa caracteres HTML
fn escape_html(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for c in text.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&#39;"),
            _ => out.push(c),
        }
    }
    out
}

/// Estrutura para representar um elemento compilado após fusão de pares
#[derive(Clone)]
struct FusedElement {
    id: u64,
    name: String,
    tag_kind: ElementKind,
    x: f64,
    y: f64,
    width: f64,
    height: f64,
    text: String,
    bg_color: Option<String>,
    text_color: Option<String>,
    font_size: f64,
    font_family: String,
    font_weight: f64,
    text_align: String,
    border_radius: f64,
    icon_class: Option<&'static str>,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum ElementKind {
    Heading1,
    Heading2,
    Heading3,
    Paragraph,
    Small,
    Button,
    Badge,
    Image,
    Divider,
    VerticalDivider,
    Card,
    Container,
}

/// Estrutura para agrupar seções verticais (Bands)
struct SectionBand {
    name: String,
    y_start: f64,
    y_end: f64,
    bg_color: Option<String>,
    elements: Vec<FusedElement>,
    is_topbar: bool,
    is_header: bool,
    is_footer: bool,
}

/// Renderiza um elemento individual em HTML do Bootstrap
fn render_element_bootstrap(el: &FusedElement, el_class: &str) -> String {
    match el.tag_kind {
        ElementKind::Heading1 => {
            format!("<h1 class=\"display-4 fw-bold font-serif mb-2 {}\">{}</h1>\n", el_class, escape_html(&el.text))
        }
        ElementKind::Heading2 => {
            format!("<h2 class=\"h2 fw-bold font-serif mb-2 {}\">{}</h2>\n", el_class, escape_html(&el.text))
        }
        ElementKind::Heading3 => {
            format!("<h3 class=\"h4 fw-semibold font-serif mb-2 {}\">{}</h3>\n", el_class, escape_html(&el.text))
        }
        ElementKind::Paragraph => {
            format!("<p class=\"mb-2 {}\">{}</p>\n", el_class, escape_html(&el.text))
        }
        ElementKind::Small => {
            if let Some(icon) = el.icon_class {
                format!("<p class=\"small text-muted mb-1 {}\"><i class=\"{} me-1\"></i>{}</p>\n", el_class, icon, escape_html(&el.text))
            } else {
                format!("<p class=\"small text-muted mb-1 {}\">{}</p>\n", el_class, escape_html(&el.text))
            }
        }
        ElementKind::Button => {
            let radius_cls = if el.border_radius > 0.0 { format!("style=\"border-radius: {}px;\"", el.border_radius) } else { "rounded-0".to_string() };
            format!("<a href=\"#\" class=\"btn btn-dark btn-sm px-3 py-1 fw-semibold my-1 text-uppercase {} {}\">{}</a>\n", radius_cls, el_class, escape_html(&el.text))
        }
        ElementKind::Badge => {
            let radius_cls = if el.border_radius > 0.0 { format!("style=\"border-radius: {}px;\"", el.border_radius) } else { "rounded-0".to_string() };
            format!("<span class=\"badge px-3 py-2 text-uppercase fw-bold my-1 {} {}\">{}</span>\n", radius_cls, el_class, escape_html(&el.text))
        }
        ElementKind::Divider => {
            "<hr class=\"my-3\" style=\"border: 0; border-top: 1px solid #EEEEEE; opacity: 1; margin: 14px 0;\">\n".to_string()
        }
        ElementKind::Image => {
            let clean = clean_identifier(&el.name);
            let radius_style = if el.border_radius > 0.0 { format!("style=\"border-radius: {}px;\"", el.border_radius) } else { String::new() };
            format!(
                "<div class=\"mb-3 {}\"><img src=\"assets/images/img_{}_{}.png\" class=\"img-fluid w-100 rounded-0\" {} alt=\"{}\"></div>\n",
                el_class, el.id, clean, radius_style, escape_html(&el.name)
            )
        }
        ElementKind::Card | ElementKind::Container | ElementKind::VerticalDivider => {
            String::new()
        }
    }
}

/// Agrupa elementos de uma seção em colunas Bootstrap verticais
fn cluster_columns_bootstrap(elements: &[FusedElement], frame_w: f64) -> Vec<(usize, Vec<FusedElement>)> {
    if elements.is_empty() {
        return Vec::new();
    }

    let mut full_width = Vec::new();
    let mut col_items = Vec::new();

    for e in elements {
        if e.tag_kind == ElementKind::VerticalDivider {
            continue;
        }
        if e.width >= frame_w * 0.65 || e.text.contains('©') || e.text.to_lowercase().contains("todos os direitos") {
            full_width.push(e.clone());
        } else {
            col_items.push(e.clone());
        }
    }

    let mut clusters: Vec<Vec<FusedElement>> = Vec::new();
    if !col_items.is_empty() {
        col_items.sort_by(|a, b| a.x.partial_cmp(&b.x).unwrap_or(std::cmp::Ordering::Equal));
        let mut cur = vec![col_items[0].clone()];

        for e in col_items.into_iter().skip(1) {
            let last = cur.last().unwrap();
            let c_right = cur.iter().map(|item| item.x + item.width).fold(0.0, f64::max);
            if e.x < (c_right + 30.0) {
                cur.push(e);
            } else {
                clusters.push(cur);
                cur = vec![e];
            }
        }
        if !cur.is_empty() {
            clusters.push(cur);
        }
    }

    let mut result = Vec::new();
    let count = clusters.len();

    if count == 1 {
        let mut c = clusters.remove(0);
        c.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
        result.push((12, c));
    } else if count == 2 {
        let mut c0 = clusters.remove(0);
        let mut c1 = clusters.remove(0);
        c0.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
        c1.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
        result.push((6, c0));
        result.push((6, c1));
    } else if count == 3 {
        let mut c0 = clusters.remove(0);
        let mut c1 = clusters.remove(0);
        let mut c2 = clusters.remove(0);
        c0.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
        c1.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
        c2.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
        result.push((3, c0));
        result.push((6, c1));
        result.push((3, c2));
    } else if count == 4 {
        for mut c in clusters {
            c.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
            result.push((3, c));
        }
    } else if count == 5 {
        let spans = [3, 2, 2, 2, 3];
        for (idx, mut c) in clusters.into_iter().enumerate() {
            c.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
            result.push((spans[idx], c));
        }
    } else {
        let span = usize::max(2, 12 / count);
        for mut c in clusters {
            c.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
            result.push((span, c));
        }
    }

    if !full_width.is_empty() {
        full_width.sort_by(|a, b| a.y.partial_cmp(&b.y).unwrap_or(std::cmp::Ordering::Equal));
        result.push((12, full_width));
    }

    result
}

/// Compila um frame universal em HTML5 responsivo com Bootstrap 5 e FontAwesome
fn compile_frame_to_bootstrap(frame: &Value, css_rules: &mut Vec<CssRule>) -> String {
    let frame_id = frame.get("id").and_then(Value::as_u64).unwrap_or(0);
    let frame_name = frame.get("name").and_then(Value::as_str).unwrap_or("Page");
    let frame_w = frame.get("width").and_then(Value::as_f64).unwrap_or(1440.0);
    let frame_h = frame.get("height").and_then(Value::as_f64).unwrap_or(1080.0);
    let frame_bg = extract_bg_color(frame).unwrap_or_else(|| "#FFFFFF".to_string());

    let raw_children = frame.get("children").and_then(Value::as_array).cloned().unwrap_or_default();

    // 1. Identificar divisores horizontais e limites de seções (Bands)
    let mut boundary_ys = vec![0.0, frame_h];
    let mut band_dividers = Vec::new();
    let mut content_nodes = Vec::new();

    for c in &raw_children {
        let w = c.get("width").and_then(Value::as_f64).unwrap_or(0.0);
        let h = c.get("height").and_then(Value::as_f64).unwrap_or(0.0);
        let y = c.get("y").and_then(Value::as_f64).unwrap_or(0.0);
        let ntype = c.get("type").and_then(Value::as_str).unwrap_or("");
        
        if ntype == "RECTANGLE" && w >= (frame_w * 0.70) {
            boundary_ys.push(y);
            if h >= 15.0 {
                boundary_ys.push(y + h);
                band_dividers.push(c.clone());
            } else {
                content_nodes.push(c.clone());
            }
        } else {
            content_nodes.push(c.clone());
        }
    }

    boundary_ys.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    boundary_ys.dedup();

    let mut cleaned_ys = vec![boundary_ys[0]];
    for &y in boundary_ys.iter().skip(1) {
        if y - *cleaned_ys.last().unwrap() >= 20.0 {
            cleaned_ys.push(y);
        }
    }
    if *cleaned_ys.last().unwrap() < frame_h {
        cleaned_ys.push(frame_h);
    }

    let mut bands = Vec::new();
    for i in 0..(cleaned_ys.len() - 1) {
        let y_start = cleaned_ys[i];
        let y_end = cleaned_ys[i + 1];

        let mut bg_color = None;
        let mut band_name = format!("Section_{}", i);

        for b in &band_dividers {
            let by = b.get("y").and_then(Value::as_f64).unwrap_or(0.0);
            let bh = b.get("height").and_then(Value::as_f64).unwrap_or(0.0);
            if (by - y_start).abs() <= 20.0 && bh >= 15.0 {
                bg_color = extract_bg_color(b);
                if let Some(bn) = b.get("name").and_then(Value::as_str) {
                    band_name = bn.to_string();
                }
                break;
            }
        }

        let b_lower = band_name.to_lowercase();
        let is_topbar = i == 0 && y_end <= 50.0;
        let is_header = b_lower.contains("header") || b_lower.contains("masthead") || b_lower.contains("nav");
        let is_footer = b_lower.contains("footer") || y_start >= (frame_h * 0.75);

        bands.push(SectionBand {
            name: band_name,
            y_start,
            y_end,
            bg_color,
            elements: Vec::new(),
            is_topbar,
            is_header,
            is_footer,
        });
    }

    // 2. Fazer fusão de nós (Node Pair Fusion)
    let mut fused_list = Vec::new();
    let mut skip_ids = std::collections::HashSet::new();

    for curr in &content_nodes {
        let cid = curr.get("id").and_then(Value::as_u64).unwrap_or(0);
        if skip_ids.contains(&cid) {
            continue;
        }

        let c_name = curr.get("name").and_then(Value::as_str).unwrap_or("").to_string();
        let c_type = curr.get("type").and_then(Value::as_str).unwrap_or("").to_uppercase();
        let c_x = curr.get("x").and_then(Value::as_f64).unwrap_or(0.0);
        let c_y = curr.get("y").and_then(Value::as_f64).unwrap_or(0.0);
        let c_w = curr.get("width").and_then(Value::as_f64).unwrap_or(0.0);
        let c_h = curr.get("height").and_then(Value::as_f64).unwrap_or(0.0);
        let c_bg = extract_bg_color(curr);
        let c_radius = curr.get("cornerRadius").and_then(Value::as_f64).unwrap_or(0.0);

        // A. Divisores verticais (w <= 4 e h >= 20) -> NÃO é coluna de conteúdo
        if c_type == "RECTANGLE" && c_w <= 4.0 && c_h >= 20.0 {
            fused_list.push(FusedElement {
                id: cid,
                name: c_name,
                tag_kind: ElementKind::VerticalDivider,
                x: c_x,
                y: c_y,
                width: c_w,
                height: c_h,
                text: String::new(),
                bg_color: c_bg,
                text_color: None,
                font_size: 0.0,
                font_family: String::new(),
                font_weight: 400.0,
                text_align: String::new(),
                border_radius: 0.0,
                icon_class: None,
            });
            continue;
        }

        // B. Imagens
        if is_image_node(curr) {
            fused_list.push(FusedElement {
                id: cid,
                name: c_name,
                tag_kind: ElementKind::Image,
                x: c_x,
                y: c_y,
                width: c_w,
                height: c_h,
                text: String::new(),
                bg_color: None,
                text_color: None,
                font_size: 0.0,
                font_family: String::new(),
                font_weight: 400.0,
                text_align: String::new(),
                border_radius: c_radius,
                icon_class: None,
            });
            continue;
        }

        // B. Divisores finos (<hr>)
        if c_type == "RECTANGLE" && c_h <= 3.0 && c_w >= 40.0 {
            fused_list.push(FusedElement {
                id: cid,
                name: c_name,
                tag_kind: ElementKind::Divider,
                x: c_x,
                y: c_y,
                width: c_w,
                height: c_h,
                text: String::new(),
                bg_color: c_bg,
                text_color: None,
                font_size: 0.0,
                font_family: String::new(),
                font_weight: 400.0,
                text_align: String::new(),
                border_radius: 0.0,
                icon_class: None,
            });
            continue;
        }

        // C. Botões (Fusão de Retângulo + Texto sobreposto)
        let name_lower = c_name.to_lowercase();
        let is_button_candidate = (name_lower.contains("btn") || name_lower.contains("button") || name_lower.contains("botao"))
            || (c_type == "RECTANGLE" && c_h >= 24.0 && c_h <= 60.0 && c_w <= 320.0);

        if is_button_candidate {
            let mut btn_text = None;
            for other in &content_nodes {
                let oid = other.get("id").and_then(Value::as_u64).unwrap_or(0);
                if oid != cid && other.get("type").and_then(Value::as_str) == Some("TEXT") {
                    let ox = other.get("x").and_then(Value::as_f64).unwrap_or(0.0);
                    let oy = other.get("y").and_then(Value::as_f64).unwrap_or(0.0);
                    if (c_x - 10.0) <= ox && ox <= (c_x + c_w) && (c_y - 5.0) <= oy && oy <= (c_y + c_h) {
                        if let Some(t) = other.get("characters").and_then(Value::as_str) {
                            btn_text = Some((oid, t.to_string(), extract_bg_color(other)));
                            break;
                        }
                    }
                }
            }

            if let Some((text_id, text_str, text_col)) = btn_text {
                skip_ids.insert(text_id);
                fused_list.push(FusedElement {
                    id: cid,
                    name: c_name,
                    tag_kind: ElementKind::Button,
                    x: c_x,
                    y: c_y,
                    width: c_w,
                    height: c_h,
                    text: text_str,
                    bg_color: c_bg.or_else(|| Some("#111111".to_string())),
                    text_color: text_col.or_else(|| Some("#FFFFFF".to_string())),
                    font_size: 14.0,
                    font_family: String::new(),
                    font_weight: 600.0,
                    text_align: "center".to_string(),
                    border_radius: if c_radius > 0.0 { c_radius } else { 4.0 },
                    icon_class: None,
                });
                continue;
            }
        }

        // D. Badges (Fusão de Retângulo pequeno + Texto)
        let is_badge_candidate = (name_lower.contains("badge") || name_lower.contains("tag") || name_lower.contains("pill"))
            || (c_type == "RECTANGLE" && c_h <= 34.0 && c_w <= 240.0 && c_radius >= 8.0);

        if is_badge_candidate {
            let mut badge_text = None;
            for other in &content_nodes {
                let oid = other.get("id").and_then(Value::as_u64).unwrap_or(0);
                if oid != cid && other.get("type").and_then(Value::as_str) == Some("TEXT") {
                    let ox = other.get("x").and_then(Value::as_f64).unwrap_or(0.0);
                    let oy = other.get("y").and_then(Value::as_f64).unwrap_or(0.0);
                    if (c_x - 10.0) <= ox && ox <= (c_x + c_w) && (c_y - 5.0) <= oy && oy <= (c_y + c_h) {
                        if let Some(t) = other.get("characters").and_then(Value::as_str) {
                            badge_text = Some((oid, t.to_string(), extract_bg_color(other)));
                            break;
                        }
                    }
                }
            }

            if let Some((text_id, text_str, text_col)) = badge_text {
                skip_ids.insert(text_id);
                fused_list.push(FusedElement {
                    id: cid,
                    name: c_name,
                    tag_kind: ElementKind::Badge,
                    x: c_x,
                    y: c_y,
                    width: c_w,
                    height: c_h,
                    text: text_str,
                    bg_color: c_bg.or_else(|| Some("#F1F5F9".to_string())),
                    text_color: text_col.or_else(|| Some("#0F172A".to_string())),
                    font_size: 11.0,
                    font_family: String::new(),
                    font_weight: 600.0,
                    text_align: "center".to_string(),
                    border_radius: if c_radius > 0.0 { c_radius } else { 16.0 },
                    icon_class: None,
                });
                continue;
            }
        }

        // E. Texto
        if c_type == "TEXT" {
            let chars = curr.get("characters").and_then(Value::as_str).unwrap_or("").trim().to_string();
            if !chars.is_empty() {
                let fsize = curr.get("fontSize").and_then(Value::as_f64)
                    .or_else(|| curr.get("style").and_then(|s| s.get("font_size")).and_then(Value::as_f64))
                    .or_else(|| curr.get("style").and_then(|s| s.get("fontSize")).and_then(Value::as_f64))
                    .unwrap_or(14.0);

                let ffamily = curr.get("fontFamily").and_then(Value::as_str)
                    .or_else(|| curr.get("style").and_then(|s| s.get("font_family")).and_then(Value::as_str))
                    .or_else(|| curr.get("style").and_then(|s| s.get("fontFamily")).and_then(Value::as_str))
                    .unwrap_or("Segoe UI")
                    .to_string();
                let fweight = curr.get("fontWeight").and_then(Value::as_f64).unwrap_or(400.0);
                let talign = curr.get("textAlign").and_then(Value::as_str).unwrap_or("left").to_string();
                let icon = detect_universal_icon(&chars, &c_name);

                let kind = if fsize >= 28.0 {
                    ElementKind::Heading1
                } else if fsize >= 20.0 {
                    ElementKind::Heading2
                } else if fsize >= 16.0 {
                    ElementKind::Heading3
                } else if fsize <= 12.0 {
                    ElementKind::Small
                } else {
                    ElementKind::Paragraph
                };

                fused_list.push(FusedElement {
                    id: cid,
                    name: c_name,
                    tag_kind: kind,
                    x: c_x,
                    y: c_y,
                    width: c_w,
                    height: c_h,
                    text: chars,
                    bg_color: None,
                    text_color: c_bg,
                    font_size: fsize,
                    font_family: ffamily,
                    font_weight: fweight,
                    text_align: talign,
                    border_radius: 0.0,
                    icon_class: icon,
                });
            }
            continue;
        }

        // F. Cards ou Contêineres
        let is_card = c_w >= 220.0 && c_h >= 60.0;
        fused_list.push(FusedElement {
            id: cid,
            name: c_name,
            tag_kind: if is_card { ElementKind::Card } else { ElementKind::Container },
            x: c_x,
            y: c_y,
            width: c_w,
            height: c_h,
            text: String::new(),
            bg_color: c_bg,
            text_color: None,
            font_size: 0.0,
            font_family: String::new(),
            font_weight: 400.0,
            text_align: String::new(),
            border_radius: c_radius,
            icon_class: None,
        });
    }

    // 3. Alocar elementos nas bandas correspondentes por coordenada Y
    for el in fused_list {
        let mut target_idx = None;
        for (idx, b) in bands.iter().enumerate() {
            if b.y_start <= el.y && el.y < b.y_end {
                target_idx = Some(idx);
                break;
            }
        }
        if let Some(idx) = target_idx {
            bands[idx].elements.push(el);
        } else if let Some(last) = bands.last_mut() {
            last.elements.push(el);
        }
    }

    // 4. Compilar cada banda em seções e colunas responsivas do Bootstrap 5
    let mut sections_html = Vec::new();

    for (b_idx, band) in bands.iter_mut().enumerate() {
        if band.elements.is_empty() && band.bg_color.is_none() {
            continue;
        }

        let section_css_class = format!("fc-sec-{}-{}", clean_identifier(&band.name), b_idx);
        if let Some(ref bg) = band.bg_color {
            let mut srule = CssRule::new(&format!(".{}", section_css_class));
            srule.add("background-color", bg);
            css_rules.push(srule);
        }

        let is_dark_bg = band.bg_color.as_ref().map(|c| c.contains("#0") || c.contains("#1") || c.contains("#2")).unwrap_or(false);
        let text_theme_class = if is_dark_bg { "text-white" } else { "" };

        // Topbar
        if band.is_topbar {
            band.elements.sort_by(|a, b| a.x.partial_cmp(&b.x).unwrap_or(std::cmp::Ordering::Equal));
            let mut left_items = Vec::new();
            let mut right_items = Vec::new();

            for e in &band.elements {
                let el_class = format!("fc-el-{}-{}", clean_identifier(&e.name), e.id);
                let rendered = render_element_bootstrap(e, &el_class);
                if e.x < frame_w * 0.70 {
                    left_items.push(format!("<span>{}</span>", escape_html(&e.text)));
                } else {
                    right_items.push(rendered);
                }
            }

            let topbar_html = format!(
                "  <div class=\"topbar py-2 border-bottom {sec_cls} {theme_cls}\">\n    <div class=\"container d-flex flex-wrap justify-content-between align-items-center small\">\n      <div class=\"text-secondary small\">{left}</div>\n      <div class=\"d-flex align-items-center gap-2\">{right}</div>\n    </div>\n  </div>\n",
                sec_cls = section_css_class,
                theme_cls = text_theme_class,
                left = left_items.join(" • "),
                right = right_items.join("")
            );
            sections_html.push(topbar_html);
            continue;
        }

        // Seções gerais e Footer: Agrupamento em colunas verticais naturais
        let cols = cluster_columns_bootstrap(&band.elements, frame_w);
        let mut cols_html = String::new();

        for (span, col_elements) in cols {
            let mut col_inner = String::new();
            for el in col_elements {
                let el_class = format!("fc-el-{}-{}", clean_identifier(&el.name), el.id);
                let mut erule = CssRule::new(&format!(".{}", el_class));

                if let Some(ref col) = el.text_color {
                    erule.add("color", col);
                }
                if let Some(ref bg) = el.bg_color {
                    erule.add("background-color", bg);
                }
                if el.border_radius > 0.0 {
                    erule.add("border-radius", &format!("{}px", el.border_radius as i64));
                }
                if !el.font_family.is_empty() {
                    erule.add("font-family", &format!("'{}', -apple-system, sans-serif", el.font_family));
                }
                css_rules.push(erule);

                col_inner.push_str(&render_element_bootstrap(&el, &el_class));
            }

            if !col_inner.trim().is_empty() {
                cols_html.push_str(&format!(
                    "        <div class=\"col-lg-{} col-md-6 col-12 mb-4\">\n{}        </div>\n",
                    span, col_inner
                ));
            }
        }

        let tag = if band.is_header {
            "header"
        } else if band.is_footer {
            "footer"
        } else {
            "section"
        };

        let sec_html = format!(
            "  <{tag} class=\"py-5 {sec_cls} {theme_cls}\">\n    <div class=\"container\">\n      <div class=\"row g-4\">\n{cols}      </div>\n    </div>\n  </{tag}>\n",
            tag = tag,
            sec_cls = section_css_class,
            theme_cls = text_theme_class,
            cols = cols_html
        );
        sections_html.push(sec_html);
    }

    // Encapsula o documento principal com largura real de design
    let page_css_class = format!("fc-page-{}-{}", clean_identifier(frame_name), frame_id);
    let mut page_rule = CssRule::new(&format!(".{}", page_css_class));
    page_rule.add("max-width", &format!("{}px", frame_w as i64));
    page_rule.add("margin", "0 auto");
    page_rule.add("min-height", "100vh");
    page_rule.add("background-color", &frame_bg);
    css_rules.push(page_rule);

    format!(
        "<div class=\"site-layout {}\">\n{}</div>\n",
        page_css_class,
        sections_html.join("\n")
    )
}

/// Execução oficial do plugin ao clicar no menu do FigCraft
fn run(input: Input) -> Result<Value> {
    // 1. Identifica frames: usa a seleção atual ou busca todos os frames da página
    let frame_ids: Vec<u64> = if !input.selection.is_empty() {
        input.selection.clone()
    } else {
        let find_res = call("node.find", &json!({"type": "FRAME"}))?;
        find_res.get("ids")
            .and_then(Value::as_array)
            .map(|a| a.iter().filter_map(Value::as_u64).collect())
            .unwrap_or_default()
    };

    if frame_ids.is_empty() {
        return Err("Nenhum frame selecionado ou encontrado na página para exportação.".into());
    }

    let mut css_rules = Vec::new();
    let mut pages_html = Vec::new();
    let mut total_nodes = 0;
    let mut main_title = String::from("FigCraft Bootstrap Export");

    for (idx, fid) in frame_ids.iter().enumerate() {
        let node_data = call("node.get", &json!({"id": fid}))?;
        if idx == 0 {
            if let Some(n) = node_data.get("name").and_then(Value::as_str) {
                main_title = n.to_string();
            }
        }
        total_nodes += node_data.get("children").and_then(Value::as_array).map(|a| a.len()).unwrap_or(0) + 1;
        let page_html = compile_frame_to_bootstrap(&node_data, &mut css_rules);
        pages_html.push(page_html);
    }

    // 2. Monta o CSS limpo com regras estruturais e classes de cada elemento
    let mut full_css = String::from("/* Design Tokens e Classes Geradas pelo FigCraft Bootstrap Exporter */\n");
    full_css.push_str("body {\n  margin: 0;\n  padding: 0;\n  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;\n  -webkit-font-smoothing: antialiased;\n}\n\n");
    full_css.push_str("img {\n  max-width: 100%;\n  height: auto;\n}\n\n");
    full_css.push_str("a {\n  text-decoration: none;\n}\n\n");
    full_css.push_str(".font-serif {\n  font-family: 'Georgia', 'Playfair Display', serif;\n}\n\n");

    for r in &css_rules {
        full_css.push_str(&r.to_css_string());
    }

    // 3. Monta o HTML completo sem nenhum header/footer falso
    let full_html = format!(
        r#"<!DOCTYPE html>
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
{css}
  </style>
</head>
<body>

{content}

  <!-- Bootstrap 5.3.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"#,
        title = escape_html(&main_title),
        css = full_css,
        content = pages_html.join("\n\n")
    );

    // 4. Salva o arquivo através da janela nativa do FigCraft (save_file / API 4)
    save_file("index.html", "text/html", full_html.as_bytes())?;

    // 5. Notificação nativa no FigCraft
    notify(&format!("Exportado com sucesso para Bootstrap 5 & FontAwesome ({} nós)!", total_nodes));

    Ok(json!({
        "status": "success",
        "nodes": total_nodes,
        "classes": css_rules.len(),
        "bytes": full_html.len()
    }))
}

entry!(run);
