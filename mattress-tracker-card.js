class MattressTrackerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  get hass() {
    return this._hass;
  }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;

    if (!this.shadowRoot.innerHTML) {
      this._initialRender();
    }

    if (this._shouldUpdate(oldHass, hass)) {
        this._updateCard();
    }
  }

  _shouldUpdate(oldHass, hass) {
    if (!oldHass) return true;
    const mattressId = this._config.mattress_id;
    const entities = [
        `sensor.${mattressId}_current_side`,
        `sensor.${mattressId}_current_rotation`,
        `sensor.${mattressId}_last_flipped`,
        `sensor.${mattressId}_last_rotated`
    ];
    return entities.some(entity => oldHass.states[entity] !== hass.states[entity]);
  }

  _initialRender() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        ha-card {
          padding: 16px;
        }
        .status-container {
          display: flex;
          justify-content: space-between;
          margin-bottom: 16px;
        }
        .status-item {
          display: flex;
          align-items: center;
        }
        .status-item ha-icon {
          margin-right: 8px;
        }
        .buttons-container {
          display: flex;
          gap: 8px;
          margin-bottom: 16px;
        }
        .buttons-container mwc-button {
          flex: 1;
          --mdc-theme-primary: var(--primary-color);
          --mdc-button-outline-color: var(--primary-color);
          background-color: var(--primary-color);
          color: white;
          border-radius: 4px;
          --mdc-typography-button-font-size: 0.9em;
          --mdc-button-horizontal-padding: 8px;
          display: block;
          height: 36px;
          line-height: 36px;
          text-align: center;
          font-weight: 500;
          cursor: pointer;
          box-shadow: var(--shadow-elevation-2dp, 0 2px 2px 0 rgba(0,0,0,0.14), 0 3px 1px -2px rgba(0,0,0,0.12), 0 1px 5px 0 rgba(0,0,0,0.2));
        }
        .buttons-container mwc-button:hover {
          filter: brightness(1.1);
        }
        .progress-container {
          margin-top: 16px;
        }
        .progress-bar {
          background-color: var(--secondary-background-color);
          border-radius: 4px;
          height: 12px;
          width: 100%;
          overflow: hidden;
          margin-bottom: 8px;
        }
        .progress-fill {
          height: 100%;
          transition: width 0.5s ease-in-out, background-color 0.5s ease-in-out;
        }
        .overdue {
          color: var(--error-color);
          display: flex;
          align-items: center;
          font-weight: bold;
          margin-top: 8px;
        }
        .overdue ha-icon {
          margin-right: 4px;
        }
        .info-text {
          font-size: 0.9em;
          color: var(--secondary-text-color);
          margin-bottom: 4px;
        }
        .card-header {
          padding-bottom: 12px;
          font-size: 1.2em;
          font-weight: 500;
        }
        .error {
          color: var(--error-color);
          padding: 16px;
        }
      </style>
      <ha-card>
        <div id="content"></div>
      </ha-card>
    `;
    this._content = this.shadowRoot.getElementById('content');
  }

  _updateCard() {
    const config = this._config;
    const hass = this._hass;
    const mattressId = config.mattress_id;

    const sideState = hass.states[`sensor.${mattressId}_current_side`];
    const rotationState = hass.states[`sensor.${mattressId}_current_rotation`];
    const flippedState = hass.states[`sensor.${mattressId}_last_flipped`];
    const rotatedState = hass.states[`sensor.${mattressId}_last_rotated`];

    if (!rotatedState) {
        this._content.innerHTML = `<div class="error">Entity not found: sensor.${mattressId}_last_rotated</div>`;
        return;
    }

    const lastRotatedDateStr = rotatedState.state;
    let diffMonths = 0;
    let progress = 0;
    let isOverdue = false;
    let lastRotatedDisplay = 'Never';

    if (lastRotatedDateStr && !['unknown', 'unavailable'].includes(lastRotatedDateStr)) {
        const lastRotatedDate = new Date(lastRotatedDateStr);
        const now = new Date();
        const diffTime = Math.abs(now - lastRotatedDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        diffMonths = diffDays / 30.44;
        lastRotatedDisplay = lastRotatedDate.toLocaleDateString();
    }

    const limitMonths = config.rotation_limit_months || 6;
    progress = Math.min((diffMonths / limitMonths) * 100, 100);
    isOverdue = diffMonths >= limitMonths;

    const progressColor = isOverdue ? 'var(--error-color)' : 'var(--primary-color)';

    const lastFlippedDateStr = flippedState ? flippedState.state : 'unknown';
    let lastFlippedDisplay = 'Never';
    if (lastFlippedDateStr && !['unknown', 'unavailable'].includes(lastFlippedDateStr)) {
        lastFlippedDisplay = new Date(lastFlippedDateStr).toLocaleDateString();
    }

    // Using a template string for structure, but being mindful of content
    this._content.innerHTML = `
      ${config.title ? `<div class="card-header">${this._escapeHtml(config.title)}</div>` : ''}
      <div class="status-container">
        <div class="status-item">
          <ha-icon icon="mdi:file-replace"></ha-icon>
          <span>Side: ${this._escapeHtml(sideState ? sideState.state : 'Unknown')}</span>
        </div>
        <div class="status-item">
          <ha-icon icon="mdi:rotate-right"></ha-icon>
          <span>Orientation: ${this._escapeHtml(rotationState ? rotationState.state : 'Unknown')}</span>
        </div>
      </div>

      <div class="buttons-container">
        <mwc-button raised id="flip-btn">Flip Mattress</mwc-button>
        <mwc-button raised id="rotate-btn">Rotate Mattress</mwc-button>
      </div>

      <div class="progress-container">
        <div class="info-text">Rotation Progress</div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${progress}%; background-color: ${progressColor};"></div>
        </div>
        <div class="info-text">
          ${diffMonths.toFixed(1)} months elapsed / ${limitMonths} months limit (${Math.round((diffMonths / limitMonths) * 100)}%)
        </div>
        <div class="info-text">Last rotated: ${lastRotatedDisplay}</div>
        <div class="info-text">Last flipped: ${lastFlippedDisplay}</div>
        ${isOverdue ? `
          <div class="overdue">
            <ha-icon icon="mdi:alert"></ha-icon>
            OVERDUE FOR ROTATION
          </div>
        ` : ''}
      </div>
    `;

    this.shadowRoot.getElementById('flip-btn').onclick = () => this._pressButton(`button.${mattressId}_flip`);
    this.shadowRoot.getElementById('rotate-btn').onclick = () => this._pressButton(`button.${mattressId}_rotate`);
  }

  _escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
  }

  _pressButton(entityId) {
    this._hass.callService('button', 'press', {
      entity_id: entityId
    });
  }

  setConfig(config) {
    if (!config.mattress_id) {
      throw new Error('You need to define mattress_id');
    }
    this._config = config;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('mattress-tracker-card', MattressTrackerCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "mattress-tracker-card",
  name: "Mattress Tracker Card",
  description: "A card to track and manage mattress flip and rotation.",
  preview: true,
});
