/**
 * Parmair MAC Home Assistant Lovelace Custom Card
 * Clean Scandinavian HVAC schematic with real counterflow heat recovery airflow,
 * live channel temperatures, electric/water post-heater power, and mode controls.
 * Fully responsive: embedded inline SVG preserves 100% pixel-perfect coordinates across all screen sizes.
 */

class ParmairMacCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this.content) {
      this.initCard();
    }
    this.updateCard();
  }

  setConfig(config) {
    this._config = config;
    if (!this.content) {
      this.initCard();
    }
  }

  connectedCallback() {
    if (!this.content) {
      this.initCard();
    }
    if (this._hass) {
      this.updateCard();
    }
  }

  getCardSize() {
    return 6;
  }

  static async getConfigElement() {
    return document.createElement("parmair-mac-card-editor");
  }

  static getStubConfig() {
    return {
      type: "custom:parmair-mac-card",
      name: "Parmair MAC",
    };
  }

  initCard() {
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: var(--ha-card-font-family, inherit);
        }
        ha-card {
          background: var(--ha-card-background, #1e242c);
          color: var(--primary-text-color, #ffffff);
          border-radius: var(--ha-card-border-radius, 16px);
          box-shadow: var(--ha-card-box-shadow, none);
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, #334155);
          overflow: hidden;
          padding: 16px;
          position: relative;
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 12px;
        }
        .brand {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 19px;
          font-weight: 700;
          letter-spacing: 0.5px;
          color: #ffffff;
        }
        .brand ha-icon {
          color: #009fe3;
          --mdc-icon-size: 24px;
        }
        .header-chips {
          display: flex;
          gap: 8px;
          align-items: center;
          flex-wrap: wrap;
        }
        .chip {
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 14.5px;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 5px;
        }
        .chip-humidity {
          background: rgba(6, 182, 212, 0.16);
          border: 1.5px solid #06b6d4;
          color: #22d3ee;
        }
        .chip-co2 {
          background: rgba(16, 185, 129, 0.16);
          border: 1.5px solid #10b981;
          color: #34d399;
        }
        .status-pill {
          background: #0066b3;
          border: 1.5px solid #009fe3;
          color: #ffffff;
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 14.5px;
          font-weight: 700;
        }
        .speed-badge {
          background: rgba(51, 65, 85, 0.5);
          border: 1.5px solid #64748b;
          color: #cbd5e1;
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 14.5px;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 5px;
        }
        .clickable-badge {
          cursor: pointer;
          transition: opacity 0.15s ease, filter 0.15s ease;
        }
        .clickable-badge:hover {
          opacity: 0.85;
          filter: brightness(1.2);
        }
        .clickable-metric {
          cursor: pointer;
          transition: background 0.15s ease, border-color 0.15s ease;
        }
        .clickable-metric:hover {
          background: rgba(30, 41, 59, 0.85);
          border-color: #0284c7;
        }

        /* SVG Schematic Container */
        .schematic-box {
          width: 100%;
          border-radius: 12px;
          overflow: hidden;
          margin-bottom: 12px;
          background: #131922;
        }
        .schematic-svg {
          display: block;
          width: 100%;
          height: auto;
        }

        /* Metrics row */
        .metrics-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
          gap: 10px;
          margin-bottom: 12px;
        }
        .metric-item {
          display: flex;
          align-items: center;
          gap: 10px;
          background: rgba(15, 23, 42, 0.6);
          border-radius: 10px;
          padding: 11px 16px;
          border: 1px solid #334155;
          font-size: 15px;
          overflow: hidden;
        }
        .metric-item ha-icon {
          --mdc-icon-size: 20px;
        }
        .metric-label {
          color: #94a3b8;
          font-size: 14px;
          font-weight: 500;
          white-space: nowrap;
        }
        .metric-value {
          font-weight: 700;
          font-size: 16px;
          color: #f1f5f9;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        /* Mode Selectors */
        .mode-grid {
          display: grid;
          grid-template-columns: repeat(5, minmax(0, 1fr));
          gap: 8px;
        }
        .mode-btn {
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid #334155;
          border-radius: 10px;
          padding: 10px 4px;
          color: #94a3b8;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 5px;
          cursor: pointer;
          transition: all 0.2s ease;
          overflow: hidden;
        }
        .mode-btn ha-icon {
          --mdc-icon-size: 22px;
        }
        .mode-btn:hover {
          background: rgba(51, 65, 85, 0.7);
          color: #f1f5f9;
        }
        .mode-btn.active {
          background: #0066b3;
          border-color: #009fe3;
          color: #ffffff;
          box-shadow: 0 0 10px rgba(0, 159, 227, 0.3);
        }
        .mode-btn span {
          font-size: 13.5px;
          font-weight: 600;
          white-space: nowrap;
          text-overflow: ellipsis;
          overflow: hidden;
        }
        @media (max-width: 450px) {
          .header-chips {
            gap: 4px;
          }
          .chip, .speed-badge, .status-pill {
            font-size: 12.5px;
            padding: 4px 10px;
          }
          .metric-item {
            font-size: 13.5px;
            padding: 8px 10px;
          }
          .mode-btn span {
            font-size: 11px;
          }
          .mode-btn ha-icon {
            --mdc-icon-size: 19px;
          }
        }
      </style>

      <ha-card>
        <div class="header">
          <div class="brand">
            <ha-icon icon="mdi:fan"></ha-icon>
            <span id="title">PARMAIR MAC</span>
          </div>
          <div class="header-chips">
            <div id="chip_humidity" class="chip chip-humidity clickable-badge" title="Klikkaa avataksesi kosteusanturin tiedot">💧 -- %</div>
            <div id="chip_co2" class="chip chip-co2 clickable-badge" title="Klikkaa avataksesi CO2-anturin tiedot" style="display: none;">🌱 -- ppm</div>
            <div id="speed" class="speed-badge clickable-badge" title="Klikkaa avataksesi anturitiedot"><ha-icon icon="mdi:fan"></ha-icon> Nopeus --</div>
            <div id="state_pill" class="status-pill clickable-badge" title="Klikkaa avataksesi tilatiedot">--</div>
          </div>
        </div>

        <div class="schematic-box">
          <svg class="schematic-svg" viewBox="25 15 750 438" preserveAspectRatio="xMidYMid meet">
            <defs>
              <linearGradient id="cardBgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#18202c" />
                <stop offset="100%" stop-color="#10151e" />
              </linearGradient>

              <!-- Flow Gradients (Finnish HVAC / LVI Standard Colors) -->
              <!-- 1) Ulkoilma / Fresh Air: Finnish LVI Green -->
              <linearGradient id="freshAirGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#10b981" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#059669" stop-opacity="0.9" />
              </linearGradient>
              <!-- 2) Poistoilma / Exhaust Air: Finnish LVI Yellow / Amber -->
              <linearGradient id="exhaustAirGrad" x1="100%" y1="0%" x2="0%" y2="0%">
                <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#d97706" stop-opacity="0.9" />
              </linearGradient>
              <!-- 3) Jäteilma / Waste Air: Finnish LVI Blue / Cool Slate -->
              <linearGradient id="wasteAirGrad" x1="100%" y1="0%" x2="0%" y2="0%">
                <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#2563eb" stop-opacity="0.9" />
              </linearGradient>
              <!-- 4) Tuloilma / Supply Air: Finnish LVI Warm Red / Coral -->
              <linearGradient id="supplyAirGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#ef4444" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#dc2626" stop-opacity="0.9" />
              </linearGradient>

              <linearGradient id="coreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#1e293b" />
                <stop offset="50%" stop-color="#0f172a" />
                <stop offset="100%" stop-color="#1e293b" />
              </linearGradient>

              <!-- Crossing internal flow streams through LTO core -->
              <!-- Fresh (Top-Left) -> Supply (Bottom-Right) -->
              <linearGradient id="freshCoreFlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#10b981" />
                <stop offset="50%" stop-color="#fbbf24" />
                <stop offset="100%" stop-color="#ef4444" />
              </linearGradient>
              <!-- Exhaust (Top-Right) -> Waste (Bottom-Left) -->
              <linearGradient id="exhaustCoreFlow" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#fbbf24" />
                <stop offset="50%" stop-color="#60a5fa" />
                <stop offset="100%" stop-color="#3b82f6" />
              </linearGradient>

              <!-- Glow filter for post-heater and direction arrows -->
              <filter id="heaterGlow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="3.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="arrowGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="badgeShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="3.5" flood-color="#000000" flood-opacity="0.7" />
              </filter>
            </defs>

            <!-- Machine Chassis -->
            <rect x="200" y="52" width="400" height="366" rx="14" fill="#0b0f14" stroke="#475569" stroke-width="2.5" />
            <rect x="214" y="66" width="372" height="338" rx="10" fill="#131922" stroke="#1e293b" stroke-width="1.5" />

            <!-- Internal flow curves -->
            <path d="M 200 120 C 270 120, 320 150, 400 235 C 470 300, 520 348, 600 348"
                  stroke="url(#freshCoreFlow)" stroke-width="5.5" stroke-dasharray="8,5" fill="none" opacity="0.85" />
            <path d="M 600 120 C 530 120, 480 150, 400 235 C 330 300, 280 348, 200 348"
                  stroke="url(#exhaustCoreFlow)" stroke-width="5.5" stroke-dasharray="8,5" fill="none" opacity="0.85" />

            <!-- CENTER: Heat Recovery Exchanger Core (Diamond) with Unified Metrics Badge -->
            <g transform="translate(400, 235)" id="badge_lto_center" class="clickable-badge">
              <polygon points="0,-106 106,0 0,106 -106,0" fill="#0f172a" stroke="#009fe3" stroke-width="2" />
              <!-- Heat transfer lamellas -->
              <line x1="-62" y1="-44" x2="62" y2="44" stroke="#334155" stroke-width="1.5" />
              <line x1="-44" y1="-62" x2="44" y2="62" stroke="#334155" stroke-width="1.5" />
              <line x1="-24" y1="-82" x2="82" y2="24" stroke="#334155" stroke-width="1.5" />
              <line x1="-82" y1="-24" x2="24" y2="82" stroke="#334155" stroke-width="1.5" />

              <!-- Unified Center Badge: Width 176px, Height 92px -->
              <rect x="-88" y="-46" width="176" height="92" rx="12" fill="#090d12" stroke="#009fe3" stroke-width="1.8" filter="url(#badgeShadow)" />
              <text x="0" y="-18" fill="#ffffff" font-size="16.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_recovery_eff">LTO: -- %</text>
              <text x="0" y="7" text-anchor="middle" font-family="sans-serif" id="badge_lto_temp">
                <tspan fill="#94a3b8" font-size="13.5" font-weight="600">Lämpötila: </tspan>
                <tspan fill="#34d399" font-size="15.5" font-weight="bold" id="svg_lto_temp">-- °C</tspan>
              </text>
              <text x="0" y="30" fill="#38bdf8" font-size="14.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_recovery_power">Talteenotto: -- W</text>
            </g>

            <!-- ==================== 1) TOP-LEFT: ULKOILMA ==================== -->
            <path d="M 35 120 L 200 120" stroke="#10b981" stroke-width="48" stroke-linecap="round" fill="none" opacity="0.16" />
            <path d="M 35 120 L 200 120" stroke="url(#freshAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- 3 Symmetrical Chevrons >>> ending BEFORE the badge with 16px gap (tips at 66, 80, 94) -->
            <path d="M 54 108 L 66 120 L 54 132" fill="none" stroke="#34d399" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 68 108 L 80 120 L 68 132" fill="none" stroke="#34d399" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 82 108 L 94 120 L 82 132" fill="none" stroke="#ffffff" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <!-- Stacked 2-line Badge: Width 90px, spans X=110..200 -->
            <g transform="translate(155, 120)" id="badge_fresh" class="clickable-badge">
              <rect x="-45" y="-22" width="90" height="44" rx="9" fill="rgba(11, 15, 20, 0.96)" stroke="#10b981" stroke-width="1.8" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="13" font-weight="600" font-family="sans-serif" text-anchor="middle">Ulkoilma</text>
              <text x="0" y="15" fill="#34d399" font-size="16.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_fresh">-- °C</text>
            </g>
            <!-- G4 Coarse Filter at Ulkoilma Inlet -->
            <g transform="translate(230, 93)">
              <rect x="0" y="0" width="12" height="54" rx="2" fill="#059669" opacity="0.85" />
              <line x1="2" y1="5" x2="10" y2="49" stroke="#34d399" stroke-width="1.5" />
              <line x1="10" y1="5" x2="2" y2="49" stroke="#34d399" stroke-width="1.5" />
              <text x="6" y="70" fill="#94a3b8" font-size="13" font-weight="bold" font-family="sans-serif" text-anchor="middle">G4</text>
            </g>

            <!-- ==================== 2) TOP-RIGHT: POISTOILMA ==================== -->
            <path d="M 765 120 L 600 120" stroke="#fbbf24" stroke-width="48" stroke-linecap="round" fill="none" opacity="0.16" />
            <path d="M 765 120 L 600 120" stroke="url(#exhaustAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- 3 Symmetrical Chevrons <<< ending BEFORE the badge with 16px gap (tips at 734, 720, 706) -->
            <path d="M 746 108 L 734 120 L 746 132" fill="none" stroke="#fbbf24" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 732 108 L 720 120 L 732 132" fill="none" stroke="#fbbf24" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 718 108 L 706 120 L 718 132" fill="none" stroke="#ffffff" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <!-- Stacked 2-line Badge: Width 90px, spans X=600..690 -->
            <g transform="translate(645, 120)" id="badge_exhaust" class="clickable-badge">
              <rect x="-45" y="-22" width="90" height="44" rx="9" fill="rgba(11, 15, 20, 0.96)" stroke="#fbbf24" stroke-width="1.8" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="13" font-weight="600" font-family="sans-serif" text-anchor="middle">Poistoilma</text>
              <text x="0" y="15" fill="#fbbf24" font-size="16.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_exhaust">-- °C</text>
            </g>
            <!-- G4 Coarse Filter at Poistoilma Inlet -->
            <g transform="translate(558, 93)">
              <rect x="0" y="0" width="12" height="54" rx="2" fill="#d97706" opacity="0.85" />
              <line x1="2" y1="5" x2="10" y2="49" stroke="#fbbf24" stroke-width="1.5" />
              <line x1="10" y1="5" x2="2" y2="49" stroke="#fbbf24" stroke-width="1.5" />
              <text x="6" y="70" fill="#94a3b8" font-size="13" font-weight="bold" font-family="sans-serif" text-anchor="middle">G4</text>
            </g>

            <!-- ==================== 3) BOTTOM-LEFT: JÄTEILMA ==================== -->
            <!-- Poistopuhallin -->
            <g transform="translate(315, 348)" id="badge_exhaust_fan" class="clickable-badge" title="Klikkaa avataksesi poistopuhaltimen tiedot">
              <circle cx="0" cy="0" r="23" fill="#1e293b" stroke="#3b82f6" stroke-width="1.8" />
              <circle cx="0" cy="0" r="5" fill="#60a5fa" />
              <path d="M 0,-17 Q 5,-7 0,0 Q -5,-7 0,-17" fill="#60a5fa" opacity="0.8" />
              <path d="M 17,0 Q 7,5 0,0 Q 7,-5 17,0" fill="#60a5fa" opacity="0.8" />
              <path d="M 0,17 Q -5,7 0,0 Q 5,7 0,17" fill="#60a5fa" opacity="0.8" />
              <path d="M -17,0 Q -7,-5 0,0 Q -7,5 -17,0" fill="#60a5fa" opacity="0.8" />
              <text x="0" y="32" fill="#94a3b8" font-size="12.5" font-weight="600" font-family="sans-serif" text-anchor="middle">Poistopuhallin</text>
              <text x="0" y="50" fill="#60a5fa" font-size="15.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_exhaust_fan">-- %</text>
            </g>
            <path d="M 200 348 L 35 348" stroke="#3b82f6" stroke-width="48" stroke-linecap="round" fill="none" opacity="0.16" />
            <path d="M 200 348 L 35 348" stroke="url(#wasteAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- Stacked 2-line Badge: Width 90px, spans X=110..200 -->
            <g transform="translate(155, 348)" id="badge_waste" class="clickable-badge">
              <rect x="-45" y="-22" width="90" height="44" rx="9" fill="rgba(11, 15, 20, 0.96)" stroke="#3b82f6" stroke-width="1.8" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="13" font-weight="600" font-family="sans-serif" text-anchor="middle">Jäteilma</text>
              <text x="0" y="15" fill="#60a5fa" font-size="16.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_waste">-- °C</text>
            </g>
            <!-- 3 Symmetrical Chevrons <<< starting AFTER the badge with 16px gap (tips at 82, 68, 54) -->
            <path d="M 94 336 L 82 348 L 94 360" fill="none" stroke="#60a5fa" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 80 336 L 68 348 L 80 360" fill="none" stroke="#60a5fa" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 66 336 L 54 348 L 66 360" fill="none" stroke="#ffffff" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />

            <!-- ==================== 4) BOTTOM-RIGHT: TULOILMA ==================== -->
            <!-- Tulopuhallin -->
            <g transform="translate(485, 348)" id="badge_supply_fan" class="clickable-badge" title="Klikkaa avataksesi tulopuhaltimen tiedot">
              <circle cx="0" cy="0" r="23" fill="#1e293b" stroke="#ef4444" stroke-width="1.8" />
              <circle cx="0" cy="0" r="5" fill="#f87171" />
              <path d="M 0,-17 Q 5,-7 0,0 Q -5,-7 0,-17" fill="#f87171" opacity="0.8" />
              <path d="M 17,0 Q 7,5 0,0 Q 7,-5 17,0" fill="#f87171" opacity="0.8" />
              <path d="M 0,17 Q -5,7 0,0 Q 5,7 0,17" fill="#f87171" opacity="0.8" />
              <path d="M -17,0 Q -7,-5 0,0 Q -7,5 -17,0" fill="#f87171" opacity="0.8" />
              <text x="0" y="32" fill="#94a3b8" font-size="12.5" font-weight="600" font-family="sans-serif" text-anchor="middle">Tulopuhallin</text>
              <text x="0" y="50" fill="#f87171" font-size="15.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_supply_fan">-- %</text>
            </g>

            <!-- F7 (ePM1) Hienosuodatin tuloilmalle puhaltimen ja lämmittimen välissä -->
            <g transform="translate(530, 321)">
              <rect x="0" y="0" width="12" height="54" rx="2" fill="#0284c7" opacity="0.85" />
              <line x1="2" y1="5" x2="10" y2="49" stroke="#38bdf8" stroke-width="1.5" />
              <line x1="10" y1="5" x2="2" y2="49" stroke="#38bdf8" stroke-width="1.5" />
              <text x="6" y="70" fill="#38bdf8" font-size="13" font-weight="bold" font-family="sans-serif" text-anchor="middle">F7</text>
            </g>

            <!-- Kaksirivinen Lämmitin-laatikko: Täydellinen sovitus, ei koskaan leikkaannu! -->
            <g transform="translate(566, 276)" id="badge_heater" class="clickable-badge">
              <rect x="-38" y="-19" width="76" height="38" rx="8" fill="rgba(24, 21, 18, 0.96)" stroke="#ea580c" stroke-width="1.6" id="svg_heater_badge" filter="url(#badgeShadow)" />
              <text x="0" y="-3" fill="#fb923c" font-size="12" font-weight="600" font-family="sans-serif" text-anchor="middle">Lämmitin</text>
              <text x="0" y="13" fill="#f97316" font-size="14.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_heater_power">0 W</text>
            </g>

            <!-- Post-Heater Coil Element -->
            <g transform="translate(568, 348)" id="heater_coil">
              <rect x="-9" y="-22" width="18" height="44" rx="4" fill="#181512" stroke="#ea580c" stroke-width="1.5" />
              <path d="M -4,-15 L 4,-9 L -4,-3 L 4,3 L -4,9 L 4,15" fill="none" stroke="#ea580c" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" id="heater_path" />
            </g>

            <path d="M 600 348 L 765 348" stroke="#ef4444" stroke-width="48" stroke-linecap="round" fill="none" opacity="0.16" />
            <path d="M 600 348 L 765 348" stroke="url(#supplyAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- Stacked 2-line Badge: Width 90px, spans X=600..690 -->
            <g transform="translate(645, 348)" id="badge_supply" class="clickable-badge">
              <rect x="-45" y="-22" width="90" height="44" rx="9" fill="rgba(11, 15, 20, 0.96)" stroke="#ef4444" stroke-width="1.8" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="13" font-weight="600" font-family="sans-serif" text-anchor="middle">Tuloilma</text>
              <text x="0" y="15" fill="#f87171" font-size="16.5" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_supply">-- °C</text>
            </g>
            <!-- 3 Symmetrical Chevrons >>> starting AFTER the badge with 16px gap (tips at 718, 732, 746) -->
            <path d="M 706 336 L 718 348 L 706 360" fill="none" stroke="#f87171" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 720 336 L 732 348 L 720 360" fill="none" stroke="#f87171" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
            <path d="M 734 336 L 746 348 L 734 360" fill="none" stroke="#ffffff" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" />
          </svg>
        </div>

        <div class="metrics-row">
          <div class="metric-item clickable-metric" id="metric_power">
            <ha-icon icon="mdi:flash" style="color: #38bdf8;"></ha-icon>
            <span class="metric-label">Ottoteho:</span>
            <span id="total_power" class="metric-value">-- W</span>
          </div>
          <div class="metric-item clickable-metric" id="metric_energy">
            <ha-icon icon="mdi:counter" style="color: #fbbf24;"></ha-icon>
            <span class="metric-label">Energia:</span>
            <span id="total_energy" class="metric-value">-- kWh</span>
          </div>
          <div class="metric-item clickable-metric" id="metric_filter">
            <ha-icon icon="mdi:air-filter" style="color: #4ade80;"></ha-icon>
            <span class="metric-label">Suodatin:</span>
            <span id="filter_days" class="metric-value">OK</span>
          </div>
        </div>

        <div class="mode-grid">
          <button class="mode-btn" data-mode="Away">
            <ha-icon icon="mdi:home-export-outline"></ha-icon>
            <span>Poissa</span>
          </button>
          <button class="mode-btn" data-mode="Home">
            <ha-icon icon="mdi:home"></ha-icon>
            <span>Kotona</span>
          </button>
          <button class="mode-btn" data-mode="Boost">
            <ha-icon icon="mdi:fan-chevron-up"></ha-icon>
            <span>Tehostus</span>
          </button>
          <button class="mode-btn" data-mode="Sauna">
            <ha-icon icon="mdi:radiator"></ha-icon>
            <span>Sauna</span>
          </button>
          <button class="mode-btn" data-mode="Fireplace">
            <ha-icon icon="mdi:fire"></ha-icon>
            <span>Takka</span>
          </button>
        </div>
      </ha-card>
    `;

    // Add click listeners to mode buttons
    const buttons = this.shadowRoot.querySelectorAll(".mode-btn");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.getAttribute("data-mode");
        this._setMode(mode);
      });
    });

    // Add click listeners to badges & metrics for more-info popup
    this._attachMoreInfo("badge_fresh", ["fresh_air_temperature", "fresh_air_temp"]);
    this._attachMoreInfo("badge_exhaust", ["exhaust_air_temperature", "exhaust_temp"]);
    this._attachMoreInfo("badge_lto_temp", [
      "supply_air_temperature_after_recovery",
      "supply_after_recovery_temp",
    ]);
    this._attachMoreInfo("badge_supply", ["supply_air_temperature", "supply_temp"]);
    this._attachMoreInfo("badge_waste", ["waste_air_temperature", "waste_temp"]);
    this._attachMoreInfo("badge_lto_center", [
      "heat_recovery_efficiency",
      "heat_recovery_power",
    ]);
    this._attachMoreInfo("badge_heater", ["post_heater_power", "heater_power"]);
    this._attachMoreInfo("metric_power", ["total_power"]);
    this._attachMoreInfo("metric_energy", ["total_energy"]);
    this._attachMoreInfo("metric_filter", ["filter_status", "filter_state"]);
    this._attachMoreInfo("state_pill", ["control_state", "operational_mode", "state"]);
    this._attachMoreInfo("speed", ["current_speed", "actual_speed", "actual_fan_speed"]);
    this._attachMoreInfo("badge_supply_fan", ["supply_fan_speed"]);
    this._attachMoreInfo("badge_exhaust_fan", ["exhaust_fan_speed"]);
    this._attachMoreInfo("chip_humidity", ["humidity", "exhaust_humidity"]);
    this._attachMoreInfo("chip_co2", ["co2_exhaust", "co2_exhaust_air", "co2"]);

    this.content = true;
  }

  _attachMoreInfo(id, suffixes) {
    const el = this.shadowRoot.getElementById(id);
    if (el) {
      el.addEventListener("click", () => this._fireMoreInfo(suffixes));
    }
  }

  _getParmairEntities() {
    if (this._cachedEntities && this._cachedHassStates === this._hass.states) {
      return this._cachedEntities;
    }
    this._cachedHassStates = this._hass.states;
    const map = {};
    if (this._hass && this._hass.states) {
      for (const [entityId, stateObj] of Object.entries(this._hass.states)) {
        if (entityId.includes("parmair_mac") || entityId.includes("parmair")) {
          map[entityId] = stateObj;
        }
      }
    }
    this._cachedEntities = map;
    return map;
  }

  _findEntityId(suffixes) {
    if (!this._hass || !this._hass.states) return null;
    const parmairEntities = this._getParmairEntities();
    const suffixList = Array.isArray(suffixes) ? suffixes : [suffixes];
    for (const suffix of suffixList) {
      for (const entityId of Object.keys(parmairEntities)) {
        if (entityId.endsWith(`_${suffix}`) || entityId.endsWith(`.${suffix}`)) {
          return entityId;
        }
      }
    }
    return null;
  }

  _fireMoreInfo(suffixes) {
    const entityId = this._findEntityId(suffixes);
    if (!entityId) return;
    const event = new CustomEvent("hass-more-info", {
      detail: { entityId },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  // Flexible entity getter across different device name conventions
  _findValue(suffixes) {
    if (!this._hass || !this._hass.states) return null;
    const parmairEntities = this._getParmairEntities();
    const suffixList = Array.isArray(suffixes) ? suffixes : [suffixes];

    for (const suffix of suffixList) {
      for (const [entityId, stateObj] of Object.entries(parmairEntities)) {
        if (entityId.endsWith(`_${suffix}`) || entityId.endsWith(`.${suffix}`)) {
          if (stateObj && stateObj.state !== "unavailable" && stateObj.state !== "unknown") {
            return stateObj.state;
          }
        }
      }
    }
    return null;
  }

  updateCard() {
    if (!this.shadowRoot || !this._hass) return;

    // 1) Mode & Speed
    const currentMode =
      this._findValue(["control_state", "state", "operational_mode"]) || "Home";
    const speed =
      this._findValue(["current_speed", "actual_speed", "actual_fan_speed"]) || "--";

    const statePill = this.shadowRoot.getElementById("state_pill");
    if (statePill) statePill.textContent = currentMode;

    const speedBadge = this.shadowRoot.getElementById("speed");
    if (speedBadge) {
      speedBadge.innerHTML = `<ha-icon icon="mdi:fan"></ha-icon> Nopeus ${speed}`;
    }

    // Highlight active button
    const buttons = this.shadowRoot.querySelectorAll(".mode-btn");
    buttons.forEach((btn) => {
      const mode = btn.getAttribute("data-mode");
      if (mode && mode.toLowerCase() === currentMode.toLowerCase()) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // 2) Temperatures (SVG Badges)
    const fresh = this._findValue(["fresh_air_temperature", "fresh_air_temp"]);
    const exhaust = this._findValue(["exhaust_air_temperature", "exhaust_temp"]);
    const ltoTemp = this._findValue([
      "supply_air_temperature_after_recovery",
      "supply_after_recovery_temp",
    ]);
    const supply = this._findValue(["supply_air_temperature", "supply_temp"]);
    const waste = this._findValue(["waste_air_temperature", "waste_temp"]);

    const elFresh = this.shadowRoot.getElementById("svg_fresh");
    const elExhaust = this.shadowRoot.getElementById("svg_exhaust");
    const elLtoTemp = this.shadowRoot.getElementById("svg_lto_temp");
    const elSupply = this.shadowRoot.getElementById("svg_supply");
    const elWaste = this.shadowRoot.getElementById("svg_waste");

    if (elFresh && fresh !== null) elFresh.textContent = `${fresh} °C`;
    if (elExhaust && exhaust !== null) elExhaust.textContent = `${exhaust} °C`;
    if (elLtoTemp && ltoTemp !== null) elLtoTemp.textContent = `${ltoTemp} °C`;
    if (elSupply && supply !== null) elSupply.textContent = `${supply} °C`;
    if (elWaste && waste !== null) elWaste.textContent = `${waste} °C`;

    // 3) Recovery (SVG Center Diamond)
    const eff = this._findValue([
      "heat_recovery_efficiency",
      "lto_heat_recovery_control",
    ]);
    const recPower = this._findValue(["heat_recovery_power"]);

    const elEff = this.shadowRoot.getElementById("svg_recovery_eff");
    const elRecPower = this.shadowRoot.getElementById("svg_recovery_power");

    if (elEff && eff !== null) elEff.textContent = `LTO: ${eff} %`;
    if (elRecPower && recPower !== null) elRecPower.textContent = `Talteenotto: ${recPower} W`;

    // 4) Heater Power & Visual Glow
    const heaterPower =
      this._findValue(["post_heater_power", "heater_power"]) || "0";
    const elHeaterPower = this.shadowRoot.getElementById("svg_heater_power");
    const elHeaterBadge = this.shadowRoot.getElementById("svg_heater_badge");
    const elHeaterPath = this.shadowRoot.getElementById("heater_path");

    if (elHeaterPower) {
      elHeaterPower.textContent = `${heaterPower} W`;
      const pVal = parseFloat(heaterPower);
      if (!isNaN(pVal) && pVal > 0) {
        if (elHeaterBadge) {
          elHeaterBadge.setAttribute("stroke", "#f97316");
          elHeaterBadge.setAttribute("fill", "rgba(50, 20, 10, 0.95)");
        }
        if (elHeaterPath) {
          elHeaterPath.setAttribute("stroke", "#f97316");
          elHeaterPath.setAttribute("filter", "url(#heaterGlow)");
        }
      } else {
        if (elHeaterBadge) {
          elHeaterBadge.setAttribute("stroke", "#475569");
          elHeaterBadge.setAttribute("fill", "rgba(24, 21, 18, 0.95)");
        }
        if (elHeaterPath) {
          elHeaterPath.setAttribute("stroke", "#64748b");
          elHeaterPath.removeAttribute("filter");
        }
      }
    }

    // 5) Fan Speeds (SVG Fans)
    const supplyFan = this._findValue(["supply_fan_speed"]);
    const exhaustFan = this._findValue(["exhaust_fan_speed"]);

    const elSupplyFan = this.shadowRoot.getElementById("svg_supply_fan");
    const elExhaustFan = this.shadowRoot.getElementById("svg_exhaust_fan");

    if (elSupplyFan && supplyFan !== null) elSupplyFan.textContent = `${supplyFan} %`;
    if (elExhaustFan && exhaustFan !== null) elExhaustFan.textContent = `${exhaustFan} %`;

    // 6) Total Metrics (Bottom Row)
    const totalPower = this._findValue(["total_power"]);
    const totalEnergy = this._findValue(["total_energy"]);
    const filterState = this._findValue(["filter_status", "filter_state"]);

    const elTotalPower = this.shadowRoot.getElementById("total_power");
    const elTotalEnergy = this.shadowRoot.getElementById("total_energy");
    const elFilterDays = this.shadowRoot.getElementById("filter_days");

    if (elTotalPower && totalPower !== null) elTotalPower.textContent = `${totalPower} W`;
    if (elTotalEnergy && totalEnergy !== null) elTotalEnergy.textContent = `${totalEnergy} kWh`;
    if (elFilterDays && filterState !== null) {
      let displayFilter = filterState;
      if (typeof filterState === "string" && filterState.toLowerCase().includes("replace reminder")) {
        displayFilter = "Vaihda";
      }
      elFilterDays.textContent = displayFilter;
    }

    // 7) Environmental Sensors in Header Chips (Humidity & CO2)
    const humidity = this._findValue(["humidity", "exhaust_humidity"]);
    const co2 = this._findValue(["co2_exhaust", "co2_exhaust_air", "co2"]);

    const elHumidity = this.shadowRoot.getElementById("chip_humidity");
    const elCo2 = this.shadowRoot.getElementById("chip_co2");

    if (elHumidity && humidity !== null) {
      elHumidity.textContent = `💧 ${humidity} %`;
    }
    if (elCo2) {
      if (co2 !== null && !isNaN(parseFloat(co2))) {
        const co2Val = Math.round(parseFloat(co2));
        elCo2.textContent = `🌱 ${co2Val} ppm`;
        elCo2.style.display = "";
      } else {
        elCo2.style.display = "none";
      }
    }
  }

  _setMode(mode) {
    if (!this._hass || !this._hass.states) return;
    const parmairEntities = this._getParmairEntities();
    const selectEntity = Object.keys(parmairEntities).find(
      (id) =>
        (id.endsWith("control_state") || id.endsWith("state")) &&
        id.startsWith("select.")
    );

    if (selectEntity) {
      this._hass.callService("select", "select_option", {
        entity_id: selectEntity,
        option: mode,
      });
    }
  }
}

class ParmairMacCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    if (!this.innerHTML) {
      this.innerHTML = `
        <div style="padding: 16px; font-family: inherit;">
          <p style="margin: 0 0 8px; font-weight: 600;">Parmair MAC Card</p>
          <p style="margin: 0; color: var(--secondary-text-color, #94a3b8); font-size: 13px;">
            Tämä kortti yhdistää automaattisesti kaikki asennetun Parmair MAC -laitteesi anturit ja käyttötilat.
            Lisäasetuksia ei tarvita!
          </p>
        </div>
      `;
    }
  }
}

customElements.define("parmair-mac-card-editor", ParmairMacCardEditor);
customElements.define("parmair-mac-card", ParmairMacCard);

window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "parmair-mac-card")) {
  window.customCards.push({
    type: "parmair-mac-card",
    name: "Parmair MAC Card",
    preview: true,
    description: "Interactive Scandinavian HVAC schematic card with live airflow, LTO heat recovery, and heating element controls for Parmair MAC.",
  });
}
