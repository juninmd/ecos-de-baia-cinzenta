from pathlib import Path

def generate_narration(texto: str, output_path: Path) -> float:
    """
    Generate TTS narration using gTTS (stable choice).
    
    Args:
        texto: Text to narrate
        output_path: Output audio file path
        
    Returns:
        Duration in seconds
    """
    from gtts import gTTS
    from pydub import AudioSegment
    
    # Limit text to avoid extremely long videos
    max_chars = 3000
    if len(texto) > max_chars:
        print(f"⚠ Text truncated from {len(texto)} to {max_chars} chars")
        texto = texto[:max_chars] + "..."
    
    print(f"🎙 Generating narration (Normal PT-BR)...")
    
    # Using pt-BR for better flow. No pitch shifting to avoid 'ET' effect.
    tts = gTTS(text=texto, lang='pt', tld='com.br', slow=False)
    tts.save(str(output_path))
    
    # Get audio duration
    audio = AudioSegment.from_file(str(output_path))
    duration = len(audio) / 1000.0  # Convert to seconds
    
    print(f"✓ Narration created: {duration:.1f}s")
    return duration
