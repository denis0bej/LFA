import sys
from collections import deque

class FiniteAutomaton:
    def __init__(self):
        self.states = set()
        self.symbols = set()
        self.transitions = dict()  # (state, symbol) -> set of states
        self.epsilon_transitions = dict()  # state -> set of states
        self.start_state = None
        self.accept_states = set()
        self.type = "DFA"

    def load_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            return f"[ERROR] File '{file_path}' not found"

        sections = self._parse_sections(content)
        
        required_sections = {'States', 'Symbols', 'Rules', 'Start', 'Accept'}
        missing = required_sections - sections.keys()
        if missing:
            return f"[ERROR] Missing sections: {', '.join(missing)}"

        self.states = set(sections['States'])
        if not self.states:
            return "[ERROR] No states defined"

        self.symbols = set(sections['Symbols'])
        if not self.symbols:
            return "[ERROR] No symbols defined"

        if len(sections['Start']) != 1:
            return "[ERROR] Exactly one start state required"
        self.start_state = sections['Start'][0]
        if self.start_state not in self.states:
            return f"[ERROR] Start state '{self.start_state}' not in states"

        self.accept_states = set(sections['Accept'])
        if not self.accept_states:
            return "[ERROR] No accept states defined"
        invalid_accept = self.accept_states - self.states
        if invalid_accept:
            return f"[ERROR] Accept states not in states: {', '.join(invalid_accept)}"

        self._process_transitions(sections['Rules'])
        
        # Process additional epsilon rules if they exist
        if 'EpsilonRules' in sections:
            self._process_epsilon_transitions(sections['EpsilonRules'])
            self.type = "NFA"
        
        return None

    def _parse_sections(self, content):
        sections = {}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('$'):
                current_section = line[1:]
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        return sections

    def _process_transitions(self, rules):
        for rule in rules:
            parts = [p.strip() for p in rule.split('>')]
            if len(parts) != 3:
                continue
            
            from_state, symbol, to_state = parts
            
            if from_state not in self.states or to_state not in self.states:
                continue
            
            # Handle epsilon transitions
            if symbol == 'ε':
                if from_state not in self.epsilon_transitions:
                    self.epsilon_transitions[from_state] = set()
                self.epsilon_transitions[from_state].add(to_state)
                self.type = "NFA"  # Mark as NFA if epsilon transitions exist
            else:
                # Handle regular transitions
                if symbol not in self.symbols:
                    continue
                    
                key = (from_state, symbol)
                if key not in self.transitions:
                    self.transitions[key] = set()
                self.transitions[key].add(to_state)

    def _process_epsilon_transitions(self, epsilon_rules):
        for rule in epsilon_rules:
            parts = [p.strip() for p in rule.split('>')]
            if len(parts) != 2:
                continue
            
            from_state, to_state = parts
            if from_state not in self.states or to_state not in self.states:
                continue
            
            if from_state not in self.epsilon_transitions:
                self.epsilon_transitions[from_state] = set()
            self.epsilon_transitions[from_state].add(to_state)

    def _epsilon_closure(self, states):
        closure = set(states)
        queue = deque(states)
        
        while queue:
            state = queue.popleft()
            
            if state in self.epsilon_transitions:
                for next_state in self.epsilon_transitions[state]:
                    if next_state not in closure:
                        closure.add(next_state)
                        queue.append(next_state)
        
        return closure

    def get_possible_transitions(self, current_states, symbol):
        """Get all possible next states for given symbol from current states"""
        next_states = set()
        
        for state in current_states:
            key = (state, symbol)
            if key in self.transitions:
                next_states.update(self.transitions[key])
        
        return self._epsilon_closure(next_states) if next_states else set()

    def get_available_symbols(self, current_states):
        """Get all symbols that have transitions from current states"""
        available = set()
        
        for state in current_states:
            for (from_state, symbol), _ in self.transitions.items():
                if from_state == state:
                    available.add(symbol)
        
        return available

    def interactive_simulation(self):
        """Run interactive step-by-step simulation"""
        print(f"\n=== Interactive {self.type} Simulation ===")
        print("Enter symbols one by one, or special commands:")
        print("  'reset' - restart from beginning")
        print("  'status' - show current status")
        print("  'help' - show available symbols")
        print("  'quit' - exit simulation")
        print("-" * 50)
        
        # Initialize current states
        if self.type == "DFA":
            current_states = {self.start_state}
        else:
            current_states = self._epsilon_closure({self.start_state})
        
        input_so_far = []
        
        self._show_status(current_states, input_so_far)
        
        while True:
            print(f"\nEnter next symbol:")
            user_input = input(">>> ").strip()
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'reset':
                if self.type == "DFA":
                    current_states = {self.start_state}
                else:
                    current_states = self._epsilon_closure({self.start_state})
                input_so_far = []
                print("\nReset to initial state")
                self._show_status(current_states, input_so_far)
                continue
            elif user_input.lower() == 'status':
                self._show_status(current_states, input_so_far)
                continue
            elif user_input.lower() == 'help':
                self._show_help(current_states)
                continue
            
            # Process the symbol
            if len(user_input) != 1:
                print("Please enter exactly one symbol")
                continue
            
            symbol = user_input
            
            # Check if symbol is valid
            if symbol not in self.symbols:
                print(f"Invalid symbol '{symbol}'. Valid symbols: {sorted(self.symbols)}")
                continue
            
            # Get next states
            next_states = self.get_possible_transitions(current_states, symbol)
            
            if not next_states:
                print(f"No transitions available from current state(s) on symbol '{symbol}'")
                print("Automaton is stuck - string would be REJECTED")
                print("Use 'reset' to start over")
                continue
            
            # Update state
            current_states = next_states
            input_so_far.append(symbol)
            
            print(f"Processed symbol '{symbol}'")
            
            # Check if we reached an accepting state
            accepting_states = current_states & self.accept_states
            if accepting_states:
                print(f"\nACCEPTED - Reached accepting state(s): {sorted(accepting_states)}")
                print(f"Final input: {''.join(input_so_far)}\n")
                sys.exit(0)
            
            
            self._show_status(current_states, input_so_far)

    def _show_status(self, current_states, input_so_far):
        """Show current automaton status"""
        print("\n" + "="*50)
        print(f"CURRENT STATUS:")
        print(f"   Input so far: {''.join(input_so_far) if input_so_far else '(empty)'}")
        print(f"   Current state(s): {sorted(current_states)}")
        print(f"   Not in accepting state")
        
        # Show transitions for each symbol
        print(f"   Possible transitions:")
        for symbol in sorted(self.symbols):
            next_states = self.get_possible_transitions(current_states, symbol)
            if next_states:
                accepting_next = next_states & self.accept_states
                if accepting_next:
                    print(f"     '{symbol}' -> {sorted(next_states)} (accepting: {sorted(accepting_next)})")
                else:
                    print(f"     '{symbol}' -> {sorted(next_states)}")
        
        print("="*50)

    def _show_help(self, current_states):
        """Show detailed help about available transitions"""
        print("\nAVAILABLE TRANSITIONS:")
        
        for symbol in sorted(self.symbols):
            next_states = self.get_possible_transitions(current_states, symbol)
            if next_states:
                print(f"   '{symbol}' -> {sorted(next_states)}")
                accepting_next = next_states & self.accept_states
                if accepting_next:
                    print(f"       (would reach accepting state(s): {sorted(accepting_next)})")

def main():
    if len(sys.argv) != 2:
        print("Usage: python automaton.py <input_file>")
        return
    
    automaton = FiniteAutomaton()
    error = automaton.load_from_file(sys.argv[1])
    
    if error:
        print(error)
        return
    
    print(f"Loaded {automaton.type} with:")
    print(f"- States: {', '.join(sorted(automaton.states))}")
    print(f"- Symbols: {', '.join(sorted(automaton.symbols))}")
    print(f"- Start state: {automaton.start_state}")
    print(f"- Accept states: {', '.join(sorted(automaton.accept_states))}")
    
    # Start interactive simulation
    automaton.interactive_simulation()

if __name__ == "__main__":
    main()
