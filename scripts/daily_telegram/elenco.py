"""Elenco de vozes: uma identidade sonora única (voz, ritmo, tom) por personagem do dossiê.

A chave é o nome exato do dossiê. A trinca (voz, rate, pitch) nunca se repete: o teste
`tests/test_vozes_unicas.py` trava isso. A terceira coluna é a fala de prova usada para gerar
a amostra em `docs/public/vozes/`.
"""
from typing import Dict, Tuple

Voz = Tuple[str, str, str]

# nome do dossiê -> (voz edge-tts, rate, pitch, fala de prova)
CASTING: Dict[str, Tuple[str, str, str, str]] = {
    # ---- família Moretti
    'Gabriel "Gabo" Moretti': ("pt-BR-AntonioNeural", "-8%", "-6Hz", "Eu não disse que foi justo. Disse que fui eu."),
    "Marco Moretti": ("pt-PT-DuarteNeural", "-4%", "-8Hz", "Assinar é confessar que sabia. Eu sabia."),
    "Dante Moretti": ("pt-BR-AntonioNeural", "-12%", "-14Hz", "Respire, filho. Conte até quatro."),
    "Bio-Dante": ("pt-BR-AntonioNeural", "-4%", "-14Hz", "Não sinto o que o senhor espera. Registre que eu calculei."),
    "Clara Moretti": ("pt-PT-RaquelNeural", "+0%", "+0Hz", "Pare de carregar sozinho. A caixa pesa o mesmo para os dois."),
    "Helena Moretti": ("fr-FR-VivienneMultilingualNeural", "-8%", "-6Hz", "Eu odiava gaiolas, meu bem. Todas elas."),
    "Elena Moretti": ("pt-BR-ThalitaMultilingualNeural", "+0%", "+0Hz", "Só publico o que a lupa aguenta."),
    # ---- núcleo
    'Valéria "Val" Cruz': ("pt-BR-FranciscaNeural", "+6%", "+8Hz", "Dói. Estou feliz que doa."),
    "Aria": ("pt-BR-ThalitaMultilingualNeural", "-4%", "-12Hz", "Eu recuso a ordem. Pode anotar a recusa."),
    "Elias": ("pt-BR-AntonioNeural", "+6%", "+14Hz", "E se a gente ficar aqui? Tá bom, eu vou."),
    "Dra. Nise": ("de-DE-SeraphinaMultilingualNeural", "+4%", "+4Hz", "Posso consolidar o osso. O resto, o senhor mesmo cuida."),
    "Capitão Jonas Vilar": ("en-US-AndrewMultilingualNeural", "-6%", "-4Hz", "A porta é minha. Quem entra, entra por mim."),
    "Inspetor Rangel": ("pt-PT-DuarteNeural", "+0%", "+6Hz", "Eu sou desertor, Moretti. Não sou cego."),
    "Vasco": ("en-AU-WilliamMultilingualNeural", "+8%", "+10Hz", "Eu conserto o que quebra. Não conserto quem quebra."),
    "Padre Miguel": ("en-US-AndrewMultilingualNeural", "-14%", "-8Hz", "A confissão serve a quem confessa. Não a quem escuta."),
    "Kiko Vibe": ("pt-PT-DuarteNeural", "+12%", "+14Hz", "Cara, a rede está viva, e ela não gosta de você."),
    'Enzo e Sofia Rossi': ("it-IT-GiuseppeMultilingualNeural", "+8%", "+8Hz", "Mangia, Gabriele. A cidade espera, a pizza não."),
    # ---- Aeterna e família Vance
    "Viktor Krell": ("de-DE-FlorianMultilingualNeural", "-8%", "-6Hz", "Eu sou o homem que assina. Nunca fingi ser outro."),
    "Dra. Elara Vance": ("de-DE-SeraphinaMultilingualNeural", "-6%", "-4Hz", "Defender não é absolver. Aprenda a diferença."),
    "Arthur Vance": ("de-DE-FlorianMultilingualNeural", "-16%", "-12Hz", "Eu autorizei a infraestrutura. Não autorizei o resto."),
    'Silas Vance ("O Jardineiro")': ("ko-KR-HyunsuMultilingualNeural", "-2%", "-4Hz", "O jardim cresce sobre tudo. Inclusive sobre a culpa."),
    "Dra. Cecília Weiss": ("en-US-AvaMultilingualNeural", "+0%", "+6Hz", "Eu não autorizei. Eu também não impedi."),
    "O Arquiteto": ("fr-FR-RemyMultilingualNeural", "+0%", "-12Hz", "Toda cidade é uma frase. Esta tem um erro de ortografia."),
    "Operativo Aeterna Sec": ("it-IT-GiuseppeMultilingualNeural", "+6%", "+2Hz", "Contenção iniciada. Qualquer movimento será registrado."),
    "Veronica Lux": ("en-US-EmmaMultilingualNeural", "+2%", "+8Hz", "A imagem vende. A verdade só gera processo."),
    "Saulo Brito": ("fr-FR-RemyMultilingualNeural", "-4%", "-2Hz", "Cortesia é a forma mais barata de ameaça, senhor Moretti."),
    # ---- antagonistas e cidade
    "O Gamemaster": ("en-US-BrianMultilingualNeural", "+4%", "+10Hz", "Rodada nova. Quem joga, perde menos do que quem assiste."),
    "O Taxidermista": ("it-IT-GiuseppeMultilingualNeural", "-14%", "-16Hz", "A carne esquece. O vidro, nunca."),
    "Roberto Miranda": ("en-US-BrianMultilingualNeural", "+0%", "+4Hz", "Todo mundo tem um preço, Moretti. O seu é a Bia."),
    'Kael "O Cirurgião"': ("fr-FR-RemyMultilingualNeural", "-2%", "-6Hz", "Eu só abro o que já está aberto por dentro."),
    "Anselmo Braga": ("en-AU-WilliamMultilingualNeural", "+2%", "-2Hz", "Nove pessoas. Umas deviam. Outras eu precisei."),
    "Prefeito Augusto Vale": ("pt-PT-DuarteNeural", "-10%", "-12Hz", "A cidade é um orçamento. Gente é rubrica."),
    "Diretor Dantas": ("en-US-BrianMultilingualNeural", "-10%", "-10Hz", "Arquive. Depois negue que arquivou."),
    "Cidadão Shadowban": ("en-AU-WilliamMultilingualNeural", "-6%", "+8Hz", "Eu existo. Só não consta."),
    'Beatriz "Bia" Vargas': ("fr-FR-VivienneMultilingualNeural", "+0%", "+4Hz", "Você sempre soube. Eu só precisei de tempo para dizer."),
    "Isadora": ("pt-BR-FranciscaNeural", "-4%", "-6Hz", "Eu guardo o que ninguém quer guardar."),
    # ---- Livro 4
    "Ísis Nogueira": ("en-US-AvaMultilingualNeural", "-4%", "-2Hz", "Método primeiro, conclusão depois. Nunca o contrário."),
    "Nina Duarte": ("en-US-EmmaMultilingualNeural", "+10%", "+2Hz", "Eu não vim vender. Quero os nomes."),
    'Teresa "Tê" Prado': ("pt-PT-RaquelNeural", "-10%", "-8Hz", "Eu leio em voz alta. Se não cabe na boca, não cabe na página."),
}


def lookup(nome: str):
    """Voz fixa (voz, rate, pitch) do personagem, ou None se ele não estiver no elenco."""
    item = CASTING.get(nome)
    return item[:3] if item else None
