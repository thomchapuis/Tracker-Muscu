
import pandas as pd

def volume_par_seance(df: pd.DataFrame) -> pd.DataFrame:
    """Volume total = séries × reps × poids, agrégé par date."""
    df = df.copy()
    df["volume"] = df["series"] * df["reps"] * df["poids_kg"]
    return (
        df.groupby("date")["volume"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

def charge_par_groupe_semaine(df: pd.DataFrame) -> pd.DataFrame:
    """Nombre de séries par groupe musculaire par semaine."""
    df = df.copy()
    df["semaine"] = df["date"].dt.to_period("W").astype(str)
    return (
        df.groupby(["semaine", "groupe"])["series"]
        .sum()
        .reset_index()
    )

def progression_exercice(df: pd.DataFrame, exercice: str) -> pd.DataFrame:
    """Poids max soulevé par date pour un exercice donné."""
    ex_df = df[df["exercice"] == exercice].copy()
    return (
        ex_df.groupby("date")["poids_kg"]
        .max()
        .reset_index()
        .sort_values("date")
    )

def volume_exercice(df: pd.DataFrame, exercice: str) -> pd.DataFrame:
    """Volume total par date pour un exercice."""
    ex_df = df[df["exercice"] == exercice].copy()
    ex_df["volume"] = ex_df["series"] * ex_df["reps"] * ex_df["poids_kg"]
    return (
        ex_df.groupby("date")["volume"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

def resume_semaine(df: pd.DataFrame) -> dict:
    """Résumé de la semaine en cours."""
    today = pd.Timestamp.today().normalize()
    start_week = today - pd.Timedelta(days=today.weekday())
    week_df = df[df["date"] >= start_week]
    return {
        "seances": week_df["date"].nunique(),
        "series_totales": int(week_df["series"].sum()),
        "volume_total": int((week_df["series"] * week_df["reps"] * week_df["poids_kg"]).sum()),
        "groupes_travailles": week_df["groupe"].nunique(),
    }
