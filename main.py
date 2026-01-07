from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import random
import os 

app = Flask(__name__)

state = {
    "puan": 0,
    "hizli_musait": True,
    "uzun_musait": True,
    "hizli_yeni_zaman": None,
    "uzun_yeni_zaman": None,
    "aktif_hizli": None,
    "aktif_uzun": None
}

hizli_gorevler = [
    {"id": 1, "baslik": "Işık Avcısı", "gorev": "Odaların ışığını kapat.", "puan": 10},
    {"id": 2, "baslik": "Fiş Operasyonu", "gorev": "Kullanmadığın fişleri çek.", "puan": 15},
    {"id": 3, "baslik": "Su Tasarrufu", "gorev": "Muslukları kontrol et.", "puan": 10},
    {"id": 4, "baslik": "Dijital Temizlik", "gorev": "Gereksiz 10 e-postayı sil.", "puan": 20},
    {"id": 5, "baslik": "Güneş Gücü", "gorev": "Perdeleri aç, doğal ışığı kullan.", "puan": 10},
    {"id": 6, "baslik": "Matara Modu", "gorev": "Bugün dışarıdan pet şişe su alma.", "puan": 25},
    {"id": 7, "baslik": "Merdiven Zamanı", "gorev": "Asansör yerine merdiven kullan.", "puan": 15},
    {"id": 8, "baslik": "Eko-Mod", "gorev": "Bilgisayarını 'Güç Tasarrufu' moduna al.", "puan": 10},
    {"id": 9, "baslik": "Soğuk Su Akımı", "gorev": "Elerini yıkarken sadece soğuk su kullan.", "puan": 15},
    {"id": 10, "baslik": "Kağıt Tasarrufu", "gorev": "Alışveriş fişini dijital olarak iste.", "puan": 20},
    {"id": 11, "baslik": "Parlaklık Kontrolü", "gorev": "Telefonunun parlaklığını %40 indir.", "puan": 15},
    {"id": 12, "baslik": "Kupa Modu", "gorev": "Karton bardak yerine kendi kupanı kullan.", "puan": 35}
]

uzun_gorevler = [
    {"id": 101, "baslik": "Atık Detoksu", "gorev": "Haftalık plastik kullanımını kes.", "puan": 150},
    {"id": 102, "baslik": "Yeşil Ulaşım", "gorev": "3 gün boyunca sadece yürü.", "puan": 200},
    {"id": 103, "baslik": "Etsiz Gün", "gorev": "Bugün tamamen sebze ağırlıklı beslen.", "puan": 100},
    {"id": 104, "baslik": "Sıfır Atık", "gorev": "Evdeki çöpleri kağıt/metal ayır.", "puan": 250},
    {"id": 105, "baslik": "Bez Çanta Devrimi", "gorev": "Bu haftaki market alışverişlerinde poşet kullanma.", "puan": 120},
    {"id": 106, "baslik": "Kısa Duş", "gorev": "Duş süreni 5 dakikanın altına indir.", "puan": 100},
    {"id": 107, "baslik": "Eko-Alışveriş", "gorev": "Yerel üreticiden/pazardan alışveriş yap.", "puan": 180},
    {"id": 108, "baslik": "İkinci Şans", "gorev": "Eski bir eşyanı atmayıp tamir et veya dönüştür.", "puan": 300},
    {"id": 109, "baslik": "Toplu Taşıma Haftası", "gorev": "Tüm hafta boyunca şahsi aracını kullanma.", "puan": 400},
    {"id": 110, "baslik": "İkinci El Dostu", "gorev": "Yeni bir şey almak yerine 2. el opsiyonlara bak.", "puan": 200},
    {"id": 111, "baslik": "Moda Diyeti", "gorev": "Bu ay hiç yeni kıyafet satın alma.", "puan": 350},
    {"id": 112, "baslik": "Gıda Koruyucu", "gorev": "Hafta boyunca hiç yemek israf etme/çöpe atma.", "puan": 280}
]

@app.route('/', methods=['GET', 'POST'])
def index():
    simdi = datetime.now()
    

    if state["aktif_hizli"] is None or (not state["hizli_musait"] and simdi >= state["hizli_yeni_zaman"]):
        state["aktif_hizli"] = random.choice(hizli_gorevler)
        state["hizli_musait"] = True

    if state["aktif_uzun"] is None or (not state["uzun_musait"] and simdi >= state["uzun_yeni_zaman"]):
        state["aktif_uzun"] = random.choice(uzun_gorevler)
        state["uzun_musait"] = True


    hizli_timer = ""
    uzun_timer = ""
    if not state["hizli_musait"]:
        fark = state["hizli_yeni_zaman"] - simdi
        hizli_timer = f"{fark.seconds // 60} dk kaldı"
    if not state["uzun_musait"]:
        fark = state["uzun_yeni_zaman"] - simdi
        uzun_timer = f"{fark.days} gün {fark.seconds // 3600} sa kaldı"


    sonuc, agac = None, 0
    if request.method == 'POST':
        try:
            km = abs(float(request.form.get('km', 0)))
            arac = request.form.get('arac', 'benzin')

            katsayilar = {"benzin": 120, "dizel": 140, "elektrik": 50, "toplu": 20, "hibrit": 70}
            salinim = (km * katsayilar.get(arac, 120)) / 1000
            sonuc = f"{salinim:.2f} kg CO2"
            agac = round((salinim * 365) / 20)
        except: sonuc = "Hatalı veri!"

    return render_template('index.html', p=state, ht=hizli_timer, ut=uzun_timer, s=sonuc, a=agac)

@app.route('/tamamla/<tur>/<int:miktar>')
def tamamla(tur, miktar):
    state["puan"] += miktar
    simdi = datetime.now()
    if tur == "hizli":
        state["hizli_musait"] = False
        state["hizli_yeni_zaman"] = simdi + timedelta(seconds=10)
    else:
        state["uzun_musait"] = False
        state["uzun_yeni_zaman"] = simdi + timedelta(days=1)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)