EXERCISES = {
    "Pectoraux": [
        "Développé couché barre",
        "Développé couché haltères",
        "Développé couché Smith",
        "Développé incliné barre",
        "Développé incliné haltères",
        "Développé incliné Smith",
        "Chest Press BasicFit",
        "Écarté haltère",
        "Écartés machine - Butterfly Chest BasicFit",
        "Écarté poulie",
        "Dips",
    ],
    "Dos": [
        "Tractions prise pronation",
        "Tractions prise pronation large",
        "Tractions prise supination",
        "Tractions prise neutre",
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
        "Ischio assis - machine",
        "Ischio couché - machine",
        "Soulevé de terre",
        "Soulevé de terre roumain",
        "Leg curl",
        "Presse à cuisses",
        "Fentes",
        "Mollets",
    ],
    "Bras": [
        "Curl barre",
        "Curl haltères",
        "Dips triceps",
        "Extensions triceps",
    ],
    
    "Grip": [
        "Suspendu 1 bras - gauche",
        "Suspendu 1 bras - droite",
        "Dead Hang",
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
