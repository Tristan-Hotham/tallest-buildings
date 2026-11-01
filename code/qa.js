// QA: open index.html at desktop and phone widths, log console errors, take screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server 9463; set PORT to change).
const { chromium } = require("playwright");
// Leaflet from a local npm copy (the CDN is not reachable from the build container); tiles and fonts are blocked here.
const LEAF = process.env.LEAFLET_DIST || "/dev/shm/piracy/npm/node_modules/leaflet/dist";
(async () => {
  const b = await chromium.launch();
  const errs = [];
  for (const [nm, vw, vh] of (process.env.ONLY ? [[process.env.ONLY, process.env.ONLY === "phone" ? 390 : 1280, 900]] : [["desktop", 1280, 900], ["phone", 390, 844]])) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
    await p.route(/leaflet.min.js/, r => r.fulfill({ path: LEAF + "/leaflet.js" }));
    await p.route(/leaflet.min.css/, r => r.fulfill({ path: LEAF + "/leaflet.css" }));
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::/.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + (process.env.PORT || 9463) + "/index.html", { waitUntil: "networkidle" });
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `qa/${nm}_top.png` });
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(700); await p.locator(sel).screenshot({ path: `qa/${nm}_${f}.png` }); };
    await shot("#atlas", "map");
    await p.locator("#step").evaluate(e => { e.value = 2; e.dispatchEvent(new Event("input")); }); await p.waitForTimeout(900); await shot("#atlas", "step_lincoln");
    await p.locator("#step").evaluate(e => { e.value = 14; e.dispatchEvent(new Event("input")); }); await p.waitForTimeout(900); await shot("#atlas", "step_eiffel");
    await p.click("#play"); await p.waitForTimeout(4500); await shot("#atlas", "playing"); await p.click("#play");
    await p.locator("#step").evaluate(e => { e.value = e.max; e.dispatchEvent(new Event("input")); });
    await p.click('#focusRow .btn:has-text("Dubai")'); await p.waitForTimeout(1500); await shot("#atlas", "dubai");
    await p.click('#colRow [data-c="reg"]'); await p.click('#focusRow .btn:has-text("Pearl River Delta")'); await p.waitForTimeout(1500); await shot("#atlas", "prd_region");
    await p.click('#colRow [data-c="dec"]');
    await p.click(".lyrBtn"); await p.check('.lyrPanel [data-k="unchecked"]'); await p.waitForTimeout(400); await p.click('#focusRow .btn:has-text("Manhattan")'); await p.waitForTimeout(1500); await shot("#map", "layers_panel"); await p.uncheck('.lyrPanel [data-k="unchecked"]'); await p.click(".lyrBtn");
    await p.fill("#q", "Shanghai Tower"); await p.waitForTimeout(500); await p.keyboard.press("Enter"); await p.waitForTimeout(2000); await shot("#atlas", "search_building");
    await p.fill("#q", "Lincoln"); await p.waitForTimeout(500); await p.keyboard.press("Enter"); await p.waitForTimeout(2000); await shot("#atlas", "search_lincoln");
    for (const c of ["skyline", "ribbon", "cityYears", "boom", "cities", "ucTable"]) await shot("#" + c, c);
    await p.click('#boomMode [data-m="list"]'); await p.waitForTimeout(400); await shot("#boom", "boom_list");
    await p.click('#cityMode [data-m="n350"]'); await p.waitForTimeout(400); await shot("#cities", "cities_350");
    await shot(".defs", "defs"); await shot(".ucard", "ucard");
    if (nm === "phone") {
      await p.click("#theme"); await p.waitForTimeout(1500); await shot("#atlas", "dark_map"); await shot("#skyline", "dark_skyline");
      await p.locator("#atlas").scrollIntoViewIfNeeded(); await p.click(".mfs-btn"); await p.waitForTimeout(1500); await p.screenshot({ path: `qa/${nm}_fullscreen.png` });
    }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    console.log(nm, "horizontal overflow px:", ov);
    await p.close();
  }
  console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
