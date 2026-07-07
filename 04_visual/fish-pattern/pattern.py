#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シロザケ 体の模様 — 計算ベース 2手法 × 7生活史段階
  A) 鱗の格子 (scale lattice / quincunx, 実側線鱗数ベース)
  B) 反応拡散 (anisotropic Gray-Scott Turing pattern)
7段階で模様が変化: 仔魚→稚魚(parr)→スモルト(銀化)→海洋(銀)→沿岸→遡上(婚姻色出始め)→産卵後(婚姻色フル→痩せ斑)
出力: fish-pattern-montage.png (2行×7列)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from _paths import out as _OUT

SEED = 20260614
rng = np.random.default_rng(SEED)

# ---- 生物パラメータ(出典確認要) ----
LATERAL_SCALES = 140   # シロザケ側線鱗 ~124-153 の代表値
SCALE_ROWS_V   = 26    # 体高方向の鱗列(背〜腹)概数
PARR_COUNT     = 11    # 稚魚パーマーク本数(概数)

# ---- 段階定義 ----
# flank: 体側ベース色, dorsal: 背の色, bar: 縦縞色, bartype, baramp, sizefac
STAGES = [
  dict(n=1, jp="1 仔魚",   flank=(212,202,206), dorsal=(150,150,160), bar=(120,120,130), bartype="none",     baramp=0.0, size=0.30),
  dict(n=2, jp="2 稚魚",   flank=(150,162,120), dorsal=(95,108,80),   bar=(78,86,62),     bartype="parr",     baramp=0.55,size=0.42),
  dict(n=3, jp="3 スモルト",flank=(196,210,220),dorsal=(120,140,160), bar=(150,170,185),  bartype="parr",     baramp=0.18,size=0.55),
  dict(n=4, jp="4 海洋",   flank=(206,220,228), dorsal=(52,84,112),   bar=(150,170,185),  bartype="none",     baramp=0.0, size=1.00),
  dict(n=5, jp="5 沿岸",   flank=(196,208,210), dorsal=(70,96,108),   bar=(120,140,120),  bartype="none",     baramp=0.0, size=1.00),
  dict(n=6, jp="6 遡上",   flank=(132,144,96),  dorsal=(70,86,60),    bar=(116,72,104),   bartype="nuptial",  baramp=0.55,size=0.98),
  dict(n=7, jp="7 産卵後", flank=(98,116,72),   dorsal=(54,64,46),    bar=(74,44,76),     bartype="nuptial",  baramp=0.95,size=0.96),
]

# ---- 実画像キャリブレーション(calibration.json)で色・バー本数を上書き ----
import json, os
_CALP=os.path.join(os.path.dirname(os.path.abspath(__file__)),"calibration.json")
def _h(s): return tuple(int(s[p:p+2],16) for p in (1,3,5))
if os.path.exists(_CALP):
    _cal=json.load(open(_CALP))
    for st in STAGES:
        c=_cal.get(str(st["n"]))
        if not c: continue
        if "flank" in c:  st["flank"]=_h(c["flank"])
        if "dorsal" in c: st["dorsal"]=_h(c["dorsal"])
        if st["bartype"]=="nuptial" and c.get("bar_red"): st["bar"]=_h(c["bar_red"])
        elif c.get("bar_dark"): st["bar"]=_h(c["bar_dark"])
        if c.get("bar_count"): st["barcount"]=int(c["bar_count"])
    print("calibrated from", _CALP)

# ---- サケ シルエット (正規化 x:0..1 鼻先→尾柄, y 体高; 体高は体長の~0.26 紡錘形) ----
def salmon_polygon():
    top = [(0.00,0.00),(0.03,0.04),(0.08,0.075),(0.15,0.105),(0.25,0.125),(0.36,0.130),
           (0.50,0.122),(0.64,0.100),(0.78,0.066),(0.88,0.038)]
    bot = [(0.00,0.00),(0.04,-0.045),(0.10,-0.085),(0.20,-0.115),(0.32,-0.125),(0.46,-0.122),
           (0.60,-0.100),(0.74,-0.070),(0.85,-0.042),(0.88,-0.036)]
    # 二叉尾びれ from 尾柄(0.88)
    tail = [(1.00,0.155),(0.95,0.00),(1.00,-0.155)]
    pts = top + tail + list(reversed(bot))
    return pts

def fins():
    # 背びれ・脂びれ(サケ科の証)・尻びれ・胸びれ
    dorsal  = [(0.40,0.125),(0.46,0.210),(0.52,0.118)]
    adipose = [(0.74,0.066),(0.77,0.100),(0.80,0.060)]
    anal    = [(0.58,-0.100),(0.62,-0.190),(0.66,-0.095)]
    pect    = [(0.18,-0.060),(0.24,-0.160),(0.27,-0.050)]
    return [dorsal,adipose,anal,pect]

def build_mask(W,H, pad=0.05):
    """body mask(uint8 0/1), plus body-only mask(no fins) and coords."""
    sx = W*(1-2*pad); sy = H*0.5
    ox = W*pad;       oy = H*0.5
    def tx(p): return (ox+p[0]*sx, oy - p[1]*sx)  # y up positive; keep aspect via sx
    body_img = Image.new("L",(W,H),0); bd=ImageDraw.Draw(body_img)
    bd.polygon([tx(p) for p in salmon_polygon()], fill=255)
    full_img = body_img.copy(); fd=ImageDraw.Draw(full_img)
    for f in fins(): fd.polygon([tx(p) for p in f], fill=255)
    body = (np.array(body_img)>128)
    full = (np.array(full_img)>128)
    return body, full, (ox,oy,sx)

# ---- 段階ごとの「縞/濃淡フィールド」(体bbox上, 値0..1 = 暗さ) ----
def pattern_field(W,H, body, transform, st):
    ox,oy,sx = transform
    ys,xs = np.mgrid[0:H,0:W]
    # 体に沿った正規化座標
    xn = (xs-ox)/sx                      # 0鼻先..0.9尾柄
    yn = (oy-ys)/sx                      # 体高(+上)
    # 体高の局所最大(縦位置正規化用) ざっくり: 体中央で±0.42
    field = np.zeros((H,W))
    bt = st["bartype"]; amp=st["baramp"]
    if bt=="parr":
        # 縦パーマーク: 体側上半に等間隔の縦バー
        pc = st.get("barcount", PARR_COUNT)
        bars = 0.5+0.5*np.cos(2*np.pi*pc*np.clip(xn/0.9,0,1))
        bars = (bars>0.55).astype(float)
        bars *= (yn> -0.05)              # 背側中心〜上
        field += amp*gaussian_filter(bars,2)
    elif bt=="nuptial":
        # 婚姻色: やや不規則な太い縦バー(本数少なめ) + まだら
        nb = st.get("barcount", 8)
        phase = rng.uniform(0,2*np.pi)
        bars = 0.5+0.5*np.cos(2*np.pi*nb*np.clip(xn/0.9,0,1)+phase)
        bars = np.clip((bars-0.35)/0.65,0,1)
        mottle = gaussian_filter(rng.standard_normal((H,W)),6)
        mottle = (mottle-mottle.min())/(np.ptp(mottle)+1e-9)
        field += amp*(0.7*bars+0.3*mottle)
        if st["n"]==7:   # 痩せ: 部分的な退色(白抜け斑)
            wear = gaussian_filter(rng.standard_normal((H,W)),9)
            field -= 0.5*np.clip((wear-wear.std()),0,None)
    # カウンターシェーディング(背暗・腹明) 全段階共通に薄く
    cs = np.clip((yn+0.42)/0.84,0,1)     # 0腹..1背
    field += 0.0  # baseはcolorで表現
    field = np.clip(field,0,1)
    field[~body]=0
    return field, cs

def colorize(st, field, cs, body):
    flank=np.array(st["flank"]); dorsal=np.array(st["dorsal"]); bar=np.array(st["bar"])
    H,W = field.shape
    img = np.ones((H,W,4))*255; img[...,3]=0
    base = flank[None,None,:]*(1-cs[...,None]) + dorsal[None,None,:]*(cs[...,None])
    col  = base*(1-field[...,None]) + bar[None,None,:]*(field[...,None])
    img[...,:3]=col; img[...,3]=np.where(body,255,0)
    return img.astype(np.uint8)

# ---- 手法A: 鱗の格子 ----
def approach_scales(W,H, body, full, transform, st):
    ox,oy,sx = transform
    field, cs = pattern_field(W,H, body, transform, st)
    base = colorize(st, field, cs, full)
    img = Image.fromarray(base,"RGBA"); dr=ImageDraw.Draw(img,"RGBA")
    # 鱗中心: 斜めquincunx格子. x方向 LATERAL_SCALES, y方向 SCALE_ROWS_V
    nx=LATERAL_SCALES; nv=SCALE_ROWS_V
    sxlen = sx*0.9
    dxs = sxlen/nx
    # 各鱗を後縁の弧(クレッセント)で表現
    sc = max(1.2, dxs*0.62)
    ys_idx,xs_idx = np.where(body)
    ymin,ymax=ys_idx.min(),ys_idx.max(); xmin,xmax=xs_idx.min(),xs_idx.max()
    for i in range(nx+1):
        cx = ox + i*dxs
        # この列の体高
        col_mask = body[:, int(np.clip(cx,0,W-1))]
        if not col_mask.any(): continue
        yy=np.where(col_mask)[0]; top=yy.min(); bot=yy.max()
        offset = (i%2)*0.5
        for j in range(nv+1):
            cy = top + (j+offset)*(bot-top)/nv
            if cy<top or cy>bot: continue
            if not body[int(np.clip(cy,0,H-1)), int(np.clip(cx,0,W-1))]: continue
            # 鱗の濃さ = field(暗いほどbarで暗) + 微小ゆらぎ
            fv = field[int(cy),int(cx)]
            shade = 0.25+0.55*fv + rng.uniform(-0.05,0.05)
            a = int(np.clip(120+150*fv,90,255))
            r=sc
            dr.arc([cx-r,cy-r,cx+r,cy+r], start=20,end=160, fill=(40,40,46,a), width=max(1,int(sc*0.5)))
    # 目
    eye=(ox+0.07*sx, oy-0.02*sx)
    dr.ellipse([eye[0]-sc*1.3,eye[1]-sc*1.3,eye[0]+sc*1.3,eye[1]+sc*1.3], fill=(30,30,34,255))
    return img

# ---- 手法B: 反応拡散 (anisotropic Gray-Scott, 低解像度→拡大) ----
def gray_scott(gh,gw, F,k, Du,Dv, ax,ay, steps, seed_kind, salt=0):
    lrng=np.random.default_rng(SEED+salt*101)
    U=np.ones((gh,gw)); V=np.zeros((gh,gw))
    rr=lrng.random((gh,gw)); V[rr<0.06]=0.6; U[rr<0.06]=0.25
    def lap(Z):
        return (ax*(np.roll(Z,1,1)+np.roll(Z,-1,1)-2*Z) +
                ay*(np.roll(Z,1,0)+np.roll(Z,-1,0)-2*Z))
    for _ in range(steps):
        uvv=U*V*V
        U += (Du*lap(U) - uvv + F*(1-U))
        V += (Dv*lap(V) + uvv - (F+k)*V)
    V=(V-V.min())/(np.ptp(V)+1e-9)
    return V

def _upscale(V, W,H):
    im=Image.fromarray((np.clip(V,0,1)*255).astype(np.uint8)).resize((W,H), Image.BILINEAR)
    return np.array(im)/255.0

def approach_rd(W,H, body, full, transform, st):
    ox,oy,sx = transform
    _,cs = pattern_field(W,H, body, transform, st)
    bt=st["bartype"]; gh,gw=110,230
    # 全段 安定領域 F=.038,k=.061。縦バーは異方性(ay>ax)で斑を縦に伸ばす
    if bt=="parr":      # 細い縦の斑(幼魚斑)
        V=gray_scott(gh,gw, 0.038,0.061, 0.14,0.07, ax=0.55,ay=1.5, steps=5000, seed_kind="rand", salt=st["n"]); amp=st["baramp"]
    elif bt=="nuptial": # 太い縦バー(婚姻色)
        V=gray_scott(gh,gw, 0.038,0.061, 0.14,0.07, ax=0.5,ay=1.6, steps=6000, seed_kind="rand", salt=st["n"]); amp=st["baramp"]
    else:               # 銀: 微細な斑のみ(ほぼ無地)
        V=gray_scott(gh,gw, 0.038,0.061, 0.14,0.07, ax=1.0,ay=1.0, steps=4000, seed_kind="rand", salt=st["n"]); amp=0.10
    print("RD stage",st["n"],"Vstd=%.3f"%float(V.std()))
    Vup=_upscale(V, W,H)
    field=np.clip(amp*Vup,0,1); field[~body]=0
    base=colorize(st, field, cs, full)
    img=Image.fromarray(base,"RGBA"); dr=ImageDraw.Draw(img,"RGBA")
    sc=max(2,sx*0.012)
    eye=(ox+0.07*sx, oy-0.02*sx)
    dr.ellipse([eye[0]-sc,eye[1]-sc,eye[0]+sc,eye[1]+sc], fill=(30,30,34,255))
    return img

# ---- montage ----
def main():
    FW,FH=860,380
    cols=len(STAGES)
    pad=18; labelh=34
    MW=cols*FW+(cols+1)*pad
    MH=2*FH+3*pad+2*labelh+40
    canvas=Image.new("RGB",(MW,MH),(250,250,248))
    dr=ImageDraw.Draw(canvas)
    try: font=ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",18)
    except: font=ImageFont.load_default()
    try: fontb=ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc",20)
    except: fontb=font
    dr.text((pad,8),"A) 鱗の格子 (実側線鱗 ~%d / 縦列 %d / parr %d本)"%(LATERAL_SCALES,SCALE_ROWS_V,PARR_COUNT),fill=(40,40,40),font=fontb)
    rowA_y=40+labelh
    for i,st in enumerate(STAGES):
        w=int(FW*0.98); h=int(FH*0.96)
        body,full,tr=build_mask(w,h)
        im=approach_scales(w,h,body,full,tr,st)
        x=pad+i*(FW+pad); y=rowA_y+(FH-h)//2
        canvas.paste(im,(x,y),im)
        dr.text((x+4,rowA_y+FH+2),st["jp"],fill=(60,60,60),font=font)
    rowB_label=rowA_y+FH+labelh+pad
    dr.text((pad,rowB_label),"B) 反応拡散 (anisotropic Gray-Scott, 縦縞バイアス)",fill=(40,40,40),font=fontb)
    rowB_y=rowB_label+labelh
    for i,st in enumerate(STAGES):
        w=int(FW*0.98); h=int(FH*0.96)
        body,full,tr=build_mask(w,h)
        im=approach_rd(w,h,body,full,tr,st)
        x=pad+i*(FW+pad); y=rowB_y+(FH-h)//2
        canvas.paste(im,(x,y),im)
        dr.text((x+4,rowB_y+FH+2),st["jp"],fill=(60,60,60),font=font)
    out=_OUT("pattern", "fish-pattern-montage.png")
    canvas.save(out)
    print("saved",out, canvas.size)

if __name__=="__main__":
    main()
