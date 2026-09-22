# Att Dados Cadastrais DADGER

Script que aplica, a um arquivo DADGER (DECOMP), o conjunto de mudanças
cadastrais identificadas na comparação entre o deck atual e o deck
"sombra" (blocos 25 - Modificação do Cadastro, 32 - Taxa de Irrigação e
35 - Restrições de Volume Armazenado/Vazão Defluente).

O script só altera os registros previstos no código (por UHE/código de
restrição). Todo o resto do arquivo — comentários, outros registros,
ordem das linhas — permanece exatamente como estava. O arquivo de
entrada **nunca é modificado**: o resultado é gravado em uma cópia.

## Estrutura de pastas necessária

Este repositório contém apenas o algoritmo. Para executá-lo, crie ao
lado do script a seguinte estrutura de pastas (não versionadas neste
repositório):

```
.
├── aplica_mudancas_sombra.py
├── requirements.txt
├── Arquivo Dadger/          # coloque aqui o arquivo DADGER de entrada
│   └── dadger.rv3           # (o nome do arquivo pode variar)
└── Arquivo de Saída/        # criada automaticamente pelo script
    └── dadger.rv3           # copia do arquivo de entrada, ja com as mudancas
```

- **Arquivo Dadger/**: pasta onde deve ficar o único arquivo DADGER a
  ser processado. O nome do arquivo pode variar a cada execução
  (`dadger.rv3`, `dadger.rv4`, etc.) — o script localiza o arquivo
  automaticamente, desde que seja o único presente na pasta.
- **Arquivo de Saída/**: criada automaticamente pelo script, caso não
  exista. Recebe uma cópia do arquivo de entrada já com as mudanças
  aplicadas, mantendo o mesmo nome do arquivo original.

## Instalação

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

O script usa apenas bibliotecas padrão do Python — o `requirements.txt`
está preparado para eventuais dependências futuras.

## Uso

```bash
python aplica_mudancas_sombra.py
```

Sem argumentos, o script localiza sozinho o arquivo dentro de
`Arquivo Dadger/` e grava o resultado em `Arquivo de Saída/`.

Também é possível informar entrada e saída manualmente:

```bash
python aplica_mudancas_sombra.py entrada.rv3 saida.rv3
```

### Rodando pelo VS Code

Basta configurar o interpretador do workspace para a venv criada e
executar o script com F5 / "Run Python File", sem precisar digitar
comandos no terminal.
