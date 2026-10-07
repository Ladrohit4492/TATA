"""
CS1 - AUTOSAR HLD Document Analysis Assistant: evaluation runner.

Runs each test question through the real pipeline (answer_question from qa.py),
records the answer, cited pages and response time, and checks the answer against
ground-truth keywords from the case-study document.
Usage (with venv active): python evaluate.py
Outputs: Evaluation_Results.csv and Evaluation_Results.md
The keyword check is an automatic check; answers are also reviewed manually.
"""
import csv, time, datetime
from qa import answer_question

# (id, question, expected behaviour, [any-of keyword groups], pass threshold)
TESTS = [
 (1, "What is the title of this document?",
     "Identifies the document as 'Case Study 1: AUTOSAR HLD Document Analysis'.",
     [["case study 1"], ["autosar hld document analysis", "autosar hld"]], 1.0),
 (2, "What is the recommended vector database for this solution?",
     "States FAISS or ChromaDB, with Milvus or self-hosted Weaviate for scale.",
     [["faiss"], ["chroma"], ["milvus", "weaviate"]], 0.67),
 (3, "Who are the primary users and stakeholders for this assistant?",
     "Lists system architects, AUTOSAR architects, software developers, integration engineers, test engineers, engineering managers.",
     [["architect"], ["developer"], ["integration"], ["test"], ["manager"]], 0.8),
 (4, "What are the key risks associated with this solution?",
     "Mentions incorrect extraction from tables/diagrams, hallucinated relationships, unauthorized access, outdated document versions, with controls.",
     [["table", "diagram", "extraction"], ["hallucinat"], ["unauthori", "access"], ["outdated", "version"]], 0.75),
 (5, "What does the high-level workflow involve, from document upload to generating an answer?",
     "Describes upload, extraction, chunking, embedding, retrieval, grounded response with citations, and engineer review.",
     [["upload", "select"], ["extract"], ["chunk"], ["embed"], ["retriev"], ["review", "correct", "export"]], 0.67),
]
# Extra negative test (not one of the 5 report tests): the model must NOT answer from general knowledge.
NEG = ("X1", "What is the capital of France?",
       "Declines / says the answer is not in the document.",
       [["not", "no information", "cannot", "does not", "unable", "n't"]], 1.0)

def run_one(q):
    t0 = time.time()
    for attempt in range(3):                      # small retry for API hiccups / rate limits
        try:
            r = answer_question(q)
            return r["answer"].strip(), sorted(r["source_pages"]), time.time() - t0, ""
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(4)
    return "", [], time.time() - t0, err

def check(answer, groups, thr):
    a = answer.lower().replace("*", "")
    hit = sum(any(k in a for k in g) for g in groups)
    score = hit / len(groups)
    return score, score >= thr

rows = []
for tid, q, exp, groups, thr in TESTS + [NEG]:
    ans, pages, secs, err = run_one(q)
    score, ok = check(ans, groups, thr) if not err else (0.0, False)
    is_neg = tid == "X1"
    cited = bool(pages)
    auto = "ERROR" if err else ("PASS" if ok and (cited or is_neg) else "FAIL")
    rows.append(dict(id=tid, question=q, expected=exp, answer=ans or err,
                     pages_0_based=", ".join(map(str, pages)),
                     pages_1_based=", ".join(str(p + 1) for p in pages),
                     keyword_score=f"{score:.0%}", seconds=f"{secs:.1f}",
                     auto_check=auto, manual_review=""))
    print(f"[{tid}] {auto}  score={score:.0%}  {secs:.1f}s  pages={pages}")

stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open("Evaluation_Results.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

main = [r for r in rows if r["id"] != "X1"]
passed = sum(r["auto_check"] == "PASS" for r in main)
lat = [float(r["seconds"]) for r in main]
with open("Evaluation_Results.md", "w", encoding="utf-8") as f:
    f.write(f"# CS1 Evaluation Results\n\nRun: {stamp} | top-k = 3 | gemini-3.6-flash + gemini-embedding-001\n\n")
    f.write(f"Auto-check pass: {passed}/{len(main)} | Avg latency: {sum(lat)/len(lat):.1f}s | Max: {max(lat):.1f}s\n\n")
    f.write("Page numbers: PyPDFLoader index is 0-based (page 0 = first page of the PDF).\n\n")
    for r in rows:
        f.write(f"## Test {r['id']}: {r['question']}\n- Expected: {r['expected']}\n- Answer: {r['answer']}\n"
                f"- Cited pages: {r['pages_0_based']} (0-based) / {r['pages_1_based']} (1-based)\n"
                f"- Keyword score: {r['keyword_score']} | Latency: {r['seconds']}s | Auto-check: {r['auto_check']}\n"
                f"- Manual review (Pass/Fail + notes): ________\n\n")
print(f"\nSaved Evaluation_Results.csv and Evaluation_Results.md  ({passed}/{len(main)} auto-pass)")
