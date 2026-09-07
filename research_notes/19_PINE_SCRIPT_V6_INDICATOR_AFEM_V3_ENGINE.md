# 19: FM · RS Engine göstergesi — amaç, ekran ve satır satır kod

Güncelleme: 7 Eylül 2026. Kod: `scripts/fractal_reclaim_strength.pine` (417 satır, Pine v6).
Canlı durum: BTCUSDT.P 1h'de doğrulandı (BASE N=2274, 0 derleme hatası, tablo + 2 çizgi + etiket screenshot ile görüldü).

Bu doküman üç soruyu cevaplar: gösterge **ne için** var (§1), ekranda **ne gösteriyor** (§2–§3),
kod **satır satır ne yapıyor** (§4). Sınırlar §6'da, bakım kuralları §7'dedir.

## 1. Amaç: ne, ne değil

Gösterge, Fractal Model C2 sweep/reclaim kurulumunun iki şeyi grafiğe taşır:

1. **Canlı kurulumun iki referans seviyesi** — süpürülen C1 ucu + korunması gereken C2 ucu
   (notprofgreen "one setup" görselindeki iki çizginin birebir karşılığı).
2. **Geçmiş başarı oranları tablosu** — her RS kademesinde C4'e ulaşma / tam C4 / iptal oranları
   ve aktif kurulumun durum panosu.

Bilerek **yapmadıkları** (felsefe, değişmeyecek):

- "Uygun / Pas" yargısı yok. RS %, Fitil %, geçmiş oranlar ham veri olarak sunulur; karar trader'ındır.
- Giriş çizgisi (Wick EQ / denge), TP çizgisi, hedef etiketi yok. Referans görsellerde de yoktur.
- Mum üstü rozet yok. Yalnızca 2 yatay çizgi + 1 fiyat etiketi + sağ üst (varsayılan) tablo çizilir.
- CISD teyidi ölçülmez/çizilmez (ayrı çalışma: not 08, not 17).
- PnL, maliyet, stop-emri tetiklenmesi modellenmez. Eşitlik korunur kuralı gerçek stop kuralı değildir.

Arayüz dili İngilizce'dir (public yayın hedefi). Bu doküman Türkçe açıklar, UI metinlerini aynen aktarır.

## 2. Ekranda ne görünür

### 2.1. Tablo (varsayılan: sağ üst, küçük)

Satır 0 — başlık: `FM · RS ENGINE (BTCUSDT.P · 1h)`. Sembol + periyot otomatik.

Satır 1 — durum panosu, üç halden biri:

- `LIVE: Bear (C4) · RS: %4.1 · Wick: %14.9` — setup yaşıyor; yön, faz (C2/C3/C4), RS ve fitil.
- `INVALIDATED: Bear (C3) · C2 Extreme Broken` — uç kırıldı; parantez kırılmanın C3'te mi C4'te mi olduğunu söyler.
- `STANDBY` / `STANDBY (Last: Bear · %27.4 · Invalidated)` — aktif pencere yok; parantez son kurulumu özetler.

Satır 2 — sütunlar: `RS | N | Reach C4 | Full C4 | XC2 | Base Δ`.

- **Reach C4**: C3 boyunca uç korunma oranı (C4'e ulaşma). Matrisin "C4 Hayatta Kalma Oranı" ile aynı baz.
- **Full C4**: C3 VE C4 boyunca korunma oranı (tam survival).
- **XC2**: C3 veya C4'te uç ihlali oranı. Reach + XC2 her satırda %100'e tamamlar (eşitlik korunduğu için ara durum yoktur).
- **Base Δ**: kademe `Reach% − BASE Reach%`. Örnek: 0–10% kademesi 50.4 − 68.8 = −18.4%.

Satır 3–8 — 6 RS kademesi (N + 3 oran + Δ). Aktif kurulumun kademesi mavi vurgulanır.

Satır 9 — `BASE`: tüm örneklemin N'i ve 3 oranı + `Ref`.

Gerçek 1h değerleri (7 Eylül 2026): BASE 2274 | 68.8% | 55.8% | 44.2%. Kademe monotonluğu
(≥100%: 92.0/80.9/19.1 → 0–10%: 50.4/38.9/61.1) RS etkisinin betimsel resmidir; nedensellik/PnL iddiası değildir.

### 2.2. Çizgiler ve etiket

- **C1 Swept** (gri noktalı, kalınlık 1): süpürülen seviye. Boğada C1 dibinden, ayıda C1 tepesinden başlar.
- **C2 Extreme** (yön rengi kesikli, kalınlık 2): korunması gereken uç. Boğada yeşil, ayıda kırmızı.
- Kırılınca uç çizgisi kırmızıya döner, etiket `C2 Extreme (Broken ✗): 79448.7` olur.
- Etiket her zaman çizginin sağ ucundadır (`label.style_label_left`).
- Ömür: C2 kapanışında doğar, C4 kapanışında silinir (4 bar genişlik). Yeni setup eskisini siler.

### 2.3. Girdiler menüsü (2 grup)

1. **LEVELS**: `Level Lines (C1 & C2 Extreme)` (aç/kapa), `Price Labels` (aç/kapa).
2. **STATS TABLE**: `Show Table`, `Position` (4 köşe), `Size` (Small/Tiny/Normal),
   `Sample` (All Available Bars / Last 5000 / 1000 / 500 Bars).

## 3. Matematik (kodun uyguladığı sözleşme)

Kurulum (not 00 ile aynı):

- Boğa: `C2 Low < C1 Low` (fitille süpürme) ve `C2 Close > C1 Low` (kapanışla reclaim).
- Ayı: aynanın tersi (`C2 High > C1 High` ve `C2 Close < C1 High`).
- İkisini birden sağlayan outside bar (`dual`) yönsüz sayılır, dışlanır.
- Sıfır aralıklı C1/C2 (`rng > 0` şartı) dışlanır.

Formüller:

- Boğa RS = 100 × (C2 Close − C1 Low) / C1 range. Ayı RS = 100 × (C1 High − C2 Close) / C1 range.
- Boğa fitil = 100 × (C1 Low − C2 Low) / C2 range. Ayı fitil = 100 × (C2 High − C1 High) / C2 range.
  (Süpürülen kısmın C2 boyuna oranı; tüm alt/üst fitil değil. Not 06'daki ayrıma uygun.)
- Sonuçlar (C2'nin kendi barından sonraki 2 bar): C3'te uç korunursa **Reach**,
  C3+C4'te korunursa **Full**, herhangi birinde strict ihlal (`<`/`>`; eşitlik korunur) varsa **XC2**.
- Kademeler: [10,25,50,75,100] eşikleri, `side='right'` (Python `np.searchsorted` ile birebir):
  0–10 / 10–25 / 25–50 / 50–75 / 75–100 / ≥100. Tam %100 son kademededir.

## 4. Kod satır satır

Dosya 7 bloktan oluşur. Blok 4 (motor) ve blok 3 (event-store) istatistik çekirdeğidir;
blok 5–6 canlı takip, blok 7 sunumdur. Bloklar birbirine yalnızca şu değişkenlerle bağlanır:
`active_*` (5→6,7), sayaç dizileri (4→7), inputlar (1→4,6,7).

### 4.1. Başlık — L1–L2

- L1 `//@version=6`: Pine v6 derleyicisi.
- L2 `indicator("Fractal Model - ...", "FM·RS", overlay=true, max_lines_count=500,
  max_labels_count=500, max_bars_back=5000)`: ana mumların üstüne çizer (`overlay`);
  çizgi/etiket kotası 500 (aynı anda en fazla 1 setup'ın çizgileri yaşadığı için asla dolmaz);
  `max_bars_back=5000` — `[3]` gibi geriye bakışların izin verilen derinliği.
  Kısa başlık ≤10 karakter olmalı (TV kuralı; eskiden 14 karakterdi, derleme patlatıyordu).

### 4.2. Girdiler — L9–L20

- L9–L10: iki grup etiketi (`1. LEVELS`, `2. STATS TABLE`).
- L13 `show_lines`: seviye çizgileri anahtarı. L14 `show_line_labels`: fiyat etiketi anahtarı.
- L17 `show_tbl` (+`inline="tbl_view"` ile L18–L19'la aynı satırda gruplanır).
- L18 `tbl_pos`: 4 köşe. L19 `tbl_size_in`: Small/Tiny/Normal. L20 `bars_mode`: örneklem penceresi.
  Not: input değişince Pine scripti baştan hesaplar; tüm `var` durum sıfırlanır, sayaçlar temiz kurulur.

### 4.3. Yardımcılar — L26–L59

- L26–L27 `is_too_low`: sert 15m kuralı. `timeframe.in_seconds()` na dönerse (günlük üstü bazı
  periyotlar) saniye/dakika bayraklarıyla yedek hesap yapar; 900 saniyenin altı gizlenir.
  Gizleme tamdır: motor (L97), çizgiler (L235), tablo (L316) aynı bayrağa bakar.
- L29–L43 `get_bin`: RS→kademe. `else` dalı ≥100'ü yakalar (L42 `b := 5`).
- L45–L53 `bin_label`: kademe etiketi; son `=> "–"` hiçbirine uymayan teorik durumun sigortası.
- L55–L56 `format_pct`: na→"–", yoksa tek ondalık + %.
- L58–L59 `format_delta`: artıya explicit `+` işareti koyar (taban farkının yönü renkle de kodlanır: L401–L403).

### 4.4. Event-store ve sayaçlar — L62–L88

Tasarım notu: pencereli modların (`Last 500`) her kapanışta tam doğru kalması için her kapanmış
setup bir kez saklanır, sayaçlar depodan yeniden kurulur.

- L68: paketleme şeması `bin | reaches?8 | full?16 | xc2?32` (toplama ile; Pine'da bitwise `|`/`&` YOKTUR,
  o yüzden `+`, `%`, `math.floor` kullanılır — L126, L146–149).
- L70–L71 `ev_bar` (setup'ın C2 bar numarası) + `ev_code` (paketlenmiş kademe+sonuç). İkisi paralel diziler.
- L73–L76 kademe sayaçları (N / reaches / full / xc2, altışarlı), L78–L81 taban toplamları. Hepsi `var`
  (barlar arası yaşar), hepsi rebuild'de sıfırlanır (L133–L140).
- L84–L88 `max_lookback`: pencere genişliği. `var` DEĞİL — her barda inputtan yeniden okunur,
  o yüzden pencere değişimi anında geçerli olur. Pencere setup'ın **C2 barına** göre uygulanır
  (L144): sonuca göre değil, oluşuma göre örneklenir.

### 4.5. Geçmiş olay motoru — L97–L160

- L97 kapı: `bar_index >= 3` (en az [3]..[0] dörtlüsü var), `barstate.isconfirmed` (repaint yok;
  realtime tick'lerde çalışmaz, kapanışta bir kez), `not is_too_low`.
- L98–L105: C1=[3], C2=[2] OHLC okuma. Zamanlama mantığı: [0] kapanırken [2]'deki C2'nin
  C3 ([1]) ve C4 ([0]) sonucu kesinleşmiş olur.
- L107: sıfır aralıklı mum filtresi. L108–L110 sweep/reclaim şartları + dual.
  L112–L113 dual-dışı yön seçimi.
- L115–L128 (yön varsa): L116 RS; L118–L119 strict ihlal bayrakları (C3/C4);
  L121–L123 üç sonuç (reaches/full/xc2 — reaches+xc2 her zaman %100'e tamamlar);
  L125–L128 kademe + paket + depoya ekleme (`bar_index - 2` = C2'nin barı).
- L130–L160 sayaç rebuild: L133–L140 sıfırlama; L141 `ev_total`; L142 `if ev_total > 0`
  guard'ı (boş depoda `for i = 0 to -1` bar 3'te runtime patlatıyordu — 1h hotfix'i);
  L143–L160 döngü: L144 pencere filtresi, L145–L149 paket açma, L150–L160 sayma.
  Döngü confirmed kapanışlarda çalışır; tick başına maliyet sıfırdır.


Canlı (henüz sonuçlanmamış) kurulumun RAM'i. Geçmiş motordan bağımsızdır.

- L165–L172: C1=[1], C2=[0] (henüz kapanmamış bar dahil) okuma.
- L174–L181: aynı setup şartları, canlı bar üzerinde.
- L183–L193 `active_*` durumu: yön, C2 barı, C2 uçları, RS, fitil, süpürülen seviye, uç seviye,
  fail bayrağı/barı, kademe. `var` ile yaşar.
- L196–L207: C2 kapanışında (`isconfirmed` + setup var) durum güncellenir/sıfırlanır.
  L197 yön İngilizce "Bull"/"Bear" (iç kod; tablo L360'ta renge bağlanır).
  L203–L204 RS/fitil formülleri motorla aynı. L205–L206 çizilecek iki fiyat.
- L212–L216: C3+C4 boyunca her tick uç ihlali bakılır (strict). İlk ihlalde fail kilitlenir
  (`not active_failed` şartı; kilit bir daha açılmaz).
- L219 `is_setup_expired`: C4'ten sonrası. Çizgi temizliği (L288) ve `is_live` bitişi (L344) buraya bakar.

### 4.7. Çizgiler — L227–L296

- L227–L233: çizgi/etiket handle'ları (`var`, na başlar) + 3 renk (boğa yeşili, ayı kırmızısı, ihlal kırmızısı).
- L235–L244: gizli mod (düşük TF veya çizgiler kapalı) — yaşayan her şeyi silip na'lar.
  Her delete `not na` guard'lıdır (korumasız `delete(na)` runtime hatasıdır).
- L245–L264: yeni C2 kapanışında önce eskiler silinir (L251–L259), sonra L261 gri noktalı swept
  (C1 barından başlar: `active_c2_bar - 1`), L263 yön-renkli kesikli uç (C2 barından başlar).
  İkisi de `end_bar = C2+2`'de biter (L246) — 4 bar ömür.
- L266–L272: etiket yalnızca `show_line_labels` açıksa üretilir (`C2 Extreme: <fiyat>`).
- L275–L280: fail görseli — çizgi + etiket kırmızıya döner, metin `C2 Extreme (Broken ✗): <fiyat>`.
- L282–L285: etiket anahtarı sonradan kapatılırsa yaşayan etiket silinir.
- L288–L296: süre dolumu — üç nesne de guard'lı silinir, handle'lar na'lanır (girdi anahtarı orta-setup'ta oynanırsa da patlamaz).

### 4.8. Tablo — L302–L417

- L302–L311: konum + boyut çözümleme. İkisi de `var` — input değişimi scripti resetlediği için
  tazeliği sorun olmaz. `tbl_size_in`'de tanınmayan değer tiny'ye düşer.
- L313 `var table t`: tek tablo nesnesi, 6 sütun × 10 satır, koyu zemin.
- L315 `if barstate.islast`: tablo yalnızca son barda çizilir/güncellenir.
- L316–L319: düşük TF'de tabloyu sil-gizle. L320–L322: yoksa üret.
- L324–L326: taban oranları (sıfıra bölme guard'lı `total_n > 0`).
- L329–L341: başlık (sembol + periyot kısaltması: 1h/4h/Daily/...).
- L344–L366: durum panosu. `is_live` = C2'den beri ≤2 bar (L344). Faz hesabı L347–L348.
  Failde kırılma barından C3/C4 etiketi türetilir (L355). Renkler: canlı yön rengi, fail gri, boş slate.
- L369–L374: başlıklar `RS | N | Reach C4 | Full C4 | XC2 | Base Δ`.
- L377–L405: 6 kademe satırı. L380–L383 oranlar + **Base Δ = kademe Reach% − BASE Reach%**
  (matrisin survival bazıyla aynı). L385 aktif kademe mavi vurgu. L388–L393 kademe renk skalası
  (kırmızı→yeşil). L401–L403 delta renk yönü.
- L408–L413: BASE satırı (N + 3 oran + `Ref`).
- L414–L417: tablo anahtarı kapatılırsa temizlik.

## 5. Zaman akışı (bir setup'ın hayatı)

1. C2 kapanır → L196 bloğu durumu kurar; banner `LIVE: Bear (C2) · RS/Wick` olur; L261/L263 çizgileri doğar.
2. C3 akar → L212 her tick ucu yoklar. Kırılırsa L215 kilitler: çizgi kırmızı, banner
   `INVALIDATED: Bear (C3) · C2 Extreme Broken`. Kırılmazsa C3 kapanışı Reach sayımına aday olur.
3. C4 akar/kapanır → aynı takip; kapanışta L97 motoru bu setup'ı depoya yazar (sonuç kesin),
   L219/L288 çizgileri siler, banner `STANDBY (Last: …)` döner.
4. Her kapanışta L130 rebuild'i pencereyi tazeler (Tüm modda kümülatif büyür; Last 500'de kayar).

## 6. Bilinen sınırlar (bug değil, tasarım)

- TV'nin yüklediği history kadar: `max_bars_back=5000` + TV yükleme limiti. Offline 9.6M bar değil.
- Pencere C2-bazlıdır: "Last 500" = C2'si son 500 barda olan setup'lar (sonuç barına göre değil).
- Fail bayrağı intrabar güncellenir (canlı pano); istatistik motoru yalnızca confirmed çalışır.
- Gerçek stop emri modellenmez; eşitlik korunur kuralı ölçüm sözleşmesidir (not 00).
- `<15m` periyotlarda her şey gizlenir (motor dahil). 15m altı backtest bu göstergede yapılmaz.
- Oranlar betimsel, dönem içi; setup pencereleri örtüşür (bağımsız örneklem değildir).

## 7. Bakım kuralları (koda dokunan okusun)

1. `barstate.isconfirmed` motor kapısından (L97) asla kaldırılmaz; tick'te sayım = repaint.
2. İhlallerde strict `<`/`>`; eşitlik her zaman korunur (L118–L119, L213).
3. Dual outside bar elenmeye devam eder (L110, L177).
4. Her `delete` guard'lı olur; boş dizi loop'u `ev_total > 0` ister (L142 — 1h dersi).
5. Pine'da bitwise operatör YOKTUR: paketleme toplama/mod/`math.floor` ile yapılır (L126, L146–149).
6. Üçüncü çizgi / giriş / TP / "Uygun" rozeti eklenmez — felsefe §1. İsteyen not 18'deki öneriye yeni
   gösterge yazar, bunu bozmaz.
7. Yeni input eklenirse: `var` sıfırlanma davranışını ve `in_N` sıra-id'lerini bozma
   (harici otomasyon `in_3`/`in_4`/`in_5` id'lerine bağlıdır).

İlgili: [00](00_FRACTAL_MODEL_ANATOMI_VE_TANIMLAR.md) (ölçüm sözleşmesi),
[06](06_RECLAIM_STRENGTH_MASTERCLASS.md) (RS/fitil geometrisi),
[18] `_archive/18_AFEM_V3_WICK_RESCUE_VE_C2_HEDEFI.md` (entegre OLMAYAN yürütme önerisi — station arşivinde, bu repoda yok),
`data/verified_metrics.json` (offline ölçüm — station verisi, bu repoda yok).
