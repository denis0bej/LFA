# Limbaje formale si automate (An 1 Sem. 2)
Pentru rularea acestor scripturi nu trebuie să instalezi librării suplimentare, folosesc doar librăriile standard Python.  
Fisierele atasate sunt rezultatul urmatoarelor teme:
### 1. - DFA si NFA -
  - Ambele abordate in fisierul [machine.py](machine.py).  
  - Fisierul de input este [machine.bd](machine.bd).
  - Reprezentarea grafica a NFA-ului din fisier:
>![Diagrama DFA/NFA](imagini/diag1.png)
  - Comanda de rulare este urmatoarea:
>  ```bash
>  python3 machine.py machine.bd  
### 2. - Joc in DFA/NFA -
  - Pentru joc am creat un script separat care accepta inputul *symbol cu symbol* pentru a fi mai distractiv, scriptul este [secvential_input.py](secvential_input.py).  
  - Fisierul de input este [castle_game.bd](castle_game.bd).
  - Actiunile posibile sunt:
    - n - mergi in nord
    - e - mergi in est
    - s - mergi in sud
    - w - mergi in vest
    - p - ridica cheie (pick up)
  - Reprezentarea grafica a jocului:
>![Diagrama abstracta - castle game](imagini/castle_game.png)
  - Reprezentarea de mai sus e o forma simplificata a diagramei adevarate intrucat fiecare camera are o forma **cu** si **fara** cheie pentru a simula camerele incuiate 
  - Comanda de rulare este urmatoarea:
>  ```bash
>  python3 secvential_input.py castle_game.bd
### 3. - PDA -
  - Abordata in fisierul [pda.py](pda.py).  
  - Fisierul de input este [pda.bd](pda.bd).
  - Acest pda verifica daca inputul este de forma { a<sup>n</sup>b<sup>m</sup> | n>0, m>0, n>m }
  - Comanda de rulare este urmatoarea:
>  ```bash
>  python3 pda.py pda.bd
### 4. - Masina Turing -
  - Abordata in fisierul [turing.py](turing.py).  
  - Fisierul de input este [turing.bd](turing.bd).
  - Aceasta masina turing verifica daca inputul este de forma { 0<sup>n</sup>1<sup>n</sup> | n>0 }
  - Comanda de rulare este urmatoarea:
>  ```bash
>  python3 turing.py turing.bd
