// Screenshot local HTML pages in headless Chromium; tools/screenshot/screenshot.sh sets PW and the browser path.
//   node tools/screenshot/screenshot.cjs OUTDIR [--width PIXELS] PAGE.html[#ANCHOR]...
const {chromium} = require(process.env.PW);
const {mkdirSync} = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');

const MOBILE_WIDTH = 800;  // narrower viewports are named -mobile
const DRAW_WAIT_MS = 1500;  // math, charts and viewers draw within a few hundred milliseconds of load

(async () => {
  const [outdir, ...rest] = process.argv.slice(2);
  let width = 1440;
  if (rest[0] === '--width') {
    width = Number(rest[1]);
    rest.splice(0, 2);
  }
  mkdirSync(outdir, {recursive: true});
  const browser = await chromium.launch({headless: true, args: ['--no-sandbox']});
  let failed = false;
  for (const page_path of rest) {
    const page = await browser.newPage({viewport: {width, height: 1000}});
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    const [file, anchor] = page_path.split('#');
    await page.goto(pathToFileURL(path.resolve(file)).href + (anchor ? `#${anchor}` : ''));
    await page.waitForTimeout(DRAW_WAIT_MS);
    const page_name = path.relative('.', path.resolve(file)).replace(/^(\.\.\/)+/, '')
      .replace(/^.*docs\/_build\/html\//, '').replace(/\.html$/, '').replaceAll('/', '_');
    const name = page_name + (anchor ? `_${anchor}` : '') + (width < MOBILE_WIDTH ? '-mobile' : '');
    const png = path.join(outdir, `${name}.png`);
    await page.screenshot({path: png, fullPage: !anchor});  // an anchor shows the one screen at that heading
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    failed ||= errors.length > 0 || overflow;
    console.log(png, errors.length ? errors : 'ok', overflow ? 'OVERFLOW' : '');
    await page.close();
  }
  await browser.close();
  process.exitCode = failed ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode = 1; });
