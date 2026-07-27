from scripts.daily_telegram import camera, film


def test_letterbox_e_proporcao_de_cinema():
    # 1280 / 2.39 ≈ 535, com barras iguais em cima e embaixo
    assert film.ALTURA_UTIL == 534
    assert film.BARRA == (film.ALTURA - film.ALTURA_UTIL) // 2
    assert 2 * film.BARRA + film.ALTURA_UTIL == film.ALTURA


def test_grade_tem_as_camadas_do_look():
    filtro = film.grade_filter()
    for camada in ("curves", "eq=", "vignette", "noise", "crop", "pad"):
        assert camada in filtro


def test_grade_permite_ajustar_o_grao():
    assert "alls=2" in film.grade_filter(grao=2)
    assert "alls=12" in film.grade_filter(grao=12)


def test_fade_sai_antes_do_fim_do_plano():
    filtro = film.fade_filter(10.0, entrada=0.2, saida=0.2)
    assert "fade=t=in:st=0:d=0.20" in filtro
    assert "st=9.80" in filtro


def test_fade_em_plano_curtissimo_nao_fica_negativo():
    filtro = film.fade_filter(0.1, saida=0.5)
    assert "st=0.00" in filtro


def test_camera_alterna_movimento_entre_planos():
    movimentos = {camera.MOVIMENTOS[(i // 100 + i) % len(camera.MOVIMENTOS)] for i in range(6)}
    assert len(movimentos) == 6  # zoom sempre igual é o que vira slideshow


def test_camera_tem_push_pull_pan_tilt_e_diagonal():
    assert len(camera.MOVIMENTOS) == 6
    assert all(len(m) == 3 for m in camera.MOVIMENTOS)


def test_ambiencia_mistura_tres_camadas():
    # a cama sonora é sintetizada, sem trilha baixada e sem licença
    import inspect

    fonte = inspect.getsource(film.ambiencia)
    assert "anoisesrc" in fonte and "sine" in fonte
    assert "amix=inputs=3" in fonte


def test_mix_usa_ducking_e_normalizacao():
    import inspect

    fonte = inspect.getsource(film.mixar)
    assert "sidechaincompress" in fonte  # ambiente abaixa quando alguém fala
    assert "loudnorm" in fonte
