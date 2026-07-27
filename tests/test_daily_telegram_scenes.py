from scripts.daily_telegram import characters, hf_space
from scripts.daily_telegram.scenes import Scene, split_scenes

TEXTO = "\n".join(
    f"Gabo caminhou pelo distrito enquanto Valéria observava os sensores em silêncio. Bloco {i}. "
    "A chuva ácida escorria pelas placas de concreto rachado do setor industrial abandonado."
    for i in range(12)
)


def test_split_scenes_respects_count():
    cenas = split_scenes(TEXTO, 4)
    assert len(cenas) == 4
    assert [c.indice for c in cenas] == [1, 2, 3, 4]
    assert all(c.texto for c in cenas)


def test_split_scenes_never_exceeds_paragraphs():
    assert len(split_scenes("Um único parágrafo bem curto mas com mais de sessenta caracteres aqui.", 8)) == 1


def test_split_scenes_detects_characters():
    cenas = split_scenes(TEXTO, 2)
    nomes = {c["name"] for cena in cenas for c in cena.personagens}
    assert any("Gabo" in nome for nome in nomes)


def test_motion_prompt_varies_between_scenes():
    cenas = split_scenes(TEXTO, 4)
    assert len({c.motion_prompt for c in cenas}) == 4


def test_image_prompt_includes_style_and_setting():
    cena = Scene(indice=1, texto="Gabo encara o corpo na laje.")
    prompt = cena.image_prompt("O Relógio de Sangue", "Distrito 4")
    assert "Distrito 4" in prompt
    assert "cyberpunk" in prompt
    assert "O Relógio de Sangue" in prompt


def test_edit_prompt_locks_identity_and_wardrobe():
    gabo = characters.detect("Gabo acendeu a lanterna.")[0]
    prompt = Scene(indice=1, texto="ele corre pelo túnel").edit_prompt(gabo, "Subnível 3")
    assert "face, hair and beard unchanged" in prompt
    assert "signature outfit: Sobretudo bege" in prompt  # vestuário como cláusula própria
    assert "canonical look that must not change" in prompt
    assert "Subnível 3" in prompt


def test_shot_varies_across_scenes():
    cenas = split_scenes(TEXTO, 4)
    assert len({c.shot for c in cenas}) == 4  # sem isso toda cena vira o mesmo close-up


def test_action_prefers_narration_over_dialogue():
    cena = Scene(indice=1, texto="— Ameace com obstrução de justiça se for preciso, disse ele. "
                                 "A chuva ácida escorria pelo concreto rachado do distrito.")
    assert cena.action.startswith("A chuva ácida")


def test_action_falls_back_to_dialogue_when_only_option():
    cena = Scene(indice=1, texto="— Consiga um culpado antes do amanhecer, disse o inspetor.")
    assert cena.action


def test_compact_prompt_fits_clip_limit():
    gabo = characters.detect("Gabo acendeu a lanterna.")[0]
    cena = split_scenes(TEXTO, 4)[0]
    prompt = cena.compact_prompt(gabo, "Distrito 4")
    assert len(prompt.split()) < 60  # CLIP corta em 77 tokens
    assert cena.shot in prompt
    assert "Sobretudo bege" in prompt


def test_wardrobe_extracted_from_indented_markdown():
    gabo = characters.detect("Gabo acendeu a lanterna.")[0]
    assert characters.wardrobe(gabo).startswith("Sobretudo bege")


def test_character_db_has_reference_portraits():
    db = characters.get_db()
    com_ref = [c for c in db.characters.values() if characters.reference_image(c)]
    assert len(com_ref) >= 10


def test_pick_anchor_prefers_character_with_portrait():
    encontrados = characters.detect("Gabo e Valéria discutiam no beco.")
    assert encontrados
    ancora = characters.pick_anchor(encontrados)
    assert ancora is not None
    assert characters.reference_image(ancora).exists()


def test_mention_score_ignores_short_ambiguous_aliases():
    # "O Taxidermista" gera o alias "O", que casaria com todo artigo do texto
    char = {"name": "O Taxidermista", "aliases": ["O Taxidermista", "O"]}
    texto = "o corpo estava no beco e o inspetor observou o chão molhado"
    assert characters.mention_score(char, texto) == 0


def test_detect_drops_characters_without_real_mentions():
    nomes = [c["name"] for c in characters.detect("o carro parou e o rádio chiou na madrugada")]
    assert nomes == []


def test_detect_ranks_protagonist_first():
    texto = "Gabo revistou o beco. Gabo acendeu a lanterna. Gabo chamou Rangel uma vez."
    detectados = characters.detect(texto)
    assert detectados
    assert "Gabo" in detectados[0]["name"]


def test_describe_includes_visual_traits():
    gabo = characters.detect("Gabo acendeu a lanterna.")[0]
    assert characters.describe(gabo).startswith(gabo["name"])


def test_extract_path_digs_through_gradio_payload():
    payload = ({"video": "/tmp/out.mp4", "subtitles": None}, 42)
    assert hf_space._extract_path(payload) == "/tmp/out.mp4"
    assert hf_space._extract_path([{"path": "/tmp/img.jpg"}]) == "/tmp/img.jpg"
    assert hf_space._extract_path([{"path": None, "url": "http://x/y.png"}]) == "http://x/y.png"
