#ifndef TABLE_H
#define TABLE_H

#define MAX_COLS 20
#define MAX_ROWS 1000
#define MAX_NAME 64
#define MAX_VAL  256

typedef struct {
    char name[MAX_NAME];
    char type[MAX_NAME];  // "INT", "VARCHAR", "FLOAT"
} Column;

typedef struct {
    char values[MAX_COLS][MAX_VAL];
} Row;

typedef struct {
    char   name[MAX_NAME];
    int    col_count;
    int    row_count;
    Column columns[MAX_COLS];
    Row    rows[MAX_ROWS];
} Table;

// Function signatures (you will implement these in table.c)
Table* create_table(const char *name, Column *cols, int col_count);
Table* load_table(const char *name);
void   save_table(Table *t);
void   free_table(Table *t);
void   print_table(Table *t);
void   print_row(Table *t, Row *row);
int    get_col_index(Table *t, const char *col_name);

#endif