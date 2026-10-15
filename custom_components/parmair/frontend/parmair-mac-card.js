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
          font-size: 18px;
          font-weight: 700;
          letter-spacing: 0.5px;
          color: #ffffff;
        }
        .brand ha-icon {
          color: #009fe3;
        }
        .header-chips {
          display: flex;
          gap: 8px;
          align-items: center;
        }
        .status-pill {
          background: rgba(2, 132, 199, 0.2);
          border: 1px solid #0284c7;
          color: #38bdf8;
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 13px;
          font-weight: 600;
        }
        .speed-badge {
          background: rgba(51, 65, 85, 0.5);
          border: 1px solid #475569;
          color: #94a3b8;
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 4px;
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
          gap: 8px;
          margin-bottom: 12px;
        }
        .metric-item {
          display: flex;
          align-items: center;
          gap: 8px;
          background: rgba(15, 23, 42, 0.5);
          border-radius: 8px;
          padding: 8px 12px;
          border: 1px solid #334155;
          font-size: 13px;
        }
        .metric-label {
          color: #94a3b8;
        }
        .metric-value {
          font-weight: 600;
          color: #f1f5f9;
        }

        /* Mode Selectors */
        .mode-grid {
          display: grid;
          grid-template-columns: repeat(5, minmax(0, 1fr));
          gap: 6px;
        }
        .mode-btn {
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid #334155;
          border-radius: 10px;
          padding: 8px 4px;
          color: #94a3b8;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
          overflow: hidden;
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
          font-size: 12px;
          font-weight: 500;
          white-space: nowrap;
          text-overflow: ellipsis;
          overflow: hidden;
        }
        @media (max-width: 400px) {
          .mode-btn span {
            font-size: 10px;
          }
          .mode-btn ha-icon {
            --mdc-icon-size: 18px;
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
            <div id="speed" class="speed-badge clickable-badge" title="Klikkaa avataksesi anturitiedot"><ha-icon icon="mdi:fan"></ha-icon> Nopeus --</div>
            <div id="state_pill" class="status-pill clickable-badge" title="Klikkaa avataksesi tilatiedot">--</div>
          </div>
        </div>

        <div class="schematic-box">
          <svg class="schematic-svg" viewBox="0 0 800 480" preserveAspectRatio="xMidYMid meet">
            <defs>
              <linearGradient id="cardBgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#1e242c" />
                <stop offset="100%" stop-color="#14181d" />
              </linearGradient>

              <!-- Flow Gradients -->
              <linearGradient id="freshAirGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#0284c7" stop-opacity="0.9" />
              </linearGradient>
              <linearGradient id="supplyAirGrad" x1="100%" y1="0%" x2="0%" y2="0%">
                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#ea580c" stop-opacity="0.9" />
              </linearGradient>
              <linearGradient id="exhaustAirGrad" x1="100%" y1="0%" x2="0%" y2="0%">
                <stop offset="0%" stop-color="#f87171" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#ef4444" stop-opacity="0.9" />
              </linearGradient>
              <linearGradient id="wasteAirGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#64748b" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#475569" stop-opacity="0.9" />
              </linearGradient>

              <linearGradient id="coreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#1e293b" />
                <stop offset="50%" stop-color="#0f172a" />
                <stop offset="100%" stop-color="#1e293b" />
              </linearGradient>

              <!-- Counterflow internal gradients -->
              <linearGradient id="freshCoreFlow" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#0284c7" />
                <stop offset="50%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#f59e0b" />
              </linearGradient>
              <linearGradient id="exhaustCoreFlow" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#ef4444" />
                <stop offset="50%" stop-color="#f87171" />
                <stop offset="100%" stop-color="#64748b" />
              </linearGradient>

              <!-- Glow filter for post-heater -->
              <filter id="heaterGlow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="3.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>

              <!-- Glow filter for direction arrows -->
              <filter id="arrowGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2.5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>

              <!-- Drop shadow for vector badges -->
              <filter id="badgeShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.6" />
              </filter>
            </defs>

            <!-- Card Background -->
            <rect width="800" height="480" rx="14" fill="url(#cardBgGrad)" stroke="#334155" stroke-width="1.5" />

            <!-- Chassis Frame -->
            <rect x="200" y="60" width="400" height="350" rx="14" fill="#0b0f14" stroke="#475569" stroke-width="2.5" />
            <rect x="214" y="74" width="372" height="322" rx="10" fill="#131922" stroke="#1e293b" stroke-width="1.5" />

            <!-- DUCTS WITH REAL-WORLD DIRECTION ARROWS (MULTI-CHEVRON WITH GLOW) -->
            <!-- 1) Top-Left: Ulkoilma (Fresh outdoor air in) -->
            <path d="M 50 120 L 200 120" stroke="#0284c7" stroke-width="36" stroke-linecap="round" fill="none" opacity="0.15" />
            <path d="M 50 120 L 200 120" stroke="url(#freshAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- Inward Multi-Chevron Arrows >>> -->
            <path d="M 152 108 L 164 120 L 152 132" fill="none" stroke="#38bdf8" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 168 108 L 180 120 L 168 132" fill="none" stroke="#38bdf8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 184 108 L 196 120 L 184 132" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />

            <!-- 2) Top-Right: Poistoilma (Exhaust room air in) -->
            <path d="M 750 120 L 600 120" stroke="#ef4444" stroke-width="36" stroke-linecap="round" fill="none" opacity="0.15" />
            <path d="M 750 120 L 600 120" stroke="url(#exhaustAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- Inward Multi-Chevron Arrows <<< -->
            <path d="M 648 108 L 636 120 L 648 132" fill="none" stroke="#f87171" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 632 108 L 620 120 L 632 132" fill="none" stroke="#f87171" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 616 108 L 604 120 L 616 132" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />

            <!-- 3) Bottom-Right: Jäteilma (Waste air out to outdoors) -->
            <path d="M 600 350 L 750 350" stroke="#64748b" stroke-width="36" stroke-linecap="round" fill="none" opacity="0.15" />
            <path d="M 600 350 L 750 350" stroke="url(#wasteAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- Outward Multi-Chevron Arrows >>> -->
            <path d="M 702 338 L 714 350 L 702 362" fill="none" stroke="#94a3b8" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 718 338 L 730 350 L 718 362" fill="none" stroke="#94a3b8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 734 338 L 746 350 L 734 362" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />

            <!-- 4) Bottom-Left: Tuloilma (Supply warm air out to home) -->
            <path d="M 200 350 L 50 350" stroke="#f59e0b" stroke-width="36" stroke-linecap="round" fill="none" opacity="0.15" />
            <path d="M 200 350 L 50 350" stroke="url(#supplyAirGrad)" stroke-width="7" stroke-linecap="round" fill="none" />
            <!-- Outward Multi-Chevron Arrows <<< -->
            <path d="M 98 338 L 86 350 L 98 362" fill="none" stroke="#f59e0b" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 82 338 L 70 350 L 82 362" fill="none" stroke="#f59e0b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />
            <path d="M 66 338 L 54 350 L 66 362" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#arrowGlow)" />

            <!-- Filters -->
            <!-- F7 Fresh Air Filter (Top-Left) -->
            <g transform="translate(230, 95)">
              <rect x="0" y="0" width="10" height="50" rx="2" fill="#0284c7" opacity="0.75" />
              <line x1="2" y1="5" x2="8" y2="45" stroke="#38bdf8" stroke-width="1.5" />
              <line x1="8" y1="5" x2="2" y2="45" stroke="#38bdf8" stroke-width="1.5" />
              <text x="5" y="62" fill="#94a3b8" font-size="9" font-family="sans-serif" text-anchor="middle">F7</text>
            </g>

            <!-- G4 Exhaust Filter (Top-Right) -->
            <g transform="translate(560, 95)">
              <rect x="0" y="0" width="10" height="50" rx="2" fill="#ef4444" opacity="0.75" />
              <line x1="2" y1="5" x2="8" y2="45" stroke="#f87171" stroke-width="1.5" />
              <line x1="8" y1="5" x2="2" y2="45" stroke="#f87171" stroke-width="1.5" />
              <text x="5" y="62" fill="#94a3b8" font-size="9" font-family="sans-serif" text-anchor="middle">G4</text>
            </g>

            <!-- AIRFLOW PATHS PASSING THROUGH HEAT EXCHANGER CORE -->
            <!-- Fresh stream: (200,120) -> curves through LTO core -> (200,350) -->
            <path d="M 200 120 C 270 120, 310 150, 360 200 C 390 230, 370 270, 320 290 C 270 310, 240 330, 200 350"
                  stroke="url(#freshCoreFlow)" stroke-width="5" stroke-dasharray="8,5" fill="none" opacity="0.85" />

            <!-- Exhaust stream: (600,120) -> curves through LTO core -> (600,350) -->
            <path d="M 600 120 C 530 120, 490 150, 440 200 C 410 230, 430 270, 480 290 C 530 310, 560 330, 600 350"
                  stroke="url(#exhaustCoreFlow)" stroke-width="5" stroke-dasharray="8,5" fill="none" opacity="0.85" />

            <!-- CENTER: Heat Recovery Exchanger Core (Diamond) -->
            <g transform="translate(400, 235)" id="badge_lto_center" class="clickable-badge">
              <polygon points="0,-95 95,0 0,95 -95,0" fill="url(#coreGrad)" stroke="#38bdf8" stroke-width="2" />
              <!-- Heat transfer lamellas -->
              <line x1="-55" y1="-40" x2="55" y2="40" stroke="#334155" stroke-width="1.5" />
              <line x1="-40" y1="-55" x2="40" y2="55" stroke="#334155" stroke-width="1.5" />
              <line x1="-20" y1="-75" x2="75" y2="20" stroke="#334155" stroke-width="1.5" />
              <line x1="-75" y1="-20" x2="20" y2="75" stroke="#334155" stroke-width="1.5" />

              <!-- Clean center badge for LTO Efficiency & Thermal Power -->
              <rect x="-75" y="-32" width="150" height="64" rx="10" fill="#090d12" stroke="#009fe3" stroke-width="1.5" filter="url(#badgeShadow)" />
              <text x="0" y="-8" fill="#ffffff" font-size="13" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_recovery_eff">LTO: -- %</text>
              <text x="0" y="16" fill="#38bdf8" font-size="12" font-weight="600" font-family="sans-serif" text-anchor="middle" id="svg_recovery_power">Talteenotto: -- W</text>
            </g>

            <!-- Tulopuhallin (Bottom-Left Bay) -->
            <g transform="translate(260, 350)">
              <circle cx="0" cy="0" r="22" fill="#1e293b" stroke="#475569" stroke-width="1.5" />
              <circle cx="0" cy="0" r="4" fill="#38bdf8" />
              <path d="M 0,-15 Q 5,-7 0,0 Q -5,-7 0,-15" fill="#38bdf8" opacity="0.8" />
              <path d="M 15,0 Q 7,5 0,0 Q 7,-5 15,0" fill="#38bdf8" opacity="0.8" />
              <path d="M 0,15 Q -5,7 0,0 Q 5,7 0,15" fill="#38bdf8" opacity="0.8" />
              <path d="M -15,0 Q -7,-5 0,0 Q -7,5 -15,0" fill="#38bdf8" opacity="0.8" />
              <text x="0" y="32" fill="#94a3b8" font-size="9" font-family="sans-serif" text-anchor="middle">Tulopuhallin</text>
            </g>

            <!-- Poistopuhallin (Bottom-Right Bay) -->
            <g transform="translate(540, 350)">
              <circle cx="0" cy="0" r="22" fill="#1e293b" stroke="#475569" stroke-width="1.5" />
              <circle cx="0" cy="0" r="4" fill="#f87171" />
              <path d="M 0,-15 Q 5,-7 0,0 Q -5,-7 0,-15" fill="#f87171" opacity="0.8" />
              <path d="M 15,0 Q 7,5 0,0 Q 7,-5 15,0" fill="#f87171" opacity="0.8" />
              <path d="M 0,15 Q -5,7 0,0 Q 5,7 0,15" fill="#f87171" opacity="0.8" />
              <path d="M -15,0 Q -7,-5 0,0 Q -7,5 -15,0" fill="#f87171" opacity="0.8" />
              <text x="0" y="32" fill="#94a3b8" font-size="9" font-family="sans-serif" text-anchor="middle">Poistopuhallin</text>
            </g>

            <!-- Post-Heater Coil Component (Active thermal element) -->
            <g transform="translate(195, 350)" id="heater_coil">
              <rect x="-14" y="-24" width="28" height="48" rx="4" fill="#181512" stroke="#ea580c" stroke-width="1.5" />
              <path d="M -6,-16 L 6,-10 L -6,-4 L 6,2 L -6,8 L 6,14" fill="none" stroke="#ea580c" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" id="heater_path" />
            </g>

            <!-- VECTOR-LOCKED SENSOR BADGES (CANNOT COLLIDE OR DRIFT) -->
            <!-- 1) Ulkoilma Badge (Top-Left) -->
            <g transform="translate(90, 120)" id="badge_fresh" class="clickable-badge">
              <rect x="-60" y="-22" width="120" height="44" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#0284c7" stroke-width="1.5" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="11" font-weight="600" font-family="sans-serif" text-anchor="middle">Ulkoilma</text>
              <text x="0" y="14" fill="#38bdf8" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_fresh">-- °C</text>
            </g>

            <!-- 2) Poistoilma Badge (Top-Right) -->
            <g transform="translate(710, 120)" id="badge_exhaust" class="clickable-badge">
              <rect x="-60" y="-22" width="120" height="44" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#ef4444" stroke-width="1.5" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="11" font-weight="600" font-family="sans-serif" text-anchor="middle">Poistoilma</text>
              <text x="0" y="14" fill="#f87171" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_exhaust">-- °C</text>
            </g>

            <!-- 3) LTO Intermediate Temp Badge (After Recovery Core) -->
            <g transform="translate(305, 280)" id="badge_lto_temp" class="clickable-badge">
              <rect x="-55" y="-14" width="110" height="28" rx="6" fill="rgba(15, 23, 42, 0.95)" stroke="#0284c7" stroke-width="1.2" filter="url(#badgeShadow)" />
              <text x="0" y="5" fill="#38bdf8" font-size="12" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_lto_temp">LTO: -- °C</text>
            </g>

            <!-- 4) Post-Heater Power Badge (Above heating coil) -->
            <g transform="translate(195, 295)" id="badge_heater" class="clickable-badge">
              <rect x="-55" y="-14" width="110" height="28" rx="6" fill="rgba(24, 21, 18, 0.95)" stroke="#ea580c" stroke-width="1.2" id="svg_heater_badge" filter="url(#badgeShadow)" />
              <text x="0" y="5" fill="#fb923c" font-size="11" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_heater_power">Lämmitin: 0 W</text>
            </g>

            <!-- 5) Tuloilma Badge (Bottom-Left) -->
            <g transform="translate(142, 350)" id="badge_supply" class="clickable-badge">
              <rect x="-50" y="-22" width="100" height="44" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#ea580c" stroke-width="1.5" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="11" font-weight="600" font-family="sans-serif" text-anchor="middle">Tuloilma</text>
              <text x="0" y="14" fill="#f59e0b" font-size="15" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_supply">-- °C</text>
            </g>

            <!-- 6) Jäteilma Badge (Bottom-Right) -->
            <g transform="translate(658, 350)" id="badge_waste" class="clickable-badge">
              <rect x="-50" y="-22" width="100" height="44" rx="8" fill="rgba(15, 23, 42, 0.9)" stroke="#475569" stroke-width="1.5" filter="url(#badgeShadow)" />
              <text x="0" y="-4" fill="#94a3b8" font-size="11" font-weight="600" font-family="sans-serif" text-anchor="middle">Jäteilma</text>
              <text x="0" y="14" fill="#94a3b8" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle" id="svg_waste">-- °C</text>
            </g>
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

    this.content = true;
  }

  _attachMoreInfo(id, suffixes) {
    const el = this.shadowRoot.getElementById(id);
    if (el) {
      el.addEventListener("click", () => this._fireMoreInfo(suffixes));
    }
  }

  _findEntityId(suffixes) {
    if (!this._hass || !this._hass.states) return null;
    const suffixList = Array.isArray(suffixes) ? suffixes : [suffixes];
    for (const suffix of suffixList) {
      for (const entityId of Object.keys(this._hass.states)) {
        if (
          (entityId.includes("parmair_mac") || entityId.includes("parmair")) &&
          (entityId.endsWith(`_${suffix}`) || entityId.endsWith(`.${suffix}`))
        ) {
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
    const suffixList = Array.isArray(suffixes) ? suffixes : [suffixes];

    for (const suffix of suffixList) {
      // 1. Exact entity search
      for (const entityId of Object.keys(this._hass.states)) {
        if (
          (entityId.includes("parmair_mac") || entityId.includes("parmair")) &&
          (entityId.endsWith(`_${suffix}`) || entityId.endsWith(`.${suffix}`))
        ) {
          const stateObj = this._hass.states[entityId];
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
    if (elLtoTemp && ltoTemp !== null) elLtoTemp.textContent = `LTO: ${ltoTemp} °C`;
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
      elHeaterPower.textContent = `Lämmitin: ${heaterPower} W`;
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

    // 5) Total Metrics (Bottom Row)
    const totalPower = this._findValue(["total_power"]);
    const totalEnergy = this._findValue(["total_energy"]);
    const filterState = this._findValue(["filter_status", "filter_state"]);

    const elTotalPower = this.shadowRoot.getElementById("total_power");
    const elTotalEnergy = this.shadowRoot.getElementById("total_energy");
    const elFilterDays = this.shadowRoot.getElementById("filter_days");

    if (elTotalPower && totalPower !== null) elTotalPower.textContent = `${totalPower} W`;
    if (elTotalEnergy && totalEnergy !== null) elTotalEnergy.textContent = `${totalEnergy} kWh`;
    if (elFilterDays && filterState !== null) elFilterDays.textContent = filterState;
  }

  _setMode(mode) {
    if (!this._hass || !this._hass.states) return;
    const selectEntity = Object.keys(this._hass.states).find(
      (id) =>
        (id.includes("parmair_mac") || id.includes("parmair")) &&
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
window.customCards.push({
  type: "parmair-mac-card",
  name: "Parmair MAC Card",
  preview: true,
  description: "Interactive Scandinavian HVAC schematic card with live airflow, LTO heat recovery, and heating element controls for Parmair MAC.",
});
