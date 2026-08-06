import asyncio, json, pathlib, shutil, subprocess, sys
from playwright.async_api import async_playwright
FPS=30; W=1080; H=1920
async def main(html, outdir, dur):
    fr = pathlib.Path(outdir)/'_f'
    if fr.exists(): shutil.rmtree(fr)
    fr.mkdir(parents=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(channel=None,
                                     args=['--no-sandbox','--disable-dev-shm-usage','--single-process','--no-zygote','--disable-gpu','--js-flags=--max-old-space-size=192'])
        p = await b.new_page(viewport={'width':W,'height':H}, device_scale_factor=1)
        await p.goto('file://'+str(pathlib.Path(html).resolve()))
        await p.evaluate("document.fonts.ready")
        await p.wait_for_timeout(400)
        n = int(dur*FPS)
        for i in range(n):
            await p.evaluate(f"setT({i/FPS})")
            await p.screenshot(path=str(fr/f"f{i:05d}.jpg"), type='jpeg', quality=95)
        await b.close()
    print('frame', n)
asyncio.run(main(sys.argv[1], sys.argv[2], float(sys.argv[3])))
