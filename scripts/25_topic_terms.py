#!/usr/bin/env python3
"""
EDU01 R1 — Step 25: recent topic emphasis per wave (input to module design)
===========================================================================
For each wave, counts how many 2021-2025 matched titles mention each term of
a fixed, a-priori list of candidate syllabus topics (device, circuit,
architecture, algorithm, application layers). The resulting ranking is used
to decide which topics each proposed module foregrounds (Section VI).
Output: data/topic_terms.csv
"""
import csv, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "data"
TOPICS = {
    "ai_hardware": {
        "SRAM compute-in-memory macros": r"\bsram\b",
        "RRAM/memristor crossbars": r"\b(rram|reram|memristor|memristive|crossbar)",
        "FPGA accelerators": r"\bfpga",
        "quantization / low precision": r"quantiz|low[- ]bit|binary|\bbit\b|precision",
        "sparsity / pruning": r"spars|prun",
        "transformers / attention": r"transformer|attention",
        "CNN/DNN inference": r"\b(cnn|dnn|convolution\w*)\b",
        "on-device training / learning": r"training|on[- ]chip learning|on[- ]device",
        "energy efficiency": r"energy|power|tops/w",
        "edge / TinyML": r"\bedge\b|tinyml|iot",
        "dataflow / systolic": r"dataflow|systolic",
        "ADC / analog readout": r"\badc\b|analog",
    },
    "neuromorphic": {
        "synaptic devices (transistors, memristors)": r"synap\w* (device|transistor)|memristor|memristive|rram",
        "spiking neuron circuits (LIF)": r"\bneuron|\blif\b|integrate[- ]and[- ]fire",
        "SNN training algorithms": r"training|learning|backprop|surrogate",
        "STDP / plasticity": r"stdp|plasticity|spike[- ]timing",
        "event-based vision": r"event|vision|dvs",
        "neuromorphic processors / chips": r"processor|chip|accelerator|architecture",
        "FPGA implementation": r"\bfpga",
        "optoelectronic / photonic": r"opto|photo|optical|light",
        "reservoir computing": r"reservoir",
        "energy efficiency": r"energy|power|low[- ]power",
    },
    "iot_security": {
        "PUF design (SRAM, ring-oscillator, arbiter)": r"\bpufs?\b|unclonable",
        "ML modelling attacks on PUFs": r"machine learning|modeling attack|modelling attack|deep learning",
        "power / EM side-channel analysis": r"side[- ]channel|power analysis|\bem\b|electromagnetic",
        "countermeasures (masking, shuffling)": r"mask|shuffl|countermeasure|protect",
        "hardware Trojans": r"trojan",
        "logic locking / obfuscation": r"lock|obfusc|camouflag",
        "authentication protocols (IoT)": r"authenticat|protocol|key (exchange|agreement)",
        "TRNG / key generation": r"\btrng|random number|key generation",
        "emerging-device PUFs (RRAM, MRAM)": r"rram|mram|memristor|fefet",
        "FPGA implementation": r"\bfpga",
    },
    "quantum_hw": {
        "quantum algorithms (VQE, QAOA, annealing)": r"variational|vqe|qaoa|anneal|algorithm",
        "quantum machine learning": r"machine learning|neural|classif|learning",
        "quantum circuits / compilation / mapping": r"circuit|compil|mapping|routing|transpil",
        "error correction / mitigation": r"error|correct|mitigat|fault[- ]tolerant|surface code",
        "cryo-CMOS control and readout electronics": r"cryo|readout|control|lna|oscillator|dac\b",
        "spin and superconducting qubits (devices)": r"spin|superconduct|transmon|qubit device|silicon",
        "noise / NISQ benchmarking": r"noise|nisq|benchmark|fidelity",
        "software stacks / programming": r"software|programming|stack|framework",
        "applications (optimisation, finance, comms)": r"optimi|portfolio|scheduling|wireless|communication",
    },
}


def main():
    titles = defaultdict(list)
    for r in csv.DictReader(open(V2 / "wave_matches.csv")):
        if 2021 <= int(r["year"]) <= 2025:
            for w in r["waves"].split(";"):
                titles[w].append(r["title"].lower())
    rows = []
    for w, tops in TOPICS.items():
        n = len(titles[w])
        for name, pat in tops.items():
            k = sum(1 for t in titles[w] if re.search(pat, t))
            rows.append([w, name, k, n, round(100 * k / n, 1)])
    rows.sort(key=lambda r: (r[0], -r[2]))
    with open(V2 / "topic_terms.csv", "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["wave", "topic", "n_titles", "n_wave_titles_2021_25", "pct"]); wr.writerows(rows)
    macro = {("iot_security", "PUF design (SRAM, ring-oscillator, arbiter)"): "tPUF",
             ("iot_security", "power / EM side-channel analysis"): "tSCA",
             ("ai_hardware", "RRAM/memristor crossbars"): "tXbar",
             ("ai_hardware", "CNN/DNN inference"): "tCNN",
             ("ai_hardware", "quantization / low precision"): "tQuant",
             ("neuromorphic", "synaptic devices (transistors, memristors)"): "tSyn",
             ("neuromorphic", "spiking neuron circuits (LIF)"): "tNeuron",
             ("quantum_hw", "quantum algorithms (VQE, QAOA, annealing)"): "tQalg",
             ("quantum_hw", "quantum circuits / compilation / mapping"): "tQcirc",
             ("quantum_hw", "cryo-CMOS control and readout electronics"): "tCryo"}
    lines = ["% generated by scripts/25_topic_terms.py — do not edit"]
    for r in rows:
        if (r[0], r[1]) in macro:
            lines.append(f"\\newcommand{{\\{macro[(r[0], r[1])]}}}{{{r[4]:.0f}}}")
    (ROOT / "manuscript" / "numbers_topics.tex").write_text("\n".join(lines) + "\n")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
