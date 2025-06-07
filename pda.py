class PushdownAutomaton:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.stack_alphabet = set()
        self.transitions = []
        self.start_state = None
        self.accept_states = set()
        
    def add_transition(self, from_state, input_symbol, stack_top, to_state, stack_push):
        """
        Adaugă o tranziție: (stare_curentă, simbol_input, vârf_stivă) -> (stare_nouă, simboluri_de_pus)
        """
        self.transitions.append({
            'from': from_state,
            'input': input_symbol,
            'stack_top': stack_top,
            'to': to_state,
            'stack_push': stack_push
        })
    
    def simulate(self, input_string):
        """
        Simulează PDA-ul pe un șir de intrare
        """
        # Configurația inițială: (stare, poziția în șir, stiva)
        initial_config = (self.start_state, 0, ['$'])  # $ este marcatorul de fund al stivei
        
        # Folosim o coadă pentru BFS (explorare în lățime)
        queue = [initial_config]
        visited = set()
        
        while queue:
            current_state, pos, stack = queue.pop(0)
            
            # Evităm configurațiile deja vizitate pentru a preveni ciclurile infinite
            config_key = (current_state, pos, tuple(stack))
            if config_key in visited:
                continue
            visited.add(config_key)
            
            # Verificăm dacă am ajuns la sfârșitul șirului
            if pos == len(input_string):
                # Acceptăm dacă suntem în stare finală
                if current_state in self.accept_states:
                    return True
                # Continuăm cu tranziții epsilon
                input_symbol = ''
            else:
                input_symbol = input_string[pos]
            
            # Încercăm toate tranzițiile posibile
            for transition in self.transitions:
                if transition['from'] != current_state:
                    continue
                
                # Verificăm simbolul de intrare
                if transition['input'] != input_symbol and transition['input'] != '':
                    continue
                
                # Verificăm vârful stivei
                if not stack:
                    continue
                    
                if transition['stack_top'] != stack[-1] and transition['stack_top'] != '':
                    continue
                
                # Executăm tranziția
                new_stack = stack.copy()
                
                # Scoatem simbolul din vârful stivei (dacă nu e epsilon)
                if transition['stack_top'] != '':
                    new_stack.pop()
                
                # Adăugăm simbolurile noi în stivă (dacă nu e epsilon)
                if transition['stack_push'] != '':
                    # Adăugăm în ordine inversă pentru că stiva e LIFO
                    for symbol in reversed(transition['stack_push']):
                        new_stack.append(symbol)
                
                # Calculăm noua poziție
                new_pos = pos + (1 if transition['input'] != '' else 0)
                
                # Adăugăm noua configurație în coadă
                new_config = (transition['to'], new_pos, new_stack)
                queue.append(new_config)
        
        return False

def parse_pda_file(filename):
    """
    Parsează un fișier cu definirea PDA-ului
    """
    pda = PushdownAutomaton()
    current_section = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                # Eliminăm comentariile
                if '#' in line:
                    line = line[:line.index('#')]
                
                # Eliminăm spațiile din față și din spate
                line = line.strip()
                
                # Sărim liniile goale
                if not line:
                    continue
                
                # Verificăm dacă e o secțiune nouă
                if line.startswith('$'):
                    current_section = line[1:].strip().lower()
                    continue
                
                # Procesăm conținutul secțiunii
                if current_section == 'states':
                    pda.states.add(line)
                
                elif current_section == 'alphabet':
                    pda.alphabet.add(line)
                
                elif current_section == 'stack_alphabet':
                    pda.stack_alphabet.add(line)
                
                elif current_section == 'start_state':
                    pda.start_state = line
                
                elif current_section == 'accept_states':
                    pda.accept_states.add(line)
                
                elif current_section == 'transitions':
                    # Format: from_state > input_symbol,stack_top > to_state,stack_push
                    parts = line.split('>')
                    if len(parts) != 3:
                        print(f"Eroare la linia {line_num}: format incorect pentru tranzitie")
                        continue
                    
                    from_state = parts[0].strip()
                    middle = parts[1].strip().split(',')
                    end = parts[2].strip().split(',')
                    
                    if len(middle) != 2 or len(end) != 2:
                        print(f"Eroare la linia {line_num}: format incorect pentru tranzitie")
                        continue
                    
                    input_symbol = middle[0].strip()
                    stack_top = middle[1].strip()
                    to_state = end[0].strip()
                    stack_push = end[1].strip()
                    
                    # Tratăm epsilon ca șir gol
                    if input_symbol.lower() == 'epsilon' or input_symbol == 'ε':
                        input_symbol = ''
                    if stack_top.lower() == 'epsilon' or stack_top == 'ε':
                        stack_top = ''
                    if stack_push.lower() == 'epsilon' or stack_push == 'ε':
                        stack_push = ''
                    
                    pda.add_transition(from_state, input_symbol, stack_top, to_state, stack_push)
    
    except FileNotFoundError:
        print(f"Fisierul {filename} nu a fost gasit!")
        return None
    except Exception as e:
        print(f"Eroare la citirea fisierului: {e}")
        return None
    
    return pda

def print_pda_info(pda):
    """
    Afiseaza informatiile despre PDA
    """
    print("=== Informatii PDA ===")
    print(f"Stari: {pda.states}")
    print(f"Alfabet: {pda.alphabet}")
    print(f"Alfabet stiva: {pda.stack_alphabet}")
    print(f"Stare initiala: {pda.start_state}")
    print(f"Stari de acceptare: {pda.accept_states}")
    print(f"Numarul de tranzitii: {len(pda.transitions)}")
    print("\nTranzitii:")
    for i, t in enumerate(pda.transitions):
        input_sym = t['input'] if t['input'] else 'ε'
        stack_top = t['stack_top'] if t['stack_top'] else 'ε'
        stack_push = t['stack_push'] if t['stack_push'] else 'ε'
        print(f"  {i+1}. ({t['from']}, {input_sym}, {stack_top}) → ({t['to']}, {stack_push})")

def main():
    print("=== Simulator PDA ===")
    
    # Citim fișierul
    filename = input("Introduceti numele fisierului cu PDA-ul: ").strip()
    
    pda = parse_pda_file(filename)
    if pda is None:
        return
    
    # Afișăm informațiile despre PDA
    print_pda_info(pda)
    
    # Verificăm dacă PDA-ul e valid
    if not pda.start_state:
        print("Eroare: Nu s-a specificat starea initiala!")
        return
    
    if not pda.accept_states:
        print("Eroare: Nu s-au specificat stari de acceptare!")
        return
    
    print("\n" + "="*50)
    print("Testare siruri de intrare")
    print("(Introduceti 'quit' pentru a iesi)")
    print("="*50)
    
    while True:
        input_string = input("\nIntroduceti sirul de testat(fara spatii, ex: aaabb): ").strip()
        
        if input_string.lower() == 'quit':
            break
        
        # Testăm șirul
        result = pda.simulate(input_string)
        
        if result:
            print(f"Sirul '{input_string}' este ACCEPTAT")
        else:
            print(f"Sirul '{input_string}' este RESPINS")

if __name__ == "__main__":
    main()