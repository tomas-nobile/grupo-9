# TP1 · Features y estado

`/feature F03` implementa una feature completa; `/feature F03.2`, una story. `/next` dice qué sigue. `/check` verifica. `/entregar` arma el ZIP. Cuando una story está lista se marca `[x]` acá y en su archivo.

**Entrega:** viernes **2/10/2026**, ZIP `grupo-9_TP1.zip` por el campus + oral individual de 5 min. Repo: https://github.com/tomas-nobile/grupo-9

**MVP** (lo mínimo que cumple la consigna) = F01 + F02.1–2 + F03.1–2 + F04.1–2 + F05.1–3 + F06.1–2 + F08.1–2 + F07.

## Plan (desde el 25/9)

| Día | Stories |
|---|---|
| Sáb 26/9 | F01.1–3, F02.1–3 |
| Dom 27/9 | F03.1–3, F04.1–3 |
| Lun 28/9 | F05.1–4 |
| Mar 29/9 | F06.1–3, F08.1–3 |
| Mié 30/9 | F07.1–2 (README, guía completa, registro de prompts) |
| Jue 1/10 | F07.3 (ZIP, guion y ensayo del oral) · buffer |
| Vie 2/10 | Entrega y oral |

## Orden de corte (si vamos atrasados, cortar de arriba hacia abajo)

F08.3 → F06.3 → F05.4 → F04.3 → F03.3 → F02.4

**Nunca cortar:** el MVP ni la guía.

## Estado

| Feature | Prioridad | Stories |
|---|---|---|
| [F01 · Esqueleto, modelos y datos de ejemplo](../specs/F01-esqueleto.md) | P0 | [x] .1 · [x] .2 · [x] .3 |
| [F02 · Productos](../specs/F02-productos.md) | P0/P2 | [x] .1 · [x] .2 · [x] .3 · [x] .4 |
| [F03 · Movimientos de stock](../specs/F03-movimientos.md) | P0/P1 | [x] .1 · [x] .2 · [x] .3 |
| [F04 · Alertas de reabastecimiento](../specs/F04-alertas.md) | P0/P1 | [x] .1 · [x] .2 · [x] .3 |
| [F05 · Indicadores con pandas](../specs/F05-indicadores.md) | P0/P2 | [x] .1 · [x] .2 · [x] .3 · [x] .4 |
| [F06 · Gráfico y notebook](../specs/F06-grafico-notebook.md) | P0/P2 | [x] .1 · [x] .2 · [x] .3 |
| [F08 · Fuente externa: cotización del dólar](../specs/F08-cotizacion-dolar.md) | P0/P2 | [x] .1 · [ ] .2 · [ ] .3 |
| [F07 · Entrega y oral](../specs/F07-entrega.md) | P0 | [ ] .1 · [ ] .2 · [ ] .3 |

## Qué evalúan (100 pts) y dónde se cubre

| Criterio | Pts | Se cubre en |
|---|---|---|
| Funcionamiento | 20 | todo; `/check` verde |
| Explicación | 20 | `docs/guia.md`, código en capas, `docs/decisions.md`, guion del oral (F07.3) |
| Contenidos de Python | 15 | clases, funciones tipadas, módulos, try/except (F01–F04) |
| Datos | 10 | JSON + CSV (F01–F03), API externa con caché (F08) |
| Pandas y visualización | 15 | F05, F06 |
| Pruebas y corrección | 10 | `tests/`, casos inválidos demostrables (F02.2, F03.2) |
| Uso de IA | 5 | `docs/registro_prompts.md` (F07.2) |
| Comunicación | 5 | guion de 5 min (F07.3) |

## Requisitos de la consigna (checklist)

- [ ] Cargar, obtener o recuperar información (F01, F02.1)
- [ ] Validar datos y responder ante errores (F01.1, F02.2, F03.2)
- [ ] Consultar, buscar, filtrar o modificar registros (F02)
- [ ] Al menos tres indicadores útiles (F05.1–3)
- [ ] Guardar/recuperar con JSON o CSV (F01)
- [ ] Fuente de datos externa mediante API (F08)
- [ ] Al menos una visualización clara (F06.1)
- [ ] ≥ 4 funciones propias con type hints · try/except · ≥ 2 módulos · pandas · Matplotlib
- [ ] `main.py`, módulos de lógica, `analisis.ipynb`, `datos/`, `requirements.txt`, `README.md`
- [ ] Registro de ≥ 3 prompts con decisión y verificación
