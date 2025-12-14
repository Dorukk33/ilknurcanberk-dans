from flask import Flask, render_template_string, request, jsonify
import re

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 Dans Okulu MP3 İndirici</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 24px;
            padding: 50px;
            width: 100%;
            max-width: 580px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 {
            color: #1e293b;
            font-size: 2.5rem;
            margin-bottom: 12px;
            background: linear-gradient(90deg, #6a11cb, #2575fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        .subtitle {
            color: #64748b;
            font-size: 1.25rem;
            font-weight: 400;
        }
        .input-section {
            margin-bottom: 32px;
        }
        .input-label {
            display: block;
            margin-bottom: 12px;
            color: #475569;
            font-weight: 600;
            font-size: 1.125rem;
        }
        .url-input {
            width: 100%;
            padding: 20px;
            font-size: 1.125rem;
            border: 2.5px solid #e2e8f0;
            border-radius: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: #f8fafc;
        }
        .url-input:focus {
            outline: none;
            border-color: #6a11cb;
            background: white;
            box-shadow: 0 0 0 4px rgba(106, 17, 203, 0.15);
            transform: translateY(-1px);
        }
        .url-input::placeholder {
            color: #94a3b8;
        }
        .btn-group {
            display: flex;
            gap: 16px;
            margin-bottom: 32px;
        }
        .btn-primary, .btn-secondary {
            flex: 1;
            padding: 22px;
            border: none;
            border-radius: 16px;
            font-size: 1.25rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        .btn-primary {
            background: linear-gradient(90deg, #6a11cb, #2575fc);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 24px rgba(106, 17, 203, 0.3);
        }
        .btn-secondary {
            background: #f1f5f9;
            color: #475569;
            border: 2px solid #e2e8f0;
        }
        .btn-secondary:hover {
            background: #e2e8f0;
            transform: translateY(-2px);
        }
        .btn-primary:disabled, .btn-secondary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        .status-box {
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 32px;
            text-align: center;
            font-size: 1.125rem;
            font-weight: 600;
            display: none;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .status-success { 
            background: linear-gradient(90deg, #d1fae5, #a7f3d0);
            color: #065f46;
            border: 2px solid #10b981;
        }
        .status-error { 
            background: linear-gradient(90deg, #fee2e2, #fecaca);
            color: #991b1b;
            border: 2px solid #ef4444;
        }
        .status-info { 
            background: linear-gradient(90deg, #dbeafe, #bfdbfe);
            color: #1e40af;
            border: 2px solid #3b82f6;
        }
        
        .sites-section {
            background: linear-gradient(90deg, #f8fafc, #f1f5f9);
            padding: 32px;
            border-radius: 20px;
            border-left: 6px solid #6a11cb;
            margin-bottom: 40px;
        }
        .sites-section h3 {
            color: #334155;
            margin-bottom: 24px;
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .sites-section h3::before {
            content: "📱";
            font-size: 1.75rem;
        }
        .site-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .site-card {
            background: white;
            padding: 24px;
            border-radius: 16px;
            border: 2px solid #e2e8f0;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .site-card:hover {
            border-color: #6a11cb;
            transform: translateY(-3px) translateX(5px);
            box-shadow: 0 12px 20px rgba(106, 17, 203, 0.15);
        }
        .site-icon {
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
            font-weight: bold;
            flex-shrink: 0;
        }
        .site-info {
            flex: 1;
        }
        .site-name {
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 6px;
            font-size: 1.125rem;
        }
        .site-desc {
            color: #64748b;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .instructions {
            background: linear-gradient(90deg, #fffbeb, #fef3c7);
            padding: 32px;
            border-radius: 20px;
            border-left: 6px solid #f59e0b;
            margin-bottom: 40px;
        }
        .instructions h3 {
            color: #92400e;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .instructions h3::before {
            content: "📋";
            font-size: 1.75rem;
        }
        .step-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .step {
            display: flex;
            align-items: flex-start;
            gap: 20px;
        }
        .step-number {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.25rem;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }
        .step-text {
            color: #92400e;
            font-size: 1.1rem;
            line-height: 1.6;
            padding-top: 8px;
        }
        .step-text strong {
            color: #78350f;
        }
        
        .footer {
            text-align: center;
            padding-top: 32px;
            border-top: 2px solid #e2e8f0;
        }
        .footer-text {
            color: #64748b;
            font-size: 1.125rem;
            line-height: 1.6;
        }
        .highlight {
            background: linear-gradient(90deg, #6a11cb, #2575fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-style: italic;
        }
        
        /* Responsive */
        @media (max-width: 640px) {
            .container { padding: 30px; border-radius: 20px; }
            h1 { font-size: 2rem; }
            .btn-group { flex-direction: column; }
            .site-grid { grid-template-columns: 1fr; }
            .step { flex-direction: column; align-items: center; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Dans Okulu MP3 İndirici</h1>
            <p class="subtitle">YouTube'dan müzikleri en kolay yoldan indirin</p>
        </div>
        
        <div class="input-section">
            <label class="input-label">YouTube Linkiniz:</label>
            <input type="text" id="youtubeUrl" class="url-input" 
                   placeholder="https://www.youtube.com/watch?v=..." 
                   autocomplete="off" value="https://www.youtube.com/watch?v=5qap5aO4i9A">
        </div>
        
        <div class="btn-group">
            <button class="btn-primary" onclick="convertAndRedirect()" id="convertBtn">
                <span>🚀</span> OTOMATİK MP3'E ÇEVİR
            </button>
            <button class="btn-secondary" onclick="showRecommendedSites()" id="sitesBtn">
                <span>📱</span> SİTELERİ GÖSTER
            </button>
        </div>
        
        <div id="status" class="status-box"></div>
        
        <div class="sites-section" id="sitesSection" style="display: none;">
            <h3>Önerilen MP3 İndirme Siteleri</h3>
            <div class="site-grid">
                <div class="site-card" onclick="openSite('https://ytmp3.nu')">
                    <div class="site-icon">1</div>
                    <div class="site-info">
                        <div class="site-name">ytmp3.nu</div>
                        <div class="site-desc">En hızlı ve güvenilir site, yüksek kalite MP3</div>
                    </div>
                </div>
                <div class="site-card" onclick="openSite('https://y2mate.guru')">
                    <div class="site-icon">2</div>
                    <div class="site-info">
                        <div class="site-name">y2mate.guru</div>
                        <div class="site-desc">YouTube, Facebook, Twitter desteği</div>
                    </div>
                </div>
                <div class="site-card" onclick="openSite('https://mp3-convert.org')">
                    <div class="site-icon">3</div>
                    <div class="site-info">
                        <div class="site-name">mp3-convert.org</div>
                        <div class="site-desc">Basit ve reklamsız arayüz</div>
                    </div>
                </div>
                <div class="site-card" onclick="openSite('https://ytmp3.cc')">
                    <div class="site-icon">4</div>
                    <div class="site-info">
                        <div class="site-name">ytmp3.cc</div>
                        <div class="site-desc">Hızlı dönüşüm, mobil uyumlu</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="instructions">
            <h3>Nasıl Kullanılır?</h3>
            <div class="step-list">
                <div class="step">
                    <div class="step-number">A</div>
                    <div class="step-text">
                        <strong>OTOMATİK ÇEVİRME:</strong> YouTube linkini yukarıya yapıştır, "OTOMATİK MP3'E ÇEVİR" butonuna tıkla. En iyi siteye yönlendirileceksin.
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">B</div>
                    <div class="step-text">
                        <strong>MANUEL SEÇİM:</strong> "SİTELERİ GÖSTER" butonuna tıkla, açılan sitelerden birini seç, YouTube linkini oraya yapıştır ve MP3'ü indir.
                    </div>
                </div>
                <div class="step">
                    <div class="step-number">C</div>
                    <div class="step-text">
                        <strong>TEKRAR İNDİR:</strong> Yeni bir müzik indirmek için sayfayı yenile veya "Sıradakini Dönüştür" butonuna tıkla.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p class="footer-text">
                💃 <span class="highlight">İlknur Canberk </span> için özel olarak hazırlanmıştır ❤️<br>
                <small style="color: #94a3b8; font-size: 0.95rem; display: block; margin-top: 12px;">
                    Not: Bu araç YouTube bot engellerini aşmak için güvenilir üçüncü parti servislere yönlendirme yapar.
                </small>
            </p>
        </div>
    </div>

    <script>
        function showStatus(message, type) {
            const statusBox = document.getElementById('status');
            statusBox.innerHTML = `<span>${message}</span>`;
            statusBox.className = `status-box status-${type}`;
            statusBox.style.display = 'block';
            
            // Otomatik gizleme
            if (type === 'success') {
                setTimeout(() => {
                    statusBox.style.display = 'none';
                }, 5000);
            }
        }
        
        function showRecommendedSites() {
            const section = document.getElementById('sitesSection');
            section.style.display = 'block';
            showStatus('👇 Aşağıdaki sitelerden birini seçebilirsiniz. YouTube linkini oraya yapıştırın.', 'info');
            // Sayfayı kaydır
            section.scrollIntoView({ behavior: 'smooth' });
        }
        
        function openSite(url) {
            window.open(url, '_blank');
            showStatus('✅ Site yeni sekmede açıldı! YouTube linkini oraya yapıştırın.', 'success');
        }
        
        function extractVideoId(url) {
            // YouTube video ID'sini çıkaran fonksiyon
            const patterns = [
                /youtu\.be\/([^#\&\?]{11})/,  // youtu.be/xxxxx
                /\?v=([^#\&\?]{11})/,         // ?v=xxxxx
                /&v=([^#\&\?]{11})/,          // &v=xxxxx
                /embed\/([^#\&\?]{11})/,      // embed/xxxxx
                /\/v\/([^#\&\?]{11})/         // /v/xxxxx
            ];
            
            for (const pattern of patterns) {
                const match = url.match(pattern);
                if (match) {
                    return match[1];
                }
            }
            return null;
        }
        
        async function convertAndRedirect() {
            const url = document.getElementById('youtubeUrl').value.trim();
            const btn = document.getElementById('convertBtn');
            
            // Kontroller
            if (!url) {
                showStatus('⚠️ Lütfen YouTube linkini girin!', 'error');
                return;
            }
            
            // YouTube linki kontrolü
            if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
                showStatus('❌ Geçerli bir YouTube linki girin!', 'error');
                return;
            }
            
            // Video ID çıkar
            const videoId = extractVideoId(url);
            if (!videoId || videoId.length !== 11) {
                showStatus('❌ YouTube linkini kontrol edin!', 'error');
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '<span>⏳</span> YÖNLENDİRİLİYOR...';
            showStatus('En iyi MP3 sitesine yönlendiriliyor, lütfen bekleyin...', 'info');
            
            // 1.5 saniye bekle (kullanıcı deneyimi için)
            setTimeout(() => {
                // EN GÜVENİLİR SİTEYE YÖNLENDİR
                const bestSite = `https://ytmp3.nu/@api/button/mp3/${videoId}`;
                
                // Yeni sekmede aç
                window.open(bestSite, '_blank');
                
                // Başarı mesajı göster
                showStatus('✅ <strong>ytmp3.nu</strong> sitesi açıldı! YouTube linkini oraya yapıştırın.', 'success');
                
                // Input'u temizle (opsiyonel)
                // document.getElementById('youtubeUrl').value = '';
                
                // Butonu eski haline getir
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<span>🚀</span> OTOMATİK MP3\'E ÇEVİR';
                }, 1500);
                
            }, 1500);
        }
        
        // Enter tuşu ile çevirme
        document.getElementById('youtubeUrl').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                convertAndRedirect();
            }
        });
        
        // Sayfa yüklendiğinde örnek link göster
        window.onload = function() {
            // Örnek link zaten input'ta var
            console.log('🎵 Dans Okulu MP3 İndirici hazır!');
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/recommended_sites')
def recommended_sites():
    """Önerilen MP3 sitelerini döndürür"""
    sites = [
        {
            "name": "ytmp3.nu",
            "url": "https://ytmp3.nu",
            "description": "En hızlı ve güvenilir site",
            "icon": "1"
        },
        {
            "name": "y2mate.guru",
            "url": "https://y2mate.guru",
            "description": "YouTube, Facebook, Twitter desteği",
            "icon": "2"
        },
        {
            "name": "mp3-convert.org",
            "url": "https://mp3-convert.org",
            "description": "Basit ve reklamsız arayüz",
            "icon": "3"
        },
        {
            "name": "ytmp3.cc",
            "url": "https://ytmp3.cc",
            "description": "Hızlı dönüşüm, mobil uyumlu",
            "icon": "4"
        }
    ]
    return jsonify({"sites": sites})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
