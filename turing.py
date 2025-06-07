import sys

class TuringMachine:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.tape_alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.accept_states = set()
        self.reject_states = set()
        self.blank_symbol = '_'  # Blank symbol on tape
        
    def add_transition(self, from_state, read_symbol, to_state, write_symbol, direction):
        # Add a transition: (current_state, read_symbol) -> (new_state, written_symbol, direction)
        key = (from_state, read_symbol)
        self.transitions[key] = {
            'to_state': to_state,
            'write_symbol': write_symbol,
            'direction': direction
        }
    
    def simulate(self, input_string, max_steps=10000):
        # Simulate Turing Machine on an input string

        # Initialize tape with input
        tape = list(input_string) if input_string else []
        
        # Add blank symbols at beginning and end for extensibility
        tape = [self.blank_symbol] * 100 + tape + [self.blank_symbol] * 100
        head_position = 100  # Head position (starts at beginning of input)
        current_state = self.start_state
        steps = 0
        
        print(f"Initial configuration:")
        self._print_configuration(tape, head_position, current_state, steps)
        
        while steps < max_steps:
            # Check if we reached a final state
            if current_state in self.accept_states:
                print(f"\nACCEPTED in state {current_state} after {steps} steps")
                return True
            
            if current_state in self.reject_states:
                print(f"\nREJECTED in state {current_state} after {steps} steps")
                return False
            
            # Read symbol from tape
            current_symbol = tape[head_position]
            
            # Look for corresponding transition
            key = (current_state, current_symbol)
            if key not in self.transitions:
                print(f"\nREJECTED - No transition for ({current_state}, {current_symbol}) after {steps} steps")
                return False
            
            # Execute transition
            transition = self.transitions[key]
            
            # Write new symbol
            tape[head_position] = transition['write_symbol']
            
            # Move head
            if transition['direction'].upper() == 'R' or transition['direction'] == '→':
                head_position += 1
            elif transition['direction'].upper() == 'L' or transition['direction'] == '←':
                head_position -= 1
            # If it's 'S' or 'STAY', head stays in place
            
            # Change state
            old_state = current_state
            current_state = transition['to_state']
            
            steps += 1
            
            # Display configuration (only first few steps to avoid flooding output)
            if steps <= 10 or steps % 100 == 0:
                print(f"\nStep {steps}: ({old_state}, {transition['write_symbol']}) -> ({current_state}, {transition['direction']})")
                self._print_configuration(tape, head_position, current_state, steps)
        
        print(f"\nTIMEOUT - Machine did not stop after {max_steps} steps")
        return False
    
    def _print_configuration(self, tape, head_position, state, step):
        # Display current machine configuration

        # Find useful tape boundaries (without too many blank symbols)
        start = max(0, head_position - 10)
        end = min(len(tape), head_position + 11)
        
        # Display tape
        tape_str = ''.join(tape[start:end])
        print(f"Tape: ...{tape_str}...")
        
        # Display head position
        pointer_pos = head_position - start
        pointer = ' ' * (pointer_pos + 10) + '^'  # +10 for "Tape: ..."
        print(f"       {pointer}")
        print(f"State: {state}")
    
    def get_final_tape_content(self, tape):
        # Extract useful tape content (without blank symbols at edges)

        # Find first and last non-blank symbol
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
    # Parse a file with Turing Machine definition

    tm = TuringMachine()
    current_section = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                # Remove comments
                if '#' in line:
                    line = line[:line.index('#')]
                
                # Remove leading and trailing spaces
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check if it's a new section
                if line.startswith('$'):
                    current_section = line[1:].strip().lower()
                    continue
                
                # Process section content
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
                        print(f"Error at line {line_num}: incorrect format for transition")
                        continue
                    
                    from_state = parts[0].strip()
                    read_symbol = parts[1].strip()
                    end_parts = parts[2].strip().split(',')
                    
                    if len(end_parts) != 3:
                        print(f"Error at line {line_num}: incorrect format for transition")
                        continue
                    
                    to_state = end_parts[0].strip()
                    write_symbol = end_parts[1].strip()
                    direction = end_parts[2].strip()
                    
                    # Handle blank symbol
                    if read_symbol.lower() == 'blank' or read_symbol == '_':
                        read_symbol = tm.blank_symbol
                    if write_symbol.lower() == 'blank' or write_symbol == '_':
                        write_symbol = tm.blank_symbol
                    
                    tm.add_transition(from_state, read_symbol, to_state, write_symbol, direction)
    
    except FileNotFoundError:
        print(f"File {filename} not found!")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    return tm

def print_tm_info(tm):
    # Display Turing Machine information
    print("=== Turing Machine Information ===")
    print(f"States: {tm.states}")
    print(f"Input alphabet: {tm.alphabet}")
    print(f"Tape alphabet: {tm.tape_alphabet}")
    print(f"Blank symbol: '{tm.blank_symbol}'")
    print(f"Start state: {tm.start_state}")
    print(f"Accept states: {tm.accept_states}")
    print(f"Reject states: {tm.reject_states}")
    print(f"Number of transitions: {len(tm.transitions)}")
    print("\nTransitions:")
    for i, (key, transition) in enumerate(tm.transitions.items()):
        from_state, read_symbol = key
        read_sym = read_symbol if read_symbol != tm.blank_symbol else '_'
        write_sym = transition['write_symbol'] if transition['write_symbol'] != tm.blank_symbol else '_'
        print(f"  {i+1}. ({from_state}, {read_sym}) → ({transition['to_state']}, {write_sym}, {transition['direction']})")

def main():
    print("=== Turing Machine Simulator ===")
    
    # Check if filename was provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python turing.py <filename>")
        return
    
    filename = sys.argv[1]
    
    tm = parse_turing_file(filename)
    if tm is None:
        return
    
    # Display TM information
    print_tm_info(tm)
    
    # Check if TM is valid
    if not tm.start_state:
        print("Error: Start state not specified!")
        return
    
    if not tm.accept_states and not tm.reject_states:
        print("Error: No final states specified!")
        return
    
    print("\n" + "="*50)
    print("Testing input strings")
    print("(Enter 'quit' to exit)")
    print("="*50)
    
    while True:
        input_string = input("\nEnter string to test (no spaces ex:0011): ").strip()
        
        if input_string.lower() == 'quit':
            break
        
        # Set maximum number of steps
        try:
            max_steps = int(input("Maximum number of steps (default 1000): ").strip() or "1000")
        except ValueError:
            max_steps = 1000
        
        print(f"\n{'='*60}")
        print(f"Simulation for string: '{input_string}'")
        print(f"{'='*60}")
        
        # Test the string
        result = tm.simulate(input_string, max_steps)
        
        print(f"\n{'='*60}")
        if result:
            print(f"String '{input_string}' is ACCEPTED")
        else:
            print(f"String '{input_string}' is REJECTED")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
