"""_io.py — fish-pattern 共通の入出力パス解決。

すべて __file__(=このフォルダ)基準で解決するので、どの CWD から実行しても
入力は assets/、生成物は out/<category>/ に集約される。

  from _paths import asset, out
  Image.open(asset("scale-lineart.png"))        # 手描き素材(入力)
  cv.save(out("matrix", "combo-matrix.png"))    # 生成物(出力, ディレクトリは自動作成)

Path を返すので PIL.Image.open / cv.save / Path.write_text / open() いずれにも渡せる。
calibration.json だけは rd/ が親フォルダ直下を参照するため BASE 直下のまま(assets化しない)。
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"


def asset(name):
    """手描き/取り込みの入力素材(assets/ 配下)への Path。"""
    return ASSETS / name


def out(category, name):
    """生成物の出力先 out/<category>/<name> への Path(ディレクトリは自動作成)。"""
    d = BASE / "out" / category
    d.mkdir(parents=True, exist_ok=True)
    return d / name
