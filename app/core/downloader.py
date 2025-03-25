import yt_dlp
import os
from app.core.config import settings


def download_video(url: str, format: str, resolution: str = None) -> str:
    output_template = os.path.join(settings.DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'merge_output_format': format if format != "mp3" else None,
    }

    if format == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',  # Лучшее качество для видео
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format == "mp3":
                filename = filename.rsplit(".", 1)[0] + ".mp3"
            return filename
    except Exception as e:
        raise RuntimeError(f"Download failed: {str(e)}")
