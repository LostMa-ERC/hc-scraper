import duckdb


class Database:
    def __init__(self, db_path: str):
        self.conn = duckdb.connect(db_path)

        # Create the Work table
        self.conn.execute(
            """
                    Create table if not exists Works (
                    id INT PRIMARY KEY,
                    title TEXT,
                    status VARCHAR,
                    "references" TEXT[]
                    )"""
        )

        # Create the relational Witness table
        self.conn.execute(
            """
                    Create table if not exists Witnesses (
                    work_id INT,
                    unit_id INT,
                    PRIMARY KEY (work_id, unit_id)
                    )"""
        )

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

    def work_is_present(self, id: int) -> bool:
        return self._is_present(table="Works", primary_key="id", pk=id)

    def witness_is_present(self, work_id: int, unit_id: int) -> bool:
        return self._is_present(
            table="Witnesses", primary_key="(work_id, unit_id)", pk=(work_id, unit_id)
        )

    def insert_work(self, data: dict):
        query = "insert into Works values ($id, $title, $status, $references)"
        self.conn.execute(query, parameters=data)

    def insert_witness(self, work_id: int, unit_id: int):
        query = "insert into Witnesses (work_id, unit_id) values (?, ?)"
        self.conn.execute(query, parameters=(work_id, unit_id))
