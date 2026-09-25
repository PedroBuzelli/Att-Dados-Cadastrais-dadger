#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aplica_mudancas_sombra.py

Aplica a um arquivo DADGER (DECOMP) o conjunto de mudancas cadastrais
identificadas na comparacao entre o deck atual e o deck "sombra"
(blocos 25 - MODIFICACAO DO CADASTRO, 32 - TAXA DE IRRIGACAO e
35 - RESTRICOES DE VOLUME ARMAZENADO/VAZAO DEFLUENTE).

O script SO mexe nos registros listados abaixo (por UHE/codigo de
restricao). Tudo o mais no arquivo - comentarios, outros registros,
ordem das linhas - fica exatamente como estava.

Uso:
    python aplica_mudancas_sombra.py [entrada.rv3] [saida.rv3]

Se nenhum argumento for informado, o script localiza automaticamente
o (unico) arquivo dentro da pasta "Arquivo Dadger", que fica ao lado
deste script. O nome desse arquivo pode variar a cada execucao
(dadger.rv3, dadger.rv4, etc.) - o script nao depende do nome.

Se a saida nao for informada, o arquivo de entrada NUNCA e alterado:
uma copia ja com as mudancas e gravada na pasta "Arquivo de Saída"
(criada automaticamente se nao existir), com o mesmo nome do arquivo
de entrada.

Este script pode ser executado direto pelo VS Code (botao "Run Python
File" ou F5), sem precisar digitar nada no terminal.
"""

import sys
from pathlib import Path

ENCODING = "latin-1"  # preserva acentuacao e nao mexe em bytes

# ---------------------------------------------------------------------------
# BLOCO 25 - MODIFICACAO DO CADASTRO (registros AC)
# ---------------------------------------------------------------------------
# chave: (codigo da UHE, mnemonico)  ->  novo valor (string, sem formatacao)
AC_PATCHES = {
    ("135", "VOLMAX"): "63.53",
    ("135", "VOLMIN"): "63.53",
    ("311", "VOLMIN"): "174.25",
    ("311", "VOLMAX"): "174.25",
    ("124", "VSVERT"): "204.95",
    ("117", "VSVERT"): "144.05",
    ("71",  "VSVERT"): "178.64",
    ("115", "VSVERT"): "25.75",
    ("1",   "VSVERT"): "107.60",
    ("156", "VSVERT"): "3881.13",
}

# registros AC que sao REMOVIDOS por completo no deck sombra
AC_REMOVALS = {
    ("34",  "VOLMIN"),   # override de volume minimo de Ilha Solteira (cota 323 m)
    ("124", "VMDESV"),   # descarga do reservatorio de Lajes p/ Fontes A-B
    ("73",  "VSVERT"),   # Jordao
}

# ---------------------------------------------------------------------------
# BLOCO 32 - TAXA DE IRRIGACAO (registros TI)
# ---------------------------------------------------------------------------
# chave: codigo da UHE -> (valor periodo 1, periodo 2, periodo 3)
TI_PATCHES = {
    "1": ("0.3", "0.3", "0.2"), "4": ("1.7", "1.7", "0.9"), "6": ("11.1", "11.1", "7.5"),
    "7": ("1.8", "1.8", "1.2"), "8": ("0.3", "0.3", "0.2"), "9": ("1.8", "1.8", "0.8"),
    "10": ("0.7", "0.7", "0.5"), "11": ("2.6", "2.6", "1.9"), "12": ("7.2", "7.2", "6.0"),
    "14": ("0.6", "0.6", "0.4"), "15": ("0.6", "0.6", "0.3"), "16": ("3.4", "3.4", "3.8"),
    "17": ("32.7", "32.7", "19.7"), "18": ("15.0", "15.0", "11.2"), "20": ("14.1", "14.1", "6.5"),
    "21": ("4.3", "4.3", "1.8"), "24": ("39.1", "39.1", "18.4"), "25": ("15.3", "15.3", "6.6"),
    "26": ("6.6", "6.6", "3.3"), "27": ("2.2", "2.2", "1.7"), "28": ("1.0", "1.0", "0.5"),
    "29": ("7.2", "7.2", "5.4"), "30": ("7.2", "7.2", "3.5"), "31": ("9.3", "9.3", "2.8"),
    "32": ("4.4", "4.4", "2.5"), "33": ("33.0", "33.0", "21.2"), "34": ("13.0", "13.0", "9.7"),
    "37": ("14.4", "14.4", "12.8"), "38": ("2.5", "2.5", "2.4"), "39": ("8.0", "8.0", "6.0"),
    "40": ("11.2", "11.2", "7.8"), "42": ("1.7", "1.7", "1.5"), "43": ("4.0", "4.0", "3.6"),
    "45": ("2.6", "2.6", "2.2"), "46": ("13.1", "13.1", "11.0"), "47": ("0.6", "0.6", "0.4"),
    "48": ("5.9", "5.9", "7.6"), "49": ("1.4", "1.4", "1.5"), "50": ("4.7", "4.7", "3.6"),
    "51": ("0.1", "0.1", "0.1"), "52": ("0.4", "0.4", "0.4"), "57": ("19.5", "19.5", "19.5"),
    "61": ("-15.1", "-15.1", "-15.1"), "62": ("1.6", "1.6", "1.6"), "63": ("4.2", "4.2", "4.1"),
    "66": ("21.3", "21.3", "21.6"), "71": ("6.7", "6.7", "6.7"), "74": ("3.3", "3.3", "3.4"),
    "78": ("0.2", "0.2", "0.2"), "82": ("0.9", "0.9", "0.9"), "83": ("0.5", "0.5", "0.5"),
    "86": ("0.1", "0.1", "0.1"), "88": ("0.4", "0.4", "0.4"), "89": ("0.2", "0.2", "0.2"),
    "91": ("0.2", "0.2", "0.2"), "92": ("1.5", "1.5", "1.5"), "93": ("0.7", "0.7", "0.7"),
    "97": ("18.1", "18.1", "18.1"), "98": ("2.0", "2.0", "2.0"), "99": ("10.2", "10.2", "10.2"),
    "103": ("75.3", "75.3", "75.3"), "107": ("13.1", "13.1", "12.7"), "110": ("0.1", "0.1", "0.1"),
    "111": ("0.3", "0.3", "0.4"), "113": ("0.0", "0.0", "0.1"), "114": ("0.1", "0.1", "0.2"),
    "115": ("0.0", "0.0", "0.0"), "117": ("10.4", "10.4", "10.4"), "118": ("5.6", "5.6", "5.6"),
    "120": ("8.7", "8.7", "8.6"), "121": ("0.4", "0.4", "0.4"), "123": ("3.4", "3.4", "3.8"),
    "124": ("4.2", "4.2", "4.2"), "125": ("1.2", "1.2", "1.2"), "127": ("1.5", "1.5", "1.5"),
    "130": ("-88.5", "-88.5", "-89.0"), "133": ("-0.1", "-0.1", "-0.1"), "134": ("4.7", "4.7", "4.5"),
    "135": ("-3.2", "-3.2", "-3.3"), "139": ("1.8", "1.8", "1.5"), "141": ("4.0", "4.0", "3.2"),
    "143": ("21.4", "21.4", "19.9"), "144": ("-10.5", "-10.5", "-12.5"), "145": ("0.3", "0.3", "0.1"),
    "146": ("1.3", "1.3", "1.3"), "148": ("1.3", "1.3", "0.8"), "154": ("7.1", "7.1", "5.2"),
    "155": ("12.2", "12.2", "11.4"), "156": ("10.2", "10.2", "8.0"), "162": ("8.2", "8.2", "3.7"),
    "169": ("228.1", "228.1", "153.1"), "172": ("103.1", "103.1", "108.5"), "173": ("3.0", "3.0", "3.4"),
    "174": ("0.0", "0.0", "0.0"), "178": ("0.5", "0.5", "0.6"), "181": ("0.1", "0.1", "0.1"),
    "182": ("0.1", "0.1", "0.1"), "185": ("1.7", "1.7", "1.2"), "189": ("18.6", "18.6", "16.9"),
    "190": ("4.2", "4.2", "2.7"), "192": ("3.0", "3.0", "2.7"), "193": ("-0.7", "-0.7", "-0.8"),
    "203": ("0.4", "0.4", "0.2"), "215": ("2.2", "2.2", "4.2"), "217": ("2.4", "2.4", "2.3"),
    "225": ("0.1", "0.1", "0.1"), "227": ("5.6", "5.6", "2.7"), "229": ("12.9", "12.9", "12.8"),
    "241": ("0.2", "0.2", "0.1"), "249": ("0.1", "0.1", "0.1"), "251": ("37.7", "37.7", "19.0"),
    "252": ("0.1", "0.1", "0.1"), "257": ("10.6", "10.6", "7.0"), "261": ("3.5", "3.5", "2.1"),
    "262": ("1.2", "1.2", "1.1"), "267": ("7.6", "7.6", "3.7"), "272": ("0.3", "0.3", "0.3"),
    "275": ("9.0", "9.0", "8.7"), "276": ("8.6", "8.6", "8.6"), "277": ("0.1", "0.1", "0.1"),
    "278": ("0.2", "0.2", "0.2"), "279": ("1.2", "1.2", "0.9"), "281": ("10.2", "10.2", "10.1"),
    "283": ("1.7", "1.7", "1.4"), "285": ("11.4", "11.4", "4.4"), "286": ("45.0", "45.0", "45.0"),
    "287": ("41.9", "41.9", "41.2"), "290": ("0.0", "0.0", "0.0"), "304": ("0.2", "0.2", "0.1"),
    "309": ("15.5", "15.5", "15.5"), "310": ("0.3", "0.3", "0.3"), "311": ("1.8", "1.8", "1.7"),
    "312": ("0.5", "0.5", "0.5"), "314": ("9.7", "9.7", "5.9"), "315": ("0.0", "0.0", "0.0"),
}

# ---------------------------------------------------------------------------
# BLOCO 35 - RESTRICOES DE VOLUME ARMAZENADO/VAZAO DEFLUENTE (HV/LV/CV)
# ---------------------------------------------------------------------------
# chave: (codigo da restricao, indice do registro LV) -> (valor1 ou '', valor2 ou '')
# string vazia = campo deve ficar em branco (sem limite naquele campo)
LV_PATCHES = {
    ("13", "1"):  ("756.13", ""),
    ("15", "1"):  ("1177.15", ""),
    ("17", "1"):  ("658.86", ""),
    ("19", "1"):  ("787.49", ""),
    ("42", "1"):  ("307.71", ""),
    ("50", "1"):  ("790.64", "4800.56"),
    ("65", "1"):  ("131.56", ""),
    ("66", "1"):  ("159.20", ""),
    ("67", "1"):  ("30.49", ""),
    ("71", "1"):  ("175.43", ""),
    ("73", "1"):  ("76.46", "382.92"),
    ("73", "2"):  ("76.46", "370.51"),
    ("75", "1"):  ("", "180.38"),
    ("83", "1"):  ("1100.21", ""),
    ("94", "1"):  ("", "185.44"),
    ("112", "1"): ("", "2422.81"),
    ("117", "1"): ("22.40", "22.40"),
}

# restricoes cujos registros HV/LV/CV sao removidos por completo no deck sombra
HV_LV_CV_REMOVALS = {"115", "116"}

# coeficientes CV da restricao 117 que sao alterados (mudam de sinal)
# chave: (codigo da restricao, referencia da UHE) -> novo coeficiente
CV_PATCHES = {
    ("117", "34"): "-1.0",
    ("117", "43"): "1.6663204",
}


# ---------------------------------------------------------------------------
# Funcoes de apoio (layout de colunas fixo do DADGER)
# ---------------------------------------------------------------------------

def _fmt(value, width):
    """Formata um valor a direita (ou em branco) numa largura fixa."""
    return value.rjust(width) if value != "" else " " * width


def patch_ac(line):
    """Registro AC: cod [4:7], mnemonico [9:15], valor [15:29] (14 col)."""
    if not line.startswith("AC"):
        return line, None
    code = line[4:7].strip()
    field = line[9:15].strip()
    key = (code, field)
    if key in AC_REMOVALS:
        return None, f"AC {code} {field}: removido"
    if key in AC_PATCHES:
        novo = AC_PATCHES[key]
        nova_linha = line[:15] + novo.rjust(14)
        return nova_linha, f"AC {code} {field}: -> {novo}"
    return line, None


def patch_ti(line):
    """Registro TI: cod [4:9], 3 valores de 5 colunas cada [9:24]."""
    if not line.startswith("TI") or line[2:4] != "  ":
        return line, None
    code = line[4:9].strip()
    if code in TI_PATCHES:
        v1, v2, v3 = TI_PATCHES[code]
        nova_linha = line[:9] + v1.rjust(5) + v2.rjust(5) + v3.rjust(5)
        return nova_linha, f"TI {code}: -> {v1}/{v2}/{v3}"
    return line, None


def patch_hv_lv_cv(line):
    """Registros HV/LV/CV do bloco 35."""
    mnem = line[0:2]
    if mnem not in ("HV", "LV", "CV"):
        return line, None
    code = line[4:7].strip()

    if code in HV_LV_CV_REMOVALS:
        return None, f"{mnem} {code}: removido"

    if mnem == "LV":
        idx = line[10:11].strip()
        key = (code, idx)
        if key in LV_PATCHES:
            v1, v2 = LV_PATCHES[key]
            # so escreve o 2o campo (colunas 24-33) se o registro original
            # ja o utilizava - registros de valor unico nao devem ganhar
            # espacos em branco extras no final da linha
            tinha_campo2 = len(line) > 24
            nova_linha = line[:11] + _fmt(v1, 13)
            if tinha_campo2:
                nova_linha += _fmt(v2, 10)
            return nova_linha, f"LV {code} idx{idx}: -> {v1 or '(vazio)'}/{v2 or '(vazio)'}"

    if mnem == "CV":
        ref = line[11:17].strip()
        key = (code, ref)
        if key in CV_PATCHES:
            novo = CV_PATCHES[key]
            nova_linha = line[:17] + novo.rjust(12) + line[29:]
            return nova_linha, f"CV {code} ref{ref}: -> {novo}"

    return line, None


PATCH_FUNCS = [patch_ac, patch_ti, patch_hv_lv_cv]


# ---------------------------------------------------------------------------
# Motor principal
# ---------------------------------------------------------------------------

def aplica_mudancas(caminho_entrada, caminho_saida):
    with open(caminho_entrada, "r", encoding=ENCODING, newline="") as f:
        linhas = f.readlines()

    aplicados = []
    saida = []

    for raw in linhas:
        # separa o conteudo do terminador de linha original (\r\n, \n, etc.)
        if raw.endswith("\r\n"):
            conteudo, fim = raw[:-2], "\r\n"
        elif raw.endswith("\n"):
            conteudo, fim = raw[:-1], "\n"
        else:
            conteudo, fim = raw, ""

        nova = conteudo
        removida = False
        for func in PATCH_FUNCS:
            resultado, log = func(nova)
            if log:
                aplicados.append(log)
            if resultado is None:
                removida = True
                break
            nova = resultado

        if not removida:
            saida.append(nova + fim)

    with open(caminho_saida, "w", encoding=ENCODING, newline="") as f:
        f.writelines(saida)

    return aplicados


def _checa_pendencias(aplicados):
    """Confere se todos os patches esperados foram encontrados no arquivo."""
    esperados = set()
    for (code, field) in list(AC_PATCHES.keys()) + list(AC_REMOVALS):
        esperados.add(f"AC {code} {field}")
    for code in TI_PATCHES:
        esperados.add(f"TI {code}")
    for (code, idx) in LV_PATCHES:
        esperados.add(f"LV {code} idx{idx}")
    for code in HV_LV_CV_REMOVALS:
        esperados.add(f"HV/LV/CV {code}")
    for (code, ref) in CV_PATCHES:
        esperados.add(f"CV {code} ref{ref}")

    encontrados = set()
    for log in aplicados:
        # normaliza o prefixo do log para comparar com "esperados"
        prefixo = log.split(":")[0].split(" -> ")[0].strip()
        encontrados.add(prefixo)

    faltando = []
    for e in esperados:
        achou = any(e in enc or enc in e for enc in encontrados)
        if not achou:
            faltando.append(e)
    return faltando


PASTA_DADGER = Path(__file__).resolve().parent / "Arquivo Dadger"


def _localiza_arquivo_dadger():
    """Encontra o arquivo DADGER dentro da pasta 'Arquivo Dadger'.

    O nome do arquivo pode mudar a cada execucao (ex.: dadger.rv3,
    dadger.rv4...), entao pegamos o unico arquivo presente na pasta,
    ignorando backups (.bak) e arquivos ocultos/temporarios.
    """
    if not PASTA_DADGER.is_dir():
        print(f"ERRO: pasta nao encontrada: {PASTA_DADGER}")
        sys.exit(1)

    candidatos = [
        p for p in PASTA_DADGER.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() != ".bak"
    ]

    if not candidatos:
        print(f"ERRO: nenhum arquivo encontrado em: {PASTA_DADGER}")
        sys.exit(1)
    if len(candidatos) > 1:
        print(f"ERRO: mais de um arquivo encontrado em {PASTA_DADGER}:")
        for c in candidatos:
            print(f"  - {c.name}")
        print("Deixe apenas o arquivo DADGER a ser processado nessa pasta.")
        sys.exit(1)

    return candidatos[0]


def main():
    if len(sys.argv) >= 2:
        entrada = Path(sys.argv[1])
    else:
        entrada = _localiza_arquivo_dadger()
        print(f"Arquivo detectado automaticamente: {entrada}")

    if len(sys.argv) >= 3:
        saida = Path(sys.argv[2])
    else:
        # nunca mexe no arquivo de entrada: grava uma copia, ja alterada,
        # na pasta "Arquivo de Saida" (criada se nao existir), com o
        # mesmo nome do arquivo de entrada
        pasta_saida = PASTA_DADGER.parent / "Arquivo de Saída"
        pasta_saida.mkdir(parents=True, exist_ok=True)
        saida = pasta_saida / entrada.name

    aplicados = aplica_mudancas(entrada, saida)

    print(f"\n{len(aplicados)} alteracoes aplicadas em {saida}:")
    for log in aplicados:
        print(f"  - {log}")

    faltando = _checa_pendencias(aplicados)
    if faltando:
        print(f"\nATENCAO: {len(faltando)} restricoes esperadas NAO foram "
              f"encontradas neste deck (podem ja estar diferentes, ausentes, "
              f"ou em outro formato). Confira manualmente:")
        for f in sorted(faltando):
            print(f"  - {f}")


if __name__ == "__main__":
    main()
