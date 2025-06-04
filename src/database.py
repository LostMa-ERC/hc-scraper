import duckdb


class Database:
    def __init__(self, db_path: str):
        self.conn = duckdb.connect(db_path)

        # Create the CreativeWork table
        self.execute(
            """
                    CREATE TABLE IF NOT EXISTS CreativeWork (
                    id INT PRIMARY KEY,
                    title TEXT,
                    status VARCHAR,
                    "references" TEXT[]
                    )"""
        )

        # Create ManuscriptDescription table
        self.execute(
            """
                    CREATE TABLE IF NOT EXISTS ManuscriptDescription (
                    id INT PRIMARY KEY,
                    scraped BOOL DEFAULT False,
                    writing_material VARCHAR,
                    folio_dimensions VARCHAR[],
                    written_area VARCHAR[],
                    number_of_columns VARCHAR[],
                    number_of_lines VARCHAR[],
                    stanza_layout VARCHAR[],
                    verse_layout VARCHAR[],
                    special_features TEXT[],
                    date_of_creation TEXT,
                    scribal_dialect TEXT[],
                    scriptorium_location TEXT[]
                    )"""
        )

        # Create the relational Witness table
        self.execute(
            """
                    CREATE TABLE IF NOT EXISTS Witness (
                    work_id INT,
                    ms_id INT,
                    status VARCHAR,
                    siglum VARCHAR,
                    PRIMARY KEY (work_id, ms_id)
                    )"""
        )

        # Create the LibraryItems table
        self.execute(
            """
                    CREATE TABLE IF NOT EXISTS LibraryItem (
                    id VARCHAR PRIMARY KEY,
                    ms_id INT,
                    shelfmark VARCHAR,
                    type VARCHAR,
                    city VARCHAR,
                    institution VARCHAR,
                    numbering TEXT
                    )"""
        )

    def execute(self, query: str, parameters=()) -> None:
        try:
            self.conn.execute(query, parameters=parameters)
        except Exception as e:
            print(query)
            raise e

    def _is_present(self, table: str, primary_key: str, pk: int | tuple) -> bool:
        query = f"select count(*) from {table} where {primary_key} = ?"
        # If the primary key is composite, join the string representation of its parts
        if isinstance(pk, tuple):
            pk = f"({', '.join([str(i) for i in pk])})"
        # Put the primary key in a list
        params = [pk]
        # Count the number of rows that were found in the table with that primary key
        rows = self.conn.sql(query, params=params).fetchone()[0]
        # If 1 row was found, the record is present
        if rows == 1:
            return True
        # If 0 rows were foound, the record is not present
        elif rows == 0:
            return False
        # If > 1 row was found, the table was built with a bad primary key constraint
        else:
            raise ValueError(
                f"Primary key not respected. \
{rows} rows with same value in '{primary_key}'."
            )

    def count_all_manuscripts(self) -> int:
        return self.conn.sql("SELECT COUNT(*) FROM ManuscriptDescription").fetchone()[0]

    def count_completed_manuscripts(self) -> int:
        # Complete = description was scraped
        return self.conn.sql(
            """SELECT COUNT(*)
                FROM ManuscriptDescription
                WHERE scraped"""
        ).fetchone()[0]

    def get_manuscripts_and_works(self) -> list[tuple]:
        # Complete = description was scraped
        sql = """
        SELECT
            m.id AS ms,
            list(w.work_id) AS works
        FROM ManuscriptDescription m
        LEFT JOIN Witness w ON m.id = w.ms_id
        WHERE NOT scraped
        GROUP BY m.id
        """
        return self.conn.sql(sql).fetchall()

    def work_is_present(self, id: int) -> bool:
        return self._is_present(table="CreativeWork", primary_key="id", pk=id)

    def LibraryItem_is_present(self, id: int) -> bool:
        return self._is_present(table="LibraryItem", primary_key="id", pk=id)

    def witness_is_present(self, work_id: int, ms_id: int) -> bool:
        return self._is_present(
            table="Witness", primary_key="(work_id, ms_id)", pk=(work_id, ms_id)
        )

    def manuscript_description_is_present(self, id: int) -> bool:
        return self._is_present(table="ManuscriptDescription", primary_key="id", pk=id)

    def create_work(self, data: dict):
        query = "insert into CreativeWork values ($id, $title, $status, $references)"
        self.execute(query, parameters=data)

    def create_dummy_manuscript_description(self, id: int):
        query = "insert into ManuscriptDescription (id) values (?)"
        self.execute(query, parameters=[id])

    def create_witness(self, data: dict):
        data = {k: v for k, v in data.items() if v}
        if not self.manuscript_description_is_present(id=data["ms_id"]):
            self.create_dummy_manuscript_description(id=data["ms_id"])
        cols = ", ".join(data.keys())
        params = list(data.values())
        placeholders = ", ".join(["?" for _ in params])
        query = f"insert into Witness ({cols}) values ({placeholders})"
        self.execute(query, parameters=params)

    def update_manuscript_description(self, data: dict):
        data = {k: v for k, v in data.items() if v}
        id = data.pop("id")
        data.update({"scraped": True})
        cols = ", ".join([f"{k} = ${k}" for k in data.keys()])
        query = f"update ManuscriptDescription set {cols} where id = {id}"
        self.execute(query, parameters=data)

    def create_document(self, data: dict):
        cols = ", ".join(data.keys())
        params = list(data.values())
        placeholders = ", ".join(["?" for _ in params])
        query = f"insert into LibraryItem ({cols}) values ({placeholders}) on conflict do nothing"
        self.execute(query, parameters=params)
