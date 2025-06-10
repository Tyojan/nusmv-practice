import re
import csv
import argparse


def parse_nusmv_trace(trace_lines):
    state_pattern = re.compile(r"-> State: ([^\s]+) <-")
    var_pattern = re.compile(r"\s*([^=\s]+)\s*=\s*(.+)")

    states = []
    raw_state_vars = {}

    current_state = None

    for line in trace_lines:
        line = line.strip()
        # Match state header
        m_state = state_pattern.match(line)
        if m_state:
            current_state = m_state.group(1)
            states.append(current_state)
            raw_state_vars[current_state] = {}
            continue
        # Match variable assignment within a state
        if current_state is not None and '=' in line:
            m_var = var_pattern.match(line)
            if m_var:
                var = m_var.group(1)
                val = m_var.group(2)
                # TRUE/FALSE を T/F に省略
                if val == 'TRUE':
                    val = 'T'
                elif val == 'FALSE':
                    val = 'F'
                raw_state_vars[current_state][var] = val
    return states, raw_state_vars


def build_state_table(states, raw_state_vars):
    # Collect all variables in order of first appearance
    all_vars = []
    var_set = set()
    for st in states:
        for var in raw_state_vars.get(st, {}):
            if var not in var_set:
                var_set.add(var)
                all_vars.append(var)
    # Build list of snapshots where each snapshot only contains changed vars
    snapshots = [raw_state_vars.get(st, {}) for st in states]
    return all_vars, snapshots


def write_csv(states, all_vars, snapshots, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header: first column 'variable', then state names
        writer.writerow(['variable'] + states)
        for var in all_vars:
            row = [var]
            for snap in snapshots:
                row.append(snap.get(var, ''))
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description='Parse NuSMV trace and output CSV of state transition table (changes only)')
    parser.add_argument('input', help='Input file containing NuSMV trace')
    parser.add_argument('output', help='Output CSV file path')
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        lines = f.readlines()

    states, raw_state_vars = parse_nusmv_trace(lines)
    all_vars, snapshots = build_state_table(states, raw_state_vars)
    write_csv(states, all_vars, snapshots, args.output)
    print(f"CSV written to {args.output}")

if __name__ == '__main__':
    main()
