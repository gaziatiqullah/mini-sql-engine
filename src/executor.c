#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "executor.h"
#include "table.h"

/* ── Static buffers that accumulate data while one statement is being parsed ── */
static Column col_buffer[MAX_COLS];
static int    col_buffer_count = 0;

static char value_buffer[MAX_COLS][MAX_VAL];
static int  value_buffer_count = 0;

static char select_buffer[MAX_COLS][MAX_NAME];
static int  select_buffer_count = 0;

/* ── Column buffer (CREATE TABLE) ── */
void add_column_to_buffer(const char *name, const char *type) {
    strncpy(col_buffer[col_buffer_count].name, name, MAX_NAME);
    strncpy(col_buffer[col_buffer_count].type, type, MAX_NAME);
    col_buffer_count++;
}
void reset_column_buffer(void) { col_buffer_count = 0; }

/* ── Value buffer (INSERT) ── */
void add_value_to_buffer(const char *value) {
    strncpy(value_buffer[value_buffer_count], value, MAX_VAL);
    value_buffer_count++;
}
void reset_value_buffer(void) { value_buffer_count = 0; }

/* ── Select buffer (SELECT column list) ── */
void add_select_column(const char *name) {
    strncpy(select_buffer[select_buffer_count], name, MAX_NAME);
    select_buffer_count++;
}
void reset_select_buffer(void) { select_buffer_count = 0; }

/* ── Strip the surrounding single quotes from a string literal ── */
char *strip_quotes(const char *s) {
    int len = strlen(s);
    char *out = malloc(len);
    strncpy(out, s + 1, len - 2);
    out[len - 2] = '\0';
    return out;
}

/* ── CREATE TABLE execution ── */
void execute_create_table(const char *table_name) {
    Table *t = create_table(table_name, col_buffer, col_buffer_count);
    if (t) free_table(t);
}

/* ── INSERT execution ── */
void execute_insert(const char *table_name) {
    Table *t = load_table(table_name);
    if (!t) return;

    if (value_buffer_count != t->col_count) {
        fprintf(stderr, "Error: expected %d values, got %d.\n",
                t->col_count, value_buffer_count);
        free_table(t);
        return;
    }

    Row *row = &t->rows[t->row_count];
    for (int i = 0; i < value_buffer_count; i++) {
        strncpy(row->values[i], value_buffer[i], MAX_VAL);
    }
    t->row_count++;

    save_table(t);
    printf("1 row inserted into '%s'.\n", table_name);
    free_table(t);
}

/* ── SELECT execution ── */
void execute_select(const char *table_name) {
    Table *t = load_table(table_name);
    if (!t) return;

    /* Case 1: SELECT * FROM table */
    if (select_buffer_count == 1 && strcmp(select_buffer[0], "*") == 0) {
        print_table(t);
        free_table(t);
        return;
    }

    /* Case 2: SELECT specific columns — build a temporary projected table */
    static Table proj;   /* ← changed from "Table proj;" */
    strncpy(proj.name, t->name, MAX_NAME);
    proj.col_count = select_buffer_count;
    proj.row_count = t->row_count;

    int col_indices[MAX_COLS];
    for (int i = 0; i < select_buffer_count; i++) {
        int idx = get_col_index(t, select_buffer[i]);
        if (idx == -1) {
            fprintf(stderr, "Error: column '%s' does not exist.\n", select_buffer[i]);
            free_table(t);
            return;
        }
        col_indices[i] = idx;
        proj.columns[i] = t->columns[idx];
    }

    for (int r = 0; r < t->row_count; r++) {
        for (int c = 0; c < select_buffer_count; c++) {
            strncpy(proj.rows[r].values[c], t->rows[r].values[col_indices[c]], MAX_VAL);
        }
    }

    print_table(&proj);
    free_table(t);
}