figma.showUI(__html__, { width: 460, height: 680, title: 'Markdown → Figma' });

// ─── 프리셋 ─────────────────────────────────────────────────────────────────
const PRESETS = {
  document: { width: 800,  padding: 56 },
  sns:      { width: 1080, padding: 80 },
  ad:       { width: 1200, padding: 72 },
  report:   { width: 1440, padding: 80 },
};

// ─── 테마 ────────────────────────────────────────────────────────────────────
const THEMES = {
  light: {
    bg:       { r: 1,    g: 1,    b: 1    },
    heading:  { r: 0.08, g: 0.08, b: 0.08 },
    text:     { r: 0.2,  g: 0.2,  b: 0.2  },
    muted:    { r: 0.5,  g: 0.5,  b: 0.5  },
    divider:  { r: 0.85, g: 0.85, b: 0.85 },
    tableHdr: { r: 0.96, g: 0.96, b: 0.97 },
    tableAlt: { r: 0.99, g: 0.99, b: 0.99 },
    tableRow: { r: 1,    g: 1,    b: 1    },
    border:   { r: 0.88, g: 0.88, b: 0.88 },
  },
  dark: {
    bg:       { r: 0.10, g: 0.10, b: 0.12 },
    heading:  { r: 1,    g: 1,    b: 1    },
    text:     { r: 0.85, g: 0.85, b: 0.85 },
    muted:    { r: 0.50, g: 0.50, b: 0.52 },
    divider:  { r: 0.25, g: 0.25, b: 0.27 },
    tableHdr: { r: 0.16, g: 0.16, b: 0.18 },
    tableAlt: { r: 0.13, g: 0.13, b: 0.15 },
    tableRow: { r: 0.11, g: 0.11, b: 0.13 },
    border:   { r: 0.25, g: 0.25, b: 0.27 },
  },
  brand: {
    bg:       { r: 0.486, g: 0.361, b: 0.988 },
    heading:  { r: 1,     g: 1,     b: 1     },
    text:     { r: 0.95,  g: 0.93,  b: 1     },
    muted:    { r: 0.75,  g: 0.68,  b: 0.98  },
    divider:  { r: 0.60,  g: 0.50,  b: 0.95  },
    tableHdr: { r: 0.40,  g: 0.28,  b: 0.85  },
    tableAlt: { r: 0.44,  g: 0.32,  b: 0.88  },
    tableRow: { r: 0.46,  g: 0.34,  b: 0.90  },
    border:   { r: 0.55,  g: 0.44,  b: 0.92  },
  },
};

// ─── 폰트 로드 ───────────────────────────────────────────────────────────────
async function loadFonts(family) {
  for (const style of ['Regular', 'Bold', 'Medium']) {
    try { await figma.loadFontAsync({ family, style }); } catch (_) {}
  }
}

// ─── 텍스트 노드 생성 헬퍼 ───────────────────────────────────────────────────
// 핵심: textAutoResize='HEIGHT' → resize(width) → characters 순서
function makeT(text, size, style, width, color, font) {
  const t = figma.createText();
  try { t.fontName = { family: font, style }; }
  catch (_) { t.fontName = { family: font, style: 'Regular' }; }
  t.fontSize = size;
  t.fills = [{ type: 'SOLID', color }];
  t.textAutoResize = 'HEIGHT';   // 1. 모드 먼저
  t.resize(width, 100);          // 2. 너비 고정
  t.characters = text || ' ';   // 3. 텍스트 마지막 → 높이 자동 계산
  return t;
}

// ─── 메시지 처리 ─────────────────────────────────────────────────────────────
figma.ui.onmessage = async (msg) => {
  if (msg.type === 'cancel') { figma.closePlugin(); return; }

  if (msg.type === 'insert') {
    const {
      files,
      contentType = 'document',
      theme       = 'light',
      fontFamily  = 'Inter',
      fontSize    = 16,
    } = msg;

    const palette = THEMES[theme] || THEMES.light;
    const preset  = PRESETS[contentType] || PRESETS.document;

    try {
      await loadFonts(fontFamily);

      const frames = [];
      let xOffset = 0;

      for (const file of files) {
        const frame = buildFrame(
          file.blocks, file.name, preset, palette, fontFamily, Number(fontSize)
        );
        frame.x = xOffset;
        frame.y = 0;
        figma.currentPage.appendChild(frame);
        xOffset += frame.width + 80;
        frames.push(frame);
      }

      figma.viewport.scrollAndZoomIntoView(frames);
      figma.closePlugin(`✅ ${frames.length}개 프레임 삽입 완료`);
    } catch (e) {
      figma.ui.postMessage({ type: 'error', message: e.message });
    }
  }
};

// ─── 메인 프레임 (절대좌표 배치) ──────────────────────────────────────────────
function buildFrame(blocks, filename, preset, palette, font, base) {
  const { width, padding } = preset;
  const inner = width - padding * 2;

  const frame = figma.createFrame();
  frame.name = filename || 'Markdown Content';
  frame.fills = [{ type: 'SOLID', color: palette.bg }];
  // auto-layout 없음 → 절대좌표로 배치

  let y = padding;

  for (const block of blocks) {
    const result = buildBlock(block, inner, palette, font, base);
    if (!result) continue;
    const { node, gap } = result;
    node.x = padding;
    node.y = y;
    frame.appendChild(node);
    y += node.height + gap;
  }

  frame.resize(width, y + padding);
  return frame;
}

// ─── 블록 → { node, gap } ────────────────────────────────────────────────────
function buildBlock(block, inner, palette, font, base) {
  switch (block.type) {
    case 'h1':
      return { node: makeT(block.text, Math.round(base * 2.25), 'Bold',    inner, palette.heading, font), gap: 20 };
    case 'h2':
      return { node: makeT(block.text, Math.round(base * 1.5),  'Bold',    inner, palette.heading, font), gap: 16 };
    case 'h3':
      return { node: makeT(block.text, Math.round(base * 1.15), 'Medium',  inner, palette.text,    font), gap: 12 };
    case 'paragraph':
      return { node: makeT(block.text, base, 'Regular', inner, palette.text, font), gap: 12 };
    case 'list':
      return makeList(block.items, block.ordered, inner, palette, font, base);
    case 'divider':
      return makeDivider(inner, palette);
    case 'table':
      return makeTable(block.headers, block.rows, inner, palette, font, base);
    case 'spacer':
      return makeSpacer(block.height || 16);
    default:
      return null;
  }
}

// ─── 리스트 (절대좌표) ────────────────────────────────────────────────────────
function makeList(items, ordered, width, palette, font, base) {
  const BULLET_W = ordered ? 26 : 16;
  const GAP      = 8;
  const TEXT_W   = width - BULLET_W - GAP;
  const ROW_GAP  = Math.round(base * 0.4);

  const container = figma.createFrame();
  container.name = 'List';
  container.fills = [];
  container.clipsContent = false;

  let y = 0;

  items.forEach((item, i) => {
    // 불릿
    const bullet = figma.createText();
    try { bullet.fontName = { family: font, style: 'Regular' }; }
    catch (_) { bullet.fontName = { family: font, style: 'Regular' }; }
    bullet.fontSize = base;
    bullet.fills = [{ type: 'SOLID', color: palette.muted }];
    bullet.textAutoResize = 'WIDTH_AND_HEIGHT';
    bullet.characters = ordered ? `${i + 1}.` : '•';
    bullet.x = 0;
    bullet.y = y;
    container.appendChild(bullet);

    // 내용
    const text = makeT(item, base, 'Regular', TEXT_W, palette.text, font);
    text.x = BULLET_W + GAP;
    text.y = y;
    container.appendChild(text);

    y += Math.max(bullet.height, text.height) + ROW_GAP;
  });

  container.resize(width, Math.max(y, 1));
  return { node: container, gap: 12 };
}

// ─── 구분선 ──────────────────────────────────────────────────────────────────
function makeDivider(width, palette) {
  const line = figma.createRectangle();
  line.name = 'Divider';
  line.resize(width, 1);
  line.fills = [{ type: 'SOLID', color: palette.divider }];
  return { node: line, gap: 16 };
}

// ─── 표 (절대좌표) ────────────────────────────────────────────────────────────
function makeTable(headers, rows, width, palette, font, base) {
  const colCount  = Math.max(headers.length, 1);
  const colWidth  = Math.floor(width / colCount);
  const CELL_PAD  = 12;
  const FONT_SIZE = Math.round(base * 0.875);
  const MIN_ROW_H = Math.round(base * 2.5);

  const tableFrame = figma.createFrame();
  tableFrame.name = 'Table';
  tableFrame.fills = [];
  tableFrame.clipsContent = true;
  tableFrame.strokes = [{ type: 'SOLID', color: palette.border }];
  tableFrame.strokeWeight = 1;
  tableFrame.cornerRadius = 4;

  const allRows = [
    { cells: headers, isHeader: true },
    ...rows.map(r => ({ cells: r, isHeader: false })),
  ];

  let rowY = 0;

  allRows.forEach(({ cells, isHeader }, rowIdx) => {
    // 각 셀의 텍스트를 먼저 만들어 최대 높이 계산
    const textNodes = cells.map((cell) => {
      return makeT(
        cell || ' ',
        FONT_SIZE,
        isHeader ? 'Bold' : 'Regular',
        colWidth - CELL_PAD * 2,
        isHeader ? palette.heading : palette.text,
        font
      );
    });

    const rowH = Math.max(
      MIN_ROW_H,
      ...textNodes.map(t => t.height + CELL_PAD * 2)
    );

    // 행 배경
    const rowBg = figma.createRectangle();
    rowBg.resize(width, rowH);
    rowBg.fills = [{
      type: 'SOLID',
      color: isHeader
        ? palette.tableHdr
        : (rowIdx % 2 === 0 ? palette.tableRow : palette.tableAlt),
    }];
    rowBg.x = 0;
    rowBg.y = rowY;
    tableFrame.appendChild(rowBg);

    // 행 구분선 (헤더 아래 제외)
    if (rowIdx > 0) {
      const border = figma.createRectangle();
      border.resize(width, 1);
      border.fills = [{ type: 'SOLID', color: palette.border }];
      border.x = 0;
      border.y = rowY;
      tableFrame.appendChild(border);
    }

    // 셀
    textNodes.forEach((t, colIdx) => {
      t.x = colIdx * colWidth + CELL_PAD;
      t.y = rowY + CELL_PAD;
      tableFrame.appendChild(t);

      // 열 구분선
      if (colIdx > 0) {
        const vLine = figma.createRectangle();
        vLine.resize(1, rowH);
        vLine.fills = [{ type: 'SOLID', color: palette.border }];
        vLine.x = colIdx * colWidth;
        vLine.y = rowY;
        tableFrame.appendChild(vLine);
      }
    });

    rowY += rowH;
  });

  tableFrame.resize(width, rowY);
  return { node: tableFrame, gap: 16 };
}

// ─── 스페이서 ─────────────────────────────────────────────────────────────────
function makeSpacer(height) {
  const s = figma.createFrame();
  s.name = 'Spacer';
  s.resize(10, height);
  s.fills = [];
  return { node: s, gap: 0 };
}
