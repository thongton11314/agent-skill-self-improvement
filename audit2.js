const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto('https://thongton11314.github.io/agent-skill-self-improvement/#overview', { waitUntil: 'networkidle' });

  // Check protocol-card code overflow
  const protocolCards = await page.$$eval('.protocol-card code', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    const parentRect = el.closest('.protocol-card').getBoundingClientRect();
    return {
      text: el.textContent,
      codeRight: Math.round(rect.right),
      parentRight: Math.round(parentRect.right),
      overflow: rect.right > parentRect.right,
      overflowAmount: Math.round(rect.right - parentRect.right),
    };
  }));
  console.log('=== PROTOCOL CARD CODE OVERFLOW ===');
  for (const p of protocolCards) {
    if (p.overflow) {
      console.log(`OVERFLOW: "${p.text}" overflows by ${p.overflowAmount}px`);
    } else {
      console.log(`OK: "${p.text}"`);
    }
  }

  // Check metric cards detailed heights
  const metricCards = await page.$$eval('.metric-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { height: Math.round(rect.height), top: Math.round(rect.top), text: el.querySelector('h4').textContent };
  }));
  console.log('\n=== METRIC CARD HEIGHTS ===');
  const metricRows = {};
  for (const c of metricCards) {
    const rowKey = Math.round(c.top / 20) * 20;
    if (!metricRows[rowKey]) metricRows[rowKey] = [];
    metricRows[rowKey].push(c);
  }
  for (const [key, row] of Object.entries(metricRows)) {
    const heights = row.map(c => `${c.text}: ${c.height}px`);
    console.log(`Row ~${key}: ${heights.join(' | ')}`);
  }

  // Check integration card heights per row
  const intCards = await page.$$eval('.integration-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { height: Math.round(rect.height), top: Math.round(rect.top), left: Math.round(rect.left), text: el.querySelector('h4').textContent };
  }));
  console.log('\n=== INTEGRATION CARD LAYOUT ===');
  for (const c of intCards) {
    console.log(`"${c.text}": left=${c.left}px top=${c.top}px height=${c.height}px`);
  }

  // Check agent card heights
  const agCards = await page.$$eval('.agent-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { height: Math.round(rect.height), top: Math.round(rect.top), left: Math.round(rect.left), text: el.querySelector('h4').textContent };
  }));
  console.log('\n=== AGENT CARD LAYOUT ===');
  for (const c of agCards) {
    console.log(`"${c.text}": left=${c.left}px top=${c.top}px height=${c.height}px`);
  }

  // Check comparison card heights
  const compCards = await page.$$eval('.comparison-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { height: Math.round(rect.height), top: Math.round(rect.top), text: el.querySelector('h3').textContent };
  }));
  console.log('\n=== COMPARISON CARD HEIGHTS ===');
  for (const c of compCards) {
    console.log(`"${c.text}": top=${c.top}px height=${c.height}px`);
  }

  // Check problem-card heights
  const probCards = await page.$$eval('.problem-card', els => els.map(el => {
    const rect = el.getBoundingClientRect();
    return { height: Math.round(rect.height), top: Math.round(rect.top), text: el.querySelector('h3').textContent };
  }));
  console.log('\n=== PROBLEM CARD HEIGHTS ===');
  for (const c of probCards) {
    console.log(`"${c.text}": top=${c.top}px height=${c.height}px`);
  }

  await browser.close();
})();
