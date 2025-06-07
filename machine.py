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
            
            # Skip epsilon transitions - they should be in EpsilonRules
            if symbol == 'ε':
                continue
                
            if (from_state not in self.states or 
                to_state not in self.states or 
                symbol not in self.symbols):
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

    def simulate(self, input_string):
        if self.type == "DFA":
            return self._simulate_dfa(input_string)
        else:
            return self._simulate_nfa(input_string)

    def _simulate_dfa(self, input_string):
        current_state = self.start_state
        
        for symbol in input_string:
            if symbol not in self.symbols:
                return False, f"Invalid symbol '{symbol}' in input"
            
            key = (current_state, symbol)
            if key in self.transitions:
                # DFA should have exactly one transition
                current_state = next(iter(self.transitions[key]))
            else:
                # No transition defined - reject
                return False, f"No transition from '{current_state}' on '{symbol}'"
            
        return current_state in self.accept_states, current_state

    def _simulate_nfa(self, input_string):
        current_states = self._epsilon_closure({self.start_state})
        
        for symbol in input_string:
            if symbol not in self.symbols:
                return False, f"Invalid symbol '{symbol}' in input"
            
            next_states = set()
            for state in current_states:
                key = (state, symbol)
                if key in self.transitions:
                    next_states.update(self.transitions[key])
                # Note: If no transition exists, this branch dies (correct NFA behavior)
            
            # If no states remain, the string is rejected
            if not next_states:
                return False, "No valid transitions available"
                
            current_states = self._epsilon_closure(next_states)
        
        return bool(current_states & self.accept_states), current_states

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
    
    while True:
        print("\nEnter input string or 'quit':")
        user_input = input().strip()
        
        if user_input.lower() == 'quit':
            break
        
        # Process input as sequence of characters (more standard)
        # If you want space-separated symbols, use: input_symbols = user_input.split()
        input_symbols = list(user_input) if user_input else []
        accepted, result = automaton.simulate(input_symbols)
        
        if isinstance(result, set):
            result_str = ', '.join(sorted(result))
        else:
            result_str = str(result)
        
        if accepted:
            print(f"ACCEPTED (Final state(s): {result_str})")
        else:
            print(f"REJECTED (Final state(s): {result_str})")

if __name__ == "__main__":
    main()
