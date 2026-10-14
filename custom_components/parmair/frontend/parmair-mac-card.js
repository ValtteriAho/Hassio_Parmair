/**
 * Parmair MAC Home Assistant Lovelace Card
 * Custom Card delivering an interactive Scandinavian HVAC schematic with real-time airflow,
 * heat recovery, electric post-heater output, and mode controls.
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
        /* Schematic Area */
        .schematic-container {
          position: relative;
          width: 100%;
          aspect-ratio: 800 / 500;
          background: url('/parmair/parmair_schematic.svg') center center / contain no-repeat;
          border-radius: 12px;
          margin-bottom: 14px;
        }
        .tag {
          position: absolute;
          transform: translate(-50%, -50%);
          font-weight: bold;
          font-size: 13px;
          padding: 4px 8px;
          border-radius: 6px;
          background: rgba(15, 23, 42, 0.85);
          backdrop-filter: blur(4px);
          white-space: nowrap;
          box-shadow: 0 2px 4px rgba(0,0,0,0.4);
        }
        /* Duct Tags */
        .tag-fresh {
          top: 22%;
          left: 14%;
          color: #38bdf8;
          border: 1px solid #0284c7;
        }
        .tag-exhaust {
          top: 22%;
          left: 86%;
          color: #f87171;
          border: 1px solid #ef4444;
        }
        .tag-lto-inter {
          top: 59%;
          left: 33%;
          font-size: 11px;
          color: #38bdf8;
          border: 1px solid #1e293b;
        }
        .tag-supply {
          top: 74%;
          left: 14%;
          color: #f59e0b;
          border: 1px solid #ea580c;
          font-size: 14px;
        }
        .tag-waste {
          top: 74%;
          left: 86%;
          color: #94a3b8;
          border: 1px solid #475569;
        }
        /* Center Recovery */
        .tag-recovery-eff {
          top: 44%;
          left: 50%;
          color: #ffffff;
          border: none;
          background: none;
          font-size: 13px;
        }
        .tag-recovery-power {
          top: 54%;
          left: 50%;
          color: #38bdf8;
          border: none;
          background: none;
          font-size: 12px;
        }
        /* Heater Output */
        .tag-heater {
          top: 65%;
          left: 23%;
          color: #fb923c;
          border: 1px solid #ea580c;
          font-size: 11px;
        }
        /* Metrics bar */
        .metrics-row {
          display: flex;
          justify-content: space-around;
          background: rgba(15, 23, 42, 0.4);
          border-radius: 8px;
          padding: 8px 12px;
          margin-bottom: 14px;
          border: 1px solid #334155;
          font-size: 13px;
        }
        .metric-item {
          display: flex;
          align-items: center;
          gap: 6px;
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
          grid-template-columns: repeat(5, 1fr);
          gap: 8px;
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
          gap: 6px;
          cursor: pointer;
          transition: all 0.2s ease;
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
        }
      </style>

      <ha-card>
        <div class="header">
          <div class="brand">
            <ha-icon icon="mdi:fan"></ha-icon>
            <span id="title">PARMAIR MAC</span>
          </div>
          <div class="header-chips">
            <div id="speed" class="speed-badge"><ha-icon icon="mdi:fan"></ha-icon> Nopeus --</div>
            <div id="state_pill" class="status-pill">--</div>
          </div>
        </div>

        <div class="schematic-container">
          <div id="fresh_air" class="tag tag-fresh">-- °C</div>
          <div id="exhaust_air" class="tag tag-exhaust">-- °C</div>
          <div id="recovery_temp" class="tag tag-lto-inter">LTO: -- °C</div>
          <div id="supply_air" class="tag tag-supply">-- °C</div>
          <div id="waste_air" class="tag tag-waste">-- °C</div>

          <div id="recovery_eff" class="tag tag-recovery-eff">LTO: -- %</div>
          <div id="recovery_power" class="tag tag-recovery-power">Talteenotto: -- W</div>

          <div id="heater_power" class="tag tag-heater">Lämmitin: 0 W</div>
        </div>

        <div class="metrics-row">
          <div class="metric-item">
            <ha-icon icon="mdi:flash" style="color: #38bdf8;"></ha-icon>
            <span class="metric-label">Ottoteho:</span>
            <span id="total_power" class="metric-value">-- W</span>
          </div>
          <div class="metric-item">
            <ha-icon icon="mdi:counter" style="color: #fbbf24;"></ha-icon>
            <span class="metric-label">Energia:</span>
            <span id="total_energy" class="metric-value">-- kWh</span>
          </div>
          <div class="metric-item">
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

    this.content = true;
  }

  _getEntity(entityId) {
    return this._hass?.states?.[entityId];
  }

  _findEntity(suffix) {
    if (!this._hass) return null;
    const match = Object.keys(this._hass.states).find(
      (id) => id.startsWith("select.parmair_mac_") || id.startsWith("sensor.parmair_mac_")
    );
    if (!match) return null;
    // Prefix e.g. "sensor.parmair_mac"
    const prefix = match.split("_").slice(0, 2).join("_");
    return this._hass.states[`${prefix}_${suffix}`] || null;
  }

  updateCard() {
    if (!this.shadowRoot || !this._hass) return;

    // Helper: try exact or find matching entity
    const getState = (exact, suffix) => {
      let state = this._getEntity(exact);
      if (!state && suffix) {
        state = Object.values(this._hass.states).find(
          (s) => s.entity_id.includes("parmair_mac") && s.entity_id.endsWith(suffix)
        );
      }
      return state ? state.state : null;
    };

    // 1) Mode & Speed
    const currentMode = getState("select.parmair_mac_control_state", "control_state") || "Home";
    const speed = getState("sensor.parmair_mac_actual_fan_speed", "actual_fan_speed") || "2";

    const statePill = this.shadowRoot.getElementById("state_pill");
    if (statePill) statePill.textContent = currentMode;

    const speedBadge = this.shadowRoot.getElementById("speed");
    if (speedBadge) speedBadge.innerHTML = `<ha-icon icon="mdi:fan"></ha-icon> Nopeus ${speed}`;

    // Highlight active button
    const buttons = this.shadowRoot.querySelectorAll(".mode-btn");
    buttons.forEach((btn) => {
      const mode = btn.getAttribute("data-mode");
      if (mode.toLowerCase() === currentMode.toLowerCase()) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // 2) Temperatures
    const fresh = getState("sensor.parmair_mac_fresh_air_temperature", "fresh_air_temperature");
    const exhaust = getState("sensor.parmair_mac_exhaust_air_temperature", "exhaust_air_temperature");
    const recoveryTemp = getState("sensor.parmair_mac_supply_air_temperature_after_recovery", "supply_air_temperature_after_recovery");
    const supply = getState("sensor.parmair_mac_supply_air_temperature", "supply_air_temperature");
    const waste = getState("sensor.parmair_mac_waste_air_temperature", "waste_air_temperature");

    if (fresh) this.shadowRoot.getElementById("fresh_air").textContent = `${fresh} °C`;
    if (exhaust) this.shadowRoot.getElementById("exhaust_air").textContent = `${exhaust} °C`;
    if (recoveryTemp) this.shadowRoot.getElementById("recovery_temp").textContent = `LTO: ${recoveryTemp} °C`;
    if (supply) this.shadowRoot.getElementById("supply_air").textContent = `${supply} °C`;
    if (waste) this.shadowRoot.getElementById("waste_air").textContent = `${waste} °C`;

    // 3) Recovery
    const eff = getState("sensor.parmair_mac_heat_recovery_efficiency", "heat_recovery_efficiency");
    const recPower = getState("sensor.parmair_mac_heat_recovery_power", "heat_recovery_power");

    if (eff) this.shadowRoot.getElementById("recovery_eff").textContent = `LTO: ${eff} %`;
    if (recPower) this.shadowRoot.getElementById("recovery_power").textContent = `Talteenotto: ${recPower} W`;

    // 4) Heater Power
    const heaterPower = getState("sensor.parmair_mac_post_heater_power", "post_heater_power") || "0";
    const heaterEl = this.shadowRoot.getElementById("heater_power");
    if (heaterEl) {
      heaterEl.textContent = `Lämmitin: ${heaterPower} W`;
      if (parseFloat(heaterPower) > 0) {
        heaterEl.style.color = "#f97316";
        heaterEl.style.borderColor = "#ea580c";
        heaterEl.style.boxShadow = "0 0 8px rgba(234, 88, 12, 0.4)";
      } else {
        heaterEl.style.color = "#94a3b8";
        heaterEl.style.borderColor = "#475569";
        heaterEl.style.boxShadow = "none";
      }
    }

    // 5) Total Metrics
    const totalPower = getState("sensor.parmair_mac_total_power", "total_power");
    const totalEnergy = getState("sensor.parmair_mac_total_energy", "total_energy");
    const filterState = getState("sensor.parmair_mac_filter_state", "filter_state");

    if (totalPower) this.shadowRoot.getElementById("total_power").textContent = `${totalPower} W`;
    if (totalEnergy) this.shadowRoot.getElementById("total_energy").textContent = `${totalEnergy} kWh`;
    if (filterState) this.shadowRoot.getElementById("filter_days").textContent = filterState;
  }

  _setMode(mode) {
    const selectEntity = Object.keys(this._hass.states).find(
      (id) => id.includes("parmair_mac") && id.includes("control_state") && id.startsWith("select.")
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

