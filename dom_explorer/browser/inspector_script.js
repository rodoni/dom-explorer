/**
 * DOM Explorer Injected Inspector Overlay Script
 * Injected into the browser page to provide interactive element selection and metadata extraction.
 */
(() => {
  if (window.__domExplorerInitialized) {
    return;
  }
  window.__domExplorerInitialized = true;

  window.__domExplorerSelection = null;
  window.__domExplorerHistory = [];
  window.__domExplorerActive = true;

  // Create UI elements: Overlay, Tooltip, and Floating Control Bar
  const overlayBox = document.createElement('div');
  overlayBox.id = '__dom_explorer_overlay';
  overlayBox.style.cssText = `
    position: fixed;
    pointer-events: none;
    border: 2px solid #0284c7;
    background-color: rgba(2, 132, 199, 0.18);
    z-index: 2147483640;
    transition: all 0.05s ease-out;
    display: none;
    box-sizing: border-box;
  `;

  const tooltip = document.createElement('div');
  tooltip.id = '__dom_explorer_tooltip';
  tooltip.style.cssText = `
    position: fixed;
    pointer-events: none;
    background: #0f172a;
    color: #f8fafc;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 11px;
    line-height: 1.4;
    padding: 6px 10px;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    z-index: 2147483641;
    display: none;
    max-width: 380px;
    word-break: break-word;
    border: 1px solid #334155;
  `;

  const controlBar = document.createElement('div');
  controlBar.id = '__dom_explorer_controls';
  controlBar.style.cssText = `
    position: fixed;
    bottom: 12px;
    right: 12px;
    background: #0f172a;
    color: #f8fafc;
    padding: 8px 14px;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 12px;
    z-index: 2147483645;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1px solid #38bdf8;
    user-select: none;
  `;

  controlBar.innerHTML = `
    <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#22c55e;" id="__dom_explorer_status_dot"></span>
    <span id="__dom_explorer_status_text" style="font-weight:600; color:#38bdf8;">DOM Explorer: Inspetor Ativo</span>
    <button id="__dom_explorer_toggle_btn" style="
      background: #1e293b;
      color: #f8fafc;
      border: 1px solid #475569;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 11px;
    ">Pausar (Navegar)</button>
  `;

  // Attach to DOM once document body is ready
  const attachUI = () => {
    if (document.body && !document.getElementById('__dom_explorer_overlay')) {
      document.body.appendChild(overlayBox);
      document.body.appendChild(tooltip);
      document.body.appendChild(controlBar);

      const toggleBtn = document.getElementById('__dom_explorer_toggle_btn');
      const statusDot = document.getElementById('__dom_explorer_status_dot');
      const statusText = document.getElementById('__dom_explorer_status_text');

      if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          window.__domExplorerActive = !window.__domExplorerActive;
          if (window.__domExplorerActive) {
            statusDot.style.background = '#22c55e';
            statusText.innerText = 'DOM Explorer: Inspetor Ativo';
            toggleBtn.innerText = 'Pausar (Navegar)';
            controlBar.style.borderColor = '#38bdf8';
          } else {
            statusDot.style.background = '#f59e0b';
            statusText.innerText = 'DOM Explorer: Navegação Livre';
            toggleBtn.innerText = 'Ativar Inspeção';
            controlBar.style.borderColor = '#f59e0b';
            overlayBox.style.display = 'none';
            tooltip.style.display = 'none';
          }
        });
      }
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachUI);
  } else {
    attachUI();
  }

  // Helper to compute element XPath
  const computeXPath = (element) => {
    if (!element || element.nodeType !== Node.ELEMENT_NODE) return '';
    if (element.id) {
      return `//*[@id="${element.id}"]`;
    }
    const parts = [];
    let current = element;
    while (current && current.nodeType === Node.ELEMENT_NODE && current !== document.documentElement) {
      let count = 0;
      let sibling = current.previousElementSibling;
      while (sibling) {
        if (sibling.nodeName === current.nodeName) {
          count++;
        }
        sibling = sibling.previousElementSibling;
      }
      const tag = current.nodeName.toLowerCase();
      const part = count > 0 ? `${tag}[${count + 1}]` : tag;
      parts.unshift(part);
      current = current.parentElement;
    }
    return '/' + parts.join('/');
  };

  // Helper to extract full metadata from an element
  const extractElementMetadata = (el) => {
    if (!el || el.nodeType !== Node.ELEMENT_NODE) return null;

    const rect = el.getBoundingClientRect();
    const tag = el.tagName.toLowerCase();
    const id = el.id || '';
    const name = el.getAttribute('name') || '';
    const type = el.getAttribute('type') || (tag === 'input' ? 'text' : '');
    const placeholder = el.getAttribute('placeholder') || '';
    const role = el.getAttribute('role') || '';
    const ariaLabel = el.getAttribute('aria-label') || '';
    const textContent = (el.innerText || el.textContent || '').trim().slice(0, 150);

    // Collect all attributes
    const attributes = {};
    for (let i = 0; i < el.attributes.length; i++) {
      const attr = el.attributes[i];
      attributes[attr.name] = attr.value;
    }

    // Common test ID attributes
    const testId = el.getAttribute('data-testid') || 
                   el.getAttribute('data-test') || 
                   el.getAttribute('data-cy') || 
                   el.getAttribute('data-qa') || '';

    // Class list
    const classList = Array.from(el.classList);

    // Parent hierarchy
    const hierarchy = [];
    let parent = el.parentElement;
    let depth = 0;
    while (parent && depth < 3 && parent !== document.documentElement) {
      hierarchy.push({
        tag: parent.tagName.toLowerCase(),
        id: parent.id || null,
        className: parent.className && typeof parent.className === 'string' ? parent.className : null
      });
      parent = parent.parentElement;
      depth++;
    }

    // Unique CSS selector attempt
    let uniqueCss = tag;
    if (id) {
      uniqueCss = `#${CSS.escape(id)}`;
    } else if (testId) {
      uniqueCss = `[data-testid="${testId}"]`;
    } else if (name) {
      uniqueCss = `${tag}[name="${name}"]`;
    }

    return {
      tag,
      id,
      name,
      type,
      placeholder,
      role,
      ariaLabel,
      testId,
      text: textContent,
      classList,
      attributes,
      hierarchy,
      xpath: computeXPath(el),
      cssSelector: uniqueCss,
      boundingBox: {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        width: Math.round(rect.width),
        height: Math.round(rect.height)
      },
      isInteractable: !el.disabled && el.offsetParent !== null,
      timestamp: Date.now()
    };
  };

  // Hover listener
  document.addEventListener('mouseover', (e) => {
    if (!window.__domExplorerActive) return;
    const target = e.target;
    if (!target || target === overlayBox || target === tooltip || controlBar.contains(target)) {
      return;
    }

    const rect = target.getBoundingClientRect();
    overlayBox.style.display = 'block';
    overlayBox.style.top = `${rect.top}px`;
    overlayBox.style.left = `${rect.left}px`;
    overlayBox.style.width = `${rect.width}px`;
    overlayBox.style.height = `${rect.height}px`;

    const tag = target.tagName.toLowerCase();
    const id = target.id ? `#${target.id}` : '';
    const testId = target.getAttribute('data-testid') || target.getAttribute('data-test') || target.getAttribute('data-cy');
    const role = target.getAttribute('role');
    const textSnippet = (target.innerText || target.textContent || '').trim().slice(0, 40);

    let infoHtml = `<strong style="color:#38bdf8;">&lt;${tag}${id}&gt;</strong>`;
    if (testId) infoHtml += ` <span style="color:#a78bfa;">[data-testid="${testId}"]</span>`;
    if (role) infoHtml += ` <span style="color:#f472b6;">role="${role}"</span>`;
    if (textSnippet) infoHtml += `<div style="color:#94a3b8; font-size:10px; margin-top:2px;">"${textSnippet}"</div>`;

    tooltip.innerHTML = infoHtml;
    tooltip.style.display = 'block';

    // Position tooltip above or below
    let tooltipTop = rect.top - 36;
    if (tooltipTop < 10) {
      tooltipTop = rect.bottom + 8;
    }
    let tooltipLeft = Math.max(10, Math.min(rect.left, window.innerWidth - 390));
    tooltip.style.top = `${tooltipTop}px`;
    tooltip.style.left = `${tooltipLeft}px`;
  }, true);

  // Click / Selection listener
  document.addEventListener('click', (e) => {
    if (!window.__domExplorerActive) return;
    const target = e.target;
    if (!target || target === overlayBox || target === tooltip || controlBar.contains(target)) {
      return;
    }

    // Intercept event to prevent navigation
    e.preventDefault();
    e.stopPropagation();

    // Visual feedback for selection (flash green)
    overlayBox.style.borderColor = '#22c55e';
    overlayBox.style.backgroundColor = 'rgba(34, 197, 94, 0.25)';
    setTimeout(() => {
      overlayBox.style.borderColor = '#0284c7';
      overlayBox.style.backgroundColor = 'rgba(2, 132, 199, 0.18)';
    }, 400);

    const metadata = extractElementMetadata(target);
    window.__domExplorerSelection = metadata;
    window.__domExplorerHistory.push(metadata);

    // Update control bar status
    const statusText = document.getElementById('__dom_explorer_status_text');
    if (statusText) {
      statusText.innerHTML = `Selecionado: <strong style="color:#f8fafc">&lt;${metadata.tag}${metadata.id ? '#' + metadata.id : ''}&gt;</strong>`;
    }

    // Custom notification event
    window.dispatchEvent(new CustomEvent('dom-explorer:element-selected', { detail: metadata }));
  }, true);

  // Expose global methods for Playwright bridge
  window.__domExplorerHighlight = (selector) => {
    try {
      const el = document.querySelector(selector);
      if (el) {
        const rect = el.getBoundingClientRect();
        overlayBox.style.display = 'block';
        overlayBox.style.borderColor = '#e11d48'; // Red/Pink highlight
        overlayBox.style.backgroundColor = 'rgba(225, 29, 72, 0.25)';
        overlayBox.style.top = `${rect.top}px`;
        overlayBox.style.left = `${rect.left}px`;
        overlayBox.style.width = `${rect.width}px`;
        overlayBox.style.height = `${rect.height}px`;
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => {
          overlayBox.style.borderColor = '#0284c7';
          overlayBox.style.backgroundColor = 'rgba(2, 132, 199, 0.18)';
        }, 2000);
        return true;
      }
      return false;
    } catch (err) {
      return false;
    }
  };

  console.log('[DOM Explorer] Inspector overlay loaded successfully.');
})();
