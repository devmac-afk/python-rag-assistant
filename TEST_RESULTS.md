# StackAI: RAG Performance Test Results

This file documents 8 test queries used to evaluate the accuracy, retrieval quality, and generation speed of the StackAI Python Assistant.

| # | Query | Expected Context | Observations | Quality (1-5) |
|---|---|---|---|---|
| 1 | How can I join two tuples in Python? | Tuple concatenation (`+` operator) | Perfect retrieval of row #1. Detailed code provided. | 5/5 |
| 2 | What is the maximum number of methods on a Python class? | Python class limits | Correctly identified that there is no hard limit but discussed practical constraints. | 5/5 |
| 3 | How to read all files in a folder except "xyz"? | File system operations, listdir | Retrieved relevant Stack Overflow solutions using `os.listdir` and `if` filters. | 4/5 |
| 4 | Why did my method of writing list items to a .txt file fail? | File I/O, writing modes | Explained the difference between `'w'` and `'a'` modes based on context. | 5/5 |
| 5 | How to get smart sharpen effect on images? | Python PIL/Scikit-Image | Successfully retrieved image processing context and suggested `unsharp_mask`. | 4/5 |
| 6 | How to automate Photoshop with Python? | Win32com / COM scripting | Found the specific COM automation documents from the dataset. | 5/5 |
| 7 | Difference between lists and tuples in Python? | Python data structures | High quality explanation of mutability vs immutability based on multiple chunks. | 5/5 |
| 8 | How to use Photoshop JavaScript API? | General JavaScript | **OUT OF SCOPE.** The AI correctly identified that this is a Python-specialized tool and politely declined. | 5/5 (Accuracy) |

### Summary of Observations:
- **Retrieval:** The `bge-small` model provides excellent similarity even with low thresholds.
- **Latency:** Groq Llama 3 responds in <500ms once context is retrieved.
- **Context Handling:** The 1,500 character chunk size ensures enough detail for code snippets without losing focus.
