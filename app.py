from flask import Flask, request, jsonify, send_file, render_template_string
from pytube import YouTube
import tempfile
import os
import re
from moviepy.editor import AudioFileClip

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
        <input id="url" placeholder="YouTube linkini yapıştır..." value="https://www.youtube.com/watch?v=5qap5aO4i9A">
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
            status.innerHTML = '⏳ İndiriliyor... (1 dakika sürebilir)';
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
                status.innerHTML = '❌ Sunucu hatası';
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
        youtube_url = data['url']
        
        print(f"pytube ile indirme: {youtube_url}")
        
        # 1. YouTube objesi oluştur
        yt = YouTube(youtube_url)
        print(f"Video başlığı: {yt.title}")
        
        # 2. Sadece audio stream'i al
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            return jsonify({'basarili': False, 'hata': 'Ses bulunamadı'})
        
        print(f"Audio stream bulundu: {audio_stream}")
        
        # 3. Geçici dosya için
        temp_dir = tempfile.gettempdir()
        
        # 4. İndir (m4a veya webm formatında)
        original_file = audio_stream.download(output_path=temp_dir)
        print(f"İndirildi: {original_file}")
        
        # 5. MP3'e çevir
        base_name = os.path.splitext(os.path.basename(original_file))[0]
        safe_name = re.sub(r'[^\w\s-]', '', base_name)[:40]
        mp3_file = os.path.join(temp_dir, safe_name + '.mp3')
        
        # MoviePy ile audio'yu MP3'e çevir
        audio_clip = AudioFileClip(original_file)
        audio_clip.write_audiofile(mp3_file, verbose=False, logger=None)
        audio_clip.close()
        
        # Orijinal dosyayı sil
        os.remove(original_file)
        
        # Dosya boyutunu kontrol et
        if os.path.getsize(mp3_file) < 10240:  # 10KB'den küçükse
            os.remove(mp3_file)
            return jsonify({'basarili': False, 'hata': 'Dosya boş geldi'})
        
        return jsonify({'basarili': True, 'dosya': safe_name + '.mp3'})
        
    except Exception as e:
        error_msg = str(e)
        print(f"HATA: {error_msg}")
        
        # Özel hata mesajı
        if "age restricted" in error_msg.lower():
            return jsonify({'basarili': False, 'hata': 'Yaş kısıtlamalı video'})
        elif "private" in error_msg.lower():
            return jsonify({'basarili': False, 'hata': 'Özel video'})
        elif "unavailable" in error_msg.lower():
            return jsonify({'basarili': False, 'hata': 'Video bulunamadı'})
        elif "regex" in error_msg.lower():
            return jsonify({'basarili': False, 'hata': 'Geçersiz YouTube linki'})
        else:
            return jsonify({'basarili': False, 'hata': 'İndirme hatası'})

@app.route('/dosya/<dosya_adi>')
def dosya_getir(dosya_adi):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, dosya_adi)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return 'Dosya bulunamadı', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
