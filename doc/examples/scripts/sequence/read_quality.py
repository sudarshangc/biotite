"""
Quality of sequence reads
=========================

This script plots the sequencing quality scores from an FASTQ file along
with the sequence (base calls).
"""

from io import StringIO
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import biotite
import biotite.sequence as seq
import biotite.sequence.io.fastq as fastq

# Sample FASTQ file from https://en.wikipedia.org/wiki/FASTQ_format
fastq_content = StringIO("""
@SEQ_ID
GATTTGGGGTTCAAAGCAGTATCGATCAAATAGTAAATCCATTTGTTCAACTCACAGTTT
+
!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65
""")

fastq_file = fastq.FastqFile(offset="Sanger")
fastq_file.read(fastq_content)
sequence = fastq_file.get_sequence("SEQ_ID")
scores = fastq_file.get_quality("SEQ_ID")
# Interpolate for smoother result
interp_score_func = interp1d(np.arange(len(sequence)), scores, kind="cubic")

figure, ax = plt.subplots(figsize=(8.0, 2.0))
# Plot the interpolated score values
x = np.linspace(0, len(sequence)-1, 500)
ax.plot(
    x, interp_score_func(x),
    marker="None", linestyle="-", color=biotite.colors["orange"]
)
# -1 to put space between Y-axis and sequence
ax.set_xlim(-1, len(sequence))
# The range of Phred scores
ax.set_ylim(0, 40)
ax.set_ylabel("Phred score")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)
# Show sequence as X-axis ticks
ax.set_xticks(np.arange(len(sequence)))
ax.set_xticklabels(sequence.symbols)
ax.xaxis.set_ticks_position("none") 
figure.tight_layout()
plt.show()