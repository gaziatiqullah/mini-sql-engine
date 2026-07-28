#include <stdio.h>
#include <string.h>       /* ← this was missing! */
#include "table.h"

int main() {
    /* 1. Create table */
    Column cols[3] = {
        {"id",   "INT"},
        {"name", "VARCHAR"},
        {"age",  "INT"}
    };
    Table *t = create_table("students", cols, 3);

    /* 2. Manually insert rows */
    strcpy(t->rows[0].values[0], "1");
    strcpy(t->rows[0].values[1], "Alice");
    strcpy(t->rows[0].values[2], "20");
    t->row_count++;

    strcpy(t->rows[1].values[0], "2");
    strcpy(t->rows[1].values[1], "Bob");
    strcpy(t->rows[1].values[2], "22");
    t->row_count++;

    /* 3. Save and free */
    save_table(t);
    free_table(t);

    /* 4. Reload and print */
    Table *loaded = load_table("students");
    print_table(loaded);
    free_table(loaded);

    return 0;
}