from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import requests, re, execjs, random, urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="TikTok Multi-Engine Switcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KUNCI_INTERNAL_SERVER = "TULIS_KEY_DISINI"

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("favicon.ico")

@app.get("/favicon-32x32.png")
async def get_favicon_png():
    return FileResponse("favicon-32x32.png")

@app.get("/apple-touch-icon.png")
async def get_apple_icon():
    return FileResponse("apple-touch-icon.png")

@app.get("/")
async def halaman_utama():
    return FileResponse("index.html")

@app.get("/privacy-policy")
async def privacy_page():
    return FileResponse("privacy.html")

@app.get("/terms")
async def terms_page():
    return FileResponse("terms.html")

@app.get("/contact")
async def contact_page():
    return FileResponse("contact.html")

@app.get("/robots.txt")
async def get_robots():
    return FileResponse("robots.txt")

@app.get("/sitemap.xml")
async def get_sitemap():
    return FileResponse("sitemap.xml")

@app.get("/google1a995d3a67176091.html")
async def google_verification():
    return FileResponse("google1a995d3a67176091.html")

@app.get("/ads.txt")
async def get_ads_txt():
    return FileResponse("ads.txt")

def get_random_ua():
    uas = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]
    return random.choice(uas)

def engine_snaptik(url, user_ip):
    sesi = requests.Session()
    headers = {
        'User-Agent': get_random_ua(),
        'X-Forwarded-For': user_ip 
    }
    try:
        res = sesi.get("https://snaptik.app/ID", headers=headers, timeout=10)
        token = re.search(r'name="token" value="([^"]+)"', res.text).group(1)
        res_api = sesi.post("https://snaptik.app/abc2.php", data={'url': url, 'token': token}, headers=headers, timeout=10)
        js = "function b() { " + res_api.text.replace("eval(", "return (") + " }"
        html = execjs.compile(js).call("b")
        return re.search(r'(https://[^\s"\'\\]*rapidcdn[^\s"\'\\]*)', html).group(1)
    except:
        return None

def engine_ssstik(url, user_ip):
    sesi = requests.Session()
    headers = {
        'User-Agent': get_random_ua(),
        'Referer': 'https://ssstik.io/id',
        'X-Forwarded-For': user_ip
    }
    try:
        res_home = sesi.get("https://ssstik.io/id", headers=headers, verify=False, timeout=10)
        token_tt = re.search(r"s_tt\s*=\s*'([^']+)'", res_home.text).group(1)
        
        headers.update({'HX-Request': 'true', 'HX-Target': 'target'})
        payload = {'id': url, 'locale': 'id', 'tt': token_tt, 'debug': f'ab=0&loc=ID&ip={user_ip}'}
        
        response = sesi.post("https://ssstik.io/abc?url=dl", data=payload, headers=headers, verify=False, timeout=10)
        return re.search(r'href="(https://tikcdn\.io/ssstik/[^"]+)"', response.text).group(1)
    except:
        return None

@app.get("/api/v1/get_video")
async def get_video(url: str, request: Request):
    referer = request.headers.get("referer")
    
    allowed_domains = ["127.0.0.1", "localhost"]
    is_valid = any(domain in referer for domain in allowed_domains) if referer else False

    if not is_valid:
         raise HTTPException(status_code=403, detail="Forbidden Access")

    user_ip = request.client.host
    if request.headers.get("X-Forwarded-For"):
        user_ip = request.headers.get("X-Forwarded-For").split(",")[0]

    print(f"[*] Request masuk dari {user_ip}")
    
    link_final = engine_snaptik(url, user_ip)
    if not link_final:
        print("[!] Jalur 1 Gagal. Otomatis pindah ke Jalur 2...")
        link_final = engine_ssstik(url, user_ip)

    if not link_final:
        raise HTTPException(status_code=400, detail="Semua jalur download sedang bermasalah.")

    def stream_video():
        try:
            with requests.get(link_final, stream=True, headers={'User-Agent': get_random_ua()}, verify=False, timeout=20) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=16384): 
                    yield chunk
        except Exception as e:
            print(f"[ERROR] Streaming terputus: {e}")

    angka_random = random.randint(1000, 9999)

    nama_branding = f"SUEK_TiktokDownloader_{angka_random}.mp4"

    return StreamingResponse(
        stream_video(),
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename={nama_branding}"}
    )
