# 00: Tanımlar ve ölçüm sözleşmesi

Güncelleme: 5 Eylül 2026. Güncel ölçüm sözleşmesi v1.

C1 referans, C2 sweep/reclaim, C3 ve C4 takip mumlarıdır. Setup yalnızca C2 kapanışında sınıflanır.

Boğa: C2 low < C1 low ve C2 close > C1 low. Ayı: C2 high > C1 high ve C2 close < C1 high. İki şartı birden sağlayan outside bar yönü belirsiz olduğu için dışlanır. Sıfır aralıklı C1/C2 dışlanır.

- Boğa RS = 100 × (C2 close − C1 low) / (C1 high − C1 low).
- Ayı RS = 100 × (C1 high − C2 close) / (C1 high − C1 low).
- Boğa sweep derinliği = 100 × (C1 low − C2 low) / C2 range.
- Ayı sweep derinliği = 100 × (C2 high − C1 high) / C2 range.

Sweep derinliği, standart mum fitili/gövde oranıyla aynı değildir. Kademeler [0,10), [10,25), [25,50), [50,75), [75,100), [100,∞) şeklindedir; tam %100 son kademededir.

**C4’e ulaşma:** C3 boyunca C2 ucu ihlal edilmedi. **Tam C4 korunması:** C3 ve C4 boyunca ihlal edilmedi. **XC2:** C3 veya C4 içinde ihlal. İhlal strict < / >; eşitlik olay tanımında korunur. Bu eşitlik kuralı gerçek stop emrinin tetiklenme kuralı değildir.

**C3 continuation:** Boğada C3 high > C2 high; ayıda C3 low < C2 low. Önce stop mu hedef mi geldiğini söylemez. C3 yönlü kapanışı, boğada close > open, ayıda close < open; doji başarısız yönlü kapanıştır.

Kaynaklar: [ölçüm çıktısı](../data/verified_metrics.json), [analiz kodu](../scripts/analyze_eurusd.py), [önceki sürüm arşivi](../data/legacy_snapshot.json).
