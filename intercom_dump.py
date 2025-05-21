import asyncio, re, math, zipfile, logging, sys, shutil, time
from pathlib import Path

import pandas as pd
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# ─── CONFIG ───
EXCEL_FILE       = "links.xlsx"
SHEET_NAME       = "convos"
URL_COLUMN       = "url"

DOWNLOAD_DIR     = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

CHROME_CDP        = "http://localhost:9222"
MAX_ATTEMPTS_CONV = 3
MAX_RUN_RETRY     = 1
BATCH_SIZE        = 100
# ────────────────────

def slug(url: str) -> str:
    m = re.search(r"/conversation/(\d+)", url)
    return m.group(1) if m else "unknown"

async def robust_click(page, *sels, timeout=4000):
    for sel in sels:
        try:
            await page.click(sel, timeout=timeout)
            return
        except PWTimeout:
            continue
    raise RuntimeError(f"No match for selectors: {sels}")

def hhmmss(sec: float) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"

def progress(done: int, total: int, start: float):
    elapsed = time.time() - start
    rate    = elapsed / done if done else 0
    eta     = rate * (total - done) if rate else 0

    width   = max(10, shutil.get_terminal_size((80,20)).columns - 45)
    filled  = int(width * done / total)
    bar     = "#" * filled + "-" * (width - filled)
    sys.stdout.write(
        f"\r{bar} {done}/{total} {done/total:6.2%} "
        f"TIME {hhmmss(elapsed)} ETA {hhmmss(eta)}"
    )
    sys.stdout.flush()
    if done == total:
        print()

def zip_batches(dir_: Path, size: int = BATCH_SIZE):
    files   = sorted(dir_.glob("*.txt"))
    batches = math.ceil(len(files) / size)
    for i in range(batches):
        zf = dir_ / f"batch_{i+1:03d}.zip"
        with zipfile.ZipFile(zf, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files[i*size:(i+1)*size]:
                z.write(f, f.name)
    print(f"\nPacked {len(files)} files into {batches} zip(s) of {size}")

async def scrape():
    urls  = pd.read_excel(EXCEL_FILE, SHEET_NAME)[URL_COLUMN].dropna().tolist()
    total = len(urls)
    start = time.time()
    done  = 0
    errors = []

    async with async_playwright() as p:
        ctx = (await p.chromium.connect_over_cdp(CHROME_CDP)).contexts[0]

        for url in urls:
            cid = slug(url)
            out = DOWNLOAD_DIR / f"{cid}.txt"
            if out.exists():
                done += 1
                progress(done, total, start)
                continue

            success = False
            for attempt in range(1, MAX_ATTEMPTS_CONV+1):
                page = await ctx.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded")

                    # 1) Clic menu button (⋮)
                    await robust_click(
                        page,
                        'div.popover__opener.bg-transparent > button.inbox2__button',
                        'button:has(svg.o__standard__small-ellipsis)'
                    )

                    # 2) waits popover & clics on export
                    await page.wait_for_selector('div[data-popover-content]', timeout=6000)
                    await robust_click(
                        page,
                        'div[data-popover-content] svg.o__standard__export',              # selector preciso
                        'div[data-popover-content] div[role="button"]:has-text("Export conversation")'
                    )

                    # 3) wait download and save in folder
                    dl = await page.wait_for_event("download", timeout=10000)
                    out.write_bytes(Path(await dl.path()).read_bytes())
                    success = True

                except Exception as e:
                    logging.error(f"{cid} try {attempt}: {e}")
                    if attempt < MAX_ATTEMPTS_CONV:
                        await asyncio.sleep(1)
                    else:
                        errors.append(cid)
                finally:
                    await page.close()

                if success:
                    break

            done += 1
            progress(done, total, start)

        await ctx.close()

    zip_batches(DOWNLOAD_DIR)
    return errors

if __name__ == "__main__":
    logging.basicConfig(filename="errors.log", level=logging.ERROR)
    print("Scraper Intercom iniciado")

    for run in range(MAX_RUN_RETRY+1):
        try:
            failed = asyncio.run(scrape())
            if not failed:
                print("\nCompleted without errors")
            else:
                print(f"\nFailed {len(failed)} IDs: {failed}")
            break
        except Exception as exc:
            logging.exception(exc)
            if run < MAX_RUN_RETRY:
                print(f"\nError: {exc}. Retrying {run+1}/{MAX_RUN_RETRY}…")
                time.sleep(2)
            else:
                print(f"\nFinal crash: {exc}")
                sys.exit(1)
