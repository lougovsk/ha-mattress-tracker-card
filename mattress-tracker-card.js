class MattressTrackerCard extends HTMLElement {
  get hass() {
    return this._hass;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.content) {
      this.innerHTML = `
        <ha-card>
          <div class="card-content"></div>
        </ha-card>
      `;
      this.content = this.querySelector('.card-content');
      const style = document.createElement('style');
      style.textContent = `
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
        }
        .card-header {
          padding-bottom: 8px;
        }
      `;
      this.appendChild(style);
    }

    this.updateCard();
  }

  updateCard() {
    const config = this._config;
    const hass = this._hass;

    const mattressId = config.mattress_id;
    const sideEntityId = `sensor.${mattressId}_current_side`;
    const rotationEntityId = `sensor.${mattressId}_current_rotation`;
    const lastFlippedId = `sensor.${mattressId}_last_flipped`;
    const lastRotatedId = `sensor.${mattressId}_last_rotated`;
    const flipButtonId = `button.${mattressId}_flip`;
    const rotateButtonId = `button.${mattressId}_rotate`;

    const sideState = hass.states[sideEntityId];
    const rotationState = hass.states[rotationEntityId];
    const flippedState = hass.states[lastFlippedId];
    const rotatedState = hass.states[lastRotatedId];

    if (!rotatedState) {
        this.content.innerHTML = `<div class="error">Entity not found: ${lastRotatedId}</div>`;
        return;
    }

    const lastRotatedDateStr = rotatedState.state;
    let diffMonths = 0;
    let progress = 0;
    let isOverdue = false;
    let lastRotatedDisplay = 'Never';

    if (lastRotatedDateStr && lastRotatedDateStr !== 'unknown' && lastRotatedDateStr !== 'unavailable') {
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

    this.content.innerHTML = `
      ${config.title ? `<div class="card-header"><div class="name">${config.title}</div></div>` : ''}
      <div class="status-container">
        <div class="status-item">
          <ha-icon icon="mdi:file-replace"></ha-icon>
          <span>Side: ${sideState ? sideState.state : 'Unknown'}</span>
        </div>
        <div class="status-item">
          <ha-icon icon="mdi:rotate-right"></ha-icon>
          <span>Orientation: ${rotationState ? rotationState.state : 'Unknown'}</span>
        </div>
      </div>

      <div class="buttons-container">
        <mwc-button raised id="flip-btn">
          Flip Mattress
        </mwc-button>
        <mwc-button raised id="rotate-btn">
          Rotate Mattress
        </mwc-button>
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
        <div class="info-text">Last flipped: ${flippedState ? flippedState.state : 'Never'}</div>
        ${isOverdue ? `
          <div class="overdue">
            <ha-icon icon="mdi:alert"></ha-icon>
            OVERDUE FOR ROTATION
          </div>
        ` : ''}
      </div>
    `;

    this.content.querySelector('#flip-btn').onclick = () => this._pressButton(flipButtonId);
    this.content.querySelector('#rotate-btn').onclick = () => this._pressButton(rotateButtonId);
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
