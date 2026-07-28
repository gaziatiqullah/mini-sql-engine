#include <stdio.h>
#include <string.h>
#include "table.h"

/* Bison-generated parser entry point */
extern int yyparse(void);

/* Flex-generated buffer functions — used to parse one line at a time */
typedef struct yy_buffer_state *YY_BUFFER_STATE;
extern YY_BUFFER_STATE yy_scan_string(const char *yystr);
extern void yy_delete_buffer(YY_BUFFER_STATE b);

int main() {
    char input[1024];

    printf("Mini SQL Engine (type 'exit;' to quit)\n");

    while (1) {
        printf("sql> ");
        if (!fgets(input, sizeof(input), stdin)) break;   /* Ctrl+D / EOF */

        input[strcspn(input, "\n")] = '\0';   /* strip trailing newline */

        if (strlen(input) == 0) continue;
        if (strcmp(input, "exit;") == 0 || strcmp(input, "exit") == 0) break;

        YY_BUFFER_STATE buf = yy_scan_string(input);
        yyparse();
        yy_delete_buffer(buf);
    }

    printf("Goodbye!\n");
    return 0;
}