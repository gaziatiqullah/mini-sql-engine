#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "table.h"

/* ── helpers ── */
static void get_csv_path(const char *name, char *path) {
    snprintf(path, 256, "data/%s.csv", name);
}
static void get_schema_path(const char *name, char *path) {
    snprintf(path, 256, "data/%s.schema", name);
}

/* ── print separator line used by print_table ── */
static void print_separator(Table *t) {
    int widths[MAX_COLS];
    for (int c = 0; c < t->col_count; c++) {
        widths[c] = (int)strlen(t->columns[c].name);
        for (int r = 0; r < t->row_count; r++) {
            int len = (int)strlen(t->rows[r].values[c]);
            if (len > widths[c]) widths[c] = len;
        }
    }
    printf("+");
    for (int c = 0; c < t->col_count; c++) {
        for (int i = 0; i < widths[c] + 2; i++) printf("-");
        printf("+");
    }
    printf("\n");
}

/* ── create_table ── */
Table *create_table(const char *name, Column *cols, int col_count) {
    Table *t = (Table *)malloc(sizeof(Table));
    if (!t) { fprintf(stderr, "Error: malloc failed.\n"); return NULL; }

    strncpy(t->name, name, MAX_NAME);
    t->col_count = col_count;
    t->row_count = 0;
    for (int i = 0; i < col_count; i++) t->columns[i] = cols[i];

    /* save schema */
    char path[256];
    get_schema_path(name, path);
    FILE *f = fopen(path, "w");
    if (!f) { fprintf(stderr, "Error: cannot create schema.\n"); free(t); return NULL; }
    for (int i = 0; i < col_count; i++)
        fprintf(f, "%s %s\n", t->columns[i].name, t->columns[i].type);
    fclose(f);

    /* save empty CSV with header */
    get_csv_path(name, path);
    f = fopen(path, "w");
    if (!f) { fprintf(stderr, "Error: cannot create CSV.\n"); free(t); return NULL; }
    for (int i = 0; i < col_count; i++) {
        if (i > 0) fprintf(f, ",");
        fprintf(f, "%s", t->columns[i].name);
    }
    fprintf(f, "\n");
    fclose(f);

    printf("Table '%s' created.\n", name);
    return t;
}

/* ── load_table ── */
Table *load_table(const char *name) {
    Table *t = (Table *)malloc(sizeof(Table));
    if (!t) { fprintf(stderr, "Error: malloc failed.\n"); return NULL; }

    strncpy(t->name, name, MAX_NAME);
    t->col_count = 0;
    t->row_count = 0;

    /* read schema */
    char path[256];
    get_schema_path(name, path);
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "Error: table '%s' not found.\n", name); free(t); return NULL; }

    char col_name[MAX_NAME], col_type[MAX_NAME];
    while (fscanf(f, "%s %s", col_name, col_type) == 2) {
        strncpy(t->columns[t->col_count].name, col_name, MAX_NAME);
        strncpy(t->columns[t->col_count].type, col_type, MAX_NAME);
        t->col_count++;
    }
    fclose(f);

    /* read CSV rows */
    get_csv_path(name, path);
    f = fopen(path, "r");
    if (!f) { fprintf(stderr, "Error: CSV for '%s' not found.\n", name); free(t); return NULL; }

    char line[4096];
    fgets(line, sizeof(line), f);   /* skip header row */

    while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\n")] = '\0';
        if (strlen(line) == 0) continue;

        Row *row = &t->rows[t->row_count];
        int col = 0;
        char *token = strtok(line, ",");
        while (token != NULL && col < t->col_count) {
            strncpy(row->values[col], token, MAX_VAL);
            col++;
            token = strtok(NULL, ",");
        }
        while (col < t->col_count) { row->values[col][0] = '\0'; col++; }

        t->row_count++;
        if (t->row_count >= MAX_ROWS) {
            fprintf(stderr, "Warning: MAX_ROWS reached.\n");
            break;
        }
    }
    fclose(f);
    return t;
}

/* ── save_table ── */
void save_table(Table *t) {
    if (!t) return;
    char path[256];
    get_csv_path(t->name, path);
    FILE *f = fopen(path, "w");
    if (!f) { fprintf(stderr, "Error: cannot write CSV.\n"); return; }

    for (int i = 0; i < t->col_count; i++) {
        if (i > 0) fprintf(f, ",");
        fprintf(f, "%s", t->columns[i].name);
    }
    fprintf(f, "\n");

    for (int r = 0; r < t->row_count; r++) {
        for (int c = 0; c < t->col_count; c++) {
            if (c > 0) fprintf(f, ",");
            fprintf(f, "%s", t->rows[r].values[c]);
        }
        fprintf(f, "\n");
    }
    fclose(f);
}

/* ── free_table ── */
void free_table(Table *t) {
    if (t) free(t);
}

/* ── print_table ── */
void print_table(Table *t) {
    if (!t) return;

    /* calculate column widths */
    int widths[MAX_COLS];
    for (int c = 0; c < t->col_count; c++) {
        widths[c] = (int)strlen(t->columns[c].name);
        for (int r = 0; r < t->row_count; r++) {
            int len = (int)strlen(t->rows[r].values[c]);
            if (len > widths[c]) widths[c] = len;
        }
    }

    print_separator(t);

    /* header */
    printf("|");
    for (int c = 0; c < t->col_count; c++)
        printf(" %-*s |", widths[c], t->columns[c].name);
    printf("\n");

    print_separator(t);

    /* rows */
    for (int r = 0; r < t->row_count; r++) {
        printf("|");
        for (int c = 0; c < t->col_count; c++)
            printf(" %-*s |", widths[c], t->rows[r].values[c]);
        printf("\n");
    }

    print_separator(t);
    printf("%d row(s) returned.\n", t->row_count);
}

/* ── print_row ── */
void print_row(Table *t, Row *row) {
    if (!t || !row) return;
    printf("|");
    for (int c = 0; c < t->col_count; c++) {
        int w = (int)strlen(t->columns[c].name);
        printf(" %-*s |", w, row->values[c]);
    }
    printf("\n");
}

/* ── get_col_index ── */
int get_col_index(Table *t, const char *col_name) {
    if (!t) return -1;
    for (int i = 0; i < t->col_count; i++)
        if (strcmp(t->columns[i].name, col_name) == 0)
            return i;
    return -1;
}