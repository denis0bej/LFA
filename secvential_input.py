import sys
from collections import deque

class FiniteAutomaton:
    def __init__(self):
        self.states = set()
        self.symbols = set()
        self.transitions = dict()
        self.epsilon_transitions = dict()
        self.start_state = None
        self.accept_states = set()
        self.type = "DFA"
        self.current_states = set()

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
        
        if 'EpsilonRules' in sections:
            self._process_epsilon_transitions(sections['EpsilonRules'])
            self.type = "NFA"
        
        self.reset()
        return None

    def reset(self):
        """Reset the automaton to initial state"""
        if self.type == "DFA":
            self.current_state = self.start_state
        else:
            self.current_states = self._epsilon_closure({self.start_state})

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
            
            if (from_state not in self.states or 
                to_state not in self.states or 
                (symbol != 'ε' and symbol not in self.symbols)):
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

    def get_possible_transitions(self):
        """Return available symbols and their target states"""
        transitions_info = {}
        
        if self.type == "DFA":
            current = self.current_state
            for symbol in self.symbols:
                key = (current, symbol)
                if key in self.transitions:
                    transitions_info[symbol] = next(iter(self.transitions[key]))
                else:
                    transitions_info[symbol] = current  # Stay in current state
        else:
            for symbol in self.symbols:
                targets = set()
                for state in self.current_states:
                    key = (state, symbol)
                    if key in self.transitions:
                        targets.update(self.transitions[key])
                    else:
                        targets.add(state)  # Stay in current state
                transitions_info[symbol] = self._epsilon_closure(targets)
        
        return transitions_info

    def step(self, symbol):
        """Process one input symbol and return current state(s)"""
        if symbol not in self.symbols:
            return None, f"Invalid symbol '{symbol}'"
        
        if self.type == "DFA":
            key = (self.current_state, symbol)
            if key in self.transitions:
                self.current_state = next(iter(self.transitions[key]))
            # If no transition, stay in current state
            return self.current_state, None
        else:
            next_states = set()
            for state in self.current_states:
                key = (state, symbol)
                if key in self.transitions:
                    next_states.update(self.transitions[key])
                else:
                    next_states.add(state)
            
            self.current_states = self._epsilon_closure(next_states)
            return self.current_states, None

    def is_accepted(self):
        """Check if current state(s) are accept states"""
        if self.type == "DFA":
            return self.current_state in self.accept_states
        else:
            return bool(self.current_states & self.accept_states)

def main():
    if len(sys.argv) != 2:
        print("Usage: python automaton.py <input_file>")
        return
    
    automaton = FiniteAutomaton()
    error = automaton.load_from_file(sys.argv[1])
    
    if error:
        print(error)
        return
    
    print(f"\nLoaded {automaton.type} with:")
    print(f"- States: {', '.join(sorted(automaton.states))}")
    print(f"- Symbols: {', '.join(sorted(automaton.symbols))}")
    print(f"- Start state: {automaton.start_state}")
    print(f"- Accept states: {', '.join(sorted(automaton.accept_states))}")
    
    automaton.reset()
    
    while True:
        # Display current status
        print("\n" + "="*50)
        print(f"Current state(s): {automaton.current_state if automaton.type == 'DFA' else ', '.join(sorted(automaton.current_states))}")
        
        if automaton.is_accepted():
            return
        
        # Show available transitions
        transitions = automaton.get_possible_transitions()
        print("\nAvailable transitions:")
        for symbol, target in sorted(transitions.items()):
            if automaton.type == "DFA":
                print(f"  '{symbol}': {target} (from current state)")
            else:
                print(f"  '{symbol}': {{{', '.join(sorted(target))}}}")
        
        # User input
        print("\nOptions:")
        print("  <symbol> - Input a symbol from above")
        print("  reset    - Reset automaton to start state")
        print("  quit     - Exit program")
        user_input = input("\nYour choice: ").strip().lower()
        
        if user_input == 'quit':
            break
        elif user_input == 'reset':
            automaton.reset()
            print(f"\nAutomaton reset to initial state {automaton.start_state}")
            continue
        elif user_input in automaton.symbols:
            result, error = automaton.step(user_input)
            if error:
                print(error)
            else:
                print(f"\nApplied '{user_input}' transition")
                if automaton.type == "DFA":
                    print(f"New state: {result}")
                else:
                    print(f"New states: {{{', '.join(sorted(result))}}}")
                
                if automaton.is_accepted():
                    print("★ REACHED ACCEPT STATE ★")
        else:
            print(f"\nInvalid input. Please enter one of: {', '.join(sorted(automaton.symbols))}, 'reset', or 'quit'")

if __name__ == "__main__":
    main()