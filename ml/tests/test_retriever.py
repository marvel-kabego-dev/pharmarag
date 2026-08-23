import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval.retriever import retrieve

def test_retriever_medical_question_prints_results():
    question = "What are the side effects of Humira?"
    
    results = retrieve(question)
    
    print(f"\nQuestion : {question}\n")
    for i, result in enumerate(results, start=1):
        print(f"#{i} — Score : {result['score']}")
        print(f"  Source : {result['source']}, page {result['page']}")
        print(f"  Extrait : {result['text'][:150]}...")
        print("-" * 50)
    
    assert len(results) > 0

if __name__ == "__main__":
    test_retriever_medical_question_prints_results()