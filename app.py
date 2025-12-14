from flask import Flask, request, jsonify, send_file, render_template_string
import yt_dlp
import tempfile
import os
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
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            margin: 0;
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
            box-sizing: border-box;
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
        .instructions {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            color: #666;
        }
        .step {
            margin: 10px 0;
            display: flex;
            align-items: center;
        }
        .step-number {
            background: #667eea;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Dans Okulu MP3 İndirici</h1>
        <p style="text-align:center;color:#666;margin-bottom:30px;">YouTube'dan müzikleri tek tıkla indirin</p>
        
        <input type="text" id="urlInput" placeholder="YouTube linkini buraya yapıştır...">
        <button id="downloadBtn" onclick="downloadMusic()">MP3 İNDİR</button>
        
        <div id="status" class="status"></div>
        
        <div class="instructions">
            <div class="step">
                <div class="step-number">1</div>
                <span>YouTube'dan istediğiniz müziğin linkini kopyalayın</span>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <span>Linki yukarıdaki kutuya yapıştırın</span>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <span>"MP3 İNDİR" butonuna tıkla</span>
            </div>
            <div class="step">
                <div class="step-number">4</div>
                <span>Müzik otomatik olarak indirilecek! 🎉</span>
            </div>
        </div>
        
        <div class="footer">
            <p>💃 İlknur Canberk Dans Okulu için özel olarak hazırlanmıştır ❤️</p>
        </div>
    </div>

    <script>
        async function downloadMusic() {
            const url = document.getElementById('urlInput').value.trim();
            const btn = document.getElementById('downloadBtn');
            const status = document.getElementById('status');
            
            // Kontrol
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
            showStatus('Müzik indiriliyor, lütfen bekleyin...', 'loading');
            
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
                    
                    // 3 saniye sonra mesajı kaldır
                    setTimeout(() => {
                        status.style.display = 'none';
                    }, 3000);
                    
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
        
        # YT-DLP AYARLARI (BASİT VE ÇALIŞIR)
        ydl_opts = {
            # Format 140 (m4a) - EN GARANTİLİ
            'format': '140',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            
            # Basit ayarlar
            'quiet': True,
            'no_warnings': True,
            
            # Post-processor: m4a -> mp3
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        # Müziği indir
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_title = info.get('title', 'muzik')
            
            # Güvenli dosya adı
            safe_title = re.sub(r'[^\w\s-]', '', video_title)
            safe_title = safe_title.strip()[:40]
            if not safe_title:
                safe_title = "muzik"
            filename = safe_title + ".mp3"
            
            # İndirilen dosyayı bul ve MP3'e çevrilmiş halini ara
            for file in os.listdir(temp_dir):
                if file.endswith('.mp3') and (video_title[:30] in file or safe_title[:20] in file):
                    actual_file = file
                    break
            else:
                # Eğer MP3 bulunamazsa, m4a dosyasını ara
                for file in os.listdir(temp_dir):
                    if file.endswith('.m4a') and video_title[:30] in file:
                        actual_file = file.replace('.m4a', '.mp3')
                        break
                else:
                    actual_file = filename
        
        return jsonify({
            'success': True,
            'filename': actual_file,
            'message': 'Müzik başarıyla indirildi!'
        })
        
    except Exception as e:
        error_msg = str(e)
        
        # Özel hata mesajları
        if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
            error_msg = "YouTube bot engeli! Lütfen 10 dakika bekleyip tekrar deneyin."
        elif "Private video" in error_msg:
            error_msg = "Bu video özel veya erişime kapalı."
        elif " unavailable" in error_msg:
            error_msg = "Video bulunamadı veya kaldırılmış."
        
        return jsonify({'success': False, 'error': error_msg})

@app.route('/file/<filename>')
def get_file(filename):
    temp_dir = tempfile.gettempdir()
    
    # Dosyayı bul
    for file in os.listdir(temp_dir):
        if file.endswith('.mp3') and (filename.replace('.mp3', '') in file or file.replace('.mp3', '') in filename):
            return send_file(
                os.path.join(temp_dir, file),
                as_attachment=True,
                download_name=filename,
                mimetype='audio/mpeg'
            )
    
    return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 404

# Render için gerekli
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
