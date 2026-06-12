(function () {
  'use strict';

  const BTN_ID      = '__jc-float-btn__';
  const POPUP_ID    = '__jc-float-popup__';
  const DEFAULT_URL = 'http://localhost:3737';
  const DEFAULT_POS = { xPct: 97, yPct: 92 }; // 기본: 우측 하단

  if (document.getElementById(BTN_ID)) return;

  chrome.storage.sync.get({ serverUrl: DEFAULT_URL }, ({ serverUrl }) => {
    if (window.location.href.startsWith(serverUrl)) return;
    inject(serverUrl);
  });

  function inject(serverUrl) {
    // ── 버튼 ────────────────────────────────────────────────────────────────
    const btn = document.createElement('div');
    btn.id = BTN_ID;
    btn.setAttribute('title', 'Open Checklist (drag to move)');

    const label = document.createElement('span');
    label.className = '__jc-btn-label__';
    label.textContent = 'TODO';
    btn.appendChild(label);

    document.body.appendChild(btn);

    // ── 팝업 ────────────────────────────────────────────────────────────────
    const popup = document.createElement('div');
    popup.id = POPUP_ID;
    popup.innerHTML = `<iframe src="${serverUrl}" allowtransparency="true"></iframe>`;

    const resizeHandle = document.createElement('div');
    resizeHandle.id = '__jc-float-resize__';
    popup.appendChild(resizeHandle);

    document.body.appendChild(popup);

    // ── 크기 초기화 ─────────────────────────────────────────────────────────
    let popupW = null;  // null → 뷰포트 기본값
    let popupH = null;

    // ── 위치·크기 초기화 ────────────────────────────────────────────────────
    chrome.storage.sync.get(
      { btnXPct: DEFAULT_POS.xPct, btnYPct: DEFAULT_POS.yPct, popupW: null, popupH: null },
      ({ btnXPct, btnYPct, popupW: sw, popupH: sh }) => {
        applyPosition(btn, pctToPos(btnXPct, btnYPct));
        if (sw !== null) popupW = sw;
        if (sh !== null) popupH = sh;
      }
    );

    // ── 팝업 리사이즈 ───────────────────────────────────────────────────────
    let resizing = false, rsX, rsY, rsW, rsH;

    resizeHandle.addEventListener('pointerdown', e => {
      e.stopPropagation();
      e.preventDefault();
      resizing = true;
      rsX = e.clientX; rsY = e.clientY;
      rsW = popup.offsetWidth; rsH = popup.offsetHeight;
      resizeHandle.setPointerCapture(e.pointerId);
      const ifrm = popup.querySelector('iframe');
      if (ifrm) ifrm.style.setProperty('pointer-events', 'none', 'important');
    });

    resizeHandle.addEventListener('pointermove', e => {
      if (!resizing) return;
      popupW = clamp(rsW + (e.clientX - rsX), 320, window.innerWidth  - 48);
      popupH = clamp(rsH + (e.clientY - rsY), 400, window.innerHeight - 48);
      popup.style.setProperty('width',  `${popupW}px`, 'important');
      popup.style.setProperty('height', `${popupH}px`, 'important');
    });

    resizeHandle.addEventListener('pointerup', () => {
      if (!resizing) return;
      resizing = false;
      const ifrm = popup.querySelector('iframe');
      if (ifrm) ifrm.style.removeProperty('pointer-events');
      chrome.storage.sync.set({ popupW, popupH });
    });

    // ── 팝업 토글 ───────────────────────────────────────────────────────────
    let isOpen = false;

    const openPopup = () => {
      isOpen = true;
      positionPopup();
      popup.classList.remove('closing');
      popup.classList.add('open');
      btn.classList.add('active');
    };

    const closePopup = () => {
      if (!isOpen) return;
      isOpen = false;
      btn.classList.remove('active');
      popup.classList.add('closing');
      popup.addEventListener('animationend', () => {
        popup.classList.remove('open', 'closing');
      }, { once: true });
    };

    document.addEventListener('click', (e) => { if (isOpen && !popup.contains(e.target) && !btn.contains(e.target)) closePopup(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isOpen) closePopup(); });

    // ── 드래그 ──────────────────────────────────────────────────────────────
    let dragging   = false;
    let dragMoved  = false;
    let startMouseX, startMouseY, startBtnX, startBtnY;

    btn.addEventListener('pointerdown', (e) => {
      e.stopPropagation();
      dragging   = true;
      dragMoved  = false;
      startMouseX = e.clientX;
      startMouseY = e.clientY;
      const r = btn.getBoundingClientRect();
      startBtnX = r.left;
      startBtnY = r.top;
      btn.setPointerCapture(e.pointerId);
      btn.classList.add('dragging');
    });

    btn.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      const dx = e.clientX - startMouseX;
      const dy = e.clientY - startMouseY;
      if (!dragMoved && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) dragMoved = true;
      if (!dragMoved) return;

      const bw = btn.offsetWidth;
      const bh = btn.offsetHeight;
      const newX = clamp(startBtnX + dx, 0, window.innerWidth  - bw);
      const newY = clamp(startBtnY + dy, 0, window.innerHeight - bh);
      applyPosition(btn, { x: newX, y: newY });
      if (isOpen) positionPopup();
    });

    btn.addEventListener('pointerup', (e) => {
      if (!dragging) return;
      dragging = false;
      btn.classList.remove('dragging');

      if (dragMoved) {
        // 가장 가까운 가로 끝으로 스냅
        const bw  = btn.offsetWidth;
        const bh  = btn.offsetHeight;
        const cur = btn.getBoundingClientRect();
        const snapX = cur.left + bw / 2 < window.innerWidth / 2
          ? 8
          : window.innerWidth - bw - 8;
        const finalY = clamp(cur.top, 8, window.innerHeight - bh - 8);

        btn.classList.add('snapping');
        applyPosition(btn, { x: snapX, y: finalY });
        btn.addEventListener('transitionend', () => btn.classList.remove('snapping'), { once: true });

        // 위치 저장 (% 단위)
        const xPct = snapX / window.innerWidth  * 100;
        const yPct = finalY / window.innerHeight * 100;
        chrome.storage.sync.set({ btnXPct: xPct, btnYPct: yPct });

        if (isOpen) positionPopup();
      } else {
        isOpen ? closePopup() : openPopup();
      }
    });

    // ── 팝업 위치 계산 ──────────────────────────────────────────────────────
    function positionPopup() {
      const br = btn.getBoundingClientRect();
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const pw = popupW !== null ? clamp(popupW, 320, vw - 48) : Math.min(800, vw - 48);
      const ph = popupH !== null ? clamp(popupH, 400, vh - 48) : Math.min(620, vh - 108);
      const gap = 10;

      // 가로: 버튼 오른쪽 정렬, 뷰포트 초과 시 왼쪽 정렬
      let left = br.right - pw;
      if (left < 8) left = br.left;
      left = clamp(left, 8, vw - pw - 8);

      // 세로: 버튼 위 or 아래 (공간 많은 쪽)
      let top;
      if (br.top - ph - gap >= 8) {
        top = br.top - ph - gap;           // 위
      } else {
        top = br.bottom + gap;             // 아래
      }
      top = clamp(top, 8, vh - ph - 8);

      popup.style.cssText += `
        left: ${left}px !important;
        top:  ${top}px !important;
        right:  auto !important;
        bottom: auto !important;
        width:  ${pw}px !important;
        height: ${ph}px !important;
      `;
    }

  }

  // ── 유틸 ──────────────────────────────────────────────────────────────────
  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  function pctToPos(xPct, yPct) {
    return {
      x: xPct / 100 * window.innerWidth,
      y: yPct / 100 * window.innerHeight,
    };
  }

  function applyPosition(el, { x, y }) {
    el.style.setProperty('left',   `${x}px`, 'important');
    el.style.setProperty('top',    `${y}px`, 'important');
    el.style.setProperty('right',  'auto',   'important');
    el.style.setProperty('bottom', 'auto',   'important');
  }
})();
