"""Fila de cenas: descoberta de capítulos, continuidade visual e montagem do prompt."""

from scripts.art_gen import continuidade, prompt_cena, vestuario
from scripts.art_gen.chapters import get_chapter_files, ler_capitulo
from scripts.build_scene_manifest import CENAS_POR_CAPITULO, cenas_faltantes
from scripts.daily_telegram import characters
from scripts.daily_telegram.scenes import Scene, split_scenes

GABO = 'Gabriel "Gabo" Moretti'


def test_capitulos_sao_encontrados_sem_caminho_absoluto():
    capitulos = get_chapter_files()
    assert len(capitulos) > 200
    assert all(cap["file_path"].exists() for cap in capitulos)


def test_capitulo_intercalado_vira_pasta_com_sublinhado():
    pastas = {cap["num_str"]: cap["folder_name"] for cap in get_chapter_files()}
    assert pastas.get("30.5") == "capitulo_30_5"


def test_titulo_sai_do_h1_quando_nao_ha_frontmatter():
    titulo, corpo = ler_capitulo(get_chapter_files()[0])
    assert titulo.startswith("Capítulo 1")
    assert "# " not in corpo


def test_alvo_da_obra_e_dez_cenas():
    assert CENAS_POR_CAPITULO == 10
    assert len({Scene(i, "x").shot for i in range(1, CENAS_POR_CAPITULO + 1)}) == 10


def test_cena_ja_gerada_sai_da_fila_e_reprovada_volta():
    cap = next(c for c in get_chapter_files() if c["num_str"] == "1")
    assert 1 not in cenas_faltantes(cap, set(), CENAS_POR_CAPITULO)
    reprovada = {"docs/public/cenas/capitulo_1/cena_1.jpg"}
    assert 1 in cenas_faltantes(cap, reprovada, CENAS_POR_CAPITULO)


def test_continuidade_acompanha_a_fase_fisica_do_capitulo():
    assert "fraturas" in continuidade.fase(GABO, 60)
    assert "exoesqueleto" in continuidade.fase(GABO, 106).lower()
    assert "amputado" in continuidade.fase(GABO, 200).lower()


def test_continuidade_nao_deixa_buraco_entre_marcos():
    # 177-184 fica entre "Capítulos 175-176" e "Capítulos 185-217": sem preenchimento,
    # o Gabo voltava a ter os dois braços justamente no arco em que perdeu um.
    assert "prótese" in continuidade.fase(GABO, 180).lower()


def test_clausula_de_continuidade_entra_no_prompt():
    elenco = [{"nome": GABO, "vestuario": "sobretudo bege"}]
    assert "MANDATORY CONTINUITY" in continuidade.clausula(elenco, 200)
    assert continuidade.clausula([{"nome": "Ninguém", "vestuario": ""}], 200) == ""


def test_vestuario_completo_nao_para_no_primeiro_ponto():
    dante = characters.get_db().characters["Dante Moretti"]
    assert "Fase atual" in characters.wardrobe(dante)


def test_vestuario_escolhe_a_fase_pelo_capitulo():
    dante = characters.get_db().characters["Dante Moretti"]
    roupa = characters.wardrobe(dante)
    assert "fedora" in vestuario.na_fase("Dante Moretti", roupa, 26)
    assert "macacão" in vestuario.na_fase("Dante Moretti", roupa, 104)
    assert vestuario.na_fase("Sem Ficha", "sobretudo bege", 10) == "sobretudo bege"


def test_seed_e_deterministica_e_nao_colide_com_intercalado():
    assert prompt_cena.seed_da_cena("30", 5) == 3005
    assert prompt_cena.seed_da_cena("30.5", 5) == 3055
    assert prompt_cena.seed_da_cena("31", 5) == 3105


def test_prompt_carrega_as_travas_de_fidelidade():
    cap = next(c for c in get_chapter_files() if c["num_str"] == "200")
    titulo, corpo = ler_capitulo(cap)
    cena = split_scenes(corpo, CENAS_POR_CAPITULO)[4]
    cena.indice = 5
    entrada = prompt_cena.montar_entrada(
        cap, titulo, cena, prompt_cena.montar_elenco(cena.personagens, 200.0)
    )
    assert entrada["seed"] == 20005
    assert entrada["saida"].endswith("capitulo_200/cena_5.jpg")
    for trava in (prompt_cena.SEM_TEXTO, prompt_cena.ESTILO, prompt_cena.NEGATIVO):
        assert trava in entrada["prompt"]


def test_texto_do_capitulo_entra_sem_marcacao():
    cena = Scene(1, "A placa dizia **BRAGA, A.** e o _resto_ tinha sumido na chuva ácida.")
    assert "*" not in cena.texto_limpo and "_" not in cena.texto_limpo
