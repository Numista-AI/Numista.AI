const { chromium } = require('@playwright/test');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://numista.ai');
  await page.waitForTimeout(4000);

  // Extract all elements with tags button, a, or with click handlers, or text
  const elements = await page.evaluate(() => {
    const results = [];
    
    // Check for standard interactive elements
    const interactive = document.querySelectorAll('button, a, [role="button"], input, select');
    interactive.forEach(el => {
      results.push({
        tag: el.tagName,
        text: el.innerText || el.textContent,
        id: el.id,
        className: el.className,
        role: el.getAttribute('role'),
        type: el.getAttribute('type'),
        isVisible: el.offsetWidth > 0 && el.offsetHeight > 0
      });
    });

    // Check for flutter semantics elements (often flt-semantics or custom flt- tags)
    const allElements = document.querySelectorAll('*');
    allElements.forEach(el => {
      if (el.tagName.toLowerCase().startsWith('flt-')) {
        results.push({
          tag: el.tagName,
          text: el.innerText || el.textContent,
          id: el.id,
          className: el.className,
          role: el.getAttribute('role'),
          isVisible: el.offsetWidth > 0 && el.offsetHeight > 0
        });
      }
    });

    return results;
  });

  console.log('--- FOUND INTERACTIVE / SEMANTIC ELEMENTS ---');
  console.log(JSON.stringify(elements, null, 2));

  await browser.close();
}

run();
