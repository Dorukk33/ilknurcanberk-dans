from flask import Flask, request, jsonify, send_file, render_template_string
import yt_dlp
import tempfile
import os
import re
import subprocess
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Dans Okulu MP3 İndirici</h1>
        <input id="url" placeholder="YouTube linkini yapıştır...">
        <button onclick="indir()">MP3 İNDİR</button>
        <div id="status"></div>
        <p><strong>Nasıl Kullanılır?</strong><br>
        1. YouTube linkini kopyala<br>
        2. Yukarıya yapıştır<br>
        3. Butona tıkla<br>
        4. Müzik inecek!</p>
    </div>
    <script>
        async function indir() {
            const url = document.getElementById('url').value;
            const status = document.getElementById('status');
            status.innerHTML = '⏳ İndiriliyor... (1-2 dk sürebilir)';
            status.style.color = 'blue';
            
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({url:url})
                });
                const data = await response.json();
                
                if(data.basarili) {
                    status.innerHTML = '✅ İndirildi! Dosya açılıyor...';
                    // Dosyayı indir
                    const link = document.createElement('a');
                    link.href = '/dosya/' + encodeURIComponent(data.dosya);
                    link.download = data.dosya;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                } else {
                    status.innerHTML = '❌ Hata: ' + data.hata;
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

@app.route('/download', methods=['POST'])
def indir():
    try:
        data = request.json
        url = data['url']
        
        temp_dir = tempfile.gettempdir()
        
        # YENİ YÖNTEM: External downloader kullan
        ydl_opts = {
            # Format seçimi - direkt audio stream
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            
            # EXTERNAL DOWNLOADER - YouTube'u bypass et
            'external_downloader': 'aria2c',
            'external_downloader_args': ['--max-connection-per-server=16', '--split=16', '--min-split-size=1M'],
            
            # Veya ffmpeg ile direkt stream
            #'external_downloader': 'ffmpeg',
            #'external_downloader_args': ['-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5'],
            
            # Retry mekanizması
            'retries': 20,
            'fragment_retries': 20,
            'skip_unavailable_fragments': False,
            'keep_fragments': True,
            
            # Timeout süreleri
            'socket_timeout': 30,
            'extract_timeout': 60,
            'download_timeout': 300,  # 5 dakika
            
            # HTTP ayarları
            'http_chunk_size': 10485760,  # 10MB chunk
            'continuedl': True,
            
            # Post-processor
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            
            # Debug için
            'verbose': True,
            'no_warnings': False,
            'quiet': False,
        }
        
        print(f"İndirme başlıyor: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Önce bilgileri al
            info = ydl.extract_info(url, download=False)
            print(f"Video info: {info['title']}")
            print(f"Formats: {[f['format_id'] for f in info['formats'] if f.get('acodec') != 'none']}")
            
            # En iyi audio formatını bul
            audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            if audio_formats:
                best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
                print(f"Seçilen format: {best_audio['format_id']} ({best_audio.get('abr', 'N/A')}kbps)")
            
            # İndir
            result = ydl.download([url])
            print(f"Download result: {result}")
            
            # Dosyayı bul
            for file in os.listdir(temp_dir):
                if file.endswith('.mp3') and info['title'][:20] in file:
                    dosya_adi = file
                    file_path = os.path.join(temp_dir, file)
                    
                    # Dosya boyutunu kontrol et
                    file_size = os.path.getsize(file_path)
                    print(f"Dosya boyutu: {file_size} bytes")
                    
                    if file_size < 1024:  # 1KB'den küçükse boş
                        raise Exception(f"Dosya boş! ({file_size} bytes)")
                    
                    return jsonify({'basarili': True, 'dosya': dosya_adi})
            
            raise Exception("Dosya bulunamadı")
            
    except Exception as e:
        error_msg = str(e)
        print(f"HATA DETAYI: {error_msg}")
        
        # Özel hata mesajları
        if "Dosya boş" in error_msg:
            error_msg = "YouTube boş dosya verdi! Farklı video deneyin."
        elif "Sign in" in error_msg:
            error_msg = "Bot engeli! 10 dakika bekleyin."
        elif "unavailable" in error_msg:
            error_msg = "Video bulunamadı."
        
        return jsonify({'basarili': False, 'hata': error_msg})

@app.route('/dosya/<dosya_adi>')
def dosya_getir(dosya_adi):
    temp_dir = tempfile.gettempdir()
    for dosya in os.listdir(temp_dir):
        if dosya.endswith('.mp3'):
            file_path = os.path.join(temp_dir, dosya)
            # Dosya boyutunu tekrar kontrol et
            if os.path.getsize(file_path) > 1024:
                return send_file(file_path, as_attachment=True)
    return 'Dosya bulunamadı veya boş', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
