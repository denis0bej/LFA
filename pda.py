import sys

class PushdownAutomaton:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.stack_alphabet = set()
        self.transitions = []
        self.start_state = None
        self.accept_states = set()
        
    def add_transition(self, from_state, input_symbol, stack_top, to_state, stack_push):
        self.transitions.append({
            'from': from_state,
            'input': input_symbol,
            'stack_top': stack_top,
            'to': to_state,
            'stack_push': stack_push
        })
    
    def simulate(self, input_string):
        # Initial configuration: (state, position in string, stack)
        initial_config = (self.start_state, 0, ['$'])
        
        # Use BFS to explore configurations
        queue = [initial_config]
        visited = set()
        
        while queue:
            current_state, pos, stack = queue.pop(0)
            
            # Avoid infinite loops
            config_key = (current_state, pos, tuple(stack))
            if config_key in visited:
                continue
            visited.add(config_key)
            
            # Check if we reached end of string
            if pos == len(input_string):
                if current_state in self.accept_states:
                    return True
                input_symbol = ''
            else:
                input_symbol = input_string[pos]
            
            # Try all possible transitions
            for transition in self.transitions:
                if transition['from'] != current_state:
                    continue
                
                if transition['input'] != input_symbol and transition['input'] != '':
                    continue
                
                if not stack:
                    continue
                    
                if transition['stack_top'] != stack[-1] and transition['stack_top'] != '':
                    continue
                
                # Execute transition
                new_stack = stack.copy()
                
                if transition['stack_top'] != '':
                    new_stack.pop()
                
                if transition['stack_push'] != '':
                    for symbol in reversed(transition['stack_push']):
                        new_stack.append(symbol)
                
                new_pos = pos + (1 if transition['input'] != '' else 0)
                
                new_config = (transition['to'], new_pos, new_stack)
                queue.append(new_config)
        
        return False

def parse_pda_file(filename):
    pda = PushdownAutomaton()
    current_section = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                if '#' in line:
                    line = line[:line.index('#')]
                
                line = line.strip()
                
                if not line:
                    continue
                
                if line.startswith('$'):
                    current_section = line[1:].strip().lower()
                    continue
                
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
                    parts = line.split('>')
                    if len(parts) != 3:
                        print(f"Error at line {line_num}: incorrect transition format")
                        continue
                    
                    from_state = parts[0].strip()
                    middle = parts[1].strip().split(',')
                    end = parts[2].strip().split(',')
                    
                    if len(middle) != 2 or len(end) != 2:
                        print(f"Error at line {line_num}: incorrect transition format")
                        continue
                    
                    input_symbol = middle[0].strip()
                    stack_top = middle[1].strip()
                    to_state = end[0].strip()
                    stack_push = end[1].strip()
                    
                    if input_symbol.lower() == 'epsilon' or input_symbol == 'ε':
                        input_symbol = ''
                    if stack_top.lower() == 'epsilon' or stack_top == 'ε':
                        stack_top = ''
                    if stack_push.lower() == 'epsilon' or stack_push == 'ε':
                        stack_push = ''
                    
                    pda.add_transition(from_state, input_symbol, stack_top, to_state, stack_push)
    
    except FileNotFoundError:
        print(f"File {filename} not found!")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    return pda

def print_pda_info(pda):
    print("=== PDA Information ===")
    print(f"States: {pda.states}")
    print(f"Alphabet: {pda.alphabet}")
    print(f"Stack alphabet: {pda.stack_alphabet}")
    print(f"Start state: {pda.start_state}")
    print(f"Accept states: {pda.accept_states}")
    print(f"Number of transitions: {len(pda.transitions)}")
    print("\nTransitions:")
    for i, t in enumerate(pda.transitions):
        input_sym = t['input'] if t['input'] else 'ε'
        stack_top = t['stack_top'] if t['stack_top'] else 'ε'
        stack_push = t['stack_push'] if t['stack_push'] else 'ε'
        print(f"  {i+1}. ({t['from']}, {input_sym}, {stack_top}) → ({t['to']}, {stack_push})")

def main():
    if len(sys.argv) != 2:
        print("Usage: python automaton.py <input_file>")
        return
    
    filename = sys.argv[1]
    
    print("=== PDA Simulator ===")
    
    pda = parse_pda_file(filename)
    if pda is None:
        return
    
    print_pda_info(pda)
    
    if not pda.start_state:
        print("Error: No start state specified!")
        return
    
    if not pda.accept_states:
        print("Error: No accept states specified!")
        return
    
    print("\n" + "="*50)
    print("Testing input strings")
    print("(Enter 'quit' to exit)")
    print("="*50)
    
    while True:
        input_string = input("\nEnter string to test (no spaces, ex: aaabb): ").strip()
        
        if input_string.lower() == 'quit':
            break
        
        result = pda.simulate(input_string)
        
        if result:
            print(f"String '{input_string}' is ACCEPTED")
        else:
            print(f"String '{input_string}' is REJECTED")

if __name__ == "__main__":
    main()
