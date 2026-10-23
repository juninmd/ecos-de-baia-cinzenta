"""Regressão: a referência de Aria deve continuar uma interface adulta."""

from scripts.art_gen import prompt_cena
from scripts.daily_telegram import characters
from scripts.daily_telegram.scenes import Scene


def test_aria_ancora_nao_recebe_corpo_ou_barba_do_prompt_generico():
    aria = characters.get_db().characters["Aria"]
    cena = Scene(3, "Aria responde pelo visor do terminal.", personagens=[aria])
    prompt = cena.edit_prompt(aria)
    assert "mature adult woman avatar" in prompt
    assert "translucent volumetric hologram" in prompt
    assert "beard unchanged" not in prompt
    assert "he must keep wearing" not in prompt
    assert cena.shot in prompt


def test_aria_no_elenco_recebe_limite_material_com_outra_ancora():
    db = characters.get_db().characters
    gabo, aria = db['Gabriel "Gabo" Moretti'], db["Aria"]
    cena = Scene(2, "Gabo consulta Aria no comunicador.", personagens=[gabo, aria])
    elenco = prompt_cena.montar_elenco(cena.personagens, 2)
    prompt = prompt_cena.texto_do_prompt(cena, "Teste", gabo, elenco, 2)
    assert "ARIA HOLOGRAM" in prompt
    assert "inactive physical drive" in prompt
    assert next(p for p in elenco if p["nome"] == "Aria")["referencia"].endswith("aria_2.png")
    assert "Never depict a child" in prompt


def test_cena_sem_aria_nao_recebe_avatar_nem_modulo_extra():
    gabo = characters.get_db().characters['Gabriel "Gabo" Moretti']
    cena = Scene(1, "Gabo espera sozinho.", personagens=[gabo])
    elenco = prompt_cena.montar_elenco(cena.personagens, 1)
    prompt = prompt_cena.texto_do_prompt(cena, "Teste", gabo, elenco, 1)
    assert "ARIA HOLOGRAM" not in prompt
    assert "computational drive" not in prompt


def test_mencao_posterior_a_destruicao_nao_autoriza_aparicao_ativa():
    aria = characters.get_db().characters["Aria"]
    cena = Scene(1, "Gabo lembra o silêncio de Aria.", personagens=[aria])
    elenco = prompt_cena.montar_elenco(cena.personagens, 168)
    prompt = prompt_cena.texto_do_prompt(cena, "Teste", None, elenco, 168)
    assert "do not add a live avatar" in prompt
