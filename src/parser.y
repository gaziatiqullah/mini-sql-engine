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
    int ival;
    float fval;
    char *sval;
}

%token CREATE TABLE INSERT INTO VALUES SELECT FROM WHERE
%token INT_TYPE VARCHAR_TYPE FLOAT_TYPE
%token STAR COMMA SEMICOLON LPAREN RPAREN
%token EQ GT LT GE LE NE
%token COUNT SUM AVG MIN MAX
%token <sval> IDENTIFIER STRING
%token <ival> NUMBER
%token <fval> FLOATNUM

%type <sval> value type_name

%%

statement:
      create_stmt
    | insert_stmt
    | select_stmt
    ;

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
    IDENTIFIER type_name
    {
        add_column_to_buffer($1, $2);
        free($1);
        free($2);
    }
    ;

type_name:
      INT_TYPE      { $$ = strdup("INT"); }
    | VARCHAR_TYPE   { $$ = strdup("VARCHAR"); }
    | FLOAT_TYPE     { $$ = strdup("FLOAT"); }
    ;

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
      {
          add_value_to_buffer($1);
          free($1);
      }
    | value_list COMMA value
      {
          add_value_to_buffer($3);
          free($3);
      }
    ;

value:
      NUMBER
      {
          char buf[32];
          snprintf(buf, sizeof(buf), "%d", $1);
          $$ = strdup(buf);
      }
    | FLOATNUM
      {
          char buf[32];
          snprintf(buf, sizeof(buf), "%g", $1);
          $$ = strdup(buf);
      }
    | STRING
      {
          char *clean = strip_quotes($1);
          $$ = clean;
          free($1);
      }
    ;

select_stmt:
      SELECT select_list FROM IDENTIFIER SEMICOLON
      {
          execute_select($4);
          reset_select_buffer();
          free($4);
      }
    | SELECT select_list FROM IDENTIFIER WHERE condition SEMICOLON
      {
          execute_select_where($4);
          reset_select_buffer();
          reset_condition_buffer();
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

/* --- Member 3: Aggregate Functions --- */
| COUNT LPAREN STAR RPAREN
      {
          add_select_column("*");  
          set_aggregate("COUNT", "*");
      }
    | SUM LPAREN IDENTIFIER RPAREN
      {
          add_select_column($3);   
          set_aggregate("SUM", $3);
          free($3);
      }
    | AVG LPAREN IDENTIFIER RPAREN
      {
          add_select_column($3);   
          set_aggregate("AVG", $3);
          free($3);
      }
    | MIN LPAREN IDENTIFIER RPAREN
      {
          add_select_column($3);  
          set_aggregate("MIN", $3);
          free($3);
      }
    | MAX LPAREN IDENTIFIER RPAREN
      {
          add_select_column($3);   
          set_aggregate("MAX", $3);
          free($3);
      }
;


condition:
      IDENTIFIER EQ value  { set_condition($1, "=",  $3); free($1); free($3); }
    | IDENTIFIER GT value  { set_condition($1, ">",  $3); free($1); free($3); }
    | IDENTIFIER LT value  { set_condition($1, "<",  $3); free($1); free($3); }
    | IDENTIFIER GE value  { set_condition($1, ">=", $3); free($1); free($3); }
    | IDENTIFIER LE value  { set_condition($1, "<=", $3); free($1); free($3); }
    | IDENTIFIER NE value  { set_condition($1, "!=", $3); free($1); free($3); }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Syntax error: %s\n", s);
    fflush(stderr);
}
