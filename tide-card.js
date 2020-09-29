class TideCard extends HTMLElement {

    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
    }

    setConfig(config) {
      if (!config.entity) {
        throw new Error('No source sensor defined');
      }

      const root = this.shadowRoot;
      if (root.lastChild) root.removeChild(root.lastChild);

      this.config = config;

      const card = document.createElement('ha-card');
      const content = document.createElement('div');
      const style = document.createElement('style');

      style.textContent = `
        .tide_clock_face {
          fill: var(--accent-color);
        }
        .tide_clock_lable {
          dominant-baseline: middle;
          text-anchor: middle;
          font-size: smaller;
          fill: var(--primary-text-color);
        }
        .tide_clock_lable_larger {
          dominant-baseline: middle;
          text-anchor: middle;
          fill: var(--primary-text-color);
        }
        .tide_clock_tick {
          dominant-baseline: middle;
          fill: var(--primary-text-color);
        }
        .tide_clock_arm {
          stroke: var(--primary-text-color);
          stroke-width: 3;
          transform-origin: center;
          transform: rotate(0deg);
        }
        
      `;

      content.innerHTML = `
        <div style="text-align:center;">
          <svg viewBox="0 0 200 200" height="140" width="140">
            <circle cx="100" cy="100" r="100" class="tide_clock_face"/>

            <text x="50%" y="35%" class="tide_clock_lable">High Tide</text>
            <text x="50%" y="65%" class="tide_clock_lable">Low Tide</text>

            <text x="70%" y="50%" id="tide_clock_lable_larger" class="tide_clock_lable_larger">0 m</text>

            <text x="5" y="100" transform="rotate(120 100 100)" class="tide_clock_tick">&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(150 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(180 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(210 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(240 100 100)" class="tide_clock_tick"">&#183;</text>
            <!--<text x="5" y="100" transform="rotate(270 100 100)" class="tide_clock_tick""></text>-->
            <text x="5" y="100" transform="rotate(300 100 100)" class="tide_clock_tick"">&#183;</text>
            <text x="5" y="100" transform="rotate(330 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(0 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(30 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(60 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;</text>
            <text x="5" y="100" transform="rotate(90 100 100)" class="tide_clock_tick"">&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;&#183;</text>

            <line x1="100" y1="100" x2="100" y2="20" class="tide_clock_arm" id="tide_clock_arm" transform="rotate(0 100 100)"/>
          </svg>
        </div>
      `;

      card.appendChild(content);
      card.appendChild(style);
      card.addEventListener('click', event => {
        this._fire('hass-more-info', { entityId: config.entity });
      });
      root.appendChild(card);
    }

    set hass(hass) {
      const root = this.shadowRoot;
  
      const entityId = this.config.entity;
      const state = hass.states[entityId];
      const stateStr = state ? state.state : 'unavailable';
      const degree = hass.states[entityId].attributes['degree'];

      root.getElementById("tide_clock_lable_larger").textContent = `${stateStr} m`;
      root.getElementById("tide_clock_arm").style.transform = `rotate(${degree}deg)`;
      root.lastChild.hass = hass;

    }

    _fire(type, detail, options) {
      const node = this.shadowRoot;
      options = options || {};
      detail = (detail === null || detail === undefined) ? {} : detail;
      const event = new Event(type, {
        bubbles: options.bubbles === undefined ? true : options.bubbles,
        cancelable: Boolean(options.cancelable),
        composed: options.composed === undefined ? true : options.composed
      });
      event.detail = detail;
      node.dispatchEvent(event);
      return event;
    }
  
    getCardSize() {
      return 2;
    }
  }
  
  customElements.define('tide-card', TideCard);