import streamlit as st
from qa import answer_question

st.set_page_config(page_title="AUTOSAR HLD Document Assistant", layout="centered")

st.title("AUTOSAR HLD Document Analysis Assistant")
st.caption("Ask questions about your uploaded HLD document. Answers are grounded in the document content with page citations.")

question = st.text_input("Ask a question about the document:")

if st.button("Get Answer") and question:
    with st.spinner("Searching document and generating answer..."):
        result = answer_question(question)

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Source Pages")
    st.write(", ".join(str(p) for p in result["source_pages"]))