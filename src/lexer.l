%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.tab.h"
%}

%option noyywrap

%%

[ \r\t]+                        ; /* skip whitespace */
\n                             ; /* skip newline */

[Cc][Rr][Ee][Aa][Tt][Ee]      { return CREATE; }
[Tt][Aa][Bb][Ll][Ee]          { return TABLE; }
[Ii][Nn][Ss][Ee][Rr][Tt]      { return INSERT; }
[Ii][Nn][Tt][Oo]               { return INTO; }
[Vv][Aa][Ll][Uu][Ee][Ss]      { return VALUES; }
[Ss][Ee][Ll][Ee][Cc][Tt]      { return SELECT; }
[Ff][Rr][Oo][Mm]               { return FROM; }
[Ww][Hh][Ee][Rr][Ee]          { return WHERE; }

[Ii][Nn][Tt]                   { return INT_TYPE; }
[Vv][Aa][Rr][Cc][Hh][Aa][Rr]  { return VARCHAR_TYPE; }
[Ff][Ll][Oo][Aa][Tt]          { return FLOAT_TYPE; }

[0-9]+"."[0-9]+                { yylval.fval = atof(yytext); return FLOATNUM; }
[0-9]+                          { yylval.ival = atoi(yytext); return NUMBER; }

\'[^\']*\'                      { yylval.sval = strdup(yytext); return STRING; }

[a-zA-Z_][a-zA-Z0-9_]*         { yylval.sval = strdup(yytext); return IDENTIFIER; }

","                              { return COMMA; }
"("                              { return LPAREN; }
")"                              { return RPAREN; }
"*"                              { return STAR; }
";"                              { return SEMICOLON; }
"="                              { return EQ; }
">="                             { return GE; } 
"<="                             { return LE; } 
"!="                             { return NE; }
">"                              { return GT; }
"<"                              { return LT; }

.                                { fprintf(stderr, "Unknown character: %s\n", yytext); }

%%