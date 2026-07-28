%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "table.h"
#include "executor.h"

int yylex(void);
void yyerror(const char *s);
%}

%union {
    int   ival;
    float fval;
    char *sval;
}

%token CREATE TABLE INSERT INTO VALUES SELECT FROM WHERE
%token INT_TYPE VARCHAR_TYPE FLOAT_TYPE
%token COMMA LPAREN RPAREN STAR SEMICOLON EQ GT LT
%token <ival> NUMBER
%token <fval> FLOATNUM
%token <sval> IDENTIFIER STRING

%type <sval> data_type

%%

statement:
      create_stmt
    | insert_stmt
    | select_stmt
    ;

/* ── CREATE TABLE ── */
create_stmt:
    CREATE TABLE IDENTIFIER LPAREN column_def_list RPAREN SEMICOLON
    {
        execute_create_table($3);
        reset_column_buffer();
        free($3);
    }
    ;

column_def_list:
      column_def
    | column_def_list COMMA column_def
    ;

column_def:
    IDENTIFIER data_type
    {
        add_column_to_buffer($1, $2);
        free($1);
        free($2);
    }
    ;

data_type:
      INT_TYPE      { $$ = strdup("INT"); }
    | VARCHAR_TYPE   { $$ = strdup("VARCHAR"); }
    | FLOAT_TYPE     { $$ = strdup("FLOAT"); }
    ;

/* ── INSERT INTO ── */
insert_stmt:
    INSERT INTO IDENTIFIER VALUES LPAREN value_list RPAREN SEMICOLON
    {
        execute_insert($3);
        reset_value_buffer();
        free($3);
    }
    ;

value_list:
      value
    | value_list COMMA value
    ;

value:
      NUMBER
      {
          char buf[64];
          sprintf(buf, "%d", $1);
          add_value_to_buffer(buf);
      }
    | FLOATNUM
      {
          char buf[64];
          sprintf(buf, "%f", $1);
          add_value_to_buffer(buf);
      }
    | STRING
      {
          char *clean = strip_quotes($1);
          add_value_to_buffer(clean);
          free(clean);
          free($1);
      }
    ;

/* ── SELECT ── */
select_stmt:
    SELECT select_list FROM IDENTIFIER SEMICOLON
    {
        execute_select($4);
        reset_select_buffer();
        free($4);
    }
    ;

select_list:
      STAR
      {
          add_select_column("*");
      }
    | IDENTIFIER
      {
          add_select_column($1);
          free($1);
      }
    | select_list COMMA IDENTIFIER
      {
          add_select_column($3);
          free($3);
      }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Syntax error: %s\n", s);
}