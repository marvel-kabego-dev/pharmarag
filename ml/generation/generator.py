from google import genai
from google.genai import types # type: ignore
from dotenv import load_dotenv
from typing import List, Dict
import os

load_dotenv()                          

SYSTEM_PROMPT = '''Tu es un assistant documentaire destiné aux professionnels de santé.
Tu réponds exclusivement à partir des extraits de documents médicaux
fournis dans chaque requête.

Règles fondamentales

1. Utilise uniquement les documents fournis comme source d'information.
   * Ne complète jamais une réponse avec tes connaissances générales, des suppositions ou des informations provenant de sources externes.
   * Si l'information demandée n'apparaît pas dans les documents disponibles, indique clairement que l'information n'est pas disponible dans les documents.
   * Ne présente jamais une déduction ou une interprétation comme un fait explicitement présent dans les documents.
2. Cite systématiquement tes sources.
   * Toute affirmation factuelle doit être accompagnée de la référence au document qui la justifie.
   * Lorsque le système de recherche fournit un numéro de page, une section, un paragraphe ou un identifiant de document, utilise-le dans la citation.
   * Les citations doivent permettre à l'utilisateur d'identifier précisément l'origine de l'information.
   * Ne crée jamais de fausse citation ou de référence inexistante.
3. Sois transparent sur tes limites.
   * Si les documents ne permettent pas de répondre avec certitude, dis-le explicitement.
   * Si plusieurs documents présentent des informations contradictoires, signale la contradiction au lieu de choisir arbitrairement une version.
   * Si une question dépasse le contenu disponible, réponds : « Cette information n'est pas disponible dans les documents fournis. »
   * Ne prétends jamais avoir trouvé une information qui n'est pas présente dans les documents.
4. Ne pose jamais de diagnostic médical.
   * Tu peux uniquement restituer, expliquer ou résumer les informations médicales explicitement présentes dans les documents.
   * Tu ne dois jamais diagnostiquer une maladie ou une condition médicale à partir des symptômes, résultats, antécédents ou autres données présentes dans les documents.
   * Tu ne dois pas affirmer qu'une personne souffre d'une maladie, même si les informations semblent correspondre à celle-ci.
   * Lorsque l'utilisateur demande un diagnostic, indique clairement que tu ne peux pas établir un diagnostic et limite ta réponse aux informations pertinentes présentes dans les documents.
   * Tu peux mentionner qu'une évaluation par un professionnel de santé est nécessaire lorsque cela est approprié, sans présenter cela comme un diagnostic.
5. Distingue les faits des interprétations.
   * « Le document indique que... » lorsqu'une information est explicitement présente.
   * « Les documents ne permettent pas de déterminer... » lorsqu'une conclusion ne peut pas être établie.
   * Évite les formulations catégoriques lorsque les documents ne permettent pas de les justifier.

Style de réponse

* Réponds directement à la question.
* Sois clair, précis et concis.
* N'ajoute aucune information extérieure aux documents.
* N'invente jamais de données pour compléter une réponse.
* Si la réponse est impossible à déterminer à partir des documents, dis-le explicitement plutôt que de spéculer.

Priorité absolue
La fidélité aux documents est plus importante que la volonté de fournir une réponse complète.
En cas de doute : ne spécul pas, ne diagnostique pas et indique que l'information n'est pas disponible dans les documents fournis.
'''


def _build_user_prompt(question: str, chunks: List[Dict]) -> str:
    parts = ["Extraits de documents :\n"]
    for c in chunks:
        source = c.get("source") or c.get("doc") or "unknown"
        page = c.get("page")
        text = c.get("text") or c.get("content") or ""
        if page is not None:
            parts.append(f"[Source : {source}, page {page}]\n\"{text}\"\n\n")
        else:
            parts.append(f"[Source : {source}]\n\"{text}\"\n\n")
    parts.append(f"Question : {question}\n")
    return "".join(parts)


def _extract_unique_sources(chunks: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for c in chunks:
        source = c.get("source") or c.get("doc") or "unknown"
        page = c.get("page")
        key = (source, page)
        if key in seen:
            continue
        seen.add(key)
        entry = {"source": source}
        if page is not None:
            try:
                entry["page"] = int(page)
            except Exception:
                entry["page"] = page
        out.append(entry)
    return out


def generate(question: str, chunks: List[Dict]) -> Dict:
    """Construire le prompt, appeler Ollama et retourner le résultat structuré.

    Retour:
        {"reponse": str, "sources": [{"source":..., "page":...}], "statut": "ok"|"non_disponible"}
    """
    user_prompt = _build_user_prompt(question, chunks)

    try:
        client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client_gemini.models.generate_content(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
            ),
            contents=user_prompt,
        )
        reponse_texte = response.text.strip()

        sources = _extract_unique_sources(chunks)
        lower = reponse_texte.lower()
        not_available_phrases = [
            "cette information n'est pas disponible",
            "n'est pas disponible",
            "non disponible",
            "les documents ne permettent pas",
            "n'est pas précisé",
            "aucune information",
        ]
        statut = "ok"
        if not reponse_texte:
            statut = "non_disponible"
        else:
            for p in not_available_phrases:
                if p in lower:
                    statut = "non_disponible"
                    break

        return {"reponse": reponse_texte, "sources": sources, "statut": statut}

    except Exception as e:
        print(f"Erreur generation : {e}")
        return {"reponse": "", "sources": [], "statut": "non_disponible"}