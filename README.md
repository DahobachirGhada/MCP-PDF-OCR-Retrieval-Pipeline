# MCP-PDF-OCR-Retrieval-Pipeline
A Hybrid PDF + OCR Retrieval Pipeline with MCP (RAG Over Complex Docs)
Most retrieval systems work well on clean, simple PDFs. But real documents like financial reports or scanned contracts are messy. They have tables, multiple columns, footers, charts, and even images with text. That’s where things usually break and this MCP project helps you fix that.

In this project, you will build a layout-aware Retrieval-Augmented Generation (RAG) pipeline using model control protocol as the backbone. The workflow stitches together multiple tools: PyMuPDF to parse structure, Camelot for table extraction, DocTR or PaddleOCR for image-based text, and layout heuristics to hold it all together. Once parsed and cleaned, your chunks go into a vector store like Chroma, ready for retrieval. This project helps you master the art of building a parsing pipeline that adapts based on what the document looks like and gives your LLM the best shot at answering questions with reliable, structured context.

