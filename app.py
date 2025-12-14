from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 Dans Okulu MP3 İndirici</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        button {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        .btn-primary {
            background: #6a11cb;
            color: white;
        }
        .btn-primary:hover {
            background: #5a0db5;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #f1f1f1;
            color: #333;
        }
        .btn-secondary:hover {
            background: #e1e1e1;
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
            font-weight: bold;
        }
        .success { background: #d4ffd4; color: #006600; }
        .error { background: #ffd4d4; color: #cc0000; }
        .info { background: #d4eaff; color: #0044cc; }
        .footer {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Dans Okulu MP3 İndirici</h1>
        
        <input type="text" id="urlInput" 
               placeholder="YouTube linkini yapıştır..." 
               value="https://www.youtube.com/watch?v=5qap5aO4i9A">
        
        <div class="button-group">
            <button class="btn-primary" onclick="convert()" id="convertBtn">🚀 MP3 İNDİR</button>
            <button class="btn-secondary" onclick="showSites()">📱 SİTELER</button>
        </div>
        
        <div id="status"></div>
        
        <div id="sitesBox" style="display: none; background: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 10px;">
            <p style="margin-top: 0; font-weight: bold;">Hızlı Siteler:</p>
            <button onclick="openSite('https://ytmp3.nu')" style="width: 100%; margin: 5px 0;">1. ytmp3.nu</button>
            <button onclick="openSite('https://y2mate.guru')" style="width: 100%; margin: 5px 0;">2. y2mate.guru</button>
            <button onclick="openSite('https://mp3-convert.org')" style="width: 100%; margin: 5px 0;">3. mp3-convert.org</button>
        </div>
        
        <div class="footer">
            <p>💃 İlknur Canberk için hazırlandı ❤️</p>
        </div>
    </div>

    <script>
        function showStatus(msg, type) {
            const status = document.getElementById('status');
            status.innerHTML = msg;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
        
        function showSites() {
            const box = document.getElementById('sitesBox');
            box.style.display = box.style.display === 'none' ? 'block' : 'none';
        }
        
        function openSite(url) {
            window.open(url, '_blank');
            showStatus('Site açıldı! Linki oraya yapıştır.', 'info');
        }
        
        function convert() {
            const url = document.getElementById('urlInput').value.trim();
            const btn = document.getElementById('convertBtn');
            
            if (!url) {
                showStatus('⚠️ Link girin!', 'error');
                return;
            }
            
            // Basit URL kontrolü
            if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
                showStatus('❌ Geçerli YouTube linki girin!', 'error');
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '⏳ Yönlendiriliyor...';
            showStatus('En iyi siteye yönlendiriliyor...', 'info');
            
            // Video ID çıkarma (basit)
            let videoId = '';
            if (url.includes('youtu.be/')) {
                videoId = url.split('youtu.be/')[1].split('?')[0];
            } else if (url.includes('v=')) {
                videoId = url.split('v=')[1].split('&')[0];
            }
            
            // Yönlendirme
            setTimeout(() => {
                if (videoId && videoId.length === 11) {
                    window.open('https://ytmp3.nu/@api/button/mp3/' + videoId, '_blank');
                    showStatus('✅ ytmp3.nu açıldı! Linki oraya yapıştır.', 'success');
                } else {
                    // ID bulunamazsa direkt siteye yönlendir
                    window.open('https://ytmp3.nu', '_blank');
                    showStatus('✅ ytmp3.nu açıldı! Linki kopyala-yapıştır.', 'success');
                }
                
                btn.disabled = false;
                btn.innerHTML = '🚀 MP3 İNDİR';
            }, 1000);
        }
        
        // Enter tuşu desteği
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') convert();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
