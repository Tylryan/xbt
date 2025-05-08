// X Build Tool


lexer grammar XbtLexer;

RULE : 'rule';

STRING : '"' .*? '"' ;

LBRACE : '{';
RBRACE : '}';
LPAR   : '(';
RPAR   : ')';
EQUAL  : '=';
SEMI   : ';';
COMMA  : ',';
BANG_CARROT: '$^';

ML_COMMENT : '/*' .*? '*/' ;
SHELL      : '$'.*? '\n' ;
IDENT      : [a-zA-Z_\-/.]+ [/a-zA-Z_\-!?.]*;

WS         : [ \t\r] -> skip ;
NEW_LINE   : '\n';
