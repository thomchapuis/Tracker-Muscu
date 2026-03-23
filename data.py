import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def get_client():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"],
    )

def load_data() -> pd.DataFrame:
    client = get_client()
    response = client.table("workouts").select("*").order("date").execute()
    if not response.data:
        return pd.DataFrame(columns=[
            "id", "date", "exercice", "groupe",
            "series", "reps", "poids_kg", "notes"
        ])
    df = pd.DataFrame(response.data)
    df["date"] = pd.to_datetime(df["date"])
    df["poids_kg"] = pd.to_numeric(df["poids_kg"], errors="coerce").fillna(0)
    return df

def save_set(date, exercice, groupe, series, reps, poids, notes):
    client = get_client()
    client.table("workouts").insert({
        "date":     date.strftime("%Y-%m-%d"),
        "exercice": exercice,
        "groupe":   groupe,
        "series":   int(series),
        "reps":     int(reps),
        "poids_kg": float(poids),
        "notes":    notes,
    }).execute()
    st.cache_data.clear()

def delete_row(row_id: int):
    client = get_client()
    client.table("workouts").delete().eq("id", row_id).execute()
    st.cache_data.clear()
