from flask import Flask, request, jsonify, send_file, render_template_string
import yt_dlp
import tempfile
import os
import re
import random
import time

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎵 Dans Okulu MP3 İndirici</title>
    <style>
        body { font-family: Arial; background: #667eea; padding: 20px; }
        .container { background: white; padding: 30px; border-radius: 15px; max-width: 500px; margin: auto; }
        input, button { width: 100%; padding: 15px; margin: 10px 0; font-size: 16px; }
        button { background: #764ba2; color: white; border: none; cursor: pointer; }
        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 14px; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Dans Okulu MP3 İndirici</h1>
        <input id="url" placeholder="YouTube linkini yapıştır...">
        <button onclick="indir()">MP3 İNDİR</button>
        <div id="status"></div>
        <div class="footer">
            <p>💃 İlknur Canberk Dans Okulu için özel hazırlanmıştır ❤️</p>
        </div>
    </div>
    <script>
        async function indir() {
            const url = document.getElementById('url').value;
            const status = document.getElementById('status');
            status.innerHTML = '⏳ İndiriliyor...';
            status.style.color = 'blue';
            
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({url:url})
                });
                const data = await response.json();
                
                if(data.basarili) {
                    status.innerHTML = '✅ İndirildi!';
                    const link = document.createElement('a');
                    link.href = '/dosya/' + encodeURIComponent(data.dosya);
                    link.download = data.dosya;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else {
                    status.innerHTML = '❌ ' + data.hata;
                }
            } catch(e) {
                status.innerHTML = '❌ Bağlantı hatası';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

def get_random_user_agent():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    ]
    return random.choice(agents)

@app.route('/download', methods=['POST'])
def indir():
    try:
        data = request.json
        youtube_url = data['url']
        
        temp_dir = tempfile.gettempdir()
        
        # 🚨 BOT ENGELİ ÇÖZÜMLÜ AYARLAR
        ydl_opts = {
            # 1. FORMAT STRATEJİSİ
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'format_sort': ['size', 'abr'],
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            
            # 2. USER-AGENT ROTATION
            'http_headers': {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            },
            
            # 3. EXTRACTOR BYPASS
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                    'player_skip': ['configs', 'webpage', 'js'],
                    'skip': ['hls', 'dash'],
                    'throttled': True,
                }
            },
            
            # 4. NETWORK BYPASS
            'socket_timeout': 30,
            'extract_timeout': 60,
            'retries': 15,
            'fragment_retries': 15,
            'skip_unavailable_fragments': True,
            'keep_fragments': True,
            'continuedl': True,
            'noprogress': True,
            'consoletitle': False,
            
            # 5. THROTTLING (bot gibi görünme)
            'sleep_interval': random.randint(2, 5),
            'max_sleep_interval': 8,
            'sleep_interval_requests': random.randint(1, 3),
            
            # 6. COOKIE SIMULATION
            'cookiefile': None,
            'use_cookies': True,
            'cookiesfrombrowser': ('chrome',),
            
            # 7. IP BYPASS
            'source_address': None,
            'force_ipv4': True,
            'force_ipv6': False,
            'geo_bypass': True,
            'geo_bypass_country': random.choice(['US', 'TR', 'DE', 'GB', 'FR']),
            'geo_bypass_ip_block': None,
            
            # 8. RATE LIMIT BYPASS
            'ratelimit': random.randint(500000, 1000000),  # 500KB/s - 1MB/s
            'throttledratelimit': None,
            'buffersize': 1024 * 1024,
            'noresizebuffer': True,
            'http_chunk_size': 1048576,
            
            # 9. POST-PROCESSOR
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            
            # 10. DEBUG (kapalı - bot gibi görünme)
            'verbose': False,
            'no_warnings': True,
            'ignoreerrors': False,
            'no_color': True,
            'simulate': False,
            'skip_download': False,
            'geturl': False,
            'gettitle': False,
            'getid': False,
            'getthumbnail': False,
            'getdescription': False,
            'getfilename': False,
            'getformat': False,
            'getduration': False,
            'quiet': True,
            'no_call_home': True,
            'no_check_certificate': True,
            'prefer_insecure': True,
            'user_agent': get_random_user_agent(),
            'referer': 'https://www.youtube.com/',
            'add_header': [
                'X-Forwarded-For: ' + '.'.join(str(random.randint(1, 255)) for _ in range(4)),
                'X-Client-Data: ' + ''.join(random.choices('0123456789abcdef', k=32)),
            ],
        }
        
        print(f"Bot bypass ile indirme: {youtube_url}")
        
        # Rastgele bekle (bot pattern'i kır)
        time.sleep(random.uniform(1.0, 3.0))
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Önce bilgi al (download=False)
            info = ydl.extract_info(youtube_url, download=False)
            video_title = info.get('title', 'muzik')
            print(f"Video: {video_title}")
            
            # Formatları kontrol et
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if not audio_formats:
                # Audio formatı yoksa, en iyi combined format
                ydl_opts['format'] = 'best[height<=720]'
            
            # İndir
            ydl.download([youtube_url])
            
            # Dosyayı bul
            for file in os.listdir(temp_dir):
                if (file.endswith('.mp3') or file.endswith('.m4a') or file.endswith('.webm')) and video_title[:30] in file:
                    dosya_adi = file
                    if file.endswith('.m4a') or file.endswith('.webm'):
                        # MP3'e çevir
                        base = os.path.splitext(file)[0]
                        mp3_file = base + '.mp3'
                        os.rename(os.path.join(temp_dir, file), os.path.join(temp_dir, mp3_file))
                        dosya_adi = mp3_file
                    
                    # Dosya boyutu kontrolü
                    file_path = os.path.join(temp_dir, dosya_adi)
                    if os.path.getsize(file_path) > 10240:  # 10KB'den büyükse
                        return jsonify({'basarili': True, 'dosya': dosya_adi})
                    else:
                        os.remove(file_path)
                        return jsonify({'basarili': False, 'hata': 'YouTube engelledi. Farklı link deneyin.'})
            
            return jsonify({'basarili': False, 'hata': 'Dosya oluşturulamadı'})
            
    except Exception as e:
        error_msg = str(e)
        print(f"Bot hatası: {error_msg}")
        
        # ÖZEL BOT ÇÖZÜMÜ
        if "Sign in" in error_msg or "bot" in error_msg.lower() or "confirm" in error_msg:
            # ALTERNATİF YÖNTEM: extractor değiştir
            try:
                return alternatif_indir(youtube_url)
            except:
                return jsonify({'basarili': False, 'hata': 'YouTube bot engeli. 15 dakika sonra tekrar deneyin.'})
        
        return jsonify({'basarili': False, 'hata': 'Teknik hata'})

def alternatif_indir(url):
    """ALTERNATİF BOT BYPASS YÖNTEMİ"""
    temp_dir = tempfile.gettempdir()
    
    ydl_opts = {
        # EN BASİT FORMAT
        'format': 'worstaudio/worst',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        
        # MOBILE CLIENT GİBİ DAVRAN
        'user_agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
        'referer': 'https://m.youtube.com/',
        
        # MOBILE API
        'extractor_args': {
            'youtube': {
                'player_client': 'android',
                'player_skip': ['webpage'],
            }
        },
        
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get('title', 'muzik')
        
        for file in os.listdir(temp_dir):
            if file.endswith('.mp3') and video_title[:20] in file:
                return {'basarili': True, 'dosya': file}
    
    raise Exception("Alternatif yöntem de başarısız")

@app.route('/dosya/<dosya_adi>')
def dosya_getir(dosya_adi):
    temp_dir = tempfile.gettempdir()
    for dosya in os.listdir(temp_dir):
        if dosya.endswith('.mp3'):
            return send_file(os.path.join(temp_dir, dosya), as_attachment=True)
    return 'Dosya bulunamadı', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
