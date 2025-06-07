class TuringMachine:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.tape_alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.accept_states = set()
        self.reject_states = set()
        self.blank_symbol = '_'  # Simbolul gol pe banda
        
    def add_transition(self, from_state, read_symbol, to_state, write_symbol, direction):
        #Adauga o tranzitie: (stare_curenta, simbol_citit) -> (stare_noua, simbol_scris, directie)
        key = (from_state, read_symbol)
        self.transitions[key] = {
            'to_state': to_state,
            'write_symbol': write_symbol,
            'direction': direction
        }
    
    def simulate(self, input_string, max_steps=10000):
        #Simuleaza Masina Turing pe un sir de intrare

        # Initializeaza banda cu input-ul
        tape = list(input_string) if input_string else []
        
        # Adauga simboluri goale la inceput si sfarsit pentru extensibilitate
        tape = [self.blank_symbol] * 100 + tape + [self.blank_symbol] * 100
        head_position = 100  # Pozitia capului (incepe la inceputul input-ului)
        current_state = self.start_state
        steps = 0
        
        print(f"Configuratia initiala:")
        self._print_configuration(tape, head_position, current_state, steps)
        
        while steps < max_steps:
            # Verificam daca am ajuns intr-o stare finala
            if current_state in self.accept_states:
                print(f"\nACCEPTAT in starea {current_state} dupa {steps} pasi")
                return True
            
            if current_state in self.reject_states:
                print(f"\nRESPINS in starea {current_state} dupa {steps} pasi")
                return False
            
            # Citim simbolul de pe banda
            current_symbol = tape[head_position]
            
            # Cautam tranzitia corespunzatoare
            key = (current_state, current_symbol)
            if key not in self.transitions:
                print(f"\nRESPINS - Nu exista tranzitie pentru ({current_state}, {current_symbol}) dupa {steps} pasi")
                return False
            
            # Executam tranzitia
            transition = self.transitions[key]
            
            # Scriem noul simbol
            tape[head_position] = transition['write_symbol']
            
            # Mutam capul
            if transition['direction'].upper() == 'R' or transition['direction'] == '→':
                head_position += 1
            elif transition['direction'].upper() == 'L' or transition['direction'] == '←':
                head_position -= 1
            # Daca e 'S' sau 'STAY', capul ramane pe loc
            
            # Schimbam starea
            old_state = current_state
            current_state = transition['to_state']
            
            steps += 1
            
            # Afisam configuratia (doar primii cativa pasi pentru a nu inunda output-ul)
            if steps <= 10 or steps % 100 == 0:
                print(f"\nPasul {steps}: ({old_state}, {transition['write_symbol']}) -> ({current_state}, {transition['direction']})")
                self._print_configuration(tape, head_position, current_state, steps)
        
        print(f"\n TIMEOUT - Masina nu s-a oprit dupa {max_steps} pasi")
        return False
    
    def _print_configuration(self, tape, head_position, state, step):
        #Afiseaza configuratia curenta a masinii

        # Gasim limitele utile ale benzii (fara prea multe simboluri goale)
        start = max(0, head_position - 10)
        end = min(len(tape), head_position + 11)
        
        # Afisam banda
        tape_str = ''.join(tape[start:end])
        print(f"Banda: ...{tape_str}...")
        
        # Afisam pozitia capului
        pointer_pos = head_position - start
        pointer = ' ' * (pointer_pos + 10) + '^'  # +10 pentru "Banda: ..."
        print(f"       {pointer}")
        print(f"Starea: {state}")
    
    def get_final_tape_content(self, tape):
        #Extrage continutul util al benzii (fara simbolurile goale de la margini)

        # Gasim primul si ultimul simbol non-gol
        start = 0
        while start < len(tape) and tape[start] == self.blank_symbol:
            start += 1
        
        end = len(tape) - 1
        while end >= 0 and tape[end] == self.blank_symbol:
            end -= 1
        
        if start > end:
            return ""
        
        return ''.join(tape[start:end+1])

def parse_turing_file(filename):

    #Parseaza un fisier cu definirea Masinii Turing

    tm = TuringMachine()
    current_section = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                # Eliminam comentariile
                if '#' in line:
                    line = line[:line.index('#')]
                
                # Eliminam spatiile din fata si din spate
                line = line.strip()
                
                # Sarim liniile goale
                if not line:
                    continue
                
                # Verificam daca e o sectiune noua
                if line.startswith('$'):
                    current_section = line[1:].strip().lower()
                    continue
                
                # Procesam continutul sectiunii
                if current_section == 'states':
                    tm.states.add(line)
                
                elif current_section == 'alphabet':
                    tm.alphabet.add(line)
                
                elif current_section == 'tape_alphabet':
                    tm.tape_alphabet.add(line)
                
                elif current_section == 'start_state':
                    tm.start_state = line
                
                elif current_section == 'accept_states':
                    tm.accept_states.add(line)
                
                elif current_section == 'reject_states':
                    tm.reject_states.add(line)
                
                elif current_section == 'blank_symbol':
                    tm.blank_symbol = line
                
                elif current_section == 'transitions':
                    # Format: from_state > read_symbol > to_state,write_symbol,direction
                    parts = line.split('>')
                    if len(parts) != 3:
                        print(f"Eroare la linia {line_num}: format incorect pentru tranzitie")
                        continue
                    
                    from_state = parts[0].strip()
                    read_symbol = parts[1].strip()
                    end_parts = parts[2].strip().split(',')
                    
                    if len(end_parts) != 3:
                        print(f"Eroare la linia {line_num}: format incorect pentru tranzitie")
                        continue
                    
                    to_state = end_parts[0].strip()
                    write_symbol = end_parts[1].strip()
                    direction = end_parts[2].strip()
                    # Tratam simbolul gol
                    if read_symbol.lower() == 'blank' or read_symbol == '_':
                        read_symbol = tm.blank_symbol
                    if write_symbol.lower() == 'blank' or write_symbol == '_':
                        write_symbol = tm.blank_symbol
                    
                    tm.add_transition(from_state, read_symbol, to_state, write_symbol, direction)
    
    except FileNotFoundError:
        print(f"Fisierul {filename} nu a fost gasit!")
        return None
    except Exception as e:
        print(f"Eroare la citirea fisierului: {e}")
        return None
    
    return tm

def print_tm_info(tm):
#    Afiseaza informatiile despre Masina Turing
    print("=== Informatii Masina Turing ===")
    print(f"Stari: {tm.states}")
    print(f"Alfabet intrare: {tm.alphabet}")
    print(f"Alfabet banda: {tm.tape_alphabet}")
    print(f"Simbol gol: '{tm.blank_symbol}'")
    print(f"Stare initiala: {tm.start_state}")
    print(f"Stari acceptare: {tm.accept_states}")
    print(f"Stari respingere: {tm.reject_states}")
    print(f"Numarul de tranzitii: {len(tm.transitions)}")
    print("\nTranzitii:")
    for i, (key, transition) in enumerate(tm.transitions.items()):
        from_state, read_symbol = key
        read_sym = read_symbol if read_symbol != tm.blank_symbol else '_'
        write_sym = transition['write_symbol'] if transition['write_symbol'] != tm.blank_symbol else '_'
        print(f"  {i+1}. ({from_state}, {read_sym}) → ({transition['to_state']}, {write_sym}, {transition['direction']})")

def main():
    print("=== Simulator Masina Turing ===")
    
    # Citim fisierul
    filename = input("Introduceti numele fisierului cu Masina Turing: ").strip()
    
    tm = parse_turing_file(filename)
    if tm is None:
        return
    
    # Afisam informatiile despre MT
    print_tm_info(tm)
    
    # Verificam daca MT-ul e valid
    if not tm.start_state:
        print("Eroare: Nu s-a specificat starea initiala!")
        return
    
    if not tm.accept_states and not tm.reject_states:
        print("Eroare: Nu s-au specificat stari finale!")
        return
    
    print("\n" + "="*50)
    print("Testare siruri de intrare")
    print("(Introduceti 'quit' pentru a iesi)")
    print("="*50)
    
    while True:
        input_string = input("\nIntroduceti sirul de testat: ").strip()
        
        if input_string.lower() == 'quit':
            break
        
        # Setam numarul maxim de pasi
        try:
            max_steps = int(input("Numarul maxim de pasi (implicit 1000): ").strip() or "1000")
        except ValueError:
            max_steps = 1000
        
        print(f"\n{'='*60}")
        print(f"Simulare pentru sirul: '{input_string}'")
        print(f"{'='*60}")
        
        # Testam sirul
        result = tm.simulate(input_string, max_steps)
        
        print(f"\n{'='*60}")
        if result:
            print(f"Sirul '{input_string}' este ACCEPTAT")
        else:
            print(f"Sirul '{input_string}' este RESPINS")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()