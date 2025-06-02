# Scrape metadata from the Handschriftencensus

## Install

```
pip install .
```

## Works

```
python src/main.py works
```

### `Works` table

```console
┌───────┬──────────────────────┬─────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  id   │        title         │   status    │                                                                   references                                                                   │
│ int32 │       varchar        │   varchar   │                                                                   varchar[]                                                                    │
├───────┼──────────────────────┼─────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  2448 │ 'A solis ortus car…  │ surviving   │ []                                                                                                                                             │
│  2449 │ 'Aachener Chronik'   │ surviving   │ [https://portal.dnb.de/opac.htm?query=nid%3D1267444606&method=simpleSearch&cqlMode=true, https://lobid.org/gnd/1267444606, https://www.germa…  │
│   729 │ 'ABC vom Altarssak…  │ surviving   │ []
```

### Relational `Witnesses` table
```console
┌─────────┬─────────┐
│ work_id │ unit_id │
│  int32  │  int32  │
├─────────┼─────────┤
│     729 │    3516 │
│     729 │    3517 │
```