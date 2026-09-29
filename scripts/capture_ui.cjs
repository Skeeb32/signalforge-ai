// Run from repository root after API/web/seed. Install Chromium with:
// cd apps/web && npx playwright install chromium
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const requireWeb = createRequire(path.resolve('apps/web/package.json'));
const { chromium } = requireWeb('playwright');

(async () => {
  const browser = await chromium.launch({headless:true, ...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {})});
  const page = await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror',error=>errors.push(String(error)));
  await page.goto(process.env.WEB_URL || 'http://127.0.0.1:5173');
  await page.getByText('Recent customer signals').waitFor();
  await page.screenshot({path:'docs/assets/dashboard.png',fullPage:false});
  for(const view of ['Customers','Models','Monitoring']){
    await page.getByRole('button',{name:view,exact:true}).click();
    await page.screenshot({path:`docs/assets/${view.toLowerCase()}.png`,fullPage:false});
  }
  await page.getByRole('button',{name:'Customers',exact:true}).click();
  await page.getByLabel('Search customer ID').fill('NO-MATCH');
  await page.getByText('No predictions match.',{exact:false}).waitFor();
  await page.getByLabel('Search customer ID').fill('');
  await page.getByRole('button',{name:/Inspect UCI/}).first().click();
  await page.getByText('Baseline:',{exact:false}).waitFor({timeout:60000});
  await page.screenshot({path:'docs/assets/customer-detail.png',fullPage:false});
  await page.setViewportSize({width:390,height:844});
  const mobileOverflow={};
  for(const view of ['Overview','Customers','Models','Monitoring']){
    await page.getByRole('button',{name:view,exact:true}).click();
    mobileOverflow[view]=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
    if(view==='Overview')await page.screenshot({path:'docs/assets/mobile.png',fullPage:false});
  }
  const report={browser:'Chromium',browser_errors:errors,mobile_horizontal_overflow:mobileOverflow,checks:['four live pages','customer search empty state','SHAP detail','four mobile layouts']};
  fs.writeFileSync('docs/browser-results.json',JSON.stringify(report,null,2));
  await browser.close();
  if(errors.length||Object.values(mobileOverflow).some(Boolean))throw new Error(JSON.stringify(report));
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exit(1);});
