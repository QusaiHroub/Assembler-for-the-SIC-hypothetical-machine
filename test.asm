COPY       START     1000              COPY FILE FROM INPUT
FIRST      STL       RETADER           SAVE RETURN ADDRESS
CLOOP      LDA       LENGTH            TEST FOR EOF
           COMP      ZERO
           STL       =C'EOF'
           STL       =C'EOF'
           LDA       =C'EFF'
           LDA       =X'FAFA'
           JEQ       ENDFILE           EXIT IF EOF FOUND
           J         CLOOP             LOOP
           LTORG
ENDFILE    LDA       EOF               INSERT END OF FILE MARKER
           STA       BUFFER,X
           LDA       THREE
           STA       LENGTH
           RSUB                       RETURN TO CALLER
EOF        BYTE      =C'EOF'
THREE      WORD      3
ZERO       WORD      0
ZERO       WORD      0
RETADER    RESW      1
LENGTH     RESW      1
BUFFER     RESB      4096
. WELCOME
.HI
           END       FIRST