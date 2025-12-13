from flask import Flask, request, jsonify, send_file, render_template_string
import yt_dlp
import tempfile
import os
import re
import time

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
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
        }
        input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 20px;
        }
        button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(to right, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .status {
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            display: none;
            font-weight: bold;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .loading { background: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Dans Okulu MP3 İndirici</h1>
        <input type="text" id="urlInput" placeholder="YouTube linkini buraya yapıştır...">
        <button id="downloadBtn" onclick="downloadMusic()">MP3 İNDİR</button>
        <div id="status" class="status"></div>
        <p style="color: #666; font-size: 14px; text-align: center;">
            İlknur Canberk için özel yapıldı ❤️
        </p>
    </div>

    <script>
        async function downloadMusic() {
            const url = document.getElementById('urlInput').value.trim();
            const btn = document.getElementById('downloadBtn');
            const status = document.getElementById('status');
            
            if (!url) {
                showStatus('⚠️ Lütfen YouTube linkini girin!', 'error');
                return;
            }
            
            if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
                showStatus('❌ Geçerli bir YouTube linki girin!', 'error');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = '⏳ İndiriliyor...';
            showStatus('Müzik indiriliyor, lütfen bekleyin (1-2 dakika)...', 'loading');
            
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('✅ Müzik başarıyla indirildi!', 'success');
                    
                    // Dosyayı indir
                    const downloadLink = document.createElement('a');
                    downloadLink.href = '/file/' + encodeURIComponent(result.filename);
                    downloadLink.download = result.filename;
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                    
                    // Input'u temizle
                    document.getElementById('urlInput').value = '';
                    
                } else {
                    showStatus('❌ Hata: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('❌ İndirme sırasında hata oluştu', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'MP3 İNDİR';
            }
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
        
        // Enter tuşu ile indirme
        document.getElementById('urlInput').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                downloadMusic();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'success': False, 'error': 'URL gerekli'})
        
        # Geçici dosya
        temp_dir = tempfile.gettempdir()
        
        # YT-DLP AYARLARI (BOT ENGELİ ÇÖZÜMLÜ)
        ydl_opts = {
            # Format seçimi
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            
            # Bot engeli bypass
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            
            # HTTP Headers (tarayıcı gibi davran)
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            
            # Extractor ayarları
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['configs', 'webpage', 'js'],
                    'skip': ['hls', 'dash'],
                }
            },
            
            # Retry mekanizması
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'keep_fragments': True,
            
            # Throttle (çok hızlı istek yapma)
            'sleep_interval': 2,
            'max_sleep_interval': 5,
            
            # Cookie kullan (opsiyonel)
            'cookiefile': os.path.join(temp_dir, 'cookies.txt') if os.path.exists(os.path.join(temp_dir, 'cookies.txt')) else None,
            
            # Post-processor (MP3'e çevir)
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            
            # Geçici çözümler
            'force_ipv4': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'geo_bypass_ip_block': None,
        }
        
        print(f"İndirme başlıyor: {youtube_url}")
        
        # Müziği indir
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Önce info al
            info = ydl.extract_info(youtube_url, download=False)
            print(f"Video bulundu: {info.get('title', 'Bilinmeyen')}")
            
            # Sonra indir
            ydl.download([youtube_url])
            
            video_title = info.get('title', 'muzik')
            
            # Güvenli dosya adı
            safe_title = re.sub(r'[^\w\s-]', '', video_title)
            safe_title = safe_title.strip()[:40]
            if not safe_title:
                safe_title = "muzik"
            filename = safe_title + ".mp3"
            
            # Dosyayı bul
            for file in os.listdir(temp_dir):
                if file.endswith('.mp3') and video_title[:30] in file:
                    actual_file = file
                    break
            else:
                # Yeni isimle dosyayı ara
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp3'):
                        actual_file = file
                        # Dosyayı yeniden adlandır
                        new_path = os.path.join(temp_dir, filename)
                        old_path = os.path.join(temp_dir, file)
                        if os.path.exists(old_path):
                            os.rename(old_path, new_path)
                        break
                else:
                    actual_file = filename
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Müzik başarıyla indirildi!'
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"HATA: {error_msg}")
        
        # Özel hata mesajları
        if "Sign in to confirm" in error_msg:
            error_msg = "YouTube bot engeli! 10 dakika bekleyip tekrar deneyin."
        elif "Private video" in error_msg:
            error_msg = "Bu video özel veya erişime kapalı."
        elif " unavailable" in error_msg:
            error_msg = "Video bulunamadı veya kaldırılmış."
        elif "Too Many Requests" in error_msg:
            error_msg = "Çok fazla istek gönderildi. Lütfen 30 dakika bekleyin."
        
        return jsonify({'success': False, 'error': error_msg})

@app.route('/file/<filename>')
def get_file(filename):
    try:
        temp_dir = tempfile.gettempdir()
        
        # Dosyayı bul
        for file in os.listdir(temp_dir):
            if file.endswith('.mp3') and (filename.replace('.mp3', '') in file or file.replace('.mp3', '') in filename):
                file_path = os.path.join(temp_dir, file)
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='audio/mpeg'
                )
        
        return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
