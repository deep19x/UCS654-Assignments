#!/usr/bin/env python3
"""
YouTube Mashup Creator - Roll Number: 102303673
Downloads N videos of a singer, converts to audio, cuts segments, and merges them.
Usage: python 102303673.py "Singer Name" N Y OutputFileName.mp3
Example: python 102303673.py "Sharry Maan" 20 20 102303673-output.mp3
"""

import sys
import os
import re
import shutil
from pathlib import Path

try:
    import yt_dlp
    from pydub import AudioSegment
except ImportError:
    print("Error: Required packages not found.")
    print("Install them using: pip install yt-dlp pydub")
    sys.exit(1)


def validate_inputs(args):
    """Validate command-line arguments."""
    if len(args) != 5:
        print("Error: Incorrect number of parameters.")
        print("Usage: python 102303673.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        print("Example: python 102303673.py \"Sharry Maan\" 20 20 102303673-output.mp3")
        return False
    
    singer_name = args[1]
    try:
        num_videos = int(args[2])
        duration = int(args[3])
    except ValueError:
        print("Error: NumberOfVideos and AudioDuration must be positive integers.")
        return False
    
    if num_videos <= 10:
        print(f"Error: NumberOfVideos must be greater than 10. Got: {num_videos}")
        return False
    
    if duration <= 20:
        print(f"Error: AudioDuration must be greater than 20 seconds. Got: {duration}")
        return False
    
    output_file = args[4]
    if not output_file.lower().endswith(('.mp3', '.wav', '.m4a')):
        print("Error: Output file must be an audio format (.mp3, .wav, .m4a)")
        return False
    
    if not singer_name or len(singer_name.strip()) == 0:
        print("Error: Singer name cannot be empty.")
        return False
    
    return True


def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def download_videos(singer_name, num_videos):
    """Download N videos of singer from YouTube."""
    temp_dir = "temp_videos"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"\n[1/4] Downloading {num_videos} videos of '{singer_name}'...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'max_downloads': num_videos,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"{singer_name} audio"
            print(f"Searching for: {search_query}")
            info = ydl.extract_info(f"ytsearch{num_videos}:{search_query}", download=True)
            
            if 'entries' in info:
                videos = info['entries']
                print(f"✓ Successfully downloaded {len(videos)} videos")
                return temp_dir, videos
            else:
                print("Error: No videos found.")
                return None, None
    except Exception as e:
        print(f"Error downloading videos: {str(e)}")
        return None, None


def convert_to_audio(video_dir):
    """Convert all downloaded videos to audio."""
    print(f"\n[2/4] Converting videos to audio...")
    
    audio_dir = "temp_audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    video_files = []
    for file in os.listdir(video_dir):
        if file.endswith(('.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv')):
            video_files.append(file)
    
    if not video_files:
        print("Error: No video files found to convert.")
        return None
    
    converted_count = 0
    for i, video_file in enumerate(video_files, 1):
        try:
            video_path = os.path.join(video_dir, video_file)
            audio_path = os.path.join(audio_dir, f"audio_{i}.mp3")
            
            # Load video and extract audio
            audio = AudioSegment.from_file(video_path)
            audio.export(audio_path, format="mp3")
            converted_count += 1
            print(f"  ✓ Converted: {video_file}")
        except Exception as e:
            print(f"  ✗ Error converting {video_file}: {str(e)}")
            continue
    
    if converted_count == 0:
        print("Error: No videos were successfully converted.")
        return None
    
    print(f"✓ Successfully converted {converted_count} videos to audio")
    return audio_dir


def cut_audio_segments(audio_dir, duration):
    """Cut first Y seconds from all audio files."""
    print(f"\n[3/4] Cutting first {duration} seconds from each audio...")
    
    cut_dir = "temp_cut"
    os.makedirs(cut_dir, exist_ok=True)
    
    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])
    cut_count = 0
    
    for i, audio_file in enumerate(audio_files, 1):
        try:
            audio_path = os.path.join(audio_dir, audio_file)
            cut_path = os.path.join(cut_dir, f"cut_{i}.mp3")
            
            # Load and cut audio
            audio = AudioSegment.from_mp3(audio_path)
            cut_audio = audio[:duration * 1000]  # Convert seconds to milliseconds
            cut_audio.export(cut_path, format="mp3")
            cut_count += 1
            print(f"  ✓ Cut segment {i} ({duration}s)")
        except Exception as e:
            print(f"  ✗ Error cutting {audio_file}: {str(e)}")
            continue
    
    if cut_count == 0:
        print("Error: No audio segments were successfully cut.")
        return None
    
    print(f"✓ Successfully cut {cut_count} audio segments")
    return cut_dir


def merge_audio_files(cut_dir, output_file):
    """Merge all cut audio files into a single file."""
    print(f"\n[4/4] Merging all audio segments...")
    
    cut_files = sorted([f for f in os.listdir(cut_dir) if f.endswith('.mp3')])
    
    if not cut_files:
        print("Error: No audio segments found to merge.")
        return False
    
    try:
        combined = AudioSegment.empty()
        
        for i, cut_file in enumerate(cut_files, 1):
            cut_path = os.path.join(cut_dir, cut_file)
            audio = AudioSegment.from_mp3(cut_path)
            combined += audio
            print(f"  ✓ Added segment {i} ({len(audio)/1000:.1f}s)")
        
        # Export merged file
        combined.export(output_file, format="mp3")
        total_duration = len(combined) / 1000
        print(f"✓ Successfully merged all segments into '{output_file}'")
        print(f"  Total duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        return True
    except Exception as e:
        print(f"Error merging audio files: {str(e)}")
        return False


def cleanup(temp_dir, audio_dir, cut_dir):
    """Clean up temporary directories."""
    for directory in [temp_dir, audio_dir, cut_dir]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    print("\n✓ Temporary files cleaned up")


def main():
    """Main function."""
    print("=" * 60)
    print("YouTube Mashup Creator - Roll: 102303673")
    print("=" * 60)
    
    # Validate inputs
    if not validate_inputs(sys.argv):
        sys.exit(1)
    
    singer_name = sys.argv[1]
    num_videos = int(sys.argv[2])
    duration = int(sys.argv[3])
    output_file = sys.argv[4]
    
    # Check for ffmpeg
    if shutil.which('ffmpeg') is None:
        print("Error: ffmpeg is not installed. Install it using:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)
    
    try:
        # Download videos
        video_dir, videos = download_videos(singer_name, num_videos)
        if not video_dir:
            sys.exit(1)
        
        # Convert to audio
        audio_dir = convert_to_audio(video_dir)
        if not audio_dir:
            sys.exit(1)
        
        # Cut segments
        cut_dir = cut_audio_segments(audio_dir, duration)
        if not cut_dir:
            sys.exit(1)
        
        # Merge audio
        if not merge_audio_files(cut_dir, output_file):
            sys.exit(1)
        
        # Cleanup
        cleanup(video_dir, audio_dir, cut_dir)
        
        print("\n" + "=" * 60)
        print(f"✓ Mashup creation successful!")
        print(f"Output file: {output_file}")
        print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n\nError: Process interrupted by user.")
        cleanup("temp_videos", "temp_audio", "temp_cut")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        cleanup("temp_videos", "temp_audio", "temp_cut")
        sys.exit(1)


if __name__ == "__main__":
    main()
