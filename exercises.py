EXERCISES = {
    "Pectoraux": [
        "Développé couché barre",
        "Développé couché haltères",
        "Développé incliné",
        "Écarté poulie",
        "Dips",
    ],
    "Dos": [
        "Tractions",
        "Rowing barre",
        "Rowing haltère",
        "Tirage vertical",
        "Tirage horizontal",
    ],
    "Épaules": [
        "Développé militaire",
        "Élévations latérales",
        "Oiseau",
    ],
    "Jambes": [
        "Squat",
        "Presse à cuisses",
        "Fentes",
        "Leg curl",
        "Mollets",
    ],
    "Bras": [
        "Curl barre",
        "Curl haltères",
        "Dips triceps",
        "Extensions triceps",
    ],
    "Abdos / Gainage": [
        "Planche",
        "Crunchs",
        "Relevés de jambes",
    ],
}

# Liste plate pour les sélecteurs
ALL_EXERCISES = [ex for group in EXERCISES.values() for ex in group]

# Mapping exercice → groupe musculaire
EXERCISE_TO_GROUP = {
    ex: group
    for group, exercises in EXERCISES.items()
    for ex in exercises
}
