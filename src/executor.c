#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "table.h"
#include "executor.h"

/* Helper: removes the surrounding single quotes from a string literal */
char *strip_quotes(const char *s) {
    int len = strlen(s);
    char *out = malloc(len);
    strncpy(out, s + 1, len - 2);
    out[len - 2] = '\0';
    return out;
}

/* ================= CREATE TABLE ================= */
static Column col_buffer[MAX_COLS];
static int col_buffer_count = 0;

void add_column_to_buffer(const char *name, const char *type) {
    if (col_buffer_count >= MAX_COLS) return;
    strncpy(col_buffer[col_buffer_count].name, name, MAX_NAME);
    strncpy(col_buffer[col_buffer_count].type, type, MAX_NAME);
    col_buffer_count++;
}

void reset_column_buffer(void) {
    col_buffer_count = 0;
}

void execute_create_table(const char *table_name) {
    Table *t = create_table(table_name, col_buffer, col_buffer_count);
    if (t) free_table(t);
}

/* ================= INSERT INTO ================= */
static char value_buffer[MAX_COLS][MAX_VAL];
static int value_buffer_count = 0;

void add_value_to_buffer(const char *value) {
    if (value_buffer_count >= MAX_COLS) return;
    strncpy(value_buffer[value_buffer_count], value, MAX_VAL);
    value_buffer_count++;
}

void reset_value_buffer(void) {
    value_buffer_count = 0;
}

void execute_insert(const char *table_name) {
    Table *t = load_table(table_name);
    if (!t) return;

    if (value_buffer_count != t->col_count) {
        fprintf(stderr, "Error: expected %d values but got %d.\n", t->col_count, value_buffer_count);
        fflush(stderr);
        free_table(t);
        return;
    }

    if (t->row_count >= MAX_ROWS) {
        fprintf(stderr, "Error: table '%s' is full.\n", table_name);
        fflush(stderr);
        free_table(t);
        return;
    }

    for (int i = 0; i < value_buffer_count; i++) {
        strncpy(t->rows[t->row_count].values[i], value_buffer[i], MAX_VAL);
    }
    t->row_count++;
    save_table(t);

    printf("1 row inserted into '%s'.\n", table_name);
    fflush(stdout);
    free_table(t);
}

/* ================= SUBQUERY MANAGEMENT (Member 4) ================= */
static char subquery_val[MAX_VAL] = "";
static int subquery_mode = 0;

static char select_buffer[MAX_COLS][MAX_NAME];
static int select_buffer_count = 0;

static char saved_select_buffer[MAX_COLS][MAX_NAME];
static int saved_select_buffer_count = 0;

void enable_subquery_mode(void) {
    subquery_mode = 1;
    subquery_val[0] = '\0';
}

void disable_subquery_mode(void) {
    subquery_mode = 0;
}

char *get_subquery_result(void) {
    return subquery_val;
}

void save_outer_select_buffer(void) {
    saved_select_buffer_count = select_buffer_count;
    for (int i = 0; i < select_buffer_count; i++) {
        strncpy(saved_select_buffer[i], select_buffer[i], MAX_NAME);
    }
    reset_select_buffer();
}

void restore_outer_select_buffer(void) {
    select_buffer_count = 0;
    for (int i = 0; i < saved_select_buffer_count; i++) {
        strncpy(select_buffer[i], saved_select_buffer[i], MAX_NAME);
    }
    select_buffer_count = saved_select_buffer_count;
}

/* ================= AGGREGATE FUNCTIONS (Member 3) ================= */
static char agg_func[16] = "";
static char agg_col[MAX_NAME] = "";
static int is_agg = 0;

void set_aggregate(const char *func, const char *col) {
    strncpy(agg_func, func, 15);
    strncpy(agg_col, col, MAX_NAME - 1);
    is_agg = 1;
}

void reset_aggregate(void) {
    agg_func[0] = '\0';
    agg_col[0] = '\0';
    is_agg = 0;
}

void apply_aggregate(Table *t) {
    if (!t || t->row_count == 0) {
        if (subquery_mode) {
            strncpy(subquery_val, "0", MAX_VAL);
            return;
        }
        printf("| Result |\n|--------|\n| NULL   |\n");
        return;
    }

    if (strcmp(agg_func, "COUNT") == 0) {
        if (subquery_mode) {
            snprintf(subquery_val, MAX_VAL, "%d", t->row_count);
            return;
        }
        printf("| COUNT |\n|-------|\n| %-5d |\n", t->row_count);
        return;
    }

    int idx = get_col_index(t, agg_col);
    if (idx == -1) {
        fprintf(stderr, "Error: column '%s' does not exist.\n", agg_col);
        return;
    }

    double sum = 0;
    double min = atof(t->rows[0].values[idx]);
    double max = min;

    for (int r = 0; r < t->row_count; r++) {
        double val = atof(t->rows[r].values[idx]);
        sum += val;
        if (val < min) min = val;
        if (val > max) max = val;
    }

    if (subquery_mode) {
        if (strcmp(agg_func, "SUM") == 0) snprintf(subquery_val, MAX_VAL, "%g", sum);
        else if (strcmp(agg_func, "AVG") == 0) snprintf(subquery_val, MAX_VAL, "%g", sum / t->row_count);
        else if (strcmp(agg_func, "MIN") == 0) snprintf(subquery_val, MAX_VAL, "%g", min);
        else if (strcmp(agg_func, "MAX") == 0) snprintf(subquery_val, MAX_VAL, "%g", max);
        return;
    }

    if (strcmp(agg_func, "SUM") == 0) printf("| SUM   |\n|-------|\n| %-5.2f |\n", sum);
    if (strcmp(agg_func, "AVG") == 0) printf("| AVG   |\n|-------|\n| %-5.2f |\n", sum / t->row_count);
    if (strcmp(agg_func, "MIN") == 0) printf("| MIN   |\n|-------|\n| %-5.2f |\n", min);
    if (strcmp(agg_func, "MAX") == 0) printf("| MAX   |\n|-------|\n| %-5.2f |\n", max);
}

/* ================= SELECT ================= */

void add_select_column(const char *name) {
    if (select_buffer_count >= MAX_COLS) return;
    strncpy(select_buffer[select_buffer_count], name, MAX_NAME);
    select_buffer_count++;
}

void reset_select_buffer(void) {
    select_buffer_count = 0;
}

/* Builds a projected table (chosen columns only) from a source table into `proj`.
   Caller must pass a `proj` pointer to storage that outlives this call
   (e.g. a static or heap-allocated Table) -- never a plain stack local,
   since Table is several megabytes and will overflow the default stack. */
static void build_projection(Table *src, Table *proj) {
    strncpy(proj->name, src->name, MAX_NAME);
    proj->col_count = select_buffer_count;
    proj->row_count = 0;

    int col_indices[MAX_COLS];
    for (int i = 0; i < select_buffer_count; i++) {
        int idx = get_col_index(src, select_buffer[i]);
        if (idx == -1) {
            fprintf(stderr, "Error: column '%s' does not exist.\n", select_buffer[i]);
            fflush(stderr);
            proj->col_count = 0;
            return;
        }
        col_indices[i] = idx;
        proj->columns[i] = src->columns[idx];
    }

    for (int r = 0; r < src->row_count; r++) {
        for (int c = 0; c < select_buffer_count; c++) {
            strncpy(proj->rows[r].values[c], src->rows[r].values[col_indices[c]], MAX_VAL);
        }
    }
    proj->row_count = src->row_count;
}

void execute_select(const char *table_name) {
    Table *t = load_table(table_name);
    if (!t) return;

    if (subquery_mode && !is_agg) {
        if (t->row_count > 0) {
            strncpy(subquery_val, t->rows[0].values[0], MAX_VAL);
        } else {
            strncpy(subquery_val, "0", MAX_VAL);
        }
        free_table(t);
        return;
    }

    /* Case 1: SELECT * FROM table */
    if (select_buffer_count == 1 && strcmp(select_buffer[0], "*") == 0) {
        if (is_agg) apply_aggregate(t);
        else print_table(t);
        free_table(t);
        return;
    }

    /* Case 2: SELECT specific columns */
    static Table proj;
    build_projection(t, &proj);
    if (proj.col_count > 0) {
        if (is_agg) apply_aggregate(&proj);
        else print_table(&proj);
    }
    free_table(t);
}

/* ================= WHERE condition (Member 2) ================= */
static char cond_column[MAX_NAME];
static char cond_op[4];
static char cond_value[MAX_VAL];
static int has_condition = 0;

void set_condition(const char *column, const char *op, const char *value) {
    strncpy(cond_column, column, MAX_NAME);
    strncpy(cond_op, op, sizeof(cond_op) - 1);
    cond_op[sizeof(cond_op) - 1] = '\0';
    strncpy(cond_value, value, MAX_VAL);
    has_condition = 1;
}

void reset_condition_buffer(void) {
    cond_column[0] = '\0';
    cond_op[0] = '\0';
    cond_value[0] = '\0';
    has_condition = 0;
}

/* Returns 1 if the row satisfies the currently stored condition. */
static int row_matches(Table *t, Row *row) {
    if (!has_condition) return 1;

    int idx = get_col_index(t, cond_column);
    if (idx == -1) {
        fprintf(stderr, "Error: column '%s' does not exist.\n", cond_column);
        fflush(stderr);
        return 0;
    }

    int is_numeric = (strcmp(t->columns[idx].type, "INT") == 0 ||
                       strcmp(t->columns[idx].type, "FLOAT") == 0);

    if (is_numeric) {
        double cell = atof(row->values[idx]);
        double target = atof(cond_value);
        if (strcmp(cond_op, "=")  == 0) return cell == target;
        if (strcmp(cond_op, ">")  == 0) return cell >  target;
        if (strcmp(cond_op, "<")  == 0) return cell <  target;
        if (strcmp(cond_op, ">=") == 0) return cell >= target;
        if (strcmp(cond_op, "<=") == 0) return cell <= target;
        if (strcmp(cond_op, "!=") == 0) return cell != target;
        return 0;
    } else {
        int eq = (strcmp(row->values[idx], cond_value) == 0);
        if (strcmp(cond_op, "=")  == 0) return eq;
        if (strcmp(cond_op, "!=") == 0) return !eq;
        fprintf(stderr, "Error: operator '%s' is not supported on text columns.\n", cond_op);
        fflush(stderr);
        return 0;
    }
}

void execute_select_where(const char *table_name) {
    Table *t = load_table(table_name);
    if (!t) return;

    int select_all = (select_buffer_count == 1 && strcmp(select_buffer[0], "*") == 0);

    /* static: avoids the stack-overflow bug Member 1 hit (Table is ~5MB). */
    static Table filtered;
    strncpy(filtered.name, t->name, MAX_NAME);
    filtered.col_count = t->col_count;
    filtered.row_count = 0;
    for (int c = 0; c < t->col_count; c++) {
        filtered.columns[c] = t->columns[c];
    }

    for (int r = 0; r < t->row_count; r++) {
        if (row_matches(t, &t->rows[r])) {
            filtered.rows[filtered.row_count] = t->rows[r];
            filtered.row_count++;
        }
    }

    if (select_all) {
        if (is_agg) apply_aggregate(&filtered);
        else print_table(&filtered);
    } else {
        static Table proj;
        build_projection(&filtered, &proj);
        if (proj.col_count > 0) {
            if (is_agg) apply_aggregate(&proj);
            else print_table(&proj);
        }
    }

    free_table(t);
}
