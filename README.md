# Fractal Model — Reclaim Strength (RS) Engine

TradingView (Pine v6) indikatörü: C2 sweep/reclaim kurulumunda süpürülen C1 ucu + korunması gereken C2 ucu çizgileri ve RS kademeli Reach/Full C4/XC2 istatistik tablosu. Giriş/TP çizgisi ve "Uygun" yargısı üretmez.

## Dosyalar

- `scripts/fractal_reclaim_strength.pine`: indikatör (Pine v6, 417 satır).
- `research_notes/19_PINE_SCRIPT_V6_INDICATOR_AFEM_V3_ENGINE.md`: ne yaptığı, matematik ve satır satır kod açıklaması (Türkçe).
- `research_notes/00_FRACTAL_MODEL_ANATOMI_VE_TANIMLAR.md`: ölçüm sözleşmesi.
- `research_notes/06_RECLAIM_STRENGTH_MASTERCLASS.md`: RS/fitil geometrisi.

## Kullanım

Pine Editor'e yapıştır, kaydet, grafiğe ekle. 15m altı periyotlarda motor ve çizimler gizlenir.

## Durum

`pine_check`: 0 hata / 0 uyarı; `pine_analyze`: 0 bulgu. Oranlar betimsel ve dönem içidir; PnL/edge kanıtı değildir.
