import asyncio
import os
import subprocess
import edge_tts

OUT_DIR = r"c:\Users\jonas\Downloads\projeto de estudo\CENTRAL_RADIOS_PRO\vinhetas"
os.makedirs(OUT_DIR, exist_ok=True)

VINHETAS = [
    {
        "nome": "vinheta_ofertas.mp3",
        "voz": "pt-BR-AntonioNeural",
        "rate": "+15%",
        "pitch": "+3Hz",
        "texto": "Atenção clientes! Ofertas imperdíveis em todos os setores da loja! Aproveite nossos preços especiais antes que acabe. Boas compras!"
    },
    {
        "nome": "vinheta_radiopro_brasil.mp3",
        "voz": "pt-BR-AntonioNeural",
        "rate": "+12%",
        "pitch": "+2Hz",
        "texto": "Você está ouvindo RádioPro Brasil! O melhor som ambiente, música de qualidade e energia total para sua empresa!"
    },
    {
        "nome": "vinheta_boas_vindas.mp3",
        "voz": "pt-BR-ThalitaMultilingualNeural",
        "rate": "+10%",
        "pitch": "+2Hz",
        "texto": "Seja muito bem-vindo! Qualquer dúvida, procure nossa equipe de atendimento. Estamos prontos para te ajudar, boas compras!"
    }
]

async def gerar():
    for item in VINHETAS:
        caminho_raw = os.path.join(OUT_DIR, "raw_" + item["nome"])
        caminho_final = os.path.join(OUT_DIR, item["nome"])
        
        print(f"Gerando voz: {item['nome']}...")
        com = edge_tts.Communicate(
            text=item["texto"],
            voice=item["voz"],
            rate=item["rate"],
            pitch=item["pitch"]
        )
        await com.save(caminho_raw)
        
        # Cria um chime suave de rádio FM de 0.4s usando ffmpeg lavfi e junta com a voz
        cmd_chime = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "sine=frequency=784:duration=0.15,volume=0.3",
            "-f", "lavfi", "-i", "sine=frequency=1046:duration=0.25,volume=0.4",
            "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[chime]",
            "-map", "[chime]",
            os.path.join(OUT_DIR, "chime_temp.wav")
        ]
        subprocess.run(cmd_chime, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        chime_path = os.path.join(OUT_DIR, "chime_temp.wav")
        if os.path.exists(chime_path):
            # Concatena chime + voz com fade in/out
            cmd_concat = [
                "ffmpeg", "-y",
                "-i", chime_path,
                "-i", caminho_raw,
                "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[outa];[outa]volume=1.4[outv]",
                "-map", "[outv]",
                "-b:a", "192k",
                caminho_final
            ]
            subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try: os.remove(chime_path)
            except: pass
            try: os.remove(caminho_raw)
            except: pass
        else:
            os.rename(caminho_raw, caminho_final)
            
        print(f"✅ Vinheta pronta: {caminho_final}")

if __name__ == "__main__":
    asyncio.run(gerar())
