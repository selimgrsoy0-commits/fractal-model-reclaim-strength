# 06: Reclaim gücü: fiyat geometrisi ve koşullu frekans

Güncelleme: 5 Eylül 2026. Güncel ölçüm sözleşmesi v1.

RS, C2 kapanışının C1 aralığına göre konumudur. Yüksek RS ile daha yüksek survival görülmesi araştırılabilir bir ilişkidir; tek başına nedensellik veya PnL ispatı değildir. C2 ucundan daha uzakta kapanmak korunma olasılığı ile stop mesafesini birlikte etkileyebilir.

Dashboard her RS/fitil hücresinde olay sayısını ve sonucu aynı yerel örneklemden hesaplar. Önceki %43–90 sabit skala tüm sembol/zaman dilimlerine kopyalanmaz. Boş hücreler null, küçük örneklemler açıkça işaretlidir.

Eski “ölüm bölgesi” etiketinin dar tanımı RS<10 ve sweep derinliği<20 idi. Bunu RS<25 / fitil<35’e genişletip sabit %80 stop atamak hatalıydı. Aktif ekran sabit ölüm bölgesi olasılığı veya işlem direktifi üretmez.

Kaynaklar: [ölçüm çıktısı](../data/verified_metrics.json), [analiz kodu](../scripts/analyze_eurusd.py), [önceki sürüm arşivi](../data/legacy_snapshot.json).

## Görsel rehber: iki ayrı payda

Dashboard’un ilk bölümünde boğa/ayı seçilebilen eğitim mumları var. C1 aralığı 100–110, C2 high=109, low=95, close=107 ise RS=(107−100)/10=%70; sweep=(100−95)/(109−95)=%35,71 olur. C2 open=103 ise tüm alt fitil 8 birimdir; sweep 5 birimdir. Bu yüzdeler birbirinin tamamlayıcısı değildir.

Orijinal [kaynak matris](../images/01_nq/t1_c1_15m_3.jpg) ikinci ekseni “rejection wick, % of C2 candle” diye adlandırır; açık formül vermez. Yerel sweep oranının bu kaynak tanımıyla birebir eşleştiği doğrulanmadı. Aktif çizim ve tablolar yerel formülü açıkça kullanır.

RS tek başına işlem tetiği değildir. [TTrades C3](https://ttrades.com/how-to-trade-candle-3-in-the-fractal-model/) ve [C4](https://ttrades.com/ttrades-fractal-model-candle-4/) anlatımları üst zaman dilimi bağlamı ve LTF teyidini içerir. Kaynağın yöntem anlatımı yerel veri üzerinde kâr kanıtı değildir.
