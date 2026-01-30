import asyncio
import edge_tts

async def test():
    texto = "Olá, esta é uma prova de voz com o Antonio."
    voice = "pt-BR-AntonioNeural"
    output = "test_voice.mp3"
    communicate = edge_tts.Communicate(texto, voice)
    await communicate.save(output)
    print("Sucesso!")

if __name__ == "__main__":
    asyncio.run(test())
