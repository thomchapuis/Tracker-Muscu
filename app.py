import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from data import load_data, save_set, get_client, delete_row
from stats import (
    volume_par_seance, charge_par_groupe_semaine,
    progression_exercice, volume_exercice, resume_semaine,
    radar_repartition, top_exercices, rapport_mensuel   # ← nouveaux
)
import plotly.graph_objects as go
import calendar
from exercises import ALL_EXERCISES, EXERCISE_TO_GROUP, EXERCISES


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

    mode = st.radio("Mode de saisie", ["Séance complète", "Série isolée"], horizontal=True)

    if mode == "Séance complète":
        col1, col2 = st.columns(2)
        with col1:
            seance_date = st.date_input("Date", value=date.today(), key="date_seance")
        with col2:
            dominante = st.selectbox("Dominante", ["Haut du corps", "Jambes", "Full body", "Cardio"])

        st.divider()

        groupe_filtre = st.selectbox("Groupe musculaire", list(EXERCISES.keys()))
        exercice = st.selectbox("Exercice", EXERCISES[groupe_filtre])

        col3, col4, col5 = st.columns(3)
        with col3:
            series = st.number_input("Séries", min_value=1, max_value=20, value=3)
        with col4:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=10)
        with col5:
            last_poids = 0.0
            if not df.empty and exercice in df["exercice"].values:
                last_poids = float(df[df["exercice"] == exercice]["poids_kg"].iloc[-1])
            poids = st.number_input("Poids (kg)", min_value=0.0, step=1.0, value=last_poids)

        notes = st.text_input("Notes", placeholder="Optionnel...", key="notes_seance")

        if st.button("✅ Ajouter cette série", use_container_width=True, type="primary"):
            groupe = EXERCISE_TO_GROUP.get(exercice, "Autre")
            save_set(seance_date, exercice, groupe, series, reps, poids, notes)
            st.success(f"{exercice} — {series}×{reps} @ {poids}kg ajouté")
            st.rerun()

        # Aperçu séance en cours
        if not df.empty:
            today_df = df[df["date"].dt.date == seance_date]
            if not today_df.empty:
                st.divider()
                st.caption(f"Séries enregistrées le {seance_date.strftime('%d/%m/%Y')}")
                st.dataframe(
                    today_df[["exercice", "groupe", "series", "reps", "poids_kg", "notes"]],
                    hide_index=True,
                    use_container_width=True,
                )

    else:  # Série isolée
        seance_date = st.date_input("Date", value=date.today(), key="date_iso")
        col1, col2 = st.columns([2, 1])
        with col1:
            groupe_filtre = st.selectbox("Groupe musculaire", list(EXERCISES.keys()), key="groupe_iso")
        with col2:
            exercice = st.selectbox("Exercice", EXERCISES[groupe_filtre], key="ex_iso")

        col3, col4, col5 = st.columns(3)
        with col3:
            series = st.number_input("Séries", min_value=1, max_value=20, value=3, key="s_iso")
        with col4:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=10, key="r_iso")
        with col5:
            last_poids = 0.0
            if not df.empty and exercice in df["exercice"].values:
                last_poids = float(df[df["exercice"] == exercice]["poids_kg"].iloc[-1])
            poids = st.number_input("Poids (kg)", min_value=0.0, step=1.0, value=last_poids, key="p_iso")

        notes = st.text_input("Notes", placeholder="Optionnel...", key="notes_iso")

        if st.button("✅ Enregistrer", use_container_width=True, type="primary"):
            groupe = EXERCISE_TO_GROUP.get(exercice, "Autre")
            save_set(seance_date, exercice, groupe, series, reps, poids, notes)
            st.success(f"Enregistré : {exercice} — {series}×{reps} @ {poids}kg")
            st.rerun()
    
    st.dataframe(
        #df[["date","exercice","groupe","series","reps","poids_kg","notes"]]
        df
        .sort_values("id", ascending=False)
        .head(6)
        .assign(date=lambda x: x["date"].dt.strftime("%d/%m/%Y")),
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

        filtered = df[df["date"] >= pd.Timestamp.today() - pd.Timedelta(days=n_days)].copy()
        if ex_filter:
            filtered = filtered[filtered["exercice"].isin(ex_filter)]

        filtered_display = (
            filtered.sort_values("date", ascending=False)
                    .assign(date=lambda x: x["date"].dt.strftime("%d/%m/%Y"))
                    [["id", "date", "exercice", "groupe", "series", "reps", "poids_kg", "notes"]]
        )

        st.divider()

        # ── Affichage ligne par ligne avec actions ──
        for _, row in filtered_display.iterrows():
            with st.expander(f"{row['date']} — {row['exercice']} — {row['series']}×{row['reps']} @ {row['poids_kg']}kg"):

                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                with col_a:
                    new_series = st.number_input("Séries", min_value=1, max_value=20,
                                                  value=int(row["series"]), key=f"s_{row['id']}")
                with col_b:
                    new_reps = st.number_input("Reps", min_value=1, max_value=100,
                                                value=int(row["reps"]), key=f"r_{row['id']}")
                with col_c:
                    new_poids = st.number_input("Poids (kg)", min_value=0.0, step=1.0,
                                                 value=float(row["poids_kg"]), key=f"p_{row['id']}")
                with col_d:
                    new_notes = st.text_input("Notes", value=str(row["notes"]), key=f"n_{row['id']}")
                with col_e:
                    st.write("")
                    st.write("")
                    if st.button("💾 Sauvegarder", key=f"save_{row['id']}"):
                        get_client().table("workouts").update({
                            "series":   int(new_series),
                            "reps":     int(new_reps),
                            "poids_kg": float(new_poids),
                            "notes":    new_notes,
                        }).eq("id", int(row["id"])).execute()
                        st.cache_data.clear()
                        st.success("Modifié ✓")
                        st.rerun()

                st.write("")
                if st.button("🗑️ Supprimer cette série", key=f"del_{row['id']}", type="secondary"):
                    delete_row(int(row["id"]))
                    st.success("Supprimé ✓")
                    st.rerun()

# ════════════════════════════════════════════════════════════════════
# TAB 3 — Stats & charge
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Statistiques")
    if df.empty:
        st.info("Aucune donnée encore.")
    else:
        # ── Résumé semaine ──
        resume = resume_semaine(df)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Séances cette semaine", resume["seances"])
        c2.metric("Séries totales", resume["series_totales"])
        c3.metric("Volume total (kg)", f"{resume['volume_total']:,}")
        c4.metric("Groupes musculaires", resume["groupes_travailles"])

        st.divider()

        # ── Volume par séance ──
        vol = volume_par_seance(df)
        fig_vol = px.bar(vol, x="date", y="volume",
                         title="Volume par séance (séries × reps × poids)",
                         labels={"volume": "Volume (kg)", "date": ""})
        st.plotly_chart(fig_vol, use_container_width=True)

        st.divider()

        # ── Répartition musculaire — Radar ──
        st.markdown("#### Répartition musculaire")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            periode1 = st.selectbox("Période A", ["7 derniers jours", "30 derniers jours", "90 derniers jours"], index=1, key="p1")
        with col_r2:
            periode2 = st.selectbox("Période B", ["7 derniers jours", "30 derniers jours", "90 derniers jours"], index=2, key="p2")

        jours_map = {"7 derniers jours": 7, "30 derniers jours": 30, "90 derniers jours": 90}

        df1 = radar_repartition(df, periode1, jours_map[periode1])
        df2 = radar_repartition(df, periode2, jours_map[periode2])
        tous_groupes = sorted(df["groupe"].unique().tolist())

        def to_radar_values(radar_df, groupes):
            mapping = dict(zip(radar_df["groupe"], radar_df["total"]))
            return [mapping.get(g, 0) for g in groupes]

        vals1 = to_radar_values(df1, tous_groupes)
        vals2 = to_radar_values(df2, tous_groupes)

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals1 + [vals1[0]], theta=tous_groupes + [tous_groupes[0]],
            fill="toself", name=periode1, opacity=0.6
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=vals2 + [vals2[0]], theta=tous_groupes + [tous_groupes[0]],
            fill="toself", name=periode2, opacity=0.4
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
        st.plotly_chart(fig_radar, use_container_width=True)

        st.divider()

        # ── Top exercices ──
        st.markdown("#### Principaux exercices")
        top = top_exercices(df)
        fig_top = px.bar(
            top, x="nb_seances", y="exercice", orientation="h",
            labels={"nb_seances": "Nombre de séances", "exercice": ""},
            text="nb_seances",
        )
        fig_top.update_layout(yaxis=dict(categoryorder="total ascending"))
        fig_top.update_traces(textposition="outside")
        st.plotly_chart(fig_top, use_container_width=True)

        st.divider()

        # ── Rapport mensuel ──
        st.markdown("#### Rapport mensuel")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            mois_choisi = st.selectbox("Mois", list(range(1, 13)),
                                        format_func=lambda m: calendar.month_name[m],
                                        index=date.today().month - 1)
        with col_m2:
            annee_choisie = st.selectbox("Année", sorted(df["date"].dt.year.unique().tolist(), reverse=True))

        rapport = rapport_mensuel(df, annee_choisie, mois_choisi)
        if not rapport:
            st.info("Aucune donnée pour ce mois.")
        else:
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("Séances", rapport["seances"])
            r2.metric("Séries", rapport["series_totales"])
            r3.metric("Volume (kg)", f"{rapport['volume_total']:,}",
                      delta=f"{rapport['volume_vs_mois_precedent']}% vs mois préc." if rapport["volume_vs_mois_precedent"] is not None else None)
            r4.metric("Groupes", rapport["groupes"])
            r5.metric("Exercices", rapport["exercices"])

            fig_mois = px.bar(
                x=list(rapport["par_groupe"].keys()),
                y=list(rapport["par_groupe"].values()),
                labels={"x": "Groupe musculaire", "y": "Séries"},
                title="Séries par groupe ce mois",
            )
            st.plotly_chart(fig_mois, use_container_width=True)

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

