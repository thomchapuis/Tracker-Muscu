import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from data import load_data, save_set
from stats import (
    volume_par_seance, charge_par_groupe_semaine,
    progression_exercice, volume_exercice, resume_semaine
)
from exercises import ALL_EXERCISES, EXERCISE_TO_GROUP

st.set_page_config(
    page_title="Workout Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Chargement des données ──────────────────────────────────────────
df = load_data()

# ── Navigation ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Séance du jour",
    "📅 Historique",
    "📊 Stats",
    "📈 Progression",
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — Saisie rapide
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Séance du jour")

    col1, col2 = st.columns([2, 1])
    with col1:
        exercice = st.selectbox("Exercice", ALL_EXERCISES)
    with col2:
        seance_date = st.date_input("Date", value=date.today())

    col3, col4, col5 = st.columns(3)
    with col3:
        series = st.number_input("Séries", min_value=1, max_value=20, value=3)
    with col4:
        reps = st.number_input("Reps", min_value=1, max_value=100, value=10)
    with col5:
        # Suggère le dernier poids utilisé pour cet exercice
        last_poids = 0.0
        if not df.empty and exercice in df["exercice"].values:
            last_poids = float(df[df["exercice"] == exercice]["poids_kg"].iloc[-1])
        poids = st.number_input("Poids (kg)", min_value=0.0, step=1.25, value=last_poids)

    notes = st.text_input("Notes (optionnel)", placeholder="Bonne séance, fatigue...")

    if st.button("✅ Enregistrer la série", use_container_width=True, type="primary"):
        groupe = EXERCISE_TO_GROUP.get(exercice, "Autre")
        save_set(seance_date, exercice, groupe, series, reps, poids, notes)
        st.success(f"Enregistré : {exercice} — {series}×{reps} @ {poids}kg")
        st.rerun()

    # Aperçu de la séance en cours
    if not df.empty:
        today_df = df[df["date"].dt.date == seance_date]
        if not today_df.empty:
            st.divider()
            st.caption("Séries enregistrées aujourd'hui")
            st.dataframe(
                today_df[["exercice", "series", "reps", "poids_kg", "notes"]],
                hide_index=True,
                use_container_width=True,
            )

# ════════════════════════════════════════════════════════════════════
# TAB 2 — Historique
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Historique des séances")
    if df.empty:
        st.info("Aucune donnée encore.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            ex_filter = st.multiselect("Filtrer par exercice", ALL_EXERCISES)
        with col_f2:
            n_days = st.selectbox("Période", [7, 30, 90, 365], index=1)

        filtered = df[df["date"] >= pd.Timestamp.today() - pd.Timedelta(days=n_days)]
        if ex_filter:
            filtered = filtered[filtered["exercice"].isin(ex_filter)]

        st.dataframe(
            filtered.sort_values("date", ascending=False)
                    .assign(date=lambda x: x["date"].dt.strftime("%d/%m/%Y"))
                    [["date", "exercice", "groupe", "series", "reps", "poids_kg", "notes"]],
            hide_index=True,
            use_container_width=True,
        )

# ════════════════════════════════════════════════════════════════════
# TAB 3 — Stats & charge
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Statistiques")
    if df.empty:
        st.info("Aucune donnée encore.")
    else:
        # Résumé semaine
        resume = resume_semaine(df)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Séances cette semaine", resume["seances"])
        c2.metric("Séries totales", resume["series_totales"])
        c3.metric("Volume total (kg)", f"{resume['volume_total']:,}")
        c4.metric("Groupes musculaires", resume["groupes_travailles"])

        st.divider()

        # Volume par séance
        vol = volume_par_seance(df)
        fig_vol = px.bar(vol, x="date", y="volume",
                         title="Volume par séance (séries × reps × poids)",
                         labels={"volume": "Volume (kg)", "date": ""})
        st.plotly_chart(fig_vol, use_container_width=True)

        # Charge par groupe musculaire / semaine
        charge = charge_par_groupe_semaine(df)
        fig_charge = px.bar(charge, x="semaine", y="series",
                            color="groupe_musculaire",
                            title="Séries par groupe musculaire / semaine",
                            labels={"series": "Séries", "semaine": "", "groupe_musculaire": "Groupe"})
        st.plotly_chart(fig_charge, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 4 — Progression par exercice
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Progression par exercice")
    if df.empty:
        st.info("Aucune donnée encore.")
    else:
        ex_choice = st.selectbox("Exercice", [e for e in ALL_EXERCISES if e in df["exercice"].values])
        metric_choice = st.radio("Métrique", ["Poids max (kg)", "Volume total"], horizontal=True)

        if metric_choice == "Poids max (kg)":
            prog = progression_exercice(df, ex_choice)
            fig = px.line(prog, x="date", y="poids_kg", markers=True,
                          title=f"Poids max — {ex_choice}",
                          labels={"poids_kg": "Poids (kg)", "date": ""})
        else:
            prog = volume_exercice(df, ex_choice)
            fig = px.line(prog, x="date", y="volume", markers=True,
                          title=f"Volume — {ex_choice}",
                          labels={"volume": "Volume (kg)", "date": ""})

        fig.update_traces(line_color="#7F77DD")
        st.plotly_chart(fig, use_container_width=True)

