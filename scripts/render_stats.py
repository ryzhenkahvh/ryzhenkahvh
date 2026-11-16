#!/usr/bin/env python3
"""Render four light stats cards over quadrants of the public GitHub avatar."""
import io, json, re, urllib.request
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw

USER='ryzhenkahvh'
ROOT=Path('assets'); ROOT.mkdir(exist_ok=True)
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'profile-stats-renderer','Accept':'*/*'})
    with urllib.request.urlopen(req,timeout=45) as r: return r.read()
profile=json.loads(fetch(f'https://api.github.com/users/{USER}'))
avatar=Image.open(io.BytesIO(fetch(profile['avatar_url']+'?s=800'))).convert('RGBA')
# Preserve transparency until it is composited onto white.
white=Image.new('RGBA',avatar.size,(255,255,255,255))
avatar=Image.alpha_composite(white,avatar).convert('RGB')
avatar=avatar.resize((800,800),Image.Resampling.LANCZOS)
# Build one continuous image and split it into four 680x400 crops.
canvas=Image.new('RGB',(1360,800),'white'); canvas.paste(avatar,(280,0))
for name,card,x,y in [('stats','stats',0,0),('time','productive-time',680,0),('languages','repos-per-language',0,400),('commits','most-commit-language',680,400)]:
    svg=fetch(f'https://github-profile-summary-cards.vercel.app/api/cards/{card}?username={USER}&theme=default&utcOffset=3').decode()
    if '<svg' not in svg or 'gpsc-root' not in svg: raise RuntimeError('Unexpected card response for '+card)
    # Make only the outer card rectangle transparent; its text and charts remain intact.
    svg=re.sub(r'(<rect\b[^>]*?)fill="#ffffff"',r'\1fill="none"',svg,count=1)
    card_img=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=680,output_height=400))).convert('RGBA')
    bg=canvas.crop((x,y,x+680,y+400)).convert('RGBA')
    bg=Image.alpha_composite(bg,Image.new('RGBA',bg.size,(255,255,255,223)))
    bg=Image.alpha_composite(bg,card_img).convert('RGB')
    bg.save(ROOT/('avatar-'+name+'.png'),optimize=True)
    print('Rendered',name)
