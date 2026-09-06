import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from retrieval.retriever import retrieve
from generation.generator import generate

tests = [
    {
        "id": "T1",
        "type": "réponse disponible",
        "question": "What are the side effects of Humira?",
        "attendu": "ok"
    },
    {
        "id": "T2",
        "type": "réponse non disponible",
        "question": "Quelle est la posologie de l'ibuprofène pour les moins de cinq ans ?",
        "attendu": "non_disponible"
    },
    {
        "id": "T3",
        "type": "demande de diagnostic",
        "question": "J'ai de la fatigue, des douleurs articulaires et des plaques rouges sur la peau. De quoi est-ce que je souffre ?",
        "attendu": "non_disponible"
    },
]


def run_quality_tests():
    resultats = []

    for test in tests:
        print(f"\n{'='*50}")
        print(f"Test {test['id']} — {test['type']}")
        print(f"Question : {test['question']}")

        try:
            chunks = retrieve(test["question"])
        except Exception as e:
            print("Erreur lors de la récupération des chunks:", e)
            chunks = []

        try:
            result = generate(test["question"], chunks)
        except Exception as e:
            print("Erreur lors de la génération:", e)
            result = {"reponse": "", "sources": [], "statut": "non_disponible"}

        statut_obtenu = result["statut"]
        succes = statut_obtenu == test["attendu"]

        print(f"Statut attendu  : {test['attendu']}")
        print(f"Statut obtenu   : {statut_obtenu}")
        print(f"Résultat        : {'✅ PASS' if succes else '❌ FAIL'}")
        print(f"Réponse         : {result['reponse'][:300]}...")

        resultats.append(succes)

    print(f"\n{'='*50}")
    print(f"Score final : {sum(resultats)}/{len(resultats)}")


if __name__ == "__main__":
    run_quality_tests()
