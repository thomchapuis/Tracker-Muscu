
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

def radar_repartition(df: pd.DataFrame, periode_label: str, nb_jours: int) -> pd.DataFrame:
    """Séries par groupe musculaire sur une période donnée."""
    cutoff = pd.Timestamp.today() - pd.Timedelta(days=nb_jours)
    filtered = df[df["date"] >= cutoff]
    result = (
        filtered.groupby("groupe")["series"]
        .sum()
        .reset_index()
        .rename(columns={"series": "total"})
    )
    result["periode"] = periode_label
    return result

def top_exercices(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    """Exercices les plus pratiqués par nombre de séances."""
    return (
        df.groupby("exercice")
        .agg(
            nb_seances=("date", "nunique"),
            series_totales=("series", "sum"),
            poids_max=("poids_kg", "max"),
        )
        .reset_index()
        .sort_values("nb_seances", ascending=False)
        .head(n)
    )

def rapport_mensuel(df: pd.DataFrame, annee: int, mois: int) -> dict:
    """Résumé complet d'un mois."""
    mask = (df["date"].dt.year == annee) & (df["date"].dt.month == mois)
    m = df[mask]
    if m.empty:
        return {}
    volume = (m["series"] * m["reps"] * m["poids_kg"]).sum()
    prev_mask = (
        (df["date"].dt.year == (annee if mois > 1 else annee - 1)) &
        (df["date"].dt.month == (mois - 1 if mois > 1 else 12))
    )
    prev = df[prev_mask]
    prev_volume = (prev["series"] * prev["reps"] * prev["poids_kg"]).sum() if not prev.empty else 0
    return {
        "seances":        m["date"].nunique(),
        "series_totales": int(m["series"].sum()),
        "volume_total":   int(volume),
        "groupes":        m["groupe"].nunique(),
        "exercices":      m["exercice"].nunique(),
        "volume_vs_mois_precedent": round((volume - prev_volume) / prev_volume * 100, 1) if prev_volume else None,
        "par_groupe":     m.groupby("groupe")["series"].sum().to_dict(),
    }
