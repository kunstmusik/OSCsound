<CsoundSynthesizer>
<CsInstruments>

sr=44100
ksmps=32
nchnls=2
0dbfs=1

instr 1 

kcutoff chnget "cutoff"
kres    chnget "resonance"

kcutoff port kcutoff, 0.05
kres port kres, 0.05

aout vco2 0.5, 440
aout moogladder aout, kcutoff, kres
outs aout, aout
endin

</CsInstruments>

</CsoundSynthesizer>
