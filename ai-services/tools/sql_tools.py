from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = "postgresql://postgres:password@localhost/finsphere"

engine = create_engine(DATABASE_URL)


def run_sql_query(query: str):

    try:
        df = pd.read_sql(query, engine)

        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}