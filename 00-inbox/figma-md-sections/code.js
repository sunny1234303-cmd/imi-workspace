figma.showUI(__html__, { width: 480, height: 580 });

figma.ui.onmessage = async function (msg) {
  if (msg.type === "generate") {
    await handleGenerate(msg);
  }
  if (msg.type === "close") {
    figma.closePlugin();
  }
};

async function handleGenerate(msg) {
  var markdown = msg.markdown;
  var splitLevel = Number(msg.splitLevel);
  var colorize = msg.colorize;

  var sections = parseMarkdown(markdown, splitLevel);

  if (sections.length === 0) {
    figma.ui.postMessage({
      type: "error",
      message: "H" + splitLevel + " 헤딩을 찾을 수 없습니다. 마크다운 형식을 확인하세요.",
    });
    return;
  }

  try {
    await loadFonts();
  } catch (e) {
    figma.ui.postMessage({ type: "error", message: "폰트 로드 실패: " + e.message });
    return;
  }

  try {
    var frames = createSections(sections, colorize);
    figma.viewport.scrollAndZoomIntoView(frames);
    figma.ui.postMessage({ type: "success", count: sections.length });
  } catch (e) {
    figma.ui.postMessage({ type: "error", message: "프레임 생성 실패: " + e.message });
  }
}

// ── MD 파싱 ──────────────────────────────────────────────────────────────

function parseMarkdown(md, level) {
  var prefix = "";
  for (var i = 0; i < level; i++) prefix += "#";

  var headingRe = new RegExp("^" + prefix + "(?!#) +(.+)", "gm");
  var matches = [];
  var match;

  while ((match = headingRe.exec(md)) !== null) {
    matches.push({
      title: match[1].trim(),
      index: match.index,
      end: match.index + match[0].length,
    });
  }

  var sizeRe = /<!--(\d+)px,(\d+)px-->/;
  var sections = [];
  for (var j = 0; j < matches.length; j++) {
    var title = matches[j].title;
    var end = matches[j].end;
    var nextIndex = matches[j + 1] ? matches[j + 1].index : md.length;
    var content = md.slice(end, nextIndex).trim();

    var sizeMatch = title.match(sizeRe);
    var width  = sizeMatch ? Number(sizeMatch[1]) : 800;
    var height = sizeMatch ? Number(sizeMatch[2]) : 600;
    title = title.replace(sizeRe, "").trim();

    sections.push({ title: title, content: content, width: width, height: height });
  }

  return sections;
}

// ── Figma 프레임 생성 ────────────────────────────────────────────────────

var FRAME_WIDTH = 800; // fallback 기본값
var PADDING = 40;
var FRAME_GAP = 32;

var PASTEL_COLORS = [
  { r: 0.953, g: 0.941, b: 1.0 },
  { r: 0.922, g: 0.961, b: 1.0 },
  { r: 0.929, g: 1.0,   b: 0.957 },
  { r: 1.0,   g: 0.988, b: 0.922 },
  { r: 1.0,   g: 0.941, b: 0.941 },
  { r: 0.902, g: 1.0,   b: 0.980 },
];

function createSections(sections, colorize) {
  var frames = [];
  var xOffset = 0;

  for (var i = 0; i < sections.length; i++) {
    var bgColor = colorize ? PASTEL_COLORS[i % PASTEL_COLORS.length] : null;
    var frame = buildFrame(sections[i].title, sections[i].content, bgColor, sections[i].width);
    frame.x = xOffset;
    frame.y = 0;
    figma.currentPage.appendChild(frame);
    xOffset += frame.width + FRAME_GAP;
    frames.push(frame);
  }

  return frames;
}

function buildFrame(title, content, bgColor, frameWidth) {
  var width = frameWidth || FRAME_WIDTH;
  var frame = figma.createFrame();
  frame.name = title;
  frame.resize(width, 100);
  frame.layoutMode = "VERTICAL";
  frame.primaryAxisSizingMode = "AUTO";
  frame.counterAxisSizingMode = "FIXED";
  frame.paddingLeft = PADDING;
  frame.paddingRight = PADDING;
  frame.paddingTop = PADDING;
  frame.paddingBottom = PADDING;
  frame.itemSpacing = 16;
  frame.cornerRadius = 16;
  frame.fills = [{ type: "SOLID", color: bgColor || { r: 1, g: 1, b: 1 } }];

  // 제목 — layoutAlign은 appendChild 이후에 설정
  var titleNode = figma.createText();
  titleNode.fontName = FONT_BOLD;
  titleNode.fontSize = 24;
  titleNode.characters = title;
  titleNode.textAutoResize = "HEIGHT";
  frame.appendChild(titleNode);
  titleNode.layoutAlign = "STRETCH";

  // 구분선
  var divider = figma.createRectangle();
  divider.fills = [{ type: "SOLID", color: { r: 0, g: 0, b: 0 }, opacity: 0.08 }];
  frame.appendChild(divider);
  divider.layoutAlign = "STRETCH";
  divider.resize(divider.width, 1);

  // 본문
  if (content) {
    var bodyNode = figma.createText();
    bodyNode.fontName = FONT_REGULAR;
    bodyNode.fontSize = 14;
    bodyNode.lineHeight = { value: 160, unit: "PERCENT" };
    bodyNode.characters = content;
    bodyNode.textAutoResize = "HEIGHT";
    bodyNode.fills = [{ type: "SOLID", color: { r: 0.2, g: 0.2, b: 0.2 } }];
    frame.appendChild(bodyNode);
    bodyNode.layoutAlign = "STRETCH";
  }

  return frame;
}

// ── 폰트 로드 ────────────────────────────────────────────────────────────

var FONT_BOLD    = { family: "Inter", style: "Bold" };
var FONT_REGULAR = { family: "Inter", style: "Regular" };

async function loadFonts() {
  var candidates = [
    [{ family: "Inter", style: "Bold" },   { family: "Inter", style: "Regular" }],
    [{ family: "Roboto", style: "Bold" },  { family: "Roboto", style: "Regular" }],
    [{ family: "Noto Sans", style: "Bold" }, { family: "Noto Sans", style: "Regular" }],
  ];

  for (var i = 0; i < candidates.length; i++) {
    try {
      await figma.loadFontAsync(candidates[i][0]);
      await figma.loadFontAsync(candidates[i][1]);
      FONT_BOLD    = candidates[i][0];
      FONT_REGULAR = candidates[i][1];
      return;
    } catch (e) {
      // 다음 폰트 시도
    }
  }

  throw new Error("사용 가능한 폰트를 찾을 수 없습니다.");
}
