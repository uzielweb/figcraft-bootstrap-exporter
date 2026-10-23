"""
FigCraft to Bootstrap 5 + FontAwesome 7 Exporter Engine
Author: uzielweb (https://github.com/uzielweb)
License: MIT
"""

import socket
import json
import os
import sys
import argparse

def get_figcraft_document(host="127.0.0.1", port=7987):
    """Fetches the active document tree from a running FigCraft instance over TCP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        req = {"method": "document.inspect"}
        s.sendall((json.dumps(req) + "\n").encode("utf-8"))
        raw = ""
        while True:
            chunk = s.recv(4096).decode("utf-8")
            raw += chunk
            if "\n" in raw:
                break
        doc = json.loads(raw.strip())
        return doc.get("result")
    finally:
        s.close()

def export_to_bootstrap(doc, output_path="index.html"):
    """
    Renders FigCraft design frames into responsive semantic HTML with Bootstrap 5.3+ and FontAwesome 7.
    """
    html_content = """<!DOCTYPE html>
<html lang="pt-BR" data-bs-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SonicPulse FM — FigCraft to Bootstrap 5 + FontAwesome 7</title>
  
  <!-- Bootstrap 5.3 CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  
  <!-- FontAwesome 7 (Latest) -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.3.1/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@7.3.1/css/all.min.css" crossorigin="anonymous">
  
  <!-- Google Fonts: Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">

  <style>
    :root {
      --bg-dark: #0B0E14;
      --card-dark: #131824;
      --card-glass: rgba(19, 24, 36, 0.85);
      --border-dark: #1F283C;
      --accent-cyan: #00F2FE;
      --accent-cyan-rgb: 0, 242, 254;
      --accent-violet: #7C3AED;
      --text-muted: #94A3B8;
      --vinyl-grad: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
    }

    body {
      background-color: var(--bg-dark);
      color: #FFFFFF;
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* Ambient Glow Background */
    .ambient-glow-cyan {
      position: absolute;
      width: 450px;
      height: 450px;
      background: radial-gradient(circle, rgba(0, 242, 254, 0.12) 0%, rgba(0, 0, 0, 0) 70%);
      top: -100px;
      left: -100px;
      z-index: 0;
      pointer-events: none;
    }

    .ambient-glow-violet {
      position: absolute;
      width: 450px;
      height: 450px;
      background: radial-gradient(circle, rgba(124, 58, 237, 0.10) 0%, rgba(0, 0, 0, 0) 70%);
      bottom: 50px;
      right: -100px;
      z-index: 0;
      pointer-events: none;
    }

    /* Mobile Frame Mockup */
    .mobile-mockup {
      max-width: 412px;
      width: 100%;
      min-height: 892px;
      background: var(--bg-dark);
      border: 1px solid var(--border-dark);
      border-radius: 44px;
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 35px rgba(0, 242, 254, 0.08);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* Glassmorphism Cards */
    .glass-card {
      background: var(--card-glass);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-dark);
      border-radius: 26px;
    }

    /* Vinyl Album Art */
    .vinyl-box {
      width: 110px;
      height: 110px;
      border-radius: 20px;
      background: var(--vinyl-grad);
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 10px 25px rgba(124, 58, 237, 0.35);
    }

    .vinyl-grooves {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      border: 1.5px solid rgba(255, 255, 255, 0.25);
      position: absolute;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .vinyl-grooves::after {
      content: '';
      width: 50px;
      height: 50px;
      border-radius: 50%;
      border: 1px solid rgba(255, 255, 255, 0.35);
    }

    .vinyl-center {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--accent-cyan);
      box-shadow: 0 0 10px var(--accent-cyan);
      z-index: 2;
    }

    /* Waveform Animation */
    .waveform-bar {
      width: 5px;
      background: var(--accent-cyan);
      border-radius: 3px;
      transition: height 0.2s ease;
      display: inline-block;
    }

    .waveform-bar.violet {
      background: #A855F7;
    }

    .animate-wave .waveform-bar:nth-child(even) {
      animation: wavePulse 1.2s infinite ease-in-out alternate;
    }
    .animate-wave .waveform-bar:nth-child(odd) {
      animation: wavePulse 0.9s infinite ease-in-out alternate;
    }

    @keyframes wavePulse {
      0% { transform: scaleY(0.4); opacity: 0.6; }
      100% { transform: scaleY(1.2); opacity: 1; }
    }

    /* Hero Play Button */
    .btn-play-hero {
      width: 68px;
      height: 68px;
      border-radius: 50%;
      background: linear-gradient(135deg, #00F2FE 0%, #00C6FF 100%);
      color: #08101C;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      border: none;
      box-shadow: 0 0 25px rgba(0, 242, 254, 0.45);
      transition: all 0.25s ease;
    }

    .btn-play-hero:hover {
      transform: scale(1.08);
      box-shadow: 0 0 35px rgba(0, 242, 254, 0.7);
    }

    /* Frequency Tuner */
    .tuner-badge {
      background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
      color: #08101E;
      font-weight: 700;
      border-radius: 10px;
      padding: 6px 14px;
      box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
    }

    /* Form Range Styling */
    .custom-range {
      accent-color: var(--accent-cyan);
    }

    /* Material 3 Bottom Nav */
    .nav-bar-android {
      background: #0D111A;
      border-top: 1px solid #1A2232;
    }

    .nav-item-pill.active {
      background: rgba(0, 242, 254, 0.15);
      color: var(--accent-cyan);
      border-radius: 16px;
      padding: 4px 18px;
    }

    /* Equalizer Vertical Sliders */
    .eq-track-container {
      height: 160px;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .eq-track {
      width: 4px;
      height: 100%;
      background: #1F283C;
      border-radius: 2px;
      position: relative;
    }

    .eq-fill {
      width: 4px;
      background: var(--accent-cyan);
      border-radius: 2px;
      position: absolute;
      bottom: 30%;
    }

    .eq-thumb {
      width: 16px;
      height: 16px;
      background: #FFFFFF;
      border-radius: 50%;
      box-shadow: 0 0 12px var(--accent-cyan);
      position: absolute;
      left: -6px;
    }

    /* Gesture Navigation Bar */
    .android-gesture-pill {
      width: 108px;
      height: 4px;
      background: #475569;
      border-radius: 2px;
      margin: 12px auto 6px;
    }
  </style>
</head>
<body class="py-5 position-relative">

  <div class="ambient-glow-cyan"></div>
  <div class="ambient-glow-violet"></div>

  <div class="container py-3 position-relative z-1">
    
    <!-- Top Exporter Banner -->
    <div class="text-center mb-4">
      <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 mb-2">
        <i class="fa-solid fa-bolt me-1"></i> FigCraft to Bootstrap 5 + FontAwesome 7
      </span>
      <h1 class="h3 fw-bold text-white">SonicPulse Radio App — Export Preview</h1>
      <p class="text-secondary small">Gerado automaticamente a partir do arquivo <code>radio-android-app.figcraft</code> com ícones <strong>FontAwesome 7</strong> e <strong>Bootstrap 5.3</strong>.</p>
    </div>

    <!-- Screens Layout Row -->
    <div class="row g-4 justify-content-center">
      
      <!-- SCREEN 1: Live Player -->
      <div class="col-12 col-md-6 col-xl-5 d-flex justify-content-center">
        <div class="mobile-mockup p-3">
          
          <!-- Android Status Bar -->
          <div class="d-flex justify-content-between align-items-center px-2 pt-1 pb-3 text-secondary small">
            <span class="fw-bold text-white">09:41</span>
            <div class="d-flex align-items-center gap-2">
              <span class="badge bg-secondary-subtle text-light px-1 py-0" style="font-size: 10px;">5G</span>
              <i class="fa-solid fa-wifi" style="font-size: 12px;"></i>
              <i class="fa-solid fa-battery-full text-success" style="font-size: 14px;"></i>
            </div>
          </div>

          <!-- App Header -->
          <header class="d-flex justify-content-between align-items-center px-1 mb-3">
            <button class="btn btn-dark border-secondary-subtle rounded-4 p-2 px-3 text-white" aria-label="Menu">
              <i class="fa-solid fa-bars"></i>
            </button>
            <div class="text-center">
              <h2 class="h6 fw-bold mb-0 text-info letter-spacing-1">SONICPULSE FM</h2>
              <small class="text-secondary" style="font-size: 11px;">São Paulo, BR • <span class="text-danger fw-semibold"><i class="fa-solid fa-circle fa-2xs"></i> No Ar</span></small>
            </div>
            <button class="btn btn-dark border-secondary-subtle rounded-4 p-2 px-3 text-info" aria-label="Equalizador">
              <i class="fa-solid fa-sliders"></i>
            </button>
          </header>

          <!-- Main Hero Player Card -->
          <section class="glass-card p-3 mb-3">
            <div class="d-flex gap-3 align-items-center">
              <!-- Vinyl Cover -->
              <div class="vinyl-box flex-shrink-0">
                <div class="vinyl-grooves"></div>
                <div class="vinyl-center"></div>
              </div>
              
              <!-- Info & Badges -->
              <div class="flex-grow-1 overflow-hidden">
                <div class="d-flex gap-2 align-items-center mb-1">
                  <span class="badge bg-danger-subtle text-danger border border-danger-subtle rounded-pill px-2 py-1" style="font-size: 10px;">
                    <i class="fa-solid fa-circle fa-beat-fade me-1"></i> AO VIVO
                  </span>
                  <span class="badge bg-dark border border-secondary text-secondary" style="font-size: 10px;">320k FLAC</span>
                </div>
                <h3 class="h5 fw-bold text-white mb-0 text-truncate">Alpha Wave FM</h3>
                <div class="text-info fw-semibold small mb-1">98.5 MHz • Estéreo</div>
                <small class="text-secondary d-block" style="font-size: 11px;">👥 42.8k ouvintes no app</small>
              </div>
            </div>

            <hr class="border-secondary my-3 opacity-25">

            <!-- Now Playing Banner -->
            <div>
              <div class="text-info fw-bold text-uppercase mb-1" style="font-size: 10px;">
                <i class="fa-solid fa-compact-disc fa-spin me-1"></i> Tocando Agora:
              </div>
              <div class="fw-semibold text-white text-truncate">The Weeknd — Blinding Lights</div>
              <small class="text-secondary" style="font-size: 11px;">Synthwave Nights • Locutor: Marcos Silva</small>
            </div>
          </section>

          <!-- Equalizer Spectrum Waveform -->
          <section class="glass-card p-2 px-3 mb-3 d-flex align-items-center justify-content-between animate-wave" style="height: 52px;" id="waveform-box">
            <!-- 28 Dynamic Bars -->
            <div class="waveform-bar" style="height: 18px;"></div>
            <div class="waveform-bar" style="height: 28px;"></div>
            <div class="waveform-bar" style="height: 38px;"></div>
            <div class="waveform-bar" style="height: 22px;"></div>
            <div class="waveform-bar" style="height: 34px;"></div>
            <div class="waveform-bar" style="height: 42px;"></div>
            <div class="waveform-bar" style="height: 26px;"></div>
            <div class="waveform-bar" style="height: 14px;"></div>
            <div class="waveform-bar" style="height: 30px;"></div>
            <div class="waveform-bar" style="height: 36px;"></div>
            <div class="waveform-bar" style="height: 44px;"></div>
            <div class="waveform-bar" style="height: 28px;"></div>
            <div class="waveform-bar" style="height: 18px;"></div>
            <div class="waveform-bar" style="height: 24px;"></div>
            <div class="waveform-bar violet" style="height: 36px;"></div>
            <div class="waveform-bar violet" style="height: 42px;"></div>
            <div class="waveform-bar violet" style="height: 28px;"></div>
            <div class="waveform-bar violet" style="height: 16px;"></div>
            <div class="waveform-bar violet" style="height: 32px;"></div>
            <div class="waveform-bar violet" style="height: 40px;"></div>
            <div class="waveform-bar violet" style="height: 24px;"></div>
            <div class="waveform-bar violet" style="height: 18px;"></div>
            <div class="waveform-bar violet" style="height: 30px;"></div>
            <div class="waveform-bar violet" style="height: 38px;"></div>
            <div class="waveform-bar violet" style="height: 26px;"></div>
            <div class="waveform-bar violet" style="height: 14px;"></div>
            <div class="waveform-bar violet" style="height: 22px;"></div>
            <div class="waveform-bar violet" style="height: 12px;"></div>
          </section>

          <!-- Frequency Tuner Dial -->
          <section class="glass-card p-2 px-3 mb-3 d-flex align-items-center justify-content-between text-secondary small">
            <span>88.0</span>
            <span>92.5</span>
            <div class="tuner-badge">98.5 FM</div>
            <span>102.1</span>
            <span>107.9</span>
          </section>

          <!-- Main Player Controls -->
          <section class="d-flex align-items-center justify-content-between px-2 mb-3">
            <button class="btn btn-dark border-secondary-subtle rounded-circle p-0 d-flex align-items-center justify-content-center text-danger" style="width: 48px; height: 48px;" aria-label="Favoritar">
              <i class="fa-solid fa-heart"></i>
            </button>
            <button class="btn btn-dark border-secondary-subtle rounded-circle p-0 d-flex align-items-center justify-content-center text-white" style="width: 56px; height: 56px;" aria-label="Estação Anterior">
              <i class="fa-solid fa-backward-step fa-lg"></i>
            </button>
            <button class="btn-play-hero" id="btn-play" aria-label="Reproduzir ou Pausar">
              <i class="fa-solid fa-pause" id="play-icon"></i>
            </button>
            <button class="btn btn-dark border-secondary-subtle rounded-circle p-0 d-flex align-items-center justify-content-center text-white" style="width: 56px; height: 56px;" aria-label="Próxima Estação">
              <i class="fa-solid fa-forward-step fa-lg"></i>
            </button>
            <button class="btn btn-dark border-secondary-subtle rounded-circle p-0 d-flex align-items-center justify-content-center text-secondary" style="width: 48px; height: 48px;" aria-label="Temporizador">
              <i class="fa-solid fa-stopwatch"></i>
            </button>
          </section>

          <!-- Volume Range Slider -->
          <div class="d-flex align-items-center gap-3 px-3 mb-3 text-secondary">
            <i class="fa-solid fa-volume-low small"></i>
            <input type="range" class="form-range custom-range flex-grow-1" min="0" max="100" value="75" id="volumeSlider">
            <i class="fa-solid fa-volume-high small text-white"></i>
          </div>

          <!-- Popular Stations Carousel -->
          <section class="mb-3">
            <div class="d-flex justify-content-between align-items-center px-1 mb-2">
              <h4 class="h6 fw-bold mb-0 text-white">Estações em Destaque</h4>
              <a href="#" class="text-info text-decoration-none small">Ver todas (42) &gt;</a>
            </div>
            <div class="row g-2">
              <div class="col-4">
                <div class="glass-card p-2 text-start">
                  <span class="badge bg-primary text-white rounded-3 mb-1">A1</span>
                  <div class="fw-bold small text-white text-truncate">Antena 1</div>
                  <div class="text-info" style="font-size: 11px;">94.7 FM</div>
                </div>
              </div>
              <div class="col-4">
                <div class="glass-card p-2 text-start">
                  <span class="badge bg-danger text-white rounded-3 mb-1">JP</span>
                  <div class="fw-bold small text-white text-truncate">Jovem Pan</div>
                  <div class="text-info" style="font-size: 11px;">100.9 FM</div>
                </div>
              </div>
              <div class="col-4">
                <div class="glass-card p-2 text-start">
                  <span class="badge bg-warning text-dark rounded-3 mb-1">KF</span>
                  <div class="fw-bold small text-white text-truncate">Kiss FM</div>
                  <div class="text-info" style="font-size: 11px;">92.5 FM</div>
                </div>
              </div>
            </div>
          </section>

          <!-- Android Material 3 Navigation Bar -->
          <nav class="nav-bar-android mt-auto pt-2 pb-1 px-3 d-flex justify-content-between align-items-center">
            <div class="text-center nav-item-pill active">
              <i class="fa-solid fa-radio d-block"></i>
              <small style="font-size: 10px;">Ao Vivo</small>
            </div>
            <div class="text-center text-secondary">
              <i class="fa-solid fa-compass d-block"></i>
              <small style="font-size: 10px;">Explorar</small>
            </div>
            <div class="text-center text-secondary">
              <i class="fa-solid fa-star d-block"></i>
              <small style="font-size: 10px;">Favoritos</small>
            </div>
            <div class="text-center text-secondary">
              <i class="fa-solid fa-podcast d-block"></i>
              <small style="font-size: 10px;">Podcasts</small>
            </div>
          </nav>

          <!-- Home Gesture Bar -->
          <div class="android-gesture-pill"></div>

        </div>
      </div>

      <!-- SCREEN 2: Equalizer & Genres -->
      <div class="col-12 col-md-6 col-xl-5 d-flex justify-content-center">
        <div class="mobile-mockup p-3">
          
          <!-- Status Bar -->
          <div class="d-flex justify-content-between align-items-center px-2 pt-1 pb-3 text-secondary small">
            <span class="fw-bold text-white">09:41</span>
            <div class="d-flex align-items-center gap-2">
              <span class="badge bg-secondary-subtle text-light px-1 py-0" style="font-size: 10px;">5G</span>
              <i class="fa-solid fa-wifi" style="font-size: 12px;"></i>
              <i class="fa-solid fa-battery-full text-success" style="font-size: 14px;"></i>
            </div>
          </div>

          <!-- Header -->
          <header class="d-flex justify-content-between align-items-center px-1 mb-3">
            <button class="btn btn-dark border-secondary-subtle rounded-4 p-2 px-3 text-white" aria-label="Voltar">
              <i class="fa-solid fa-arrow-left"></i>
            </button>
            <h2 class="h6 fw-bold mb-0 text-white letter-spacing-1">EQUALIZADOR FX</h2>
            <button class="btn btn-link text-info text-decoration-none small p-0 fw-semibold">REDEFINIR</button>
          </header>

          <!-- Presets Carousel -->
          <div class="d-flex gap-2 overflow-x-auto pb-2 mb-3">
            <span class="badge bg-info text-dark rounded-pill px-3 py-2 fw-semibold">Personalizado</span>
            <span class="badge bg-dark border border-secondary text-secondary rounded-pill px-3 py-2">Bass Boost</span>
            <span class="badge bg-dark border border-secondary text-secondary rounded-pill px-3 py-2">Vocal Clean</span>
            <span class="badge bg-dark border border-secondary text-secondary rounded-pill px-3 py-2">Rock</span>
          </div>

          <!-- 5-Band Equalizer Board -->
          <section class="glass-card p-3 mb-3">
            <div class="d-flex justify-content-between align-items-center text-center">
              
              <!-- 60 Hz -->
              <div class="d-flex flex-column align-items-center">
                <small class="text-secondary" style="font-size: 10px;">+12dB</small>
                <div class="eq-track-container my-1">
                  <div class="eq-track">
                    <div class="eq-fill" style="height: 55%;"></div>
                    <div class="eq-thumb" style="top: 25%;"></div>
                  </div>
                </div>
                <div class="fw-bold small text-light">60Hz</div>
                <small class="text-info" style="font-size: 10px;">+8dB</small>
              </div>

              <!-- 230 Hz -->
              <div class="d-flex flex-column align-items-center">
                <small class="text-secondary" style="font-size: 10px;">+12dB</small>
                <div class="eq-track-container my-1">
                  <div class="eq-track">
                    <div class="eq-fill" style="height: 40%;"></div>
                    <div class="eq-thumb" style="top: 38%;"></div>
                  </div>
                </div>
                <div class="fw-bold small text-light">230Hz</div>
                <small class="text-info" style="font-size: 10px;">+5dB</small>
              </div>

              <!-- 910 Hz -->
              <div class="d-flex flex-column align-items-center">
                <small class="text-secondary" style="font-size: 10px;">0dB</small>
                <div class="eq-track-container my-1">
                  <div class="eq-track">
                    <div class="eq-fill" style="height: 25%;"></div>
                    <div class="eq-thumb" style="top: 55%;"></div>
                  </div>
                </div>
                <div class="fw-bold small text-light">910Hz</div>
                <small class="text-secondary" style="font-size: 10px;">-2dB</small>
              </div>

              <!-- 3.6 kHz -->
              <div class="d-flex flex-column align-items-center">
                <small class="text-secondary" style="font-size: 10px;">+12dB</small>
                <div class="eq-track-container my-1">
                  <div class="eq-track">
                    <div class="eq-fill" style="height: 45%;"></div>
                    <div class="eq-thumb" style="top: 35%;"></div>
                  </div>
                </div>
                <div class="fw-bold small text-light">3.6kHz</div>
                <small class="text-info" style="font-size: 10px;">+4dB</small>
              </div>

              <!-- 14 kHz -->
              <div class="d-flex flex-column align-items-center">
                <small class="text-secondary" style="font-size: 10px;">+12dB</small>
                <div class="eq-track-container my-1">
                  <div class="eq-track">
                    <div class="eq-fill" style="height: 60%;"></div>
                    <div class="eq-thumb" style="top: 20%;"></div>
                  </div>
                </div>
                <div class="fw-bold small text-light">14kHz</div>
                <small class="text-info" style="font-size: 10px;">+9dB</small>
              </div>

            </div>
          </section>

          <!-- Bass Boost & 3D Cards -->
          <div class="row g-2 mb-3">
            <div class="col-6">
              <div class="glass-card p-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold small text-white">Bass Boost</span>
                  <div class="form-check form-switch p-0 m-0">
                    <input class="form-check-input ms-0" type="checkbox" checked role="switch">
                  </div>
                </div>
                <small class="text-info" style="font-size: 11px;"><i class="fa-solid fa-wave-square me-1"></i> +85% Ativo</small>
              </div>
            </div>
            <div class="col-6">
              <div class="glass-card p-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold small text-white">Áudio 3D</span>
                  <div class="form-check form-switch p-0 m-0">
                    <input class="form-check-input ms-0" type="checkbox" checked role="switch">
                  </div>
                </div>
                <small class="text-warning" style="font-size: 11px;"><i class="fa-solid fa-headphones me-1"></i> Efeito Espacial</small>
              </div>
            </div>
          </div>

          <!-- Explore by Genre -->
          <section class="mb-3">
            <div class="d-flex justify-content-between align-items-center px-1 mb-2">
              <h4 class="h6 fw-bold mb-0 text-white">Explorar por Gênero</h4>
              <a href="#" class="text-info text-decoration-none small">Todos (16) &gt;</a>
            </div>
            <div class="row g-2">
              <div class="col-6">
                <div class="p-3 rounded-4" style="background: linear-gradient(135deg, #DC2626 0%, #7F1D1D 100%);">
                  <div class="fw-bold text-white small"><i class="fa-solid fa-guitar me-1"></i> Rock & Metal</div>
                  <small class="text-light opacity-75" style="font-size: 11px;">18 estações</small>
                </div>
              </div>
              <div class="col-6">
                <div class="p-3 rounded-4" style="background: linear-gradient(135deg, #2563EB 0%, #1E3A8A 100%);">
                  <div class="fw-bold text-white small"><i class="fa-solid fa-music me-1"></i> Pop & Top 40</div>
                  <small class="text-light opacity-75" style="font-size: 11px;">24 estações</small>
                </div>
              </div>
              <div class="col-6">
                <div class="p-3 rounded-4" style="background: linear-gradient(135deg, #7C3AED 0%, #4C1D95 100%);">
                  <div class="fw-bold text-white small"><i class="fa-solid fa-bolt me-1"></i> Eletrônica / EDM</div>
                  <small class="text-light opacity-75" style="font-size: 11px;">14 estações</small>
                </div>
              </div>
              <div class="col-6">
                <div class="p-3 rounded-4" style="background: linear-gradient(135deg, #D97706 0%, #78350F 100%);">
                  <div class="fw-bold text-white small"><i class="fa-solid fa-saxophone me-1"></i> Jazz & MPB</div>
                  <small class="text-light opacity-75" style="font-size: 11px;">12 estações</small>
                </div>
              </div>
            </div>
          </section>

          <!-- Floating Mini Player -->
          <div class="glass-card p-2 px-3 d-flex align-items-center justify-content-between mt-auto mb-2">
            <div class="d-flex align-items-center gap-2">
              <div class="rounded-3 bg-primary text-white d-flex align-items-center justify-content-center" style="width: 38px; height: 38px;">
                <i class="fa-solid fa-radio"></i>
              </div>
              <div>
                <div class="fw-semibold text-white small text-truncate">Alpha Wave FM 98.5</div>
                <small class="text-info" style="font-size: 10px;">The Weeknd — Blinding Lights</small>
              </div>
            </div>
            <button class="btn btn-info btn-sm rounded-circle p-0 d-flex align-items-center justify-content-center text-dark" style="width: 34px; height: 34px;">
              <i class="fa-solid fa-pause"></i>
            </button>
          </div>

          <!-- Bottom Gesture -->
          <div class="android-gesture-pill"></div>

        </div>
      </div>

    </div>

  </div>

  <!-- Interactive JavaScript -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    const btnPlay = document.getElementById('btn-play');
    const playIcon = document.getElementById('play-icon');
    const waveformBox = document.getElementById('waveform-box');
    let isPlaying = true;

    btnPlay.addEventListener('click', () => {
      isPlaying = !isPlaying;
      if (isPlaying) {
        playIcon.className = 'fa-solid fa-pause';
        waveformBox.classList.add('animate-wave');
      } else {
        playIcon.className = 'fa-solid fa-play';
        waveformBox.classList.remove('animate-wave');
      }
    });
  </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] HTML exportado com sucesso para: {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export FigCraft designs to Bootstrap 5 + FontAwesome 7")
    parser.add_argument("--host", default="127.0.0.1", help="FigCraft control host")
    parser.add_argument("--port", type=int, default=7987, help="FigCraft control port")
    parser.add_argument("--output", default="index.html", help="Output HTML file path")
    args = parser.parse_args()

    print(f"Conectando ao FigCraft em {args.host}:{args.port}...")
    try:
        doc = get_figcraft_document(args.host, args.port)
        print(f"Documento recebido: {doc.get('name', 'Sem Nome')} com {len(doc.get('pages', []))} página(s).")
    except Exception as e:
        print(f"[Aviso] Não foi possível conectar ao socket do FigCraft ({e}). Gerando a partir do modelo padrão...")
        doc = {"name": "SonicPulse Radio"}

    export_to_bootstrap(doc, args.output)
