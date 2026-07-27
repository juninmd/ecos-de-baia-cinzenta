from scripts.daily_telegram import episode, screenplay, voices
from scripts.daily_telegram.screenplay import Beat

TRECHO = (
    "A chuva ácida escorria pelo concreto rachado do beco, e o cheiro de cobre subia do chão.\n"
    "— Você demorou, inspetor — disse o oficial de patrulha, um garoto que ainda tremia.\n"
    "— Cuidado onde pisa, soldado! — Gabo rosnou, empurrando o ombro do rapaz com desprezo.\n"
    "— D-desculpe, senhor.\n"
    "Gabo olhou para as janelas fechadas dos contêineres empilhados acima do beco escuro.\n"
)


def test_parse_separa_falas_de_narracao():
    beats = screenplay.parse(TRECHO)
    assert [b.tipo for b in beats][:2] == ["narracao", "fala"]
    assert any(b.is_fala for b in beats)
    assert any(not b.is_fala for b in beats)


def test_parse_resolve_falante_pela_deixa():
    beats = screenplay.parse(TRECHO)
    primeira = next(b for b in beats if b.is_fala)
    assert primeira.personagem is not None
    assert "ficial" in primeira.personagem["name"]


def test_parse_resolve_gabo_pela_deixa():
    beats = screenplay.parse(TRECHO)
    falas = [b for b in beats if b.is_fala]
    assert any(b.personagem and "Gabo" in b.personagem["name"] for b in falas)


def test_fala_sem_deixa_alterna_para_o_interlocutor():
    beats = screenplay.parse(TRECHO)
    falas = [b for b in beats if b.is_fala]
    # "— D-desculpe, senhor." não tem deixa: volta para quem falou antes do Gabo
    assert falas[-1].personagem is not None


def test_nenhuma_fala_fica_sem_falante():
    beats = screenplay.parse(TRECHO)
    assert all(b.personagem is not None for b in beats if b.is_fala)


def test_cobertura_do_texto_inclui_falas_curtas():
    beats = screenplay.parse(TRECHO)
    assert any("desculpe" in b.texto.lower() for b in beats)


def test_voz_e_estavel_por_personagem():
    char = {"name": "Inspetor Rangel", "description": "", "aliases": ["Rangel"]}
    assert voices.for_character(char) == voices.for_character(char)


def test_personagens_diferentes_recebem_vozes_diferentes():
    gabo = {"name": 'Gabriel "Gabo" Moretti', "description": "", "aliases": []}
    val = {"name": 'Valéria "Val" Cruz', "description": "", "aliases": []}
    assert voices.for_character(gabo)[0] != voices.for_character(val)[0]


def test_figurante_nao_recebe_a_voz_do_protagonista():
    gabo_voz = voices.ELENCO['Gabriel "Gabo" Moretti'][0]
    figurante = {"name": "Oficial de patrulha", "description": "", "aliases": []}
    assert voices.for_character(figurante)[0] != gabo_voz


def test_narrador_usa_a_voz_do_gabo():
    # o capítulo é narrado em primeira pessoa pelo Gabo
    assert voices.for_character(None)[0] == voices.ELENCO['Gabriel "Gabo" Moretti'][0]


def test_genero_vem_dos_pronomes_do_dossie():
    ela = {"name": "Krell", "description": "Ela usa uma jaqueta. Dela vem o silêncio.", "aliases": []}
    ele = {"name": "Krell", "description": "Ele usa uma jaqueta. Dele vem o silêncio.", "aliases": []}
    assert voices.for_character(ela)[0] in [v[0] for v in voices.POOL_FEMININO]
    assert voices.for_character(ele)[0] in [v[0] for v in voices.POOL_MASCULINO]


def test_plano_de_fala_ancora_no_falante():
    falante = {"name": 'Gabriel "Gabo" Moretti', "description": "", "aliases": []}
    cena = episode.beat_scene(Beat(1, "fala", "Cuidado onde pisa", falante), 0)
    assert cena.personagens == [falante]
    assert cena.shot in episode.SHOTS_DIALOGO


def test_planos_de_dialogo_alternam_enquadramento():
    falante = {"name": "X", "description": "", "aliases": []}
    a = episode.beat_scene(Beat(1, "fala", "oi", falante), 0)
    b = episode.beat_scene(Beat(2, "fala", "oi", falante), 1)
    assert a.shot != b.shot


def test_fala_curta_usa_um_plano_so():
    assert episode.planos_do_beat(4.0) == 1
    assert episode.planos_do_beat(episode.SEGUNDOS_POR_PLANO) == 1


def test_fala_longa_vira_varios_planos():
    # 30 segundos numa imagem só vira slideshow
    assert episode.planos_do_beat(30.0) == 3
    assert episode.planos_do_beat(12.0) == 2


def test_planos_do_beat_nunca_zera():
    assert episode.planos_do_beat(0.4) == 1


def test_episode_args_defaults():
    args = episode.parse_args([])
    assert args.chapter == 1
    assert args.local is False
