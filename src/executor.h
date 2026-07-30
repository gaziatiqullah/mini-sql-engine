#ifndef EXECUTOR_H
#define EXECUTOR_H

#define MAX_BUFFER 50

/* Column buffer (used while parsing CREATE TABLE) */
void add_column_to_buffer(const char *name, const char *type);
void reset_column_buffer(void);

/* Value buffer (used while parsing INSERT) */
void add_value_to_buffer(const char *value);
void reset_value_buffer(void);

/* Select buffer (used while parsing SELECT column list) */
void add_select_column(const char *name);
void reset_select_buffer(void);

/* Statement execution, called once the parser has a full statement */
void execute_create_table(const char *table_name);
void execute_insert(const char *table_name);
void execute_select(const char *table_name);

/* Helper: removes the surrounding single quotes from a string literal */
char *strip_quotes(const char *s);

void set_condition(const char *column, const char *op, const char *value); 
void reset_condition_buffer(void); 
void execute_select_where(const char *table_name); 

void set_aggregate(const char *func, const char *col);
void reset_aggregate(void);
void apply_aggregate(Table *t);

#endif
