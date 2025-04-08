import math
from textwrap import dedent
from pathlib import Path

import pandas as pd


def prob_m_in_other_hands(p, n, N, M):
    a = sum(math.comb(M, m)*math.comb(N-n-M, n*(p-1)-m)
            for m in range(1, M+1)
            if n*(p-1) >= m)
    A = math.comb(N-n, n*(p-1))
    return a/A


M_to_card = {
    1: 'Heer',
    2: 'Dame',
    3: 'Boer',
    4: '10',
    5: '9',
    6: '8',
    7: '7',
    8: '6',
    9: '5',
    10: '4',
    11: '3',
    12: '2',
}

def main():
    for p in range(4, 7):  # spelers
        result_sheets = {}
        for n0 in range(1, 52//p+1):  # aantal startkaarten pp
            results = []
            for r in range(0, n0):   # aantal reeds gespeelde potjes
                n = n0 - r      # aantal kaarten per hand
                N = 52 - r*p    # aantal kaarten nog in alle handen + in pak
                assert N-n >= n*(p-1)  # Meer kaarten in pak + andere handen dan kaarten in andere handen
                for M in range(1, 13):
                    if N - n < M:
                        # Onvoldoende kaarten in andere handen + pak
                        continue
                    prob = prob_m_in_other_hands(p, n, N, M)
                    results.append({
                        'pot': r+1,
                        'aantal betere kaarten': M,
                        'kans op verlies': prob,
                    })
            key = f'{n0} kaart' + ('en' if n0 > 1 else '')
            result_sheets[key] = pd.DataFrame(results)

        md_txt = dedent(f"""\
        # Chinees poepen met {p} spelers

        Onderstaande tabellen tonen de **kans dat jij de hoogste kaart van een
        kleur hebt**, gegeven het aantal startkaarten van de ronde waarin je
        speelt, het hoeveelste potje je speelt binnen de ronde en het aantal
        betere kaarten die nog niet gespeeld zijn.

        Speel je bijvoorbeeld een ronde met 4 startkaarten, heb je een Harten
        Boer in de hand en is de Harten Dame al gespeeld, dan zijn er nog 2
        mogelijks betere kaarten: de Harten Heer en Harten Aas. De kans dat jij
        de hoogste Harten in handen hebt bij de start van potje 3, vind je dan
        door in de tabel van "4 kaarten" te kijken, in rij "Pot 3" en in kolom
        "2 beter".
        """)
        for sheet_name, df in result_sheets.items():
            dfp = df.pivot(columns='aantal betere kaarten', index='pot')
            md_txt += f"## {sheet_name}\n\n"
            for pot, row in dfp.iterrows():
                if pot == 1:
                    md_txt += '|    '
                    for M, _ in row.items():
                        md_txt += f'| {M[1]} beter (~{M_to_card[M[1]]})'
                    md_txt += '|\n'
                    md_txt += '|-----'
                    for M, _ in row.items():
                        md_txt += '|------------'
                    md_txt += '|\n'

                md_txt += f'| Pot {pot} '
                for M, prob in row.items():
                    if str(prob) != 'nan':
                        md_txt += f'| {(1. - prob)*100:.1f}% '
                    else:
                        md_txt += '|    '
                md_txt += '|\n'
            md_txt += "\n\n"
        Path(f'chipo_{p}_spelers.md').write_text(md_txt)


if __name__ == '__main__':
    main()
