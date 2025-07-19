import json

import duckdb
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

with duckdb.connect("hsc.duckdb") as conn:
    rows = (
        conn.table("ManuscriptDescription")
        .select("id, date_of_creation")
        .filter("date_of_creation is not null")
        .fetchall()
    )

conn = duckdb.connect("dates.duckdb")
conn.execute(
    "CREATE TABLE IF NOT EXISTS Dates (id INT, date_string TEXT, translation TEXT)"
)

prompt = ChatPromptTemplate(
    [
        (
            "system",
            "Determine the time periods discussed in this sentence. \
                ",
        ),
        ("human", "{user_input}"),
    ]
)
llm = OllamaLLM(model="mistral:7b")
chain = prompt | llm

with (
    Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ) as p,
):
    t0 = p.add_task("Manuscripts...", total=len(rows))
    for row in rows:
        id, date_list = row
        t1 = p.add_task("Running inference...", total=len(date_list))
        for date_string in date_list:
            result = chain.invoke(date_string)
            conn.execute(
                "INSERT INTO Dates VALUES (?, ?, ?)",
                parameters=[id, date_string, result],
            )
            p.advance(t1)
        p.remove_task(t1)
        p.advance(t0)

table = conn.table("Dates")
cols = table.columns
data = [{k: v for k, v in zip(cols, row)} for row in table.fetchall()]
with open("manuscript_description.json", mode="w") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
