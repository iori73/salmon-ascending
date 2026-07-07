#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実画像(各段階の代表写真)から 色パレット + 縦バー統計 を抽出 → calibration.json
背景除去 → k-means採色 → 上/中/下バンドで 背・体側・腹 を分離 → 婚姻色はFFTでバー本数。
出力: calibration.json, palette_proof.png(段階ごとの抽出色スウォッチ)
"""
import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.cluster.vq import kmeans2
from _paths import out as _OUT, BASE

# 段階ごと: 画像ファイル, 魚体クロップ(fx0,fy0,fx1,fy1 比率), 背景除去種別, nuptial?
REF = {
  1: dict(img="ref/s1.png",    crop=(0.18,0.20,0.85,0.85), bg="none",  nuptial=False, note="仔魚(実写: ヨークサック稚魚クラスタ)"),
  3: dict(img="ref/s3.png",    crop=(0.08,0.30,0.92,0.74), bg="silver",nuptial=False, note="スモルト(実写: 水中の銀化群/低彩度銀のみ)"),
  4: dict(img="ref/c4fda.png", crop=(0.04,0.24,0.86,0.74), bg="dark",  nuptial=False, note="海洋(実写: FDA標本 側面)"),
  5: dict(img="ref/s5.png",    crop=(0.10,0.25,0.92,0.78), bg="none",  nuptial=False, note="沿岸(実写: 河口の群)"),
  6: dict(img="ref/c6male.png",crop=(0.06,0.30,0.94,0.78), bg="white", nuptial=True,  note="遡上婚姻色(図譜: Dog Salmon Breeding Male)"),
}

def load_crop(d):
    im=np.asarray(Image.open(d["img"]).convert("RGB")).astype(float)
    H,W,_=im.shape
    fx0,fy0,fx1,fy1=d["crop"]
    c=im[int(fy0*H):int(fy1*H), int(fx0*W):int(fx1*W)]
    return c

def bg_mask(c, kind):
    r,g,b=c[...,0],c[...,1],c[...,2]
    mx=c.max(2); mn=c.min(2); sat=mx-mn
    lum=0.3*r+0.59*g+0.11*b
    if kind=="white": return ~((mn>208)&(sat<28))      # 白/クリーム背景を除外
    if kind=="dark":  return ~(mx<48)                   # 暗背景を除外
    if kind=="silver":return (sat<42)&(lum>80)&(lum<250) # 低彩度の銀ピクセルのみ(青水を除外)
    return np.ones(c.shape[:2],bool)

def palette(c, mask, k=6):
    px=c[mask]
    if len(px)<50: px=c.reshape(-1,3)
    cent,lab=kmeans2(px, k, minit="++", seed=7)
    counts=np.bincount(lab, minlength=k)
    order=np.argsort(-counts)
    return cent[order], counts[order]

def band_color(c, mask, y0,y1):
    h=c.shape[0]; sub=c[int(y0*h):int(y1*h)]; m=mask[int(y0*h):int(y1*h)]
    px=sub[m]
    if len(px)<20: px=sub.reshape(-1,3)
    return np.median(px,0)

def bar_count(c, mask):
    # 中央体側の横ストリップ輝度の主要周波数 → 体長あたりのバー本数
    h,w,_=c.shape
    strip=c[int(0.42*h):int(0.60*h)]
    m=mask[int(0.42*h):int(0.60*h)]
    lum=(0.3*strip[...,0]+0.59*strip[...,1]+0.11*strip[...,2])
    lum=np.where(m,lum,np.nan)
    prof=np.nanmean(lum,0)
    prof=prof[~np.isnan(prof)]
    if len(prof)<32: return None,None
    prof=prof-prof.mean()
    win=np.hanning(len(prof)); F=np.abs(np.fft.rfft(prof*win))
    freqs=np.fft.rfftfreq(len(prof))  # cycles/pixel
    F[0]=0
    lo=(freqs> (3/len(prof))) & (freqs < 0.20)  # 3本〜
    if not lo.any(): return None,None
    fpk=freqs[lo][np.argmax(F[lo])]
    bars_fft=fpk*len(prof)
    spacing_px=1/fpk
    # ピーク検出(暗バー=輝度極小)で本数クロスチェック
    from scipy.ndimage import gaussian_filter1d
    sm=gaussian_filter1d(prof, max(2,len(prof)//40))
    mins=((sm<np.roll(sm,1))&(sm<np.roll(sm,-1))&(sm<-sm.std()*0.3)).sum()
    return round(float(bars_fft),1), round(float(spacing_px),1), int(mins)

def hexc(rgb): return "#%02X%02X%02X"%tuple(int(np.clip(v,0,255)) for v in rgb)

out={}
for st,d in REF.items():
    c=load_crop(d); m=bg_mask(c,d["bg"])
    cent,cnt=palette(c,m)
    dorsal=band_color(c,m,0.0,0.30)
    flank =band_color(c,m,0.38,0.62)
    belly =band_color(c,m,0.70,1.0)
    rec=dict(note=d["note"],
             dorsal=hexc(dorsal), flank=hexc(flank), belly=hexc(belly),
             palette=[hexc(x) for x in cent[:5]],
             palette_pct=[round(float(x/cnt.sum()),3) for x in cnt[:5]])
    if d["nuptial"]:
        # 婚姻色の臙脂 = 赤いピクセルの直接中央値(k-meansで埋もれるため)
        r_,g_,b_=c[...,0],c[...,1],c[...,2]
        redpx=(r_-g_>22)&(r_-b_>12)&(r_>85)&m
        red = np.median(c[redpx],0) if redpx.sum()>30 else cent[np.argmax(cent[:,0]-cent[:,1])]
        dark=cent[np.argmin(cent.sum(1))]
        bars,sp,mins=bar_count(c,m)
        rec.update(bar_red=hexc(red), bar_dark=hexc(dark),
                   bar_count_fft=bars, bar_count_peaks=mins, bar_spacing_px=sp, bar_red_px_frac=round(float(redpx.sum()/max(m.sum(),1)),3))
    out[st]=rec
    print(st, d["note"], "->", rec.get("dorsal"), rec.get("flank"), rec.get("bar_count",""))

json.dump(out, open(BASE / "calibration.json", "w"), ensure_ascii=False, indent=2)  # rd/ が親直下を参照するため BASE 直下に保つ

# ---- proof swatch ----
rows=sorted(out); sw=140; rh=120; W=sw*6+40; H=rh*len(rows)+50
img=Image.new("RGB",(W,H),(250,250,248)); dr=ImageDraw.Draw(img)
try: font=ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",16)
except: font=ImageFont.load_default()
dr.text((10,8),"実画像からの抽出色 (calibration.json)",fill=(30,30,30),font=font)
for i,st in enumerate(rows):
    r=out[st]; y=40+i*rh
    dr.text((10,y+4),"段階%d"%st,fill=(20,20,20),font=font)
    keys=[("dorsal","背"),("flank","体側"),("belly","腹")]
    if "bar_red" in r: keys+=[("bar_red","婚姻赤"),("bar_dark","暗")]
    for j,(kk,lab) in enumerate(keys):
        x=70+j*sw
        col=tuple(int(r[kk][p:p+2],16) for p in (1,3,5))
        dr.rectangle([x,y+24,x+sw-12,y+rh-12],fill=col,outline=(180,180,180))
        dr.text((x+4,y+rh-30),"%s %s"%(lab,r[kk]),fill=(255,255,255) if sum(col)<360 else (0,0,0),font=font)
    if r.get("bar_count"): dr.text((70+5*sw,y+30),"bars≈%s"%r["bar_count"],fill=(20,20,20),font=font)
img.save(_OUT("palette", "palette_proof.png")); print("saved calibration.json + palette_proof.png")
