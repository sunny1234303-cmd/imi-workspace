figma.showUI(__html__, { width: 420, height: 560, title: 'Markdown → Figma' });

// 폰트 미리 로드
async function loadFonts() {
  await Promise.all([
    figma.loadFontAsync({ family: 'Inter', style: 'Regular' }),
    figma.loadFontAsync({ family: 'Inter', style: 'Bold' }),
    figma.loadFontAsync({ family: 'Inter', style: 'Medium' }),
  ]);
}

figma.ui.onmessage = async (msg) => {
  if (msg.type === 'cancel') {
    figma.closePlugin();
    return;
  }

  if (msg.type === 'insert') {
    try {
      await loadFonts();
      const frame = await buildFrame(msg.blocks, msg.filename);
      figma.currentPage.appendChild(frame);
      figma.viewport.scrollAndZoomIntoView([frame]);
      figma.ui.postMessage({ type: 'done' });
      figma.closePlugin('✅ 삽입 완료!');
    } catch (e) {
      figma.ui.postMessage({ type: 'error', message: e.message });
    }
  }
};

// ─── 메인 프레임 생성 ───────────────────────────────────────────────────────
async function buildFrame(blocks, filename) {
  const FRAME_WIDTH = 800;
  const PADDING = 56;

  const frame = figma.createFrame();
  frame.name = filename || 'Markdown Content';
  frame.layoutMode = 'VERTICAL';
  frame.primaryAxisSizingMode = 'AUTO';
  frame.counterAxisSizingMode = 'FIXED';
  frame.resize(FRAME_WIDTH, 100);
  frame.paddingTop = PADDING;
  frame.paddingBottom = PADDING;
  frame.paddingLeft = PADDING;
  frame.paddingRight = PADDING;
  frame.itemSpacing = 0;
  frame.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];

  for (const block of blocks) {
    const node = await createNode(block, FRAME_WIDTH - PADDING * 2);
    if (node) {
      frame.appendChild(node);
    }
  }

  return frame;
}

// ─── 블록 → Figma 노드 ──────────────────────────────────────────────────────
async function createNode(block, innerWidth) {
  switch (block.type) {
    case 'h1': return makeText(block.text, 40, 'Bold', innerWidth, 24);
    case 'h2': return makeText(block.text, 28, 'Bold', innerWidth, 20);
    case 'h3': return makeText(block.text, 20, 'Medium', innerWidth, 16);
    case 'paragraph': return makeText(block.text, 16, 'Regular', innerWidth, 12);
    case 'list': return makeList(block.items, block.ordered, innerWidth);
    case 'divider': return makeDivider(innerWidth);
    case 'table': return makeTable(block.headers, block.rows, innerWidth);
    case 'spacer': return makeSpacer(block.height);
    default: return null;
  }
}

// ─── 텍스트 노드 ────────────────────────────────────────────────────────────
function makeText(text, size, style, width, bottomSpacing) {
  const wrapper = figma.createFrame();
  wrapper.name = text.slice(0, 30);
  wrapper.layoutMode = 'VERTICAL';
  wrapper.primaryAxisSizingMode = 'AUTO';
  wrapper.counterAxisSizingMode = 'FIXED';
  wrapper.resize(width, 10);
  wrapper.fills = [];
  wrapper.paddingBottom = bottomSpacing;

  const t = figma.createText();
  t.fontName = { family: 'Inter', style: style };
  t.fontSize = size;
  t.characters = text;
  t.layoutAlign = 'STRETCH';
  t.textAutoResize = 'HEIGHT';

  if (style === 'Bold' && size >= 28) {
    t.fills = [{ type: 'SOLID', color: { r: 0.08, g: 0.08, b: 0.08 } }];
  } else {
    t.fills = [{ type: 'SOLID', color: { r: 0.2, g: 0.2, b: 0.2 } }];
  }

  wrapper.appendChild(t);
  return wrapper;
}

// ─── 리스트 ─────────────────────────────────────────────────────────────────
function makeList(items, ordered, width) {
  const container = figma.createFrame();
  container.name = 'List';
  container.layoutMode = 'VERTICAL';
  container.primaryAxisSizingMode = 'AUTO';
  container.counterAxisSizingMode = 'FIXED';
  container.resize(width, 10);
  container.itemSpacing = 6;
  container.fills = [];
  container.paddingBottom = 12;

  items.forEach((item, i) => {
    const row = figma.createFrame();
    row.layoutMode = 'HORIZONTAL';
    row.primaryAxisSizingMode = 'AUTO';
    row.counterAxisSizingMode = 'AUTO';
    row.itemSpacing = 8;
    row.fills = [];
    row.name = `item-${i}`;

    const bullet = figma.createText();
    bullet.fontName = { family: 'Inter', style: 'Regular' };
    bullet.fontSize = 16;
    bullet.characters = ordered ? `${i + 1}.` : '•';
    bullet.fills = [{ type: 'SOLID', color: { r: 0.5, g: 0.5, b: 0.5 } }];
    bullet.textAutoResize = 'WIDTH_AND_HEIGHT';

    const text = figma.createText();
    text.fontName = { family: 'Inter', style: 'Regular' };
    text.fontSize = 16;
    text.characters = item;
    text.fills = [{ type: 'SOLID', color: { r: 0.2, g: 0.2, b: 0.2 } }];
    text.textAutoResize = 'WIDTH_AND_HEIGHT';

    row.appendChild(bullet);
    row.appendChild(text);
    container.appendChild(row);
  });

  return container;
}

// ─── 구분선 ─────────────────────────────────────────────────────────────────
function makeDivider(width) {
  const wrapper = figma.createFrame();
  wrapper.layoutMode = 'VERTICAL';
  wrapper.primaryAxisSizingMode = 'AUTO';
  wrapper.counterAxisSizingMode = 'FIXED';
  wrapper.resize(width, 1);
  wrapper.fills = [];
  wrapper.paddingTop = 8;
  wrapper.paddingBottom = 16;
  wrapper.name = 'Divider';

  const line = figma.createRectangle();
  line.resize(width, 1);
  line.fills = [{ type: 'SOLID', color: { r: 0.85, g: 0.85, b: 0.85 } }];
  wrapper.appendChild(line);
  return wrapper;
}

// ─── 표(Table) ──────────────────────────────────────────────────────────────
function makeTable(headers, rows, width) {
  const colCount = headers.length;
  const colWidth = Math.floor(width / colCount);
  const ROW_HEIGHT = 44;

  const tableFrame = figma.createFrame();
  tableFrame.name = 'Table';
  tableFrame.layoutMode = 'VERTICAL';
  tableFrame.primaryAxisSizingMode = 'AUTO';
  tableFrame.counterAxisSizingMode = 'AUTO';
  tableFrame.itemSpacing = 0;
  tableFrame.fills = [];
  tableFrame.paddingBottom = 16;
  tableFrame.strokes = [{ type: 'SOLID', color: { r: 0.8, g: 0.8, b: 0.8 } }];
  tableFrame.strokeWeight = 1;
  tableFrame.cornerRadius = 4;
  tableFrame.clipsContent = true;

  const allRows = [{ cells: headers, isHeader: true }, ...rows.map(r => ({ cells: r, isHeader: false }))];

  allRows.forEach(({ cells, isHeader }, rowIdx) => {
    const rowFrame = figma.createFrame();
    rowFrame.layoutMode = 'HORIZONTAL';
    rowFrame.primaryAxisSizingMode = 'AUTO';
    rowFrame.counterAxisSizingMode = 'AUTO';
    rowFrame.itemSpacing = 0;
    rowFrame.fills = isHeader
      ? [{ type: 'SOLID', color: { r: 0.96, g: 0.96, b: 0.97 } }]
      : rowIdx % 2 === 0
        ? [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]
        : [{ type: 'SOLID', color: { r: 0.99, g: 0.99, b: 0.99 } }];
    rowFrame.name = isHeader ? 'Header' : `Row ${rowIdx}`;

    if (!isHeader) {
      rowFrame.strokes = [{ type: 'SOLID', color: { r: 0.88, g: 0.88, b: 0.88 } }];
      rowFrame.strokeWeight = 1;
      rowFrame.strokeTopWeight = 1;
      rowFrame.strokeBottomWeight = 0;
      rowFrame.strokeLeftWeight = 0;
      rowFrame.strokeRightWeight = 0;
    }

    cells.forEach((cell, colIdx) => {
      const cellFrame = figma.createFrame();
      cellFrame.layoutMode = 'VERTICAL';
      cellFrame.primaryAxisAlignItems = 'CENTER';
      cellFrame.primaryAxisSizingMode = 'FIXED';
      cellFrame.counterAxisSizingMode = 'FIXED';
      cellFrame.resize(colWidth, ROW_HEIGHT);
      cellFrame.paddingLeft = 14;
      cellFrame.paddingRight = 14;
      cellFrame.paddingTop = 10;
      cellFrame.paddingBottom = 10;
      cellFrame.fills = [];
      if (colIdx > 0) {
        cellFrame.strokes = [{ type: 'SOLID', color: { r: 0.88, g: 0.88, b: 0.88 } }];
        cellFrame.strokeWeight = 1;
        cellFrame.strokeTopWeight = 0;
        cellFrame.strokeBottomWeight = 0;
        cellFrame.strokeLeftWeight = 1;
        cellFrame.strokeRightWeight = 0;
      }

      const t = figma.createText();
      t.fontName = { family: 'Inter', style: isHeader ? 'Bold' : 'Regular' };
      t.fontSize = 14;
      t.characters = cell || '';
      t.layoutAlign = 'STRETCH';
      t.textAutoResize = 'HEIGHT';
      t.fills = [{ type: 'SOLID', color: { r: 0.15, g: 0.15, b: 0.15 } }];

      cellFrame.appendChild(t);
      rowFrame.appendChild(cellFrame);
    });

    tableFrame.appendChild(rowFrame);
  });

  return tableFrame;
}

// ─── 빈 공간 ────────────────────────────────────────────────────────────────
function makeSpacer(height) {
  const spacer = figma.createFrame();
  spacer.resize(10, height);
  spacer.fills = [];
  spacer.name = 'Spacer';
  return spacer;
}
