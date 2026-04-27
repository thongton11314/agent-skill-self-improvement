const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto('https://thongton11314.github.io/agent-skill-self-improvement/#overview', { waitUntil: 'networkidle' });

  const issues = [];

  // 1. Check all section titles are centered
  const sectionTitles = await page.$$eval('.section-title', els => els.map(el => {
    const s = getComputedStyle(el);
    return { text: el.textContent.trim(), textAlign: s.textAlign, tag: el.tagName };
  }));
  for (const t of sectionTitles) {
    if (t.textAlign !== 'center') {
      issues.push(`TITLE NOT CENTERED: "${t.text}" has textAlign="${t.textAlign}"`);
    }
  }

  // 2. Check all section subtitles are centered
  const subtitles = await page.$$eval('.section-subtitle', els => els.map(el => {
    const s = getComputedStyle(el);
    return { text: el.textContent.trim().substring(0, 50), textAlign: s.textAlign };
  }));
  for (const t of subtitles) {
    if (t.textAlign !== 'center') {
      issues.push(`SUBTITLE NOT CENTERED: "${t.text}" has textAlign="${t.textAlign}"`);
    }
  }

  // 3. Check container max-widths are consistent
  const containers = await page.$$eval('.container', els => els.map(el => {
    const s = getComputedStyle(el);
    const parent = el.parentElement;
    return { 
      parentClass: parent.className.substring(0, 40),
      maxWidth: s.maxWidth,
      paddingLeft: s.paddingLeft,
      paddingRight: s.paddingRight,
    };
  }));
  const uniqueMaxWidths = [...new Set(containers.map(c => c.maxWidth))];
  if (uniqueMaxWidths.length > 1) {
    issues.push(`INCONSISTENT CONTAINER MAX-WIDTH: ${uniqueMaxWidths.join(', ')} found across ${containers.length} containers`);
  }
  const uniquePaddings = [...new Set(containers.map(c => `${c.paddingLeft}/${c.paddingRight}`))];
  if (uniquePaddings.length > 1) {
    issues.push(`INCONSISTENT CONTAINER PADDING: ${uniquePaddings.join(', ')}`);
  }

  // 4. Check grid cards have equal heights within rows
  const gridSections = [
    { selector: '.problem-card', name: 'Problem Cards' },
    { selector: '.metric-card', name: 'Metric Cards' },
    { selector: '.integration-card', name: 'Integration Cards' },
    { selector: '.agent-card', name: 'Agent Cards' },
    { selector: '.protocol-card', name: 'Protocol Cards' },
  ];

  for (const { selector, name } of gridSections) {
    const cards = await page.$$eval(selector, els => els.map(el => {
      const rect = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return { top: Math.round(rect.top), height: Math.round(rect.height), width: Math.round(rect.width), padding: s.padding };
    }));
    
    // Group cards by row (same top position, within 5px tolerance)
    const rows = {};
    for (const c of cards) {
      const rowKey = Math.round(c.top / 10) * 10;
      if (!rows[rowKey]) rows[rowKey] = [];
      rows[rowKey].push(c);
    }
    
    for (const [rowTop, rowCards] of Object.entries(rows)) {
      const heights = rowCards.map(c => c.height);
      const maxH = Math.max(...heights);
      const minH = Math.min(...heights);
      if (maxH - minH > 10) {
        issues.push(`UNEVEN CARD HEIGHTS in ${name} (row ~${rowTop}px): heights ${heights.join(', ')}px — diff ${maxH - minH}px`);
      }
    }
  }

  // 5. Check comparison cards (Human vs AI) alignment
  const compCards = await page.$$eval('.comparison-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { top: Math.round(rect.top), height: Math.round(rect.height), width: Math.round(rect.width), className: el.className };
  }));
  if (compCards.length === 2) {
    if (Math.abs(compCards[0].top - compCards[1].top) > 5) {
      issues.push(`COMPARISON CARDS MISALIGNED: tops at ${compCards[0].top}px and ${compCards[1].top}px`);
    }
    if (Math.abs(compCards[0].height - compCards[1].height) > 10) {
      issues.push(`COMPARISON CARDS UNEVEN HEIGHT: ${compCards[0].height}px vs ${compCards[1].height}px`);
    }
  }

  // 6. Check benchmark bar chart labels alignment
  const barLabels = await page.$$eval('.bar-label', els => els.map(el => {
    const s = getComputedStyle(el);
    return { text: el.textContent.trim(), textAlign: s.textAlign, width: s.width };
  }));
  const uniqueBarLabelWidths = [...new Set(barLabels.map(l => l.width))];
  if (uniqueBarLabelWidths.length > 1) {
    issues.push(`BAR LABELS INCONSISTENT WIDTH: ${uniqueBarLabelWidths.join(', ')}`);
  }
  for (const l of barLabels) {
    if (l.textAlign !== 'right') {
      issues.push(`BAR LABEL NOT RIGHT-ALIGNED: "${l.text}" has textAlign="${l.textAlign}"`);
    }
  }

  // 7. Check workflow step numbers alignment
  const stepNums = await page.$$eval('.step-num', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return { left: Math.round(rect.left), width: Math.round(rect.width), height: Math.round(rect.height) };
  }));
  const uniqueStepLefts = [...new Set(stepNums.map(s => s.left))];
  if (uniqueStepLefts.length > 1) {
    issues.push(`WORKFLOW STEP NUMBERS NOT LEFT-ALIGNED: positions ${uniqueStepLefts.join(', ')}px`);
  }

  // 8. Check mechanism numbers are centered
  const mechNums = await page.$$eval('.mechanism-num', els => els.map(el => {
    const s = getComputedStyle(el);
    return { marginLeft: s.marginLeft, marginRight: s.marginRight, display: s.display };
  }));

  // 9. Check architecture diagram vertical alignment
  const archRows = await page.$$eval('.arch-row', els => els.map((el, i) => {
    const s = getComputedStyle(el);
    return { 
      index: i,
      justifyContent: s.justifyContent,
      alignItems: s.alignItems,
    };
  }));
  for (const r of archRows) {
    if (r.justifyContent !== 'center') {
      issues.push(`ARCH ROW ${r.index} NOT CENTERED: justifyContent="${r.justifyContent}"`);
    }
  }

  // 10. Check section padding consistency
  const sections = await page.$$eval('.section', els => els.map(el => {
    const s = getComputedStyle(el);
    return {
      id: el.id || el.className.substring(0, 30),
      paddingTop: s.paddingTop,
      paddingBottom: s.paddingBottom,
    };
  }));
  const uniqueSectionPaddings = [...new Set(sections.map(s => `${s.paddingTop}/${s.paddingBottom}`))];
  if (uniqueSectionPaddings.length > 1) {
    issues.push(`SECTION PADDING INCONSISTENT: ${sections.map(s => `${s.id}: ${s.paddingTop}/${s.paddingBottom}`).join('; ')}`);
  }

  // 11. Check disclaimer text alignment
  const disclaimers = await page.$$eval('.disclaimer', els => els.map(el => {
    const s = getComputedStyle(el);
    return { text: el.textContent.substring(0, 40), textAlign: s.textAlign, fontStyle: s.fontStyle };
  }));

  // 12. Check subsection-title alignment
  const subTitles = await page.$$eval('.subsection-title', els => els.map(el => {
    const s = getComputedStyle(el);
    return { text: el.textContent.trim(), textAlign: s.textAlign };
  }));
  for (const t of subTitles) {
    if (t.textAlign !== 'left' && t.textAlign !== 'start') {
      // subsection titles should be left-aligned typically
    }
  }

  // 13. Check CTA section text alignment
  const ctaTitle = await page.$eval('.cta-title', el => {
    const s = getComputedStyle(el);
    return { textAlign: s.textAlign };
  });

  // 14. Check font consistency across section titles
  const titleFonts = await page.$$eval('.section-title', els => els.map(el => {
    const s = getComputedStyle(el);
    return { text: el.textContent.trim(), fontSize: s.fontSize, fontWeight: s.fontWeight, fontFamily: s.fontFamily.substring(0, 40) };
  }));
  const uniqueTitleSizes = [...new Set(titleFonts.map(f => f.fontSize))];
  if (uniqueTitleSizes.length > 1) {
    issues.push(`SECTION TITLE FONT SIZES INCONSISTENT: ${titleFonts.map(f => `"${f.text}": ${f.fontSize}`).join(', ')}`);
  }

  // 15. Check integration cards 5th card orphan placement
  const intCards = await page.$$eval('.integration-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { left: Math.round(rect.left), top: Math.round(rect.top), width: Math.round(rect.width) };
  }));
  if (intCards.length === 5) {
    // Last card is alone on its row
    const lastCard = intCards[4];
    const prevRowCards = intCards.filter(c => Math.abs(c.top - intCards[0].top) < 10);
    if (prevRowCards.length === 4) {
      issues.push(`INTEGRATION CARDS: 5th card "Plug-in" orphaned alone on second row (4+1 layout), consider 3+2 or centering the orphan`);
    }
  }

  // 16. Check agent cards 5th card orphan
  const agCards = await page.$$eval('.agent-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { left: Math.round(rect.left), top: Math.round(rect.top), width: Math.round(rect.width) };
  }));
  if (agCards.length === 5) {
    const lastAgCard = agCards[4];
    const firstRowAgCards = agCards.filter(c => Math.abs(c.top - agCards[0].top) < 10);
    if (firstRowAgCards.length === 4) {
      issues.push(`AGENT CARDS: 5th card "MemoryConsultant" orphaned alone on second row (4+1 layout), consider centering`);
    }
  }

  // 17. Check collab diagram branches indentation
  const collabBranches = await page.$$eval('.collab-branch', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { left: Math.round(rect.left), top: Math.round(rect.top) };
  }));

  // 18. Check code block overflow
  const codeExample = await page.$eval('.code-example', el => {
    return { scrollWidth: el.scrollWidth, clientWidth: el.clientWidth, overflow: el.scrollWidth > el.clientWidth };
  });
  if (codeExample.overflow) {
    issues.push(`CODE EXAMPLE OVERFLOWS: scrollWidth ${codeExample.scrollWidth}px > clientWidth ${codeExample.clientWidth}px`);
  }

  // Print report
  console.log('=== VISUAL AUDIT REPORT ===\n');
  if (issues.length === 0) {
    console.log('No issues found!');
  } else {
    for (let i = 0; i < issues.length; i++) {
      console.log(`${i + 1}. ${issues[i]}`);
    }
  }
  console.log(`\nTotal issues: ${issues.length}`);

  await browser.close();
})();
