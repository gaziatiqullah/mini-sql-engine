CC = gcc
CFLAGS = -Wall -g -Isrc

TARGET = sql_engine

all: $(TARGET)

$(TARGET): src/lex.yy.c src/parser.tab.c src/table.c src/executor.c src/main.c
	$(CC) $(CFLAGS) -o $(TARGET) src/lex.yy.c src/parser.tab.c src/table.c src/executor.c src/main.c

src/lex.yy.c: src/lexer.l src/parser.tab.h
	flex src/lexer.l
	mv lex.yy.c src/lex.yy.c

src/parser.tab.c src/parser.tab.h: src/parser.y
	bison -d -o src/parser.tab.c src/parser.y

clean:
	rm -f $(TARGET) src/lex.yy.c src/parser.tab.c src/parser.tab.h

.PHONY: all clean