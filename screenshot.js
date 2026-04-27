const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  
  await page.goto('https://thongton11314.github.io/agent-skill-self-improvement/#overview', { waitUntil: 'networkidle' });
  
  // Full page screenshot
  await page.screenshot({ path: 'screenshots/full-page.png', fullPage: true });

  // Section-by-section screenshots
  const sections = [
    { selector: '.hero', name: 'hero' },
    { selector: '#overview', name: 'overview' },
    { selector: '#architecture', name: 'architecture' },
    { selector: '#workflow', name: 'workflow' },
    { selector: '#evaluation', name: 'evaluation' },
    { selector: '#benchmarks', name: 'benchmarks' },
    { selector: '#simulation', name: 'simulation' },
    { selector: '#integration', name: 'integration' },
    { selector: '#agentic', name: 'agentic' },
    { selector: '.cta-section', name: 'cta' },
    { selector: '.footer', name: 'footer' },
  ];

  for (const { selector, name } of sections) {
    try {
      const el = page.locator(selector);
      await el.screenshot({ path: `screenshots/${name}.png` });
      console.log(`OK: ${name}`);
    } catch (e) {
      console.log(`FAIL: ${name} - ${e.message}`);
    }
  }

  await browser.close();
  console.log('Done');
})();
