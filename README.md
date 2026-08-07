# Mini SQL Engine with Query Optimizer

![Language](https://img.shields.io/badge/Language-C%20%7C%20Python-blue)
![Status](https://img.shields.io/badge/Status-Completed-green)
![Course](https://img.shields.io/badge/Course-CSE314-orange)

## Introduction

SQL is one of the most widely used languages for managing data, but the internal compiler-related steps are often hidden from users. Traditional database systems process complex queries behind the scenes, making it difficult for students to see how lexical scanning and syntax parsing actually evaluate mathematical and relational conditions.

The **Mini SQL Engine** is designed to bridge theory and practice by parsing, validating, and executing a subset of SQL commands. It functions as a custom compiler pipeline, utilizing **Flex** for lexical tokenization and **Bison** for syntax parsing, all seamlessly wrapped in a modern, responsive Python-based Graphical User Interface (GUI) for easy interaction.

## Features

- DDL & DML Commands: `CREATE TABLE` and `INSERT INTO` with automated `.schema` and `.csv` file generation
- Data Retrieval: `SELECT` queries with specific column projection or `SELECT *`
- Conditional Filtering: `WHERE` clauses supporting multiple comparison operators (`=`, `>`, `<`, `>=`, `<=`, `!=`)
- Aggregate Functions: Mathematical summaries including `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX`
- Subqueries: Support for single-table nested subqueries
- Modern GUI: Dark-themed desktop application with dynamic tabular data grids

## Built With

- Languages: C, Python 3
- Core Tools: Flex, Bison, CustomTkinter
- Compiler & Build System: GCC, Make (mingw32-make)
- Editor: VS Code / CodeBlocks

## How to Run

1. Clone the repository: `git clone https://github.com/gaziatiqullah/mini-sql-engine.git`
2. Navigate to the project folder: `cd mini-sql-engine`
3. Build the C backend: `mingw32-make clean && mingw32-make`
4. Launch the GUI: `python gui/app.py`

## Team Members

| Name                    | Student ID | Role |
|-------------------------|------------|------|
| Gazi Atiq Ullah Nabil   | 242-15-032 | Core Engine, File Storage & Integration |
| Khandakar Tajul Islam   | 242-15-192 | Single-Table Subqueries |
| Abir Washi              | 242-15-972 | Frontend GUI & Middleware Integration |
| Sheikh Mahir Faisal     | 242-15-991 | WHERE Clause & Comparison Logic |
| Shaidur Rahman Shanu    | 242-15-993 | Aggregate Functions |

## Submitted To

**Tamanna Sultana**
<br>
Lecturer
<br>
Department of Computer Science and Engineering 
<br>
Daffodil International University

## Submission Date

August 17, 2026